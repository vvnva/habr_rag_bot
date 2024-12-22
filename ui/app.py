import streamlit as st
from streamlit_chat import message
import time


def clear_chat_history():
    st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]


def generate_bot_response(user_input):
    return f"You said: {user_input}. That's interesting!"


def generate_links():
    """
    Placeholder function to generate links related to the bot's response.
    Replace this with actual logic to fetch relevant links.
    """
    return [
        {"title": "Habr Article 1", "url": "https://habr.com/article1"},
        {"title": "Habr Article 2", "url": "https://habr.com/article2"},
        {"title": "Habr Article 3", "url": "https://habr.com/article3"}
    ]


def render_link_button(link):
    """Custom button for a link"""
    st.link_button(link["title"], link["url"])


def main():
    st.set_page_config(page_title="🪬💬 Habr Chat Bot")


    with st.sidebar:
        st.title('🪬💬 Habr Chat Bot')
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


    if st.session_state.messages[-1].get("role") != "assistant":
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                time.sleep(1) 
                response = generate_bot_response(prompt)
                placeholder = st.empty()
                full_response = ""
                for char in response:
                    full_response += char
                    time.sleep(0.05)
                    placeholder.markdown(full_response)


                st.markdown("**Related Links:**", unsafe_allow_html=True)
                links = generate_links()
                for link in links:
                    render_link_button(link)

        message = {"role": "assistant", "content": full_response}
        st.session_state.messages.append(message)

        
if __name__ == "__main__":
    main()
