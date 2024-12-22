import streamlit as st
from streamlit_chat import message
import os
import time

def clear_chat_history():
    st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]

def generate_bot_response(user_input):
    return f"You said: {user_input}. That's interesting!"

def main():
    st.set_page_config(page_title="🪬💬 Habr Chat Bot")

    with st.sidebar:
        st.title('🪬💬 Habr Chat Bot')
        st.button('Clear Chat History', on_click=clear_chat_history)

    if "messages" not in st.session_state.keys():
        st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]

    for msg in st.session_state.messages:
        role = msg.get("role", "assistant") 
        content = msg.get("content", "")
        with st.chat_message(role):
            st.write(content)


    if prompt := st.chat_input():
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)


    if st.session_state.messages[-1].get("role") != "assistant":
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                time.sleep(2) 
                response = generate_bot_response(prompt)
                st.write(response)
        message = {"role": "assistant", "content": response}
        st.session_state.messages.append(message)


if __name__ == "__main__":
    main()
