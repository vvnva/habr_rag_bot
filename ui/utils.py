import os
import yaml
import streamlit as st
import requests
from typing import List, Dict

with open("config.yaml", "r") as file:
    config = yaml.safe_load(file)

API_URL = config['streamlit']['api_answer_link']
rag_api_url_env = os.getenv("RAG_API_URL")
if rag_api_url_env:
    API_URL = rag_api_url_env

def clear_chat_history():
    """Очищает историю чата в Streamlit session state."""
    st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]


def fetch_response_from_api(user_input: str) -> Dict:
    """Отправляет запрос в API и возвращает ответ и ссылки."""
    try:
        response = requests.post(
            API_URL,
            json={"query": user_input},
            timeout=40
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        st.error(f"Error contacting the API: {e}")
        return {"answer": "Sorry, something went wrong!", "links": []}


def remove_duplicate_links(links: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """Удаляет дубликаты ссылок по заголовкам."""
    seen_titles = set()
    unique_links = []
    for link in links:
        if link["title"] not in seen_titles:
            unique_links.append(link)
            seen_titles.add(link["title"])
    return unique_links
