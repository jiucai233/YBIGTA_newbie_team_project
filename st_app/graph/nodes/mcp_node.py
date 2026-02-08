import asyncio
from langchain_upstage import ChatUpstage
from langchain_core.messages import HumanMessage
from st_app.utils.state import GraphState
from mcp import ClientSession
from mcp.client.sse import sse_client
import os
import streamlit as st


async def call_mcp_server(tool_name: str):
    print(f"--- [DEBUG] Final Tool Name Sent to Server: '{tool_name}' ---", flush=True)
    
    url = "https://api.jiucai.info/sse"
    
    try:
        async with sse_client(url) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                
                tools = await session.list_tools()
                print(f"--- [CLIENT DEBUG] Server says it has: {[t.name for t in tools]} ---", flush=True)
                
                result = await session.call_tool(tool_name.strip())
                return result.content[0].text
    except Exception as e:
        print(f"--- [CRITICAL CALL ERROR]: {str(e)} ---", flush=True)
        return f"Error: {str(e)}"

def mcp_node(state: GraphState) -> dict:
    """
    This node handles data analysis by connecting to a separate MCP server via SSE.
    """
    print("---MCP NODE (SSE CLIENT)---", flush=True)
    
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
            
    print(f"---CALLING TOOL: {selected_tool}---", flush=True)
    
    # Run the async client in a synchronous context
    try:
        analysis_result = asyncio.run(call_mcp_server(selected_tool))
        print(f"--- [RAW DATA FROM MCP]: {analysis_result} ---", flush=True)
    except Exception as e:
        analysis_result = f"Error connecting to MCP server: {str(e)}"
        print(analysis_result, flush=True)
        
    return {"analysis_result": analysis_result}