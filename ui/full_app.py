import streamlit as st

from login_page import login_page
from signup_page import signup_page
from app import main
from utils import init_session, reset_session

init_session()

if st.session_state['authenticated']:
    main()
else:
    if st.session_state['page'] == 'login':
        reset_session()
        login_page(guest_mode=True)
    elif st.session_state['page'] == 'signup':
        signup_page(
            extra_input_params=False,
            confirmPass = False
        )