import time
import streamlit as st
from utils import authenticate_user
from save_and_load_history import load_session_history

# Pages
def login_page(guest_mode=False):
    with st.empty().container(border=True):
        col1, _, col2 = st.columns([10,1,10])
        
        with col1:
            st.write("")
            st.write("")
            st.image("data/habar.png") # 
        
        with col2:
            st.title("Login Page")

            login_name = st.text_input("Login")
            password = st.text_input("Password", type="password")

            if st.button("Login"):
                time.sleep(2)
                if not (login_name and password):
                    st.error("Please provide login name and password")
                elif authenticate_user(login_name, password):
                    st.session_state['login_name'] = login_name
                    st.session_state['authenticated'] = True
                    st.session_state['page'] = 'app'
                    st.session_state['messages'] = load_session_history(login_name)
                    st.rerun()
                else:
                    st.error("Invalid login credentials")

            if st.button("Sign Up"):
                st.session_state['page'] = 'signup'
                st.rerun()
                
            if guest_mode:
                if st.button("Continue as Guest"):
                    st.session_state['guest_mode'] = True
                    st.session_state['authenticated'] = True
                    st.session_state['page'] = 'app'
                    st.rerun()