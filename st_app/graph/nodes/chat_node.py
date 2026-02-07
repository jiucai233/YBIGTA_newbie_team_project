from langchain_upstage import ChatUpstage
from langchain_core.messages import HumanMessage
from st_app.utils.state import GraphState

def chat_node(state: GraphState) -> dict:
    """
    This node is responsible for generating a response to the user.
    It incorporates any gathered information (reviews, subjects, analysis) into the final answer.
    if no specific context is available, it handles general chat.
    """
    print("---CHAT NODE---")
    llm = ChatUpstage()
    user_input = state["user_input"]
    review_context = state.get("review", "")
    subject_context = state.get("subject", "")
    analysis_context = state.get("analysis_result", "")
    # Construct a comprehensive prompt if context is available
    context_parts = []
    if review_context and "placeholder" not in review_context.lower():
        context_parts.append(f"Review Information: {review_context}, you are a active reviewer, discuss actively about the reviews provided.")
    if subject_context and "placeholder" not in subject_context.lower():
        context_parts.append(f"Subject Information: {subject_context}, you are an expert on Lotte World, provide accurate and detailed information about the subject.")
    if analysis_context:
        context_parts.append(f"Data Analysis Result: {analysis_context}, you are the best data analystm, be confident about what you had analyzed about.")
    full_context = "\n".join(context_parts)
    if full_context:
        prompt = f"Using the following context, answer the user's question.\n\nContext:\n{full_context}\n\nUser Question: {user_input}"
    else:
        prompt = user_input

    # Create a new HumanMessage
    new_message = HumanMessage(content=prompt)

    # We use the provided chat_history for context but invoke with the new prompt
    chat_history = state["chat_history"] + [new_message]

    # Get the response from the model
    response = llm.invoke(chat_history)

    # We return the updated chat_history. The UI will pick up the last message.
    return {"chat_history": [response]}

