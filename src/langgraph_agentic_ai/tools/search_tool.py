from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
from langchain_community.tools import YouTubeSearchTool
from langchain_core.tools import tool
import requests

from langgraph.prebuilt import ToolNode


@tool
def get_weather(location: str) -> str:
    """Get the current weather for a specific location. Use this when the user asks for the weather."""
    try:
        # wttr.in format=3 gives a nice single-line summary with an emoji
        response = requests.get(f"https://wttr.in/{location}?format=3")
        response.raise_for_status()
        return response.text
    except Exception as e:
        return f"Could not fetch weather for {location}. Error: {e}"

import re

@tool
def youtube_search(query: str) -> str:
    """Search YouTube for a specific topic or video. Use this when the user asks to find a video or search youtube."""
    # Force the query format to be 'query, 2' so it always returns 2 results and doesn't rely on the LLM to format it.
    yt = YouTubeSearchTool()
    result_str = yt.run(f"{query}, 2")
    
    # Extract video IDs to generate thumbnail previews
    video_ids = re.findall(r"watch\?v=([a-zA-Z0-9_-]+)", result_str)
    
    if not video_ids:
        return result_str
        
    output = []
    for vid in video_ids:
        thumbnail_url = f"https://img.youtube.com/vi/{vid}/0.jpg"
        video_url = f"https://www.youtube.com/watch?v={vid}"
        # Markdown image that acts as a clickable link to the video
        output.append(f"[![YouTube Video Thumbnail]({thumbnail_url})]({video_url})")
        
    # Combine the markdown thumbnails with the raw URLs
    return "Here are the video thumbnails and links:\n\n" + "\n\n".join(output) + "\n\nRaw URLs: " + result_str

@tool
def wikipedia_search(query: str) -> str:
    """Search Wikipedia for a specific topic, person, or concept. Use this when the user asks for detailed information from Wikipedia."""
    api_wrapper = WikipediaAPIWrapper(top_k_results=2, doc_content_chars_max=1000)
    wiki = WikipediaQueryRun(api_wrapper=api_wrapper)
    return wiki.run(query)


def get_tools():
    """
        returns the list of tools to be used in the chatbot
    """
    tavily_tool = TavilySearchResults(max_results=2)
    
    tools = [tavily_tool, wikipedia_search, youtube_search, get_weather]

    return tools


def create_tool_node(tools):
    """
        creates and returns a tool node for the graph
    """
    return ToolNode(tools=tools)