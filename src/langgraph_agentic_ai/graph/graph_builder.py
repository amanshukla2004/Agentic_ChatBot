from langgraph.graph import StateGraph, END, START
from src.langgraph_agentic_ai.state.state import State 
from src.langgraph_agentic_ai.nodes.basic_chatbot_node import BasicChatbotNode

class GraphBuilder:

    def __init__(self, model):
        self.llm = model
        self.graph_builder = StateGraph(State)
    
    def basic_chatbot_build_graph(self):
        """
            Builds a basic chatbot using langgraph.
            This method initializes a chatbot node using the `BasicChatbotNode` class and integrates it into the graph . the ChatBot node is et as both the entry and exit pointy of the graph
            
        """
        self.basic_chatbot = BasicChatbotNode(model=self.llm)
          
        self.graph_builder.add_node("chatbot", self.basic_chatbot.process)
        self.graph_builder.add_edge(START, "chatbot")
        self.graph_builder.add_edge("chatbot", END)
    
    def setup_graph(self, usecase):
        if usecase == "Basic ChatBot":
            """
                sets up the graph fro the selected use case
            """
            self.basic_chatbot_build_graph()
            return self.graph_builder.compile()
        else:
            raise ValueError(f"Error: Invalid use case '{usecase}'.")
            

        