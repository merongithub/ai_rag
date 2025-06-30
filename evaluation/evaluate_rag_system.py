import json
import requests
import time
from difflib import SequenceMatcher
import re
from typing import List, Dict, Tuple

def load_evaluation_dataset(file_path: str = "evaluation_dataset.json") -> List[Dict]:
    """Load the evaluation dataset from JSON file"""
    with open(file_path, 'r') as f:
        return json.load(f)

def query_rag_system(question: str, base_url: str = "http://localhost:8000") -> str:
    """Query the RAG system's /ask endpoint"""
    try:
        response = requests.post(
            f"{base_url}/ask",
            json={"question": question},
            timeout=30
        )
        response.raise_for_status()
        return response.json()["answer"]
    except requests.exceptions.RequestException as e:
        print(f"❌ Error querying RAG system: {e}")
        return "ERROR"

def normalize_text(text: str) -> str:
    """Normalize text for comparison by removing extra whitespace and converting to lowercase"""
    if not text:
        return ""
    # Remove extra whitespace and convert to lowercase
    normalized = re.sub(r'\s+', ' ', text.strip()).lower()
    # Remove punctuation for some comparisons
    normalized_no_punct = re.sub(r'[^\w\s]', '', normalized)
    return normalized, normalized_no_punct

def exact_match_score(expected: str, actual: str) -> bool:
    """Check if expected and actual answers match exactly (case-insensitive)"""
    expected_norm, _ = normalize_text(expected)
    actual_norm, _ = normalize_text(actual)
    return expected_norm == actual_norm

def partial_match_score(expected: str, actual: str, threshold: float = 0.8) -> bool:
    """Check if expected and actual answers have high similarity"""
    expected_norm, expected_no_punct = normalize_text(expected)
    actual_norm, actual_no_punct = normalize_text(actual)
    
    # Try different normalization levels
    similarity1 = SequenceMatcher(None, expected_norm, actual_norm).ratio()
    similarity2 = SequenceMatcher(None, expected_no_punct, actual_no_punct).ratio()
    
    return max(similarity1, similarity2) >= threshold

def calculate_f1_score(expected: str, actual: str) -> float:
    """Calculate F1 score between expected and actual answers"""
    expected_norm, expected_no_punct = normalize_text(expected)
    actual_norm, actual_no_punct = normalize_text(actual)
    
    # Split into words for token-level comparison
    expected_words = set(expected_no_punct.split())
    actual_words = set(actual_no_punct.split())
    
    if not expected_words and not actual_words:
        return 1.0
    if not expected_words or not actual_words:
        return 0.0
    
    # Calculate precision and recall
    intersection = expected_words.intersection(actual_words)
    precision = len(intersection) / len(actual_words) if actual_words else 0
    recall = len(intersection) / len(expected_words) if expected_words else 0
    
    # Calculate F1 score
    if precision + recall == 0:
        return 0.0
    return 2 * (precision * recall) / (precision + recall)

def evaluate_rag_system(evaluation_data: List[Dict], base_url: str = "http://localhost:8000") -> Dict:
    """Evaluate the RAG system using the evaluation dataset"""
    
    print("🚀 Starting RAG System Evaluation")
    print(f"📊 Total questions to evaluate: {len(evaluation_data)}")
    print(f"🌐 RAG System URL: {base_url}")
    print("-" * 60)
    
    results = []
    exact_matches = 0
    partial_matches = 0
    f1_scores = []
    
    for i, item in enumerate(evaluation_data):
        question = item["question"]
        expected_answer = item["expected_answer"]
        
        print(f"🔍 Question {i+1}/{len(evaluation_data)}: {question}")
        
        # Query the RAG system
        actual_answer = query_rag_system(question, base_url)
        
        # Calculate metrics
        exact_match = exact_match_score(expected_answer, actual_answer)
        partial_match = partial_match_score(expected_answer, actual_answer)
        f1_score = calculate_f1_score(expected_answer, actual_answer)
        
        # Update counters
        if exact_match:
            exact_matches += 1
        if partial_match:
            partial_matches += 1
        f1_scores.append(f1_score)
        
        # Store result
        result = {
            "question": question,
            "expected": expected_answer,
            "actual": actual_answer,
            "exact_match": exact_match,
            "partial_match": partial_match,
            "f1_score": f1_score
        }
        results.append(result)
        
        # Print result
        status = "✅" if exact_match else "❌"
        print(f"   {status} Expected: {expected_answer}")
        print(f"   📝 Actual: {actual_answer}")
        print(f"   📊 F1 Score: {f1_score:.3f}")
        print()
        
        # Add small delay to avoid overwhelming the server
        time.sleep(0.5)
    
    # Calculate overall metrics
    total_questions = len(evaluation_data)
    exact_match_accuracy = exact_matches / total_questions
    partial_match_accuracy = partial_matches / total_questions
    average_f1_score = sum(f1_scores) / len(f1_scores)
    
    # Print summary
    print("=" * 60)
    print("📈 EVALUATION RESULTS SUMMARY")
    print("=" * 60)
    print(f"📊 Total Questions: {total_questions}")
    print(f"✅ Exact Matches: {exact_matches}")
    print(f"🔍 Partial Matches: {partial_matches}")
    print(f"📈 Exact Match Accuracy: {exact_match_accuracy:.3f} ({exact_match_accuracy*100:.1f}%)")
    print(f"📈 Partial Match Accuracy: {partial_match_accuracy:.3f} ({partial_match_accuracy*100:.1f}%)")
    print(f"📈 Average F1 Score: {average_f1_score:.3f}")
    print("=" * 60)
    
    # Save detailed results
    detailed_results = {
        "summary": {
            "total_questions": total_questions,
            "exact_matches": exact_matches,
            "partial_matches": partial_matches,
            "exact_match_accuracy": exact_match_accuracy,
            "partial_match_accuracy": partial_match_accuracy,
            "average_f1_score": average_f1_score
        },
        "detailed_results": results
    }
    
    with open("evaluation_results.json", "w") as f:
        json.dump(detailed_results, f, indent=2)
    
    print(f"📁 Detailed results saved to: evaluation_results.json")
    
    return detailed_results

def analyze_results_by_question_type(results: List[Dict]) -> Dict:
    """Analyze results by question type (rating, year, rental rate, etc.)"""
    
    question_types = {
        "rating": [],
        "year": [],
        "rental_rate": [],
        "description": [],
        "title_by_id": []
    }
    
    for result in results:
        question = result["question"].lower()
        if "rating" in question:
            question_types["rating"].append(result)
        elif "year" in question or "released" in question:
            question_types["year"].append(result)
        elif "rental rate" in question:
            question_types["rental_rate"].append(result)
        elif "description" in question:
            question_types["description"].append(result)
        elif "film id" in question or "id" in question:
            question_types["title_by_id"].append(result)
    
    print("\n📊 RESULTS BY QUESTION TYPE")
    print("-" * 40)
    
    for q_type, type_results in question_types.items():
        if type_results:
            exact_matches = sum(1 for r in type_results if r["exact_match"])
            avg_f1 = sum(r["f1_score"] for r in type_results) / len(type_results)
            print(f"🔍 {q_type.replace('_', ' ').title()}:")
            print(f"   Questions: {len(type_results)}")
            print(f"   Exact Match: {exact_matches}/{len(type_results)} ({exact_matches/len(type_results)*100:.1f}%)")
            print(f"   Avg F1 Score: {avg_f1:.3f}")
            print()

if __name__ == "__main__":
    # Load evaluation dataset
    print("📂 Loading evaluation dataset...")
    evaluation_data = load_evaluation_dataset()
    
    # Run evaluation
    results = evaluate_rag_system(evaluation_data)
    
    # Analyze by question type
    analyze_results_by_question_type(results["detailed_results"]) 