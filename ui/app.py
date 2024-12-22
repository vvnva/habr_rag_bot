import streamlit as st
import time

from utils import fetch_response_from_api, clear_chat_history, remove_duplicate_links


def main():
    st.set_page_config(page_title="💬 Habr Chat Bot")

    with st.sidebar:
        st.title('Habr Chat Bot')
        st.write(
            """Чатбот на основе RAG по Habr статьям.
            """
        )
        st.button('Clear Chat History', on_click=clear_chat_history)

    st.title("Habr Chat Bot")

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

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                api_response = fetch_response_from_api(prompt)
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

        message = {"role": "assistant", "content": full_response}
        st.session_state.messages.append(message)

if __name__ == "__main__":
    main()
