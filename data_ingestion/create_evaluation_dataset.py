import os
import json
import random
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Load environment variables
load_dotenv('config.env')

# Setup database connection
DATABASE_URL = os.getenv("DATABASE_URL")

def create_evaluation_dataset():
    """Create evaluation dataset with questions and expected answers from film table"""
    
    print("🔌 Connecting to database...")
    engine = create_engine(DATABASE_URL)
    conn = engine.connect()
    
    # Fetch 20 random films from the database
    print("📊 Fetching random film data...")
    result = conn.execute(text("""
        SELECT film_id, title, description, release_year, rental_rate, rating 
        FROM film 
        ORDER BY RANDOM() 
        LIMIT 20
    """)).fetchall()
    
    print(f"✅ Fetched {len(result)} random films")
    
    evaluation_data = []
    
    # Create questions for each column
    for film in result:
        film_id = film.film_id
        title = film.title
        description = film.description
        release_year = film.release_year
        rental_rate = film.rental_rate
        rating = film.rating
        
        # Question 1: Film rating
        evaluation_data.append({
            "question": f"What is the rating of the film {title}?",
            "expected_answer": str(rating) if rating else "N/A"
        })
        
        # Question 2: Film release year
        evaluation_data.append({
            "question": f"What year was the film {title} released?",
            "expected_answer": str(release_year) if release_year else "N/A"
        })
        
        # Question 3: Film rental rate
        evaluation_data.append({
            "question": f"What is the rental rate for the film {title}?",
            "expected_answer": f"${rental_rate}" if rental_rate else "N/A"
        })
        
        # Question 4: Film description (first part)
        if description:
            # Take first 50 characters of description for a manageable answer
            short_desc = description[:50] + "..." if len(description) > 50 else description
            evaluation_data.append({
                "question": f"What is the description of the film {title}?",
                "expected_answer": short_desc
            })
        
        # Question 5: Film title by ID (reverse lookup)
        evaluation_data.append({
            "question": f"What is the title of film ID {film_id}?",
            "expected_answer": title
        })
    
    # Shuffle the evaluation data
    random.shuffle(evaluation_data)
    
    # Save to JSON file
    output_file = "evaluation_dataset.json"
    with open(output_file, 'w') as f:
        json.dump(evaluation_data, f, indent=2)
    
    print(f"✅ Created evaluation dataset with {len(evaluation_data)} questions")
    print(f"📁 Saved to: {output_file}")
    
    # Print sample questions
    print("\n📋 Sample questions:")
    for i, item in enumerate(evaluation_data[:5]):
        print(f"{i+1}. Q: {item['question']}")
        print(f"   A: {item['expected_answer']}")
        print()
    
    conn.close()
    print("🔌 Database connection closed")
    
    return evaluation_data

if __name__ == "__main__":
    create_evaluation_dataset() 