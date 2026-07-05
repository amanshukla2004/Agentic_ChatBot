from langgraph.prebuilt import tools_condition, ToolNode
from src.langgraph_agentic_ai.tools.search_tool import get_tools, create_tool_node
from langgraph.graph import StateGraph, END, START
from src.langgraph_agentic_ai.state.state import State 
from src.langgraph_agentic_ai.nodes.basic_chatbot_node import BasicChatbotNode
from src.langgraph_agentic_ai.tools.chatbot_with_Tool_node import ChatbotWithToolNode


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

    # --------------------------------------------------
    def chatbot_with_tools_build_graph(self):
        """
            Builds a chatbot with tools using langgraph.
            This method initializes a chatbot node using the `ChatbotWithToolsNode` class and integrates it into the graph . 
            It defines tools, initializes the chatbot with tool capabilities, and sets up conditional and direct edges between nodes.
            the ChatBot node is et as both the entry and exit pointy of the graph
            
        """
        # define the tool and the tool node

        tools = get_tools()
        tool_node = create_tool_node(tools)

        ## define the llm
        llm = self.llm

        ## define the chatbot node
        obj_chatbot_with_node = ChatbotWithToolNode(llm)
        chatbot_node = obj_chatbot_with_node.create_chatbot(tools)
        
        # add nodes
          
        self.graph_builder.add_node("chatbot", chatbot_node)
        self.graph_builder.add_node("tools",tool_node)

        # define conditional and direct edges


        self.graph_builder.add_edge(START, "chatbot")
        self.graph_builder.add_conditional_edges("chatbot", tools_condition)
        self.graph_builder.add_edge("tools", "chatbot")
        self.graph_builder.add_edge("tools",END)
        




    
    def setup_graph(self, usecase):
        """
            sets up the graph fro the selected use case
        """
        if usecase == "Basic ChatBot":
            self.basic_chatbot_build_graph()

        if usecase == "ChatBot with Web":
            self.chatbot_with_tools_build_graph()   



        return self.graph_builder.compile()

       