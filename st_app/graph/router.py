from st_app.utils.state import GraphState


def router(state: GraphState) -> dict:
    """
    This is a router that decides which node to go to next based on the user's input.
    """
    print("---ROUTER---")
    user_input = state["user_input"].lower()
    if "review" in user_input:
        print("---ROUTING TO RAG REVIEW NODE---")
        return "rag_review_node"
    elif "subject" in user_input:
        print("---ROUTING TO SUBJECT INFO NODE---")
        return "subject_info_node"
    else:
        print("---ROUTING TO CHAT NODE---")
        return "chat_node"
