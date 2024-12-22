from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.output_parsers import JsonOutputParser
from langchain.chains import create_history_aware_retriever

from db.save_and_load_history import load_session_history,save_message

contextualize_q_system_prompt = """Учитывая историю чатов и последний вопрос пользователя, который может ссылаться на контекст в истории чата, \
                                сформулируй отдельный вопрос, который может быть понят без истории чата. НЕ отвечай на вопрос, только переформулируй его, если нужно. \
                                Переформулировка нужна в случае, если вопрос не понятен без истории чата, \
                                в случаях если история пуста или вопрос самодостаточен - его НЕ НАДО переформулировать, просто верни его же в ответе. \
                                Ответ выводи в виде JSON с единственным ключом 'answer', где будет находиться новый или не измененный вопрос. """


def get_session_history(session_id: str) -> BaseChatMessageHistory:
    store = {}
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

def create_new_prompt(llm):
    
    chain = contextualize_q_prompt | llm | JsonOutputParser()
    
    new_prompt_chain = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="input",
    history_messages_key="chat_history",
    output_messages_key="answer",
    )
    return new_prompt_chain
