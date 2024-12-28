import time
import streamlit as st

from utils import save_user, verify_duplicate_user

def input_field(input_param, type):
    """Render an input field based on the type and store the value in session state."""
    if type == 'text':
        st.session_state[input_param] = st.text_input(input_param)
    elif type == 'number':
        st.session_state[input_param] = st.number_input(input_param, step=1)

def signup_page(extra_input_params=False, confirmPass=False):
    """Render the signup page with optional extra input parameters and password confirmation."""
    if st.session_state['verifying']:
        if verify_duplicate_user(st.session_state['login_name']):
            st.error("User already exists")
            time.sleep(1)
            st.session_state['verifying'] = False
            st.rerun()
        else:
            save_user(st.session_state['login_name'], st.session_state['password'], st.session_state.get('extra_input_params', {}))
            st.success("Registration successful! Redirecting to login...")
            time.sleep(1)
            st.session_state['page'] = 'login'
            st.rerun()
    else:
        if st.button("Back to Login"):
            st.session_state['page'] = 'login'
            st.rerun()
        
        with st.empty().container(border=True):
            st.title("Sign Up Page")
            
            st.session_state['login_name'] = st.text_input("Login")
            
            st.session_state['password'] = st.text_input("Password", type='password')
            
            if confirmPass:
                confirm_password = st.text_input("Confirm Password", type='password')
            
            if extra_input_params:
                for input_param, type in st.session_state['extra_input_params'].items():
                    input_field(input_param, type)
            
            if st.session_state['login_name'] and st.session_state['password'] and \
               (not confirmPass or (confirmPass and st.session_state['password'] == confirm_password)):
                
                if extra_input_params and not all(st.session_state.get(param) for param in st.session_state['extra_input_params']):
                    st.error("Please fill in all required fields")
                else:
                    if st.button("Register"):
                        st.session_state['verifying'] = True
                        st.rerun()
            else:
                if confirmPass and st.session_state['password'] != confirm_password:
                    st.error("Passwords do not match")
                elif st.button("Register"):
                    st.error("Please fill in all required fields")