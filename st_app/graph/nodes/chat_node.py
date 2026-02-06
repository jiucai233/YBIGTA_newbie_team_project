from langchain_upstage import ChatUpstage
from langchain_core.messages import HumanMessage

from st_app.utils.state import GraphState


def chat_node(state: GraphState) -> dict:
    """
    This node is responsible for generating a response to the user.
    It takes the state as input and returns a dictionary with the updated state.
    """
    print("---CHAT NODE---")

    llm = ChatUpstage()

    # Get the user's input, subject, and review from the state
    user_input = state["user_input"]

    # Create a new HumanMessage with the formatted prompt
    new_message = HumanMessage(content=user_input)

    # Add the new message to the chat history
    chat_history = state["chat_history"] + [new_message]

    # Get the response from the model
    response = llm.invoke(chat_history)

    # Add the model's response to the chat history
    chat_history.append(response)

    return {"chat_history": chat_history}