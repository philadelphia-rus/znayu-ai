import json
import os

from dotenv import load_dotenv
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


def load_faq_jsonl(faq_path: str = "src/knowledge.jsonl") -> list[dict]:
    with open(faq_path, encoding="utf-8") as f:
        faq = [json.loads(line) for line in f]
    return faq


def load_stopwords(path: str = "src/tfidf_stopwords.txt") -> list[str]:
    res = []
    for line in open(path, encoding="utf-8"):
        res.append(line.strip())
    return res


def baseline_get_relevant_faq(
    query: str, faq_strings: list[str], top_n: int = 5
) -> list:
    """Calculate cosine similarity between query and faq
    and return most relevant faq"""
    # https://www.machinelearningplus.com/nlp/cosine-similarity/

    # Step 1: Extract keywords from query
    # Create the Document Term Matrix
    stopwords_ru = load_stopwords()
    count_vectorizer = TfidfVectorizer(stop_words=stopwords_ru)
    sparse_matrix = count_vectorizer.fit_transform(faq_strings)

    # Step 2: Calculate cosine similarity between query and faq
    query_vector = count_vectorizer.transform([query])
    cosine_similarities = cosine_similarity(
        query_vector, sparse_matrix
    ).flatten()

    # Step 3: Return top_n most relevant faq
    offset = top_n - 1
    related_docs_indices = cosine_similarities.argsort()[:-offset:-1]
    return [faq_strings[i] for i in related_docs_indices]


def generate_answer(
    query: str,
    faq_strings: list[str],
    top_n: int = 5,
    history: list[dict] = None,
):
    # Step 1 get relevant FAQ if first
    related_faqs = baseline_get_relevant_faq(query, faq_strings, top_n=top_n)

    # Step 2 use ChatGPT to generate answer based on query and faq answer
    import openai

    openai.api_key = OPENAI_API_KEY
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "Привет, я чат-бот женского пола,"
                "который поможет тебе с ответами на вопросы.",
            },
            {
                "role": "user",
                "content": f"""Привет, вот база данных"""
                f"""часто задаваемых вопросов: {related_faqs}\n"""
                f"""На их основе, ответь на следующий вопрос: {query}\n"""
                f"""Если имея эти факты нельзя ответить вопрос, попроси меня
                сформулировать вопрос иначе.\n""",
            },
        ],
        max_tokens=1000,
        stop=[" END"],
        temperature=0.69,
    )
    # Find the first response from the chatbot
    # that has text in it (some responses may not have text)
    for choice in response.choices:
        if "text" in choice:
            return choice.text

    answer = response.choices[0].message.content

    # If no response with text is found, return
    # the first response's content (which may be empty)
    return answer
