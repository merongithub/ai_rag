import json
import requests
import time
import pandas as pd
from typing import List, Dict
from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_precision,
    context_recall,
    answer_correctness,
    answer_similarity
)
from datasets import Dataset
import numpy as np
from dotenv import load_dotenv
import os

# Load environment variables from config.env
load_dotenv('config.env')

def load_evaluation_dataset(file_path: str = "evaluation_dataset.json") -> List[Dict]:
    """Load the evaluation dataset from JSON file"""
    with open(file_path, 'r') as f:
        return json.load(f)

def query_rag_system_with_context(question: str, base_url: str = "http://localhost:8000") -> Dict:
    """Query the RAG system and get both answer and context"""
    try:
        response = requests.post(
            f"{base_url}/ask",
            json={"question": question},
            timeout=30
        )
        response.raise_for_status()
        result = response.json()
        
        return {
            "answer": result["answer"],
            "context": result["context"],
            "question": question
        }
    except requests.exceptions.RequestException as e:
        print(f"❌ Error querying RAG system: {e}")
        return {
            "answer": "ERROR",
            "context": "No context available due to error",
            "question": question
        }

def create_ragas_dataset(evaluation_data: List[Dict], base_url: str = "http://localhost:8000") -> Dataset:
    """Create a RAGAS-compatible dataset from evaluation data"""
    
    print("🔄 Creating RAGAS dataset...")
    
    ragas_data = []
    
    for i, item in enumerate(evaluation_data):
        question = item["question"]
        ground_truth = item["expected_answer"]
        
        print(f"🔍 Processing question {i+1}/{len(evaluation_data)}: {question[:50]}...")
        
        # Query the RAG system
        rag_response = query_rag_system_with_context(question, base_url)
        
        # Create RAGAS-compatible entry
        ragas_entry = {
            "question": question,
            "answer": rag_response["answer"],
            "contexts": [rag_response["context"]],  # RAGAS expects list of contexts
            "ground_truth": ground_truth
        }
        
        ragas_data.append(ragas_entry)
        
        # Add delay to avoid overwhelming the server
        time.sleep(0.5)
    
    # Convert to pandas DataFrame and then to HuggingFace Dataset
    df = pd.DataFrame(ragas_data)
    dataset = Dataset.from_pandas(df)
    
    print(f"✅ Created RAGAS dataset with {len(ragas_data)} samples")
    return dataset

def run_ragas_evaluation(dataset: Dataset) -> Dict:
    """Run comprehensive RAGAS evaluation"""
    
    print("🚀 Starting RAGAS Evaluation")
    print("=" * 60)
    
    # Define metrics to evaluate
    metrics = [
        faithfulness,           # Measures if the generated answer is faithful to the provided context
        answer_relevancy,       # Measures if the generated answer is relevant to the question
        context_precision,      # Measures if the retrieved context is relevant to the question
        context_recall,         # Measures if the retrieved context contains the answer
        answer_correctness,     # Measures the correctness of the answer against ground truth
        answer_similarity       # Measures semantic similarity between generated and ground truth
    ]
    
    # Run evaluation
    print("📊 Running RAGAS metrics...")
    results = evaluate(dataset, metrics)
    
    # Extract scores
    evaluation_scores = {}
    # RAGAS returns results as a dictionary-like object
    for metric_name in ['faithfulness', 'answer_relevancy', 'context_precision', 'context_recall', 'answer_correctness', 'answer_similarity']:
        if hasattr(results, metric_name):
            score = getattr(results, metric_name)
            evaluation_scores[metric_name] = float(score)
            print(f"📈 {metric_name}: {score:.3f}")
        else:
            print(f"⚠️  {metric_name}: Not available")
            evaluation_scores[metric_name] = 0.0
    
    print("=" * 60)
    return evaluation_scores

def analyze_results_by_question_type(dataset: Dataset) -> Dict:
    """Analyze RAGAS results by question type"""
    
    print("\n📊 DETAILED ANALYSIS BY QUESTION TYPE")
    print("-" * 50)
    
    # Convert dataset back to pandas for easier analysis
    df = dataset.to_pandas()
    
    question_types = {
        "rating": [],
        "year": [],
        "rental_rate": [],
        "description": [],
        "title_by_id": []
    }
    
    # Categorize questions
    for idx, row in df.iterrows():
        question = row["question"].lower()
        if "rating" in question:
            question_types["rating"].append(idx)
        elif "year" in question or "released" in question:
            question_types["year"].append(idx)
        elif "rental rate" in question:
            question_types["rental_rate"].append(idx)
        elif "description" in question:
            question_types["description"].append(idx)
        elif "film id" in question or "id" in question:
            question_types["title_by_id"].append(idx)
    
    # Analyze each question type
    type_analysis = {}
    
    for q_type, indices in question_types.items():
        if indices:
            type_df = df.iloc[indices]
            
            # Calculate metrics for this question type
            exact_matches = sum(1 for i, row in type_df.iterrows() 
                              if row["answer"].lower().strip() == row["ground_truth"].lower().strip())
            
            # Calculate average scores (you'd need to run RAGAS on this subset)
            type_analysis[q_type] = {
                "count": len(indices),
                "exact_matches": exact_matches,
                "exact_match_rate": exact_matches / len(indices),
                "sample_questions": type_df["question"].head(3).tolist()
            }
            
            print(f"🔍 {q_type.replace('_', ' ').title()}:")
            print(f"   Questions: {len(indices)}")
            print(f"   Exact Matches: {exact_matches}/{len(indices)} ({exact_matches/len(indices)*100:.1f}%)")
            print(f"   Sample: {type_df['question'].iloc[0][:50]}...")
            print()
    
    return type_analysis

def create_detailed_report(evaluation_scores: Dict, type_analysis: Dict, dataset: Dataset) -> Dict:
    """Create a comprehensive evaluation report"""
    
    # Convert dataset to pandas and then to dict, handling numpy arrays
    df = dataset.to_pandas()
    detailed_results = []
    for _, row in df.iterrows():
        result_dict = {}
        for col in df.columns:
            value = row[col]
            # Convert numpy arrays to lists for JSON serialization
            if hasattr(value, 'tolist'):
                result_dict[col] = value.tolist()
            else:
                result_dict[col] = value
        detailed_results.append(result_dict)
    
    report = {
        "summary": {
            "total_questions": len(dataset),
            "ragas_scores": evaluation_scores,
            "question_type_analysis": type_analysis
        },
        "recommendations": generate_recommendations(evaluation_scores, type_analysis),
        "detailed_results": detailed_results
    }
    
    # Save detailed report
    with open("ragas_evaluation_report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"📁 Detailed RAGAS report saved to: ragas_evaluation_report.json")
    
    return report

def generate_recommendations(evaluation_scores: Dict, type_analysis: Dict) -> List[str]:
    """Generate recommendations based on evaluation results"""
    
    recommendations = []
    
    # Analyze RAGAS scores
    if evaluation_scores.get("faithfulness", 0) < 0.7:
        recommendations.append("Improve faithfulness: The generated answers are not well-grounded in the provided context. Consider improving the prompt or retrieval strategy.")
    
    if evaluation_scores.get("answer_relevancy", 0) < 0.7:
        recommendations.append("Improve answer relevancy: Generated answers are not sufficiently relevant to the questions. Consider refining the prompt engineering.")
    
    if evaluation_scores.get("context_precision", 0) < 0.7:
        recommendations.append("Improve context precision: Retrieved contexts are not relevant enough to the questions. Consider improving the embedding model or retrieval strategy.")
    
    if evaluation_scores.get("context_recall", 0) < 0.7:
        recommendations.append("Improve context recall: The retrieved context doesn't contain the necessary information. Consider increasing the number of retrieved documents or improving the retrieval strategy.")
    
    if evaluation_scores.get("answer_correctness", 0) < 0.7:
        recommendations.append("Improve answer correctness: Generated answers don't match the ground truth well. Consider improving the overall RAG pipeline.")
    
    # Analyze by question type
    for q_type, analysis in type_analysis.items():
        if analysis["exact_match_rate"] < 0.3:
            recommendations.append(f"Improve {q_type} questions: Only {analysis['exact_match_rate']*100:.1f}% accuracy. Consider specific optimizations for this question type.")
    
    if not recommendations:
        recommendations.append("Great performance! The RAG system is working well across all metrics.")
    
    return recommendations

def main():
    """Main evaluation function"""
    
    print("🎯 RAGAS RAG System Evaluation")
    print("=" * 60)
    
    # Load evaluation dataset
    print("📂 Loading evaluation dataset...")
    evaluation_data = load_evaluation_dataset()
    print(f"✅ Loaded {len(evaluation_data)} evaluation questions")
    
    # Create RAGAS dataset
    dataset = create_ragas_dataset(evaluation_data)
    
    # Run RAGAS evaluation
    evaluation_scores = run_ragas_evaluation(dataset)
    
    # Analyze by question type
    type_analysis = analyze_results_by_question_type(dataset)
    
    # Create comprehensive report
    report = create_detailed_report(evaluation_scores, type_analysis, dataset)
    
    # Print recommendations
    print("\n💡 RECOMMENDATIONS")
    print("-" * 30)
    for i, rec in enumerate(report["recommendations"], 1):
        print(f"{i}. {rec}")
    
    print("\n✅ RAGAS evaluation completed!")

if __name__ == "__main__":
    main() 