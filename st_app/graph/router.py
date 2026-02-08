import os
from dotenv import load_dotenv
from openai import OpenAI
from st_app.utils.state import GraphState

load_dotenv()

BASE_URL = "https://api.upstage.ai/v1/solar"
MODEL = "solar-mini"

def _get_api_key() -> str:
    """Get the first available Upstage API key."""
    key = os.getenv("UPSTAGE_API_KEY1") or os.getenv("UPSTAGE_API_KEY", "")
    return key.strip()

def router(state: GraphState) -> str:
    """
    This is a router that decides which node to go to next based on the user's input.
    Uses Upstage API (solar-mini) to classify the intent.
    """
    print("---ROUTER---", flush=True)
    user_input = state["user_input"]
    
    api_key = _get_api_key()
    client = OpenAI(api_key=api_key, base_url=BASE_URL)
    
    prompt = f"""
    You are an expert router for a Lotte World chatbot.
    Your task is to classify the user's input into one of the following categories:
    
    - 'rag_review_node': If the user is asking for specific reviews, opinions, or feedback about Lotte World (e.g., "What do people think about the rides?", "Give me some reviews").
    - 'subject_info_node': If the user is asking for general information about Lotte World subjects like attractions, facilities, or general facts (e.g., "Tell me about Magic Island", "What attractions are there?").
    - 'mcp': If the user wants data analysis, statistics, or trends (e.g., "Show me the sentiment trends", "Compare weekday vs weekend ratings", "Analyze the reviews").
    - 'chat_node': For general greetings, small talk, or if the input doesn't fit the other categories.
    
    User Input: {user_input}
    
    Return ONLY the category name as a single word.
    """
    
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    
    decision = response.choices[0].message.content.strip().lower()
    
    # Basic validation to ensure the returned string is one of our expected nodes
    if "rag_review_node" in decision:
        target = "rag_review_node"
    elif "subject_info_node" in decision:
        target = "subject_info_node"
    elif "mcp" in decision:
        target = "mcp"
    else:
        target = "chat_node"

    print(f"---ROUTING TO {target.upper()}---", flush=True)
    return target
