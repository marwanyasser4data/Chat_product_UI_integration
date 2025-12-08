import requests
import json

BASE_URL = 'http://localhost:5000'
SESSION = requests.Session()

def login(username, password):
    print(f"Logging in as {username}...")
    response = SESSION.post(f'{BASE_URL}/admin/login', json={
        'username': username,
        'password': password
    })
    if response.status_code == 200 and response.json().get('success'):
        print("Login successful")
        return True
    else:
        print(f"Login failed: {response.text}")
        return False

def get_users():
    print("Fetching users...")
    response = SESSION.get(f'{BASE_URL}/api/users')
    if response.status_code == 200:
        users = response.json().get('users', [])
        print(f"Found {len(users)} users: {[u['username'] for u in users]}")
        return users
    else:
        print(f"Failed to get users: {response.text}")
        return []

def create_user(username, password, name, role='user'):
    print(f"Creating user {username}...")
    response = SESSION.post(f'{BASE_URL}/api/users', json={
        'username': username,
        'password': password,
        'name': name,
        'role': role
    })
    if response.status_code == 200:
        print("User created successfully")
        return True
    else:
        print(f"Failed to create user: {response.text}")
        return False

def update_user(username, name, role):
    print(f"Updating user {username}...")
    response = SESSION.put(f'{BASE_URL}/api/users/{username}', json={
        'name': name,
        'role': role
    })
    if response.status_code == 200:
        print("User updated successfully")
        return True
    else:
        print(f"Failed to update user: {response.text}")
        return False

def delete_user(username):
    print(f"Deleting user {username}...")
    response = SESSION.delete(f'{BASE_URL}/api/users/{username}')
    if response.status_code == 200:
        print("User deleted successfully")
        return True
    else:
        print(f"Failed to delete user: {response.text}")
        return False

def run_tests():
    # 1. Login
    if not login('admin', 'admin'):
        return

    # 2. Get initial users
    users = get_users()
    initial_count = len(users)

    # 3. Create new user
    test_user = 'test_user_123'
    if create_user(test_user, 'password123', 'Test User', 'user'):
        # Verify creation
        users = get_users()
        if len(users) == initial_count + 1:
            print("Verification: User count increased")
        else:
            print("Verification FAILED: User count did not increase")

    # 4. Update user
    if update_user(test_user, 'Updated Name', 'admin'):
        # Verify update
        users = get_users()
        updated_user = next((u for u in users if u['username'] == test_user), None)
        if updated_user and updated_user['name'] == 'Updated Name' and updated_user['role'] == 'admin':
             print("Verification: User updated correctly")
        else:
             print("Verification FAILED: User not updated correctly")

    # 5. Delete user
    if delete_user(test_user):
        # Verify deletion
        users = get_users()
        if len(users) == initial_count:
            print("Verification: User count returned to initial")
        else:
            print("Verification FAILED: User count incorrect")

if __name__ == '__main__':
    try:
        run_tests()
    except Exception as e:
        print(f"An error occurred: {e}")
        print("Make sure the server is running on http://localhost:5000")
