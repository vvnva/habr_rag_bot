import json
import operator
from typing import Annotated, Sequence, TypedDict

from langchain import hub
from langchain.prompts import PromptTemplate
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import BaseMessage, FunctionMessage
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser, PydanticOutputParser
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.runnables import RunnablePassthrough
from langchain_community.chat_models import ChatOllama
from langchain_core.pydantic_v1 import BaseModel, Field, validator

_PYDANTIC_FORMAT_INSTRUCTIONS = """The output should be formatted as a JSON instance that conforms to the JSON schema below.

As an example, for the schema {{"properties": {{"foo": {{"title": "Foo", "description": "a list of strings", "type": "array", "items": {{"type": "string"}}}}}}, "required": ["foo"]}}
the object {{"foo": ["bar", "baz"]}} is a well-formatted instance of the schema. The object {{"properties": {{"foo": ["bar", "baz"]}}}} is not well-formatted.

Here is the output schema:
```
{schema}
```""" 

def get_format_instructions(parser) -> str:
    """Return the format instructions for the JSON output.
        Needs to implement pydantic parsing.
    Returns:
        The format instructions for the JSON output.
    """
    # Copy schema to avoid altering original Pydantic schema.
    schema = dict(parser.pydantic_object.schema().items())

    # Remove extraneous fields.
    reduced_schema = schema
    if "title" in reduced_schema:
        del reduced_schema["title"]
    if "type" in reduced_schema:
        del reduced_schema["type"]
    # Ensure json in context is well-formed with double quotes.
    schema_str = json.dumps(reduced_schema, ensure_ascii=False)

    return _PYDANTIC_FORMAT_INSTRUCTIONS.format(schema=schema_str)


### Nodes ###

def invoke_getting_new_prompt(state, llm):
    """
    New user prompt

    Args:
        state (dict): The current graph state
        
    Returns:
        state (dict): Updated question key state, that contains new prompt
    """
    print("---UPDATING PROMPT---")
        
    state_dict = state["keys"]
    question = state_dict["question"]
    history = state_dict["history"]
    cycle_count = state_dict["cycle_count"]
    
#     prompt_text = """Учитывая историю чатов и последний вопрос пользователя, который может ссылаться на контекст в истории чата, \
#              сформулируй отдельный вопрос, который может быть понят без истории чата. НЕ отвечай на вопрос, только переформулируй его, если нужно. \
#              Переформулировка нужна в случае, если вопрос не понятен без истории чата, \
#              в случаях если история пуста или вопрос самодостаточен - его НЕ НАДО переформулировать, просто верни его же в ответе. \
#              Ответ выводи в виде JSON с единственным ключом 'answer', где будет находиться новый или не измененный вопрос. """
    
#     prompt = ChatPromptTemplate.from_messages(
#     [
#         ("system", prompt_text),
#         MessagesPlaceholder("chat_history"),
#         ("human", "{input}"),
#     ]
# ) 
    
#     chain = prompt | llm | JsonOutputParser()
    
#     new_prompt_chain = RunnableWithMessageHistory(
#     chain,
#     get_session_history,
#     input_messages_key="input",
#     history_messages_key="chat_history",
#     output_messages_key="answer",
#     )

    
#     result = new_prompt_chain.invoke(
#         {"input": question},
#         config={"configurable": {"history": history}}
#     )
#     print("Invoke Result:", result)  # Для отладки

    prompt = PromptTemplate(
            template="""Considering the chat history and the user's latest question, which may refer to the context in the chat history, rephrase the question as a standalone query that can be understood without the chat history. DO NOT ANSWER THE QUESTION; only rephrase it if absolutely necessary.  
  
            Rephrasing is required only in the following cases:  
            1. If the question contains explicit references to previous messages (e.g., "А что насчёт этого?" or "Как я уже говорил").  
            2. If the question is incomplete or unclear without the context of the chat history.  

            If the question is clear and self-contained, return it unchanged. Do not add extra details or infer the user's intent.  

            Provide the response in JSON format with a single key 'answer', containing the new or unchanged question.  

            Examples:  
            - Question: "Расскажи мне про Рокетбанк" → Return unchanged: "answer": "Расскажи мне про Рокетбанк" 
            - Question: "Что насчёт этого?" (with context: "Рокетбанк классный банк" или другого упоминания) → Rephrase: "answer": "Что насчет Рокетбанка?" 
            
            User's latest question: {question}  
            Chat history: {history}  """,
            input_variables=["question","history"],
            )
    
    chain = prompt | llm | JsonOutputParser()
    
    result = chain.invoke(
        {
            "question": question,
            "history": history,
        }
    )
    
    print("Invoke Result:", result)
    
    new_prompt = result["answer"]

    return {"keys": {"question": new_prompt, "cycle_count": cycle_count}}

def retrieve(state, retriever):
    """
    Retrieve documents

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): New key added to state, documents, that contains retrieved documents
    """
    print("---RETRIEVE---")
    state_dict = state["keys"]
    question = state_dict["question"]
    cycle_count = state_dict["cycle_count"]
    documents = retriever.get_relevant_documents(question)
    print(len(documents))
    return {"keys": {"documents": documents, "question": question, "cycle_count": cycle_count}}


def grade_documents(state, llm):
    """
    Determines whether the retrieved documents are relevant to the question.

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): Updates documents key with relevant documents
    """

    print("---CHECK RELEVANCE---")
    state_dict = state["keys"]
    question = state_dict["question"]
    documents = state_dict["documents"]
    cycle_count = state_dict["cycle_count"]

    # Prompt
    prompt = PromptTemplate(
        template="""You are a grader assessing relevance of a retrieved document to a user question. \n 
        Here is the retrieved document: \n\n {context} \n\n
        Here is the user question: {question} \n
        If the document contains keywords related to the user question, grade it as relevant. \n
        It does not need to be a stringent test. The goal is to filter out erroneous retrievals. \n
        Give a binary score 'yes' or 'no' score to indicate whether the document is relevant to the question. \n
        Provide the binary score as a JSON with a single key 'score' and no premable or explaination.""",
        input_variables=["question","context"],
    )

    # Chain
    chain = prompt | llm | JsonOutputParser()

    # Score
    filtered_docs = []
    for i, d in enumerate(documents):
        print(f'{i}): {d.page_content}\n')
        score = chain.invoke(
            {
                "question": question,
                "context": d.page_content,
            }
        )
        grade = score["score"]
        if grade == "yes":
            print("---GRADE: DOCUMENT RELEVANT---")
            filtered_docs.append(d)
        else:
            print("---GRADE: DOCUMENT NOT RELEVANT---")
            continue

    return {"keys": {"documents": filtered_docs, "question": question, "cycle_count": cycle_count}}


def generate(state, llm):
    """
    Generate answer

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): New key added to state, generation, that contains LLM generation
    """
    print("---GENERATE---")
    state_dict = state["keys"]
    question = state_dict["question"]
    documents = state_dict["documents"]
    cycle_count = state_dict["cycle_count"]

    # Prompt
    prompt = hub.pull("rlm/rag-prompt")

    # Chain
    rag_chain = prompt | llm | StrOutputParser()

    # Run
    generation = rag_chain.invoke({"context": documents, "question": question})
    return {
        "keys": {"documents": documents, "question": question, "generation": generation, "cycle_count": cycle_count}
    }

class AnswerModel(BaseModel):
    improved_question: str = Field(description="This field stores the improved question as a string")

    @validator("improved_question")
    def validate_answer(cls, value):
        if not isinstance(value, str):
            raise ValueError("Поле 'improved_question' должно быть строкой.")
        if not value.strip():
            raise ValueError("Поле 'improved_question' не может быть пустым или состоять только из пробелов.")
        return value
    
def transform_query(state, llm):
    """
    Transform the query to produce a better question.

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): Updates question key with a re-phrased question
    """

    print("---TRANSFORM QUERY---")
    state_dict = state["keys"]
    question = state_dict["question"]
    documents = state_dict["documents"]
    updated_cycle_count = state_dict["cycle_count"] + 1

    parser = PydanticOutputParser(pydantic_object=AnswerModel)

    # Create a prompt template with format instructions and the query
    prompt = PromptTemplate(
        template="""You are generating questions that is well optimized for retrieval. \n 
        Look at the input and try to reason about the underlying sematic intent / meaning. \n 
        Here is the initial question:
        \n ------- \n
        {question} 
        \n ------- \n
        \n{format_instructions}""",
        input_variables=["question"],
        partial_variables={"format_instructions": get_format_instructions(parser)}
    )

    # Chain
   
    chain = prompt | llm | parser
    better_question = chain.invoke({"question": question}).improved_question

    return {"keys": {"documents": documents, "question": better_question, "cycle_count": updated_cycle_count}}


def prepare_for_final_grade(state):
    """
    Passthrough state for final grade.

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): The current graph state
    """

    print("---FINAL GRADE---")
    state_dict = state["keys"]
    question = state_dict["question"]
    documents = state_dict["documents"]
    generation = state_dict["generation"]
    cycle_count = state_dict["cycle_count"]

    return {
        "keys": {"documents": documents, "question": question, "generation": generation, "cycle_count": cycle_count}
    }


def handle_exit(state):
    """
    Handles the situation where the retry limit is reached.
    """

    state_dict = state["keys"]
    question = state_dict["question"]
    documents = state_dict["documents"]
    cycle_count = state_dict["cycle_count"]

    print("---EXITING DUE TO MAX CYCLES---")
    return {
        "keys": {
            "documents": documents,
            "question": question,
            "generation": "Unable to generate a satisfactory answer after multiple attempts.",
            "cycle_count": cycle_count}
    }
