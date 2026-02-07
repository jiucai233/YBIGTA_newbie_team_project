import streamlit as st
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage

from st_app.utils.state import GraphState
from st_app.graph.nodes.chat_node import chat_node
from st_app.graph.nodes.rag_review_node import rag_review_node
from st_app.graph.nodes.subject_info_node import subject_info_node
from st_app.graph.nodes.mcp_node import mcp_node
from st_app.graph.router import router

# 1. LangGraph Definition
workflow = StateGraph(GraphState)

workflow.add_node("chat_node", chat_node)
workflow.add_node("rag_review_node", rag_review_node)
workflow.add_node("subject_info_node", subject_info_node)
workflow.add_node("mcp_node", mcp_node)

workflow.set_conditional_entry_point(
    router,
    {
        "rag_review_node": "rag_review_node",
        "subject_info_node": "subject_info_node",
        "mcp": "mcp_node",
        "chat_node": "chat_node",
    },
)

workflow.add_edge("rag_review_node", "chat_node")
workflow.add_edge("subject_info_node", "chat_node")
workflow.add_edge("mcp_node", "chat_node")
workflow.add_edge("chat_node", END)

app = workflow.compile()

# 2. Streamlit UI
st.title("YBIGTA LangGraph Demo")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

for message in st.session_state.chat_history:
    if isinstance(message, HumanMessage):
        with st.chat_message("human"):
            st.markdown(message.content)
    elif isinstance(message, AIMessage):
        with st.chat_message("ai"):
            st.markdown(message.content)

if prompt := st.chat_input("Ask me anything..."):
    st.session_state.chat_history.append(HumanMessage(content=prompt))
    with st.chat_message("human"):
        st.markdown(prompt)

    # Invoke LangGraph
    # Initial state for the graph
    initial_state = GraphState(
        user_input=prompt,
        chat_history=st.session_state.chat_history,
        review="",
        subject="",
        messages=[],
        context="",
        analysis_result=""
    )
    
    with st.spinner("Thinking..."):
            result = app.invoke(initial_state)
        
            # Extract the AI's response from the chat_history returned by the chat_node
            ai_response_content = ""
            if "chat_history" in result and result["chat_history"]:
                last_msg = result["chat_history"][-1]
                if isinstance(last_msg, AIMessage):
                    ai_response_content = last_msg.content
            if ai_response_content:
                st.session_state.chat_history.append(AIMessage(content=ai_response_content))
                with st.chat_message("ai"):
                    st.markdown(ai_response_content)
            else:
                st.session_state.chat_history.append(AIMessage(content="I'm sorry, I couldn't generate a response."))
                with st.chat_message("ai"):
                    st.markdown("I'm sorry, I couldn't generate a response.")
