from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from backend.backend import ask

app = FastAPI(title="Film RAG API", description="AI-powered film search and recommendation system")

class Question(BaseModel):
    question: str

@app.post("/ask")
async def ask_question(question: Question):
    try:
        if not question.question.strip():
            raise HTTPException(status_code=400, detail="Question cannot be empty")
        
        response = await ask(question.question)
        return {"answer": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/")
async def root():
    return {"message": "Film RAG API is running. Use POST /ask to ask questions about films."}