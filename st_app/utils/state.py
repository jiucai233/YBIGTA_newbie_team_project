# state.py
from typing import Annotated, TypedDict, List
from langchain_core.messages import BaseMessage
import operator

class GraphState(TypedDict):
    # User input
    user_input: str
    # Chat history
    chat_history: Annotated[List[BaseMessage], operator.add]
    # RAG review result
    review: str
    # Subject information result
    subject: str
    
    # 'messages' stores the conversation history. 
    # The operator.add ensures new messages are appended rather than overwritten.
    messages: Annotated[List[BaseMessage], operator.add]
    
    # 'context' is used to store raw data retrieved from JSON or FAISS.
    context: str 
    
    # 'analysis_result' is reserved for your AWS MCP analysis output.
    analysis_result: str