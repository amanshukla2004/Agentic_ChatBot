
from dotenv import load_dotenv

from tavily import TavilyClient
from langchain_core.prompts import ChatPromptTemplate
import os

class AINewsNode:
    # constructor self -> obj 
    def __init__(self, llm):
        """
        Initialize the AINewsNode with API keys for Tavily and Groq
        """
        from dotenv import load_dotenv
        load_dotenv()

        self.tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
        

        self.llm = llm
        # this is used to capture various steps in this file so that later can be use for steps showns
        self.state = {}

        # from tavily docs
    
    def fetch_news(self, state: dict) -> dict:
        '''
            Fetch ai news based on the specified frequency.

            Args : state(dict) -> the state dictionary containing 'frequnecy'

            Returns : dict -> Updated sate with 'news_data' key containing fetched news
        '''
        print("\n--- [NODE: AI News - Fetch] Executing ---")
        user_input = state['messages'][-1].content.lower()
        
        import streamlit as st
        # safely parse frequency from natural language, but override with UI selector if present
        frequency = 'daily'
        if 'week' in user_input: frequency = 'weekly'
        elif 'month' in user_input: frequency = 'monthly'
        elif 'year' in user_input: frequency = 'year'
        
        if "timeframe" in st.session_state:
            frequency = st.session_state["timeframe"].lower()
            
        self.state['frequency'] = frequency
        days_map = {'daily' : 1, 'weekly' : 7, 'year' : 366, 'monthly' : 30}

        

        print(os.getenv("TAVILY_API_KEY"))

        try:
            # Reverted query to AI news as requested
            response = self.tavily.search(
                query="latest artificial intelligence technology news",
                topic='news',
                days=days_map[frequency],
                max_results=5
            )
        except Exception as e:
            print("TAVILY ERROR:", repr(e))
            state['news_data'] = [{'title': 'Tavily API Error', 'content': f'Tavily search failed or timed out: {str(e)}'}]
            self.state['news_data'] = state['news_data']
            return state
                    

        # news_content = "\n\n".join([f"Title: {article['title']}\nURL: {article['url']}\n" for article in response['results']])

        state['news_data'] = response.get('results', [])
        self.state['news_data'] = state['news_data']
        return state



    def summarize_news(self, state: dict) -> dict:
        import traceback
        try:
            print("\n--- [NODE: AI News - Summarize] Executing ---")
            news_items = self.state.get('news_data') or []
            frequency = self.state.get('frequency', 'daily')
            
            if not news_items:
                state['summary'] = "### Failed to Fetch News\n\nNo articles were found or the search API returned empty results. Please try again later."
                self.state['summary'] = state['summary']
                return self.state

            first_item_content = news_items[0].get('content') or ''
            if len(news_items) == 1 and "Tavily API Error" in first_item_content:
                state['summary'] = f"### Failed to Fetch News\n\n{first_item_content}\n\n*Please try again later. Tavily servers are currently unresponsive.*"
                self.state['summary'] = state['summary']
                return self.state

            prompt_template = ChatPromptTemplate.from_messages(
                [
                    (
                        "system" , f"""You are an elite AI technology journalist and summarization expert. 
                        Your task is to synthesize the following AI news articles into a beautiful, highly readable markdown report for the {frequency} timeframe.
                        
                        Formatting Requirements:
                        - ✨ **Executive Summary**: Start the entire report with a brief 2-sentence "TL;DR" of the most critical breakthroughs.
                        - 📅 **Chronological Grouping**: Organize the summary chronologically by day using headers like `### YYYY-MM-DD`.
                        - 🚀 **Impact Highlights**: For each day, use bullet points with relevant emojis (e.g., 🤖 for models, 💸 for funding, ⚖️ for regulations, 🔬 for research).
                        - 🔗 **Citations**: You MUST inline markdown links to the original resources for EVERY news item (e.g., [Read full article on The Verge](URL)).
                        
                        Keep the summary concise, engaging, and professional. 
                        DO NOT output raw URLs; always format them as clickable markdown text.
                        """
                    ),
                    ("user" , "Articles:\n{articles}")
                ]
            )

            articles_str = "\n\n".join(
                [
                     f"Title: {item.get('title') or 'Unknown'}\n Content: {item.get('content') or ''}\n URL: {item.get('url') or ''}\n Date: {item.get('published_date') or 'Unknown'}" for item in news_items
                ]
            )
            
            response =  self.llm.invoke(
                prompt_template.format(articles = articles_str)
            )
            state['summary'] = response.content
            
        except Exception as e:
            err = traceback.format_exc()
            print("SUMMARIZE CRASHED:", err)
            if "RateLimitError" in err or "429" in str(e):
                state['summary'] = "### Rate Limit Reached\n\nGroq API token limit exceeded. Please wait a minute and try again, or switch to a smaller model in the sidebar."
            else:
                state['summary'] = f"### CRASH TRACEBACK:\n\n```\n{err}\n```"
            
        self.state['summary'] = state['summary']
        return self.state

    # can work on this method more
    def save_result(self, state):
        print("\n--- [NODE: AI News - Save Result] Executing ---")
        import os
        frequency = self.state['frequency']
        summary = self.state['summary']
        
        # Ensure the directory exists
        os.makedirs("./AINews", exist_ok=True)
        filename = f"./AINews/{frequency}_summary.md"

        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"# {frequency.capitalize()} AI News Summary\n\n")
            f.write(summary)

        self.state['filename'] = filename
        return self.state 


# my State class has only one field messages , how come we are able to have these many dictionary but we have not written in the State class

# answer: 
# 1. Python Dictionaries are Dynamic: Even if your `State` is defined as a `TypedDict` with only `messages`, at runtime, it behaves like a normal Python dictionary. Python allows you to add new key-value pairs (like 'frequency' or 'news_data') to a dictionary dynamically on the fly.
# 2. `self.state` is separate: In your `__init__` method, you created `self.state = {}`. This is just a standard, empty Python dictionary that belongs to this class instance, meaning you can store any arbitrary keys in it without any restrictions.
# (Note: For LangGraph to properly manage and pass these fields between different nodes, it is best practice to declare all expected fields in your `State` TypedDict).