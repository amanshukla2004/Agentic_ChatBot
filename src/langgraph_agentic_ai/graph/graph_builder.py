from langgraph.prebuilt import tools_condition, ToolNode
from src.langgraph_agentic_ai.tools.search_tool import get_tools, create_tool_node
from langgraph.graph import StateGraph, END, START
from src.langgraph_agentic_ai.state.state import State 
from src.langgraph_agentic_ai.nodes.basic_chatbot_node import BasicChatbotNode
from src.langgraph_agentic_ai.tools.chatbot_with_Tool_node import ChatbotWithToolNode
from src.langgraph_agentic_ai.nodes.ai_news_node import AINewsNode
from src.langgraph_agentic_ai.nodes.router_node import RouterNode

def route_decision(state: State) -> str:
    """Returns the next node based on the router's decision."""
    route = state.get("route", "basic_chat")
    if route == "web_search":
        return "chatbot_with_tools"
    elif route == "news_request":
        return "fetch_news"
    else:
        return "basic_chatbot"


class GraphBuilder:

    def __init__(self, model):
        self.llm = model
        self.graph_builder = StateGraph(State)
    
    def setup_graph(self, usecase=None, checkpointer=None):
        """
        Sets up the unified multi-agent graph. The usecase argument is kept for backwards compatibility but is no longer required.
        """
        # 1. Initialize Nodes
        router_node = RouterNode(self.llm)
        basic_chatbot = BasicChatbotNode(model=self.llm)
        
        tools = get_tools()
        tool_node = create_tool_node(tools)
        obj_chatbot_with_node = ChatbotWithToolNode(self.llm)
        chatbot_node = obj_chatbot_with_node.create_chatbot(tools)
        
        ai_news_node = AINewsNode(self.llm)

        # 2. Add Nodes to Graph
        self.graph_builder.add_node("router", router_node.route)
        self.graph_builder.add_node("basic_chatbot", basic_chatbot.process)
        
        self.graph_builder.add_node("chatbot_with_tools", chatbot_node)
        self.graph_builder.add_node("tools", tool_node)
        
        self.graph_builder.add_node("fetch_news", ai_news_node.fetch_news)
        self.graph_builder.add_node("summarize_news", ai_news_node.summarize_news)
        self.graph_builder.add_node("save_results", ai_news_node.save_result)

        # 3. Add Edges and Routing
        if usecase == "news":
            self.graph_builder.set_entry_point("fetch_news")
        else:
            self.graph_builder.set_entry_point("router")
        
        # Conditional edge from router
        self.graph_builder.add_conditional_edges(
            "router",
            route_decision,
            {
                "basic_chatbot": "basic_chatbot",
                "chatbot_with_tools": "chatbot_with_tools",
                "fetch_news": "fetch_news"
            }
        )

        # Basic Chatbot flow
        self.graph_builder.add_edge("basic_chatbot", END)
        
        # Chatbot with Tools (Web Search) flow
        self.graph_builder.add_conditional_edges(
            "chatbot_with_tools", 
            tools_condition,
            {"tools": "tools", "__end__": END}
        )
        self.graph_builder.add_edge("tools", "chatbot_with_tools")
        
        # AI News flow
        self.graph_builder.add_edge("fetch_news", "summarize_news")
        self.graph_builder.add_edge("summarize_news", "save_results")
        self.graph_builder.add_edge("save_results", END)

        if checkpointer:
            return self.graph_builder.compile(checkpointer=checkpointer)
        return self.graph_builder.compile()