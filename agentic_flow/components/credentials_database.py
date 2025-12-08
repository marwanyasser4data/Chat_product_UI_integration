from local_storage import get_local_credentials_db_path
import shelve
import hashlib
from abc import ABC, abstractmethod
from utils.chainlit_logger import log_info
from typing import Literal
import asyncio

class DatabaseInterface(ABC):
    """Abstract base class for database implementations"""
    
    @staticmethod
    async def hash_password(password: str) -> str:
        """Hash password using SHA-256"""
        hasher = hashlib.sha256()
        hasher.update(password.encode('utf-8'))
        return hasher.hexdigest()
    
    @abstractmethod
    async def check_credentials(self, username: str, password: str) -> bool:
        """Check if username and password are valid"""
        pass
    
    @abstractmethod
    async def add_user(self, username: str, password: str) -> bool:
        """Add a new user to the database"""
        pass
    
    @abstractmethod
    async def delete_user(self, username: str) -> bool:
        """Delete a user from the database"""
        pass

    @abstractmethod
    async def check_user(self, username: str) -> bool:
        """check if a user exists"""
        pass

class localDatabase(DatabaseInterface):
    def __init__(self):
        self.cred_db = get_local_credentials_db_path()
        self.lock = asyncio.Lock()  
    
    def hash_password(self, password: str) -> str:
        hasher = hashlib.sha256()
        hasher.update(password.encode('utf-8'))
        hashed_value = hasher.hexdigest()
        return hashed_value

    async def check_credentials(self, username: str, password: str) -> bool:
        """Check credentials with async lock protection"""
        async with self.lock:  
            try:
                # Run blocking I/O in thread pool to not block event loop
                return await asyncio.to_thread(self._check_credentials_sync, username, password)
            except Exception as e:
                print(f"Error checking credentials: {e}")
                return False
    
    def _check_credentials_sync(self, username: str, password: str) -> bool:
        """Synchronous shelve operation"""
        with shelve.open(self.cred_db) as db:
            if username in db:
                return db[username] == self.hash_password(password)
            return False
    
    async def add_user(self, username: str, password: str) -> bool:
        """Add user with async lock protection"""
        async with self.lock:  
            try:
                return await asyncio.to_thread(self._add_user_sync, username, password)
            except Exception as e:
                print(f"Error adding user: {e}")
                return False
    
    def _add_user_sync(self, username: str, password: str) -> bool:
        """Synchronous shelve operation"""
        with shelve.open(self.cred_db) as db:
            if username in db:
                raise Exception("User already exists")
            else:
                db[username] = self.hash_password(password)
                return True
    
    async def delete_user(self, username: str) -> bool:
        """Delete user with async lock protection"""
        async with self.lock:
            try:
                return await asyncio.to_thread(self._delete_user_sync, username)
            except Exception as e:
                print(f"Error deleting user: {e}")
                return False
    
    def _delete_user_sync(self, username: str) -> bool:
        """Synchronous shelve operation"""
        with shelve.open(self.cred_db) as db:
            if username in db:
                del db[username]
                return True
            return False
    
    async def check_user(self, username: str) -> bool:
        """Check if user exists with async lock protection"""
        async with self.lock:  
            try:
                return await asyncio.to_thread(self._check_user_sync, username)
            except Exception as e:
                print(f"Error checking user: {e}")
                return False
    
    def _check_user_sync(self, username: str) -> bool:
        """Synchronous shelve operation"""
        with shelve.open(self.cred_db) as db:
            return username in db

class MongoDatabase(DatabaseInterface):
    pass


def get_credentials_db(type: Literal['on_disk', 'memory'] ):

    if type == 'on_disk':
        return localDatabase()



credentials_database = get_credentials_db('on_disk')


# Adding admin user
asyncio.run(credentials_database.add_user('admin', 'admin'))
# Adding another user
asyncio.run(credentials_database.add_user('marwan', '1234'))

log_info('Initial users asserted.')

# For testing
if __name__ == "__main__":
    credentials_database = localDatabase()
    credentials_database.add_user('marwan', '1234')

    # To test user already exist exception
    credentials_database.add_user('marwan', '1234')
    # check password test
    print(credentials_database.check_credentials('marwan', '1234'))
