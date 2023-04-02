"""FastAPI service to serve the OpenAI chatbot"""

import logging

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from db_answer import generate_answer as db_ask
from db_answer import load_faq_jsonl

load_dotenv()

logging.basicConfig(level=logging.DEBUG)

# ============================================================================
# Config
# ============================================================================

TOP_N = 5

faq = load_faq_jsonl()
faq_strings = [faq_item["prompt"] + faq_item["completion"] for faq_item in faq]

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:8081",
    "http://localhost:8082",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# Entry points
# ============================================================================


@app.get("/")
def read_root():
    return "Try visiting /docs"


# /ask post method with ability to post query
@app.post("/ask")
def ask(query: str):
    db_ask(query, faq_strings, top_n=TOP_N)
    return {"answer": db_ask(query, faq_strings)}


@app.post("/add_knowledge")
def add_knowledge(query: str, answer: str):
    faq_strings.append(query + " " + answer)
    return {"answer": "OK"}


# ============================================================================
# Main
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="localhost", port=8080)
