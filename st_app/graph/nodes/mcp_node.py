import asyncio
from langchain_upstage import ChatUpstage
from langchain_core.messages import HumanMessage
from st_app.utils.state import GraphState
from mcp import ClientSession
from mcp.client.sse import sse_client

async def call_mcp_server(tool_name: str, tool_args: dict = None):
    """Asynchronous function to call the MCP server over SSE."""
    if tool_args is None:
        tool_args = {}
    
    url = "http://localhost:8000/sse"
    async with sse_client(url) as streams:
        async with ClientSession(streams[0], streams[1]) as session:
            await session.initialize()
            result = await session.call_tool(tool_name, arguments=tool_args)
            return result.content[0].text

def mcp_node(state: GraphState) -> dict:
    """
    This node handles data analysis by connecting to a separate MCP server via SSE.
    """
    print("---MCP NODE (SSE CLIENT)---")
    
    user_input = state["user_input"]
    llm = ChatUpstage()
    
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
    
    # Filter tool name to ensure it's valid
    valid_tools = [
        "get_sentiment_summary", 
        "analyze_crowd_impact", 
        "get_seasonal_trends", 
        "extract_high_value_complaints"
    ]
    
    selected_tool = "get_sentiment_summary" # Default
    for tool in valid_tools:
        if tool in tool_name:
            selected_tool = tool
            break
            
    print(f"---CALLING TOOL: {selected_tool}---")
    
    # Run the async client in a synchronous context
    try:
        analysis_result = asyncio.run(call_mcp_server(selected_tool))
    except Exception as e:
        analysis_result = f"Error connecting to MCP server: {str(e)}"
        print(analysis_result)
        
    return {"analysis_result": analysis_result}