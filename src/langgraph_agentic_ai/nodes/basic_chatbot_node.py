
from src.langgraph_agentic_ai.state.state import State

class BasicChatbotNode:
    
    def __init__(self, model):
        self.llm = model
        
    def process(self, state: State) -> dict:
        """
            Represents a node in the graph that handles basic chatbot functionality.
            This node is responsible for processing user messages and generating responses.
        """
        return {"messages" : self.llm.invoke(state["messages"])}
        
        