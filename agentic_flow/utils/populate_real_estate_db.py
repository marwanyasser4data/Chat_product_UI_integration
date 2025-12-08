"""
Real Estate MCP Database Seeder - Direct PostgreSQL Execution from CSV
"""

from datetime import datetime
from typing import Dict, List, Tuple
import os
import csv
import psycopg2
from psycopg2.extensions import connection
from dotenv import load_dotenv
import pandas as pd
# Load environment variables
load_dotenv()
from local_storage import get_local_real_estate_data
# Configuration
CSV_FILE_PATH = get_local_real_estate_data()


def get_pg_connection() -> connection:
    """Create and return a connection to the PostgreSQL database."""
    conn = psycopg2.connect(
        host=os.getenv("POSTGRES_HOST"),
        port=os.getenv("POSTGRES_PORT"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        database=os.getenv("POSTGRES_DB"),
    )
    return conn


class RealEstateSeeder:
    """Seed real estate database with data from CSV."""
    
    def __init__(self, csv_path: str):
        self.csv_path = csv_path
        self.conn = None
        self.cursor = None
    
    def seed(self) -> Dict:
        """Execute complete database seeding operation."""
        try:
            self.conn = get_pg_connection()
            self.cursor = self.conn.cursor()
            
            print("🗑️  Dropping existing tables...")
            self._drop_tables()
            
            print("🏗️  Creating tables...")
            self._create_tables()
            
            print("📊 Reading CSV data...")
            apartments_data = self._read_csv()
            
            print(f"🏠 Inserting {len(apartments_data)} apartments...")
            inserted_count = self._insert_apartments(apartments_data)
            
            self.conn.commit()
            print("✅ Database seeding completed successfully!")
            
            return self._generate_summary(inserted_count, apartments_data)
            
        except Exception as e:
            if self.conn:
                self.conn.rollback()
            print(f"❌ Error: {e}")
            raise
        finally:
            if self.cursor:
                self.cursor.close()
            if self.conn:
                self.conn.close()
    
    def _drop_tables(self):
        """Drop all existing tables."""
        tables = ["apartments"]
        for table in tables:
            self.cursor.execute(f"DROP TABLE IF EXISTS {table} CASCADE")
    
    def _create_tables(self):
        """Create all required tables."""
        
        # apartments table
        self.cursor.execute("""
            CREATE TABLE apartments (
                id SERIAL PRIMARY KEY,
                price BIGINT,
                price_category TEXT,
                type TEXT,
                beds INTEGER,
                baths INTEGER,
                address TEXT,
                furnishing TEXT,
                completion_status TEXT,
                post_date DATE,
                average_rent BIGINT,
                building_name TEXT,
                year_of_completion INTEGER,
                total_parking_spaces INTEGER,
                total_floors INTEGER,
                total_building_area_sqft BIGINT,
                elevators INTEGER,
                area_name TEXT,
                city TEXT,
                country TEXT,
                latitude DOUBLE PRECISION,
                longitude DOUBLE PRECISION,
                purpose TEXT,
                created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now()
            )
        """)
        
        # Create indexes for common queries
        self.cursor.execute("""
            CREATE INDEX idx_apartments_city ON apartments(city)
        """)
        self.cursor.execute("""
            CREATE INDEX idx_apartments_area ON apartments(area_name)
        """)
        self.cursor.execute("""
            CREATE INDEX idx_apartments_type ON apartments(type)
        """)
        self.cursor.execute("""
            CREATE INDEX idx_apartments_purpose ON apartments(purpose)
        """)
        self.cursor.execute("""
            CREATE INDEX idx_apartments_price ON apartments(price)
        """)
    
    def _read_csv(self) -> List[Dict]:
        """Read and parse CSV file using pandas."""
        
        # Read CSV
        df = pd.read_csv(self.csv_path, encoding='utf-8')
        
        # Convert data types
        df['price'] = pd.to_numeric(df['price'], errors='coerce')
        df['beds'] = pd.to_numeric(df['beds'], errors='coerce')
        df['baths'] = pd.to_numeric(df['baths'], errors='coerce')
        df['average_rent'] = pd.to_numeric(df['average_rent'], errors='coerce')
        df['year_of_completion'] = pd.to_numeric(df['year_of_completion'], errors='coerce')
        df['total_parking_spaces'] = pd.to_numeric(df['total_parking_spaces'], errors='coerce')
        df['total_floors'] = pd.to_numeric(df['total_floors'], errors='coerce')
        df['total_building_area_sqft'] = pd.to_numeric(df['total_building_area_sqft'], errors='coerce')
        df['elevators'] = pd.to_numeric(df['elevators'], errors='coerce')
        
        df['latitude'] = pd.to_numeric(df['Latitude'], errors='coerce')
        df['longitude'] = pd.to_numeric(df['Longitude'], errors='coerce')
        
        # Parse dates
        df['post_date'] = pd.to_datetime(df['post_date'], errors='coerce')
        
        # Strip whitespace from string columns
        string_columns = ['price_category', 'type', 'address', 'furnishing', 
                        'completion_status', 'building_name', 'area_name', 
                        'city', 'country', 'purpose']
        
        for col in string_columns:
            df[col] = df[col].astype(str).str.strip()
            df[col] = df[col].replace('', None).replace('nan', None)
        
        # Rename latitude/longitude to match your schema
        df = df.rename(columns={'Latitude': 'latitude', 'Longitude': 'longitude'})
        
        # Convert to list of dictionaries
        apartments = df.to_dict('records')
        
        return apartments
    
    def _insert_apartments(self, apartments_data: List[Dict]) -> int:
        """Insert property data in batches."""
        batch_size = 1000
        inserted_count = 0
        
        for i in range(0, len(apartments_data), batch_size):
            batch = apartments_data[i:i + batch_size]
            self._execute_property_batch(batch)
            inserted_count += len(batch)
            
            if inserted_count % 1000 == 0:
                print(f"   Inserted {inserted_count}/{len(apartments_data)} apartments...")
        
        return inserted_count
    
    def _execute_property_batch(self, batch: List[Dict]):
        """Execute batch insert for apartments."""
        query = """
            INSERT INTO apartments (
                price, price_category, type, beds, baths, address,
                furnishing, completion_status, post_date, average_rent,
                building_name, year_of_completion, total_parking_spaces,
                total_floors, total_building_area_sqft, elevators,
                area_name, city, country, latitude, longitude, purpose
            )
            VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
        """
        
        values = [
            (
                p['price'], p['price_category'], p['type'], p['beds'],
                p['baths'], p['address'], p['furnishing'],
                p['completion_status'], p['post_date'], p['average_rent'],
                p['building_name'], p['year_of_completion'],
                p['total_parking_spaces'], p['total_floors'],
                p['total_building_area_sqft'], p['elevators'],
                p['area_name'], p['city'], p['country'],
                p['latitude'], p['longitude'], p['purpose']
            )
            for p in batch
        ]
        
        self.cursor.executemany(query, values)
    
    def _generate_summary(self, inserted_count: int, apartments_data: List[Dict]) -> Dict:
        """Generate execution summary with statistics."""
        
        # Calculate statistics
        cities = set(p['city'] for p in apartments_data if p['city'])
        areas = set(p['area_name'] for p in apartments_data if p['area_name'])
        property_types = set(p['type'] for p in apartments_data if p['type'])
        purposes = set(p['purpose'] for p in apartments_data if p['purpose'])
        
        prices = [p['price'] for p in apartments_data if p['price'] and p['price'] > 0]
        avg_price = sum(prices) / len(prices) if prices else 0
        min_price = min(prices) if prices else 0
        max_price = max(prices) if prices else 0
        
        return {
            "total_apartments_inserted": inserted_count,
            "unique_cities": len(cities),
            "unique_areas": len(areas),
            "property_types": list(property_types),
            "purposes": list(purposes),
            "price_statistics": {
                "average": round(avg_price, 2),
                "min": min_price,
                "max": max_price
            },
            "cities": sorted(list(cities)),
        }
    
    @staticmethod
    def _parse_int(value) -> int:
        """Safely parse integer value."""
        if not value or value == '':
            return 0
        try:
            return int(float(value))
        except (ValueError, TypeError):
            return 0
    
    @staticmethod
    def _parse_float(value) -> float:
        """Safely parse float value."""
        if not value or value == '':
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None
    
    @staticmethod
    def _parse_date(value) -> str:
        """Safely parse date value."""
        if not value or value == '':
            return None
        try:
            # Assuming format YYYY-MM-DD
            datetime.strptime(value, '%Y-%m-%d')
            return value
        except (ValueError, TypeError):
            return None


def main():
    """Main execution function."""
    import json
    
    print("🚀 Starting Real Estate MCP Database Seeder\n")
    
    if not os.path.exists(CSV_FILE_PATH):
        print(f"❌ Error: CSV file not found at {CSV_FILE_PATH}")
        print("Please update CSV_FILE_PATH variable with the correct path.")
        return
    
    seeder = RealEstateSeeder(CSV_FILE_PATH)
    summary = seeder.seed()
    
    print("\n" + "="*50)
    print("Summary:")
    print(json.dumps(summary, indent=2))
    print("="*50)


if __name__ == "__main__":
    main()