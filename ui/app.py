import streamlit as st
import time

from utils import fetch_response_from_api, handle_clear_chat, remove_duplicate_links, reset_session
from save_and_load_history import save_message

def main():
    st.set_page_config(page_title="💬 Habr Chat Bot")

    with st.sidebar:
        st.title('Habr Chat Bot')
        st.write(
            """Чатбот на основе RAG по Habr статьям.
            """
        )
        st.button('Clear Chat History', on_click=handle_clear_chat)
        if st.session_state['guest_mode']:
            st.subheader("Guest Mode")
            
            if st.button("Login"):
                reset_session()
                st.rerun()
                
        else:
            if st.button("Logout"):
                reset_session()
                st.rerun()
 
        st.markdown(
            '<a href="https://github.com/vvnva/habr_rag_bot" target="_blank" rel="HABR RAG Bot">'
            '<img src="https://badgen.net/badge/icon/GitHub?icon=github&amp;label=HABR RAG Bot" alt="GitHub">'
            "</a>",
            unsafe_allow_html=True,
        )
            
    st.title("Habr Chat Bot")

    if "messages" not in st.session_state.keys():
        st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]

    for msg in st.session_state.messages:
        role = msg.get("role", "") 
        content = msg.get("content", "")
        links = msg.get("links", [])
        with st.chat_message(role):
            st.write(content)
            if links:
                st.markdown("**Related Links:**", unsafe_allow_html=True)
                for link in links:
                    st.link_button(link["title"], link["url"])

    if prompt := st.chat_input():
        if not st.session_state['guest_mode']:
            save_message(login_name=st.session_state['login_name'],role="user",content=prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                curr_history = st.session_state.messages
                api_response = fetch_response_from_api(prompt, curr_history)
                bot_response = api_response.get("answer", "No response received.")
                links = api_response.get("links", [])
                links = remove_duplicate_links(links)
                
                placeholder = st.empty()
                full_response = ""
                for char in bot_response:
                    full_response += char
                    time.sleep(0.01) 
                    placeholder.markdown(full_response)

                st.markdown("**Related Links:**", unsafe_allow_html=True)

                for link in links:
                    st.link_button(link["title"], link["url"])
                    
        if not st.session_state['guest_mode']:
            save_message(login_name=st.session_state['login_name'],role="assistant",content=full_response, links=links)
        message = {"role": "assistant", "content": full_response, "links": links}
        st.session_state.messages.append(message)
        
    st.session_state
    
if __name__ == "__main__":
    main()
