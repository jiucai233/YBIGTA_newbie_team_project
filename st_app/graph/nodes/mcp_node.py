from langchain_upstage import ChatUpstage
from langchain_core.messages import HumanMessage
from st_app.utils.state import GraphState
import mcp_server

def mcp_node(state: GraphState) -> dict:
    """
    This node handles data analysis using tools from the MCP server.
    """
    print("---MCP NODE---")
    
    user_input = state["user_input"]
    llm = ChatUpstage()
    
    # Define the tools available in mcp_server
    # We can use the llm to decide which tool to call or just run a summary analysis
    
    prompt = f"""
    You are a data analyst for Lotte World. 
    Based on the user's request: "{user_input}"
    
    Choose the most appropriate analysis tool to use:
    1. get_sentiment_summary: Overall sentiment and ratings.
    2. analyze_crowd_impact: Comparison between weekdays and weekends.
    3. get_seasonal_trends: Monthly satisfaction trends.
    4. extract_high_value_complaints: Specific operational pain points from long negative reviews.
    
    Just return the name of the tool.
    """
    
    response = llm.invoke([HumanMessage(content=prompt)])
    tool_name = response.content.strip()
    
    analysis_result = ""
    if "get_sentiment_summary" in tool_name:
        analysis_result = mcp_server.get_sentiment_summary()
    elif "analyze_crowd_impact" in tool_name:
        analysis_result = mcp_server.analyze_crowd_impact()
    elif "get_seasonal_trends" in tool_name:
        analysis_result = mcp_server.get_seasonal_trends()
    elif "extract_high_value_complaints" in tool_name:
        analysis_result = mcp_server.extract_high_value_complaints()
    else:
        # Default to sentiment summary if unsure
        analysis_result = mcp_server.get_sentiment_summary()
        
    return {"analysis_result": analysis_result}
