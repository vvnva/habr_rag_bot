import yaml
import streamlit as st
import requests
import psycopg2
import os
import bcrypt

from psycopg2 import sql
from dotenv import load_dotenv
from typing import List, Dict
from db.save_and_load_history import delete_user_messages

with open("config.yaml", "r") as file:
    config = yaml.safe_load(file)

API_URL = config['streamlit']['api_answer_link']

def clear_chat_history():
    """Очищает историю чата в Streamlit session state."""
    st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]

def handle_clear_chat():
    if not st.session_state['guest_mode']:
        delete_user_messages(st.session_state['login_name'])  
    clear_chat_history()  
    
def fetch_response_from_api(user_input: str, chat_history: List[Dict]) -> Dict:
    """Отправляет запрос в API и возвращает ответ и ссылки."""
    try:
        formatted_history = {
            "full_history": [
                {"role": msg["role"], "content": msg["content"]}
                for msg in chat_history
            ]
        }

        payload = {
            "user_query": {"query": user_input},
            "chat_history": formatted_history,
        }
        
        response = requests.post(
            API_URL,
            json=payload,
            timeout=700
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

def init_session():
    if 'authenticated' not in st.session_state:
        st.session_state['authenticated'] = False
    if 'page' not in st.session_state:
        st.session_state['page'] = 'login'
    if 'guest_mode' not in st.session_state:
        st.session_state['guest_mode'] = False
    if 'verifying' not in st.session_state:
        st.session_state['verifying'] = False
    if 'login_name' not in st.session_state:
        st.session_state['login_name'] = ""
    if 'password' not in st.session_state:
        st.session_state['password'] = ""
    if 'extra_input_params' not in st.session_state:
        st.session_state['extra_input_params'] = {}

def reset_session():
    st.session_state['authenticated'] = False
    st.session_state['page'] = 'login'
    st.session_state['guest_mode'] = False
    st.session_state['verifying'] = False
    st.session_state['login_name'] = ""
    st.session_state['password'] = ""
    st.session_state['messages'] = [{"role": "assistant", "content": "How may I assist you today?"}]
    
    for input_param in st.session_state['extra_input_params'].keys():
        if input_param not in st.session_state:
            st.session_state[input_param] = None
            
# ---------------------- DB ----------------------
load_dotenv()

db_params = {
    "dbname":  os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASS"),
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT")
}

def verify_duplicate_user(login_name):
    conn = psycopg2.connect(**db_params)
    cur = conn.cursor()
    
    cur.execute("SELECT COUNT(*) FROM users WHERE login_name = %s", (login_name,))
    count = cur.fetchone()[0]
    
    cur.close()
    conn.close()
    
    return count > 0

def authenticate_user(login_name, password):
    conn = psycopg2.connect(**db_params)
    cur = conn.cursor()
    
    # Retrieve the stored hashed password for the user
    cur.execute("SELECT hash_password FROM users WHERE login_name = %s", (login_name,))
    stored_hashed_password = cur.fetchone()
    
    cur.close()
    conn.close()

    # Check if a user with the given login_name was found
    if stored_hashed_password is None:
        return False
    
    stored_hashed_password = stored_hashed_password[0]  # Extract the hash from the tuple

    # Compare the provided password with the stored hashed password
    return bcrypt.checkpw(password.encode(), stored_hashed_password.encode())

def save_user(login_name, password, extra_input_params):
    conn = psycopg2.connect(**db_params)
    cur = conn.cursor()
    
    # Hash the password before saving
    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode('utf-8')
    
    # Base columns and values
    columns = ['login_name', 'hash_password']
    values = [login_name, hashed_password]

    # Add extra input params to the columns and values lists
    for key in extra_input_params.keys():
        columns.append(key)
        values.append(st.session_state[f'{key}'])
    
    # Dynamically build the SQL query
    columns_str = ', '.join(columns)
    placeholders = ', '.join(['%s'] * len(values))
    
    query = sql.SQL("INSERT INTO users ({}) VALUES ({})").format(
        sql.SQL(columns_str),
        sql.SQL(placeholders)
    )
    
    # Execute the query
    cur.execute(query, values)

    conn.commit()
    cur.close()
    conn.close()

def get_users():
    conn = psycopg2.connect(**db_params)
    cur = conn.cursor()
    
    cur.execute("SELECT * FROM users")
    users = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return users