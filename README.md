# 🎬 Film RAG API

An AI-powered film search and recommendation system built with FastAPI, ChromaDB, and OpenAI. This application uses Retrieval-Augmented Generation (RAG) to provide intelligent answers about films from a PostgreSQL database.

## 🚀 Features

- **Semantic Film Search**: Find films using natural language queries
- **AI-Powered Recommendations**: Get intelligent film suggestions based on your questions
- **RESTful API**: Clean, documented API endpoints
- **Persistent Vector Storage**: ChromaDB with persistent storage for reliable data retention
- **Real-time Embeddings**: OpenAI embeddings for semantic understanding
- **Comprehensive Debugging**: Detailed logging for troubleshooting

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   FastAPI App   │    │   ChromaDB      │    │   PostgreSQL    │
│   (Port 8000)   │◄──►│   (Vector DB)   │◄──►│   (Film Data)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   OpenAI API    │    │   Data          │    │   Film          │
│   (Embeddings)  │    │   Ingestion     │    │   Database      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📋 Prerequisites

- Python 3.8+
- PostgreSQL database with the `dvdrental` schema
- OpenAI API key
- Google API key (optional)

## 🛠️ Installation

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

## 🚀 Quick Start

1. **Run data ingestion** (first time only)
   ```bash
   python3 data_ingestion/ingestion.py
   ```

2. **Start the FastAPI application**
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

3. **Access the API**
   - API Documentation: http://localhost:8000/docs
   - Alternative Docs: http://localhost:8000/redoc
   - Health Check: http://localhost:8000/

## 📚 API Endpoints

### `GET /`
Health check endpoint that confirms the API is running.

**Response:**
```json
{
  "message": "Film RAG API is running. Use POST /ask to ask questions about films."
}
```

### `POST /ask`
Ask questions about films using natural language.

**Request Body:**
```json
{
  "question": "What is Academy Dinosaur about?"
}
```

**Response:**
```json
{
  "answer": "Academy Dinosaur is an epic drama about a feminist and a mad scientist who must battle a teacher in the Canadian Rockies."
}
```

## 🔍 Example Queries

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

## 🗂️ Project Structure

```
ai_rag/
├── main.py                 # FastAPI application entry point
├── requirements.txt        # Python dependencies
├── config.env             # Environment configuration
├── README.md              # This file
├── debug_chroma.py        # Debug script for ChromaDB
├── backend/
│   └── backend.py         # RAG implementation and OpenAI integration
├── data_ingestion/
│   └── ingestion.py       # Script to populate ChromaDB with film data
└── chroma_db/             # Persistent ChromaDB storage (created automatically)
```

## 🔧 Configuration

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

## 🐛 Debugging

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

### Common Issues

1. **"No documents found in collection"**
   - Run the data ingestion script: `python3 data_ingestion/ingestion.py`

2. **Database connection errors**
   - Verify your `DATABASE_URL` in `config.env`
   - Ensure PostgreSQL is running and accessible

3. **OpenAI API errors**
   - Check your `OPENAI_API_KEY` in `config.env`
   - Verify your OpenAI account has sufficient credits

4. **ChromaDB persistence issues**
   - The application uses persistent storage in `./chroma_db/`
   - Ensure the directory has write permissions

## 🔄 Data Ingestion

The data ingestion process:

1. **Connects to PostgreSQL** and fetches film data
2. **Creates embeddings** using OpenAI's text-embedding-3-small model
3. **Stores vectors** in ChromaDB with persistent storage
4. **Indexes 100 films** by default (configurable in `ingestion.py`)

To re-run ingestion:
```bash
python3 data_ingestion/ingestion.py
```

## 🧪 Testing

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

## 🔒 Security Considerations

- Store API keys securely in environment variables
- Use HTTPS in production
- Implement rate limiting for production use
- Consider authentication for sensitive endpoints

## 🚀 Deployment

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

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request


## 🙏 Acknowledgments

- OpenAI for providing the embedding and completion APIs
- ChromaDB for vector database functionality
- FastAPI for the web framework
- PostgreSQL for the relational database

## 📞 Support

For issues and questions:
1. Check the debugging section above
2. Review the logs for error messages
3. Run the debug script to diagnose issues
4. Open an issue in the repository

---

**Happy film searching! 🎬✨** 