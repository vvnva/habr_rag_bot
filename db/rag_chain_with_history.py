from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain.chains import create_history_aware_retriever

from save_and_load_history import load_session_history,save_message

contextualize_q_system_prompt = """Учитывая историю чатов и последний вопрос пользователя, который может ссылаться на контекст в истории чата, \
                                сформулируй отдельный вопрос, который может быть понятбез истории чата. НЕ отвечайте на вопрос, только переформулируй его, если нужно, \
                                а в противном случае верни его как есть."""

def get_session_history(store, session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = load_session_history(session_id)
    return store[session_id]

contextualize_q_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", contextualize_q_system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ]
)           
def create_new_retriver(llm,retriever):
    history_aware_retriever = create_history_aware_retriever(
        llm, retriever, contextualize_q_prompt
    )
    return history_aware_retriever

def create_new_prompt(new_retr):
    new_prompt_chain = RunnableWithMessageHistory(
    new_retr,
    get_session_history,
    input_messages_key="input",
    history_messages_key="chat_history",
    output_messages_key="answer",
    )
    return new_prompt_chain

# Invoke the chain and save the messages after invocation
def invoke_and_save(store, session_id, input_text, new_prompt_chain):
    # Save the user question with role "human"
    save_message(session_id, "human", input_text)
    
    result = new_prompt_chain.invoke(
        {"input": input_text},
        config={"configurable": {"session_id": session_id, "store": store}}
    )["answer"]
    
    return result