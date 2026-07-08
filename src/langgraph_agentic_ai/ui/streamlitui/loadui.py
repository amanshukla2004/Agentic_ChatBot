import streamlit as st
import os

from src.langgraph_agentic_ai.ui.uiconfigfile import Config

class LoadStreamlitUI:
    def __init__(self):
        self.config = Config()
        self.user_controls={}
    
    def load_streamlit_ui(self):
        st.set_page_config(page_title=" " + self.config.get_page_title(), layout="wide")
        
        # Inject custom CSS from design.md
        st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono&display=swap');
        
        /* Global typography and colors */
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }
        code, pre {
            font-family: 'JetBrains Mono', monospace;
        }
        
        /* Pill-style radio buttons for mode/timeframe selection */
        div[role="radiogroup"] > label {
            background: #1A1D27;
            border-radius: 8px;
            padding: 8px 14px;
            margin-bottom: 4px;
            transition: background 0.2s ease;
            border: 1px solid #232733;
        }
        div[role="radiogroup"] > label:hover { 
            background: #232733; 
        }
        
        /* News Card Container */
        .news-card {
            background: #1A1D27;
            border: 1px solid #232733;
            border-radius: 12px;
            padding: 24px;
            color: #E5E7EB;
            margin-top: 16px;
        }
        
        /* Connected Status Badge (Top Right corner) */
        .status-badge {
            position: absolute;
            top: 20px;
            right: 20px;
            background: #34D399;
            color: #0F1117;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 600;
            z-index: 1000;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Removed API Connected badge and redundant header to clean up the UI
        
        with st.sidebar:
            llm_options = self.config.get_llm_options()

            # LLM selection
            self.user_controls["selected_llm"] = st.selectbox("LLM Provider" , options=llm_options)

            if self.user_controls["selected_llm"] == "Groq":
                groq_key = st.text_input("🔑 1. Groq API Key", type="password", key="GROQ_API_KEY")
                st.caption("Get your free Groq API key [here](https://console.groq.com/keys).")
                self.user_controls["GROQ_API_KEY"] = groq_key

                if not groq_key:
                    st.warning("Please enter your GROQ API key to proceed.")
                
                model_options = self.config.get_groq_model_options()
                self.user_controls["selected_groq_model"] = st.selectbox("🧠 2. Select Groq Model (e.g. llama3)" , options=model_options)
                
            tavily_key = st.text_input("🌐 3. TAVILY API Key (Web Search)", type="password", key="TAVILY_API_KEY")
            st.caption("Get your free Tavily API key [here](https://app.tavily.com/home).")
            os.environ["TAVILY_API_KEY"] = tavily_key
            self.user_controls["TAVILY_API_KEY"] = tavily_key

            if not tavily_key:
                st.warning("Please enter your TAVILY API key for full functionality.")

        return self.user_controls