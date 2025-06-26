#!/usr/bin/env python3
"""
Script to check PostgreSQL film table and get top 100 films ordered by film_id
"""

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Load environment variables
load_dotenv('config.env')

def check_postgres_films():
    print("🔍 Checking PostgreSQL Film Table")
    print("=" * 50)
    
    try:
        # Connect to PostgreSQL
        database_url = os.getenv("DATABASE_URL")
        print(f"🔌 Connecting to: {database_url}")
        
        engine = create_engine(database_url)
        conn = engine.connect()
        
        # Get total count
        count_result = conn.execute(text("SELECT COUNT(*) FROM film")).fetchone()
        total_films = count_result[0]
        print(f"📊 Total films in database: {total_films}")
        
        # Get top 100 films ordered by film_id
        print("\n🎬 Top 100 Films (ordered by film_id):")
        print("-" * 80)
        
        result = conn.execute(text("""
            SELECT film_id, title, description, release_year, rental_rate, rating
            FROM film 
            ORDER BY film_id 
            LIMIT 100
        """)).fetchall()
        
        print(f"{'ID':<5} {'Title':<30} {'Year':<6} {'Rate':<6} {'Rating':<8} {'Description'}")
        print("-" * 80)
        
        for row in result:
            film_id = row.film_id
            title = row.title[:28] + ".." if len(row.title) > 30 else row.title
            year = row.release_year or "N/A"
            rate = f"${row.rental_rate}" if row.rental_rate else "N/A"
            rating = row.rating or "N/A"
            description = row.description[:50] + "..." if row.description and len(row.description) > 50 else (row.description or "No description")
            
            print(f"{film_id:<5} {title:<30} {year:<6} {rate:<6} {rating:<8} {description}")
        
        print(f"\n✅ Retrieved {len(result)} films from PostgreSQL database")
        
        # Close connection
        conn.close()
        print("🔌 Database connection closed")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n💡 Troubleshooting tips:")
        print("1. Make sure PostgreSQL is running")
        print("2. Check if the dvdrental database exists")
        print("3. Verify your DATABASE_URL in config.env")
        print("4. Ensure you have access to the database")

if __name__ == "__main__":
    check_postgres_films() 