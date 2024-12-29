from functools import partial
from pprint import pprint
from langgraph.graph import END, StateGraph

from src.graph.graph_entities.nodes import (
    invoke_getting_new_prompt, retrieve, grade_documents, generate, transform_query, prepare_for_final_grade, handle_exit
)
from src.graph.graph_entities.edges import (
    decide_to_generate, grade_generation_vs_documents, grade_generation_vs_question, decide_to_retry
)
from src.graph.graph_entities.state import GraphState


def get_compiled_graph(llm, retriever):
    workflow = StateGraph(GraphState)
    # UPDATED PROMPT
    new_prompt = partial(invoke_getting_new_prompt,llm=llm)
    workflow.add_node("updated prompt", new_prompt)
    
    # RETRIEVE
    retrieve_with_retriever = partial(retrieve, retriever=retriever)
    workflow.add_node("retrieve", retrieve_with_retriever)

    # GRADE DOCUMENTS
    grade_documents_with_llm = partial(grade_documents, llm=llm)
    workflow.add_node("grade_documents", grade_documents_with_llm)  

    # GENERATE ANSWER
    generate_with_llm = partial(generate, llm=llm)
    workflow.add_node("generate", generate_with_llm)  # generate

    # TRANSFORM QUERY
    transform_query_with_llm = partial(transform_query, llm=llm)
    workflow.add_node("transform_query", transform_query_with_llm)  # transform_query

    # EXIT NODE
    workflow.add_node("exit", handle_exit)

    # PASSTHROUGH TO FINAL ANSWER
    workflow.add_node("prepare_for_final_grade", prepare_for_final_grade)


    ### === Setting edges === ###

    workflow.set_entry_point("updated prompt")
    workflow.add_edge("updated prompt", "retrieve")
    workflow.add_edge("retrieve", "grade_documents")

    # CHECK DOCUMENT RELEVANCE
    workflow.add_conditional_edges(
        "grade_documents",
        decide_to_generate,
        {
            "transform_query": "transform_query",
            "generate": "generate",
        },
    )

    # CHECK RETRY LOGIC
    workflow.add_conditional_edges(
        "transform_query",
        decide_to_retry, 
        {
            "retrieve": "retrieve",
            "exit": "exit",
        },
    )
    workflow.add_edge("exit", END)

    # CHECK IF MODEL ANSWER IS SUPPORTED BY DOCUMENTS
    grade_generation_vs_documents_with_llm = partial(grade_generation_vs_documents, llm=llm)
    workflow.add_conditional_edges(
        "generate",
        grade_generation_vs_documents_with_llm,
        {
            "supported": "prepare_for_final_grade",
            "not supported": "generate",
        },
    )

    # CHECK IF MODEL ANSWER IS USEFUL
    grade_generation_vs_question_with_llm = partial(grade_generation_vs_question, llm=llm)
    workflow.add_conditional_edges(
        "prepare_for_final_grade",
        grade_generation_vs_question_with_llm,
        {
            "useful": END,
            "not useful": "transform_query",
        },
    )

    return workflow.compile()

def run_graph(graph, query, history):
    inputs = {"keys": {"question": query, "history": history, "cycle_count": 0}}
    for output in graph.stream(inputs):
        for key, value in output.items():
            # Node
            pprint(f"Node '{key}':")
        pprint("\n---\n")

    generated_answer = value['keys']['generation']
    docs = [
        {'title': el.metadata['title'], 'link': el.metadata['link']}
        for el in value['keys']['documents']
        ]
    return generated_answer, docs
