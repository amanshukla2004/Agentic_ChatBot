from datetime import datetime
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from src.langgraph_agentic_ai.state.state import State

class RoutePrediction(BaseModel):
    """Predicts the best route based on user input."""
    route: str = Field(description="The destination route, MUST be one of: 'basic_chat', 'web_search', 'news_request'")

class RouterNode:
    def __init__(self, model):
        self.llm = model
        
        # We bind the tool to enforce structured output
        self.structured_llm = self.llm.with_structured_output(RoutePrediction)
        
        current_date = datetime.now().strftime("%Y-%m-%d")
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an intelligent router. Your job is to classify the user's intent to one of three categories:\n"
                       "- 'news_request': The user wants AI news, daily summaries, or tech news.\n"
                       "- 'web_search': The user is asking a question that requires searching the web for real-time information, looking up facts on Wikipedia, searching for YouTube videos, or asking for the Weather.\n"
                       "- 'basic_chat': The user just wants to chat, needs coding help, or is asking general knowledge questions that do not require external tools.\n"
                       f"Today's date is {current_date}. If the user asks for today's date, route them to 'basic_chat' because you already know it.\n"
                       "You MUST return one of these exact string values: 'basic_chat', 'web_search', 'news_request'."),
            ("user", "{input}")
        ])
        
        self.chain = self.prompt | self.structured_llm

    def route(self, state: State) -> dict:
        """
        Classifies the user input and returns the routing decision.
        """
        print("\n--- [NODE: Router] Executing ---")
        if not state["messages"]:
            print("Router decided: basic_chat (no messages)")
            return {"route": "basic_chat"}
        
        user_message = state["messages"][-1].content
        lower_msg = user_message.lower()
        
        # --- FAST PATHS ---
        if user_message == "give me the latest ai news":
            print("Router fast-path: news_request (button)")
            return {"route": "news_request"}
            
        # Keyword Heuristics for Web Search
        web_keywords = ["youtube", "video", "weather", "temperature", "wikipedia", "search", "google", "find out"]
        if any(kw in lower_msg for kw in web_keywords):
            print("Router fast-path: web_search (keyword heuristic)")
            return {"route": "web_search"}
            
        # Keyword Heuristics for News
        news_keywords = ["ai news", "tech news", "latest news"]
        if any(kw in lower_msg for kw in news_keywords):
            print("Router fast-path: news_request (keyword heuristic)")
            return {"route": "news_request"}
            
        # --- LLM FALLBACK ---
        try:
            prediction = self.chain.invoke({"input": user_message})
            print(f"Router decided: {prediction.route}")
            return {"route": prediction.route}
        except Exception as e:
            # Fallback in case the LLM fails to return the structured format
            print("Router failed to predict, defaulting to: basic_chat")
            return {"route": "basic_chat"}
