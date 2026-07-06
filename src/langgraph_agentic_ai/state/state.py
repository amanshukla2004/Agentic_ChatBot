from typing_extensions import TypedDict, List
from langgraph.graph.message import add_messages
from typing import Annotated, Any

class State(TypedDict):
    """
        Represents the structure of the state used in graph
    """

    messages: Annotated[List, add_messages]
    route: str
    retrieved_context: Any
    final_response: Any
    error: str
    
    # AI News specific state keys
    frequency: str
    news_data: Any
    summary: str
    filename: str