from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Tuple
from dotenv import load_dotenv

from src.vector_db.qdrant import get_qdrant_retriever
from src.llm_serving.ollama_llm import get_ollama_model
from src.graph.graph_funcs import get_compiled_graph, run_graph

load_dotenv()

app = FastAPI()
retriever = get_qdrant_retriever()
llm = get_ollama_model()
graph = get_compiled_graph(llm=llm, retriever=retriever)

class UserQuery(BaseModel):
    query: str
    
class RecordFormat(BaseModel):
    role : str | None
    content: str | None
    
class ChatHistory(BaseModel):
    full_history: List[RecordFormat]
       
class ResponseItem(BaseModel):
    title: str
    url: str

class UserResponse(BaseModel):
    answer: str
    links: List[ResponseItem]

@app.post("/rag-answer", response_model=UserResponse)
async def rag_answer(user_query: UserQuery, chat_history: ChatHistory):
    if not user_query.query:
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    
    if not chat_history.full_history:
        chat_history.full_history = [{}]

    processed_answer, docs = run_graph(graph=graph, query=user_query.query, history=chat_history.full_history)

    links = [
        ResponseItem(title=doc['title'], url=doc['link']) for doc in docs
    ]

    return UserResponse(answer=processed_answer, links=links)