# Film RAG API

An AI-powered film search and recommendation system built with FastAPI, ChromaDB, and OpenAI. This application uses Retrieval-Augmented Generation (RAG) to provide intelligent answers about films from a PostgreSQL database, with comprehensive evaluation and testing capabilities.

## Features

- **Semantic Film Search**: Find films using natural language queries
- **AI-Powered Recommendations**: Get intelligent film suggestions based on your questions
- **RESTful API**: Clean, documented API endpoints with context-aware responses
- **Persistent Vector Storage**: ChromaDB with persistent storage for reliable data retention
- **Real-time Embeddings**: OpenAI embeddings for semantic understanding
- **Comprehensive Evaluation**: RAGAS-based evaluation framework for system performance
- **Automated Testing**: Evaluation dataset generation and performance metrics
- **Detailed Debugging**: Comprehensive logging and debugging tools

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   FastAPI App   │    │   ChromaDB      │    │   PostgreSQL    │
│   (Port 8000)   │◄──►│   (Vector DB)   │◄──►│   (Film Data)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   OpenAI API    │    │   Evaluation    │    │   RAGAS         │
│   (Embeddings)  │    │   Framework     │    │   Metrics       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Prerequisites

- Python 3.8+
- PostgreSQL database with the `dvdrental` schema
- OpenAI API key
- Google API key (optional)

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ai_rag
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp config.env.example config.env
   # Edit config.env with your actual values
   ```

4. **Configure your environment variables in `config.env`:**
   ```env
   # Database Configuration
   DATABASE_URL=postgresql://username@localhost:5432/dvdrental

   # ChromaDB Configuration
   CHROMA_COLLECTION_NAME=films

   # OpenAI Configuration
   OPENAI_API_KEY=your_openai_api_key_here
   GOOGLE_API_KEY=your_google_api_key_here
   OPENAI_EMBED_MODEL=text-embedding-3-small
   ```

## Quick Start

1. **Run data ingestion** (first time only)
   ```bash
   python3 data_ingestion/ingest.py
   ```

2. **Start the FastAPI application**
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

3. **Access the API**
   - API Documentation: http://localhost:8000/docs
   - Alternative Docs: http://localhost:8000/redoc
   - Health Check: http://localhost:8000/

## API Endpoints

### `GET /`
Health check endpoint that confirms the API is running.

**Response:**
```json
{
  "message": "Film RAG API is running. Use POST /ask to ask questions about films."
}
```

### `POST /ask`
Ask questions about films using natural language. Returns both answer and context.

**Request Body:**
```json
{
  "question": "What is Academy Dinosaur about?"
}
```

**Response:**
```json
{
  "answer": "Academy Dinosaur is an epic drama about a feminist and a mad scientist who must battle a teacher in the Canadian Rockies.",
  "context": "Title: Academy Dinosaur | Description: A Epic Drama of a Feminist And a Mad Scientist who must Battle a Teacher in The Canadian Rockies | Release Year: 2006 | Rental Rate: $0.99 | Rating: PG"
}
```

## Example Queries

Here are some example questions you can ask the API:

- **Specific Film Information:**
  - "What is Academy Dinosaur about?"
  - "Tell me about Ace Goldfinger"
  - "Describe the movie Bride Intrigue"

- **Genre and Theme Queries:**
  - "Are there any movies about dinosaurs?"
  - "Find action movies in the database"
  - "What romantic comedies are available?"

- **Character and Plot Queries:**
  - "Movies with robots in them"
  - "Films about scientists"
  - "Stories set in the Canadian Rockies"

## Project Structure

```
ai_rag/
├── main.py                           # FastAPI application entry point
├── requirements.txt                  # Python dependencies
├── config.env                       # Environment configuration
├── README.md                        # This file
├── evaluation_dataset.json          # Generated evaluation dataset
├── evaluation_results.json          # Evaluation results (generated)
├── ragas_evaluation_report.json     # RAGAS evaluation report (generated)
├── backend/
│   └── backend.py                   # RAG implementation and OpenAI integration
├── data_ingestion/
│   ├── ingest.py                    # Script to populate ChromaDB with film data
│   └── create_evaluation_dataset.py # Generate evaluation questions and answers
└── chroma_db/                       # Persistent ChromaDB storage (created automatically)
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Required |
| `CHROMA_COLLECTION_NAME` | ChromaDB collection name | `films` |
| `OPENAI_API_KEY` | OpenAI API key for embeddings | Required |
| `GOOGLE_API_KEY` | Google API key (optional) | Optional |
| `OPENAI_EMBED_MODEL` | OpenAI embedding model | `text-embedding-3-small` |

### Database Schema

The application expects a PostgreSQL database with a `film` table containing:
- `film_id` (Primary Key)
- `title` (Film title)
- `description` (Film description)
- `release_year` (Release year)
- `rental_rate` (Rental price)
- `rating` (Film rating)

## Evaluation Framework

### Overview

The system includes a comprehensive evaluation framework using RAGAS (RAG Assessment) to measure system performance across multiple metrics:

- **Faithfulness**: Measures if generated answers are faithful to provided context
- **Answer Relevancy**: Measures if generated answers are relevant to questions
- **Context Precision**: Measures if retrieved context is relevant to questions
- **Context Recall**: Measures if retrieved context contains the answer
- **Answer Correctness**: Measures correctness against ground truth
- **Answer Similarity**: Measures semantic similarity between generated and ground truth

### Evaluation Dataset

Generate a comprehensive evaluation dataset:

```bash
python3 data_ingestion/create_evaluation_dataset.py
```

This creates `evaluation_dataset.json` with:
- 100 questions (5 per film × 20 randomly selected films)
- Questions covering all film attributes (rating, year, rental rate, description, title)
- Ground truth answers for comparison

### Running Evaluations

#### Basic Evaluation
```bash
python3 evaluate_rag_system.py
```

#### RAGAS Evaluation (Comprehensive)
```bash
python3 evaluation_ragas.py
```

### Evaluation Metrics

The evaluation provides:

1. **Exact Match Accuracy**: Percentage of exact matches between expected and actual answers
2. **Partial Match Accuracy**: Percentage of high-similarity matches
3. **F1 Score**: Harmonic mean of precision and recall
4. **RAGAS Metrics**: Industry-standard RAG evaluation metrics
5. **Question Type Analysis**: Performance breakdown by question category

### Evaluation Results

Results are saved to:
- `evaluation_results.json`: Detailed results with individual question analysis
- `ragas_evaluation_report.json`: Comprehensive RAGAS evaluation report

## Data Ingestion

### Standard Ingestion

The data ingestion process:

1. **Connects to PostgreSQL** and fetches film data
2. **Creates embeddings** using OpenAI's text-embedding-3-small model
3. **Stores vectors** in ChromaDB with persistent storage
4. **Indexes 100 films** by default (configurable in `ingest.py`)

To run ingestion:
```bash
python3 data_ingestion/ingest.py
```

### Enhanced Features

- **Detailed text embedding**: Includes title, description, release year, rental rate, and rating
- **Persistent storage**: ChromaDB data persists between sessions
- **Error handling**: Graceful handling of missing data and API errors
- **Progress tracking**: Real-time progress updates during ingestion

## Testing

### Manual Testing

Test the API using curl:

```bash
# Health check
curl http://localhost:8000/

# Ask a question
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is Academy Dinosaur about?"}'
```

### Automated Testing

The API includes built-in validation and error handling:
- Input validation for question format
- Error handling for API failures
- Graceful degradation for missing data
- Comprehensive evaluation framework

### Performance Testing

Run comprehensive performance tests:

```bash
# Generate evaluation dataset
python3 data_ingestion/create_evaluation_dataset.py

# Run basic evaluation
python3 evaluate_rag_system.py

# Run RAGAS evaluation (requires OpenAI API)
python3 evaluation_ragas.py
```

## Debugging

### Debug Script

Run the debug script to check system status:

```bash
python3 debug_chroma.py
```

This script will:
- Check ChromaDB collection status
- Verify database connectivity
- Test data ingestion
- Display collection counts and sample data

### Logging

The application includes comprehensive logging that shows:
- Query processing steps
- ChromaDB collection status
- Embedding creation
- Vector search results
- OpenAI API responses
- Evaluation progress and metrics

### Common Issues

1. **"No documents found in collection"**
   - Run the data ingestion script: `python3 data_ingestion/ingest.py`

2. **Database connection errors**
   - Verify your `DATABASE_URL` in `config.env`
   - Ensure PostgreSQL is running and accessible

3. **OpenAI API errors**
   - Check your `OPENAI_API_KEY` in `config.env`
   - Verify your OpenAI account has sufficient credits

4. **ChromaDB persistence issues**
   - The application uses persistent storage in `./chroma_db/`
   - Ensure the directory has write permissions

5. **Evaluation timeouts**
   - RAGAS evaluation may timeout due to API rate limits
   - Consider running evaluations during off-peak hours
   - Check OpenAI API usage and limits

## Security Considerations

- Store API keys securely in environment variables
- Use HTTPS in production
- Implement rate limiting for production use
- Consider authentication for sensitive endpoints
- Monitor API usage and costs

## Deployment

### Development
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Production
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Docker (Future Enhancement)
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Performance Optimization

### Current Performance

Based on evaluation results, the system shows:
- **Retrieval accuracy**: Needs improvement in document retrieval
- **Answer generation**: Good when relevant context is found
- **Context relevance**: Moderate performance in finding relevant documents

### Optimization Strategies

1. **Increase retrieval count**: Retrieve more documents for better coverage
2. **Improve embeddings**: Fine-tune embedding model for domain-specific performance
3. **Enhanced prompting**: Optimize prompts for better answer generation
4. **Hybrid search**: Combine semantic and keyword search
5. **Metadata filtering**: Use film attributes for targeted retrieval

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Run evaluation scripts to ensure performance
6. Submit a pull request

## Acknowledgments

- OpenAI for providing the embedding and completion APIs
- ChromaDB for vector database functionality
- FastAPI for the web framework
- PostgreSQL for the relational database
- RAGAS for comprehensive RAG evaluation metrics

## Support

For issues and questions:
1. Check the debugging section above
2. Review the logs for error messages
3. Run the debug script to diagnose issues
4. Check evaluation results for performance insights
5. Open an issue in the repository

---

**Happy film searching!** 