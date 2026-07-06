
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
        frequency = state['messages'][0].content.lower() # what is this fetching ? --> user input is being fetched here and that input is being converted to lower case.
        self.state['frequency'] = frequency
        time_range_map = {'daily' : 'day', 'weekly' : 'week','monthly': 'month', 'year' : 'year'}

        days_map = {'daily' : 1, 'weekly' : 7, 'year' : 366, 'monthly' : 30}

        

        print(os.getenv("TAVILY_API_KEY"))

        try:
            response = self.tavily.search(
                query="Top Artificial Intelligence (AI) technology news in India and globally",
                topic='news',
                days=days_map[frequency],
                max_results=12
            )
        except Exception as e:
            print("TAVILY ERROR:", repr(e))
            raise
                    

        # news_content = "\n\n".join([f"Title: {article['title']}\nURL: {article['url']}\n" for article in response['results']])

        state['news_data'] = response.get('results', [])
        self.state['news_data'] = state['news_data']
        return state



    def summarize_news(self, state: dict) -> dict:
        """
            Summarize the fetched news using an llm
            ARGS:
                state(dict) : the state dictionary containing 'news_data'
            
            RETURNS : dict -> Updated state with 'summary' key containing the summarized news
        """
        news_items = self.state['news_data']
        # we can use the news items 

        # Check if Tavily failed and returned our fake error article
        if len(news_items) == 1 and "Tavily API Error" in news_items[0].get('content', ''):
            state['summary'] = f"### Failed to Fetch News\n\n{news_items[0]['content']}\n\n*Please try again later. Tavily servers are currently unresponsive.*"
            self.state['summary'] = state['summary']
            return self.state

        prompt_template = ChatPromptTemplate.from_messages(
            [
                (
                    "system" , """You are a professional AI news summarization assistant. 
                    Your task is to summarize the following AI news articles into a clear, day-by-day markdown report.
                    
                    Requirements:
                    - Organize the summary chronologically by day (using headers like `### YYYY-MM-DD`).
                    - Under each day, summarize the key developments, breakthroughs, and announcements.
                    - You MUST include markdown links to the original resources for each point (e.g., [Source Name or Title](URL)).
                    - Keep the summary concise but highly informative.
                    - Maintain a professional and neutral tone.
                    - If multiple articles share the same date, group their insights together logically.
                    
                    Format the final output beautifully using markdown so it renders perfectly on a web UI.
                    """
                ),
                (
                    "user" , "Articles:\n{articles}"
                )
            ]
        )

        articles_str = "\n\n".join(
            [
                 f"Title: {item.get('title', 'Unknown')}\n Content: {item.get('content', '')}\n URL: {item.get('url', '')}\n Date: {item.get('published_date', 'Unknown')}" for item in news_items
            ]
        )
        
        try:
            response =  self.llm.invoke(
                prompt_template.format(articles = articles_str)
            )
            state['summary'] = response.content
        except Exception as e:
            state['summary'] = f"Groq LLM Error: {str(e)}"
            
        self.state['summary'] = state['summary'] # what is this? .
        return self.state

    # can work on this method more
    def save_result(self, state):
        import os
        frequency = self.state['frequency']
        summary = self.state['summary']
        
        # Ensure the directory exists
        os.makedirs("./AINews", exist_ok=True)
        filename = f"./AINews/{frequency}_summary.md"

        with open(filename, 'w') as f:
            f.write(f"# {frequency.capitalize()} AI News Summary\n\n")
            f.write(summary)

        self.state['filename'] = filename
        return self.state 


# my State class has only one field messages , how come we are able to have these many dictionary but we have not written in the State class

# answer: 
# 1. Python Dictionaries are Dynamic: Even if your `State` is defined as a `TypedDict` with only `messages`, at runtime, it behaves like a normal Python dictionary. Python allows you to add new key-value pairs (like 'frequency' or 'news_data') to a dictionary dynamically on the fly.
# 2. `self.state` is separate: In your `__init__` method, you created `self.state = {}`. This is just a standard, empty Python dictionary that belongs to this class instance, meaning you can store any arbitrary keys in it without any restrictions.
# (Note: For LangGraph to properly manage and pass these fields between different nodes, it is best practice to declare all expected fields in your `State` TypedDict).