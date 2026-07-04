
import streamlit as st
import os

from src.langgraph_agentic_ai.ui.uiconfigfile import Config


class LoadStreamlitUI:
    def __init__(self):
        self.config = Config()
        self.user_controls={}
    
    def load_streamlit_ui(self):
        st.set_page_config(page_title=" " + self.config.get_page_title(), layout="wide")
        st.header("😍😍" + self.config.get_page_title())

        with st.sidebar:
            # get options from config

            llm_options = self.config.get_llm_options()
            usecase_options = self.config.get_usecase_options()

            # LLM selection
            self.user_controls["selected_llm"] = st.selectbox("LLM Provider" , options=llm_options)

            if self.user_controls["selected_llm"] == "Groq":
                model_options = self.config.get_groq_model_options()

                self.user_controls["selected_groq_model"] = st.selectbox("Groq Model" , options=model_options)

                self.user_controls["GROQ_API_KEY"] = st.session_state["GROQ_API_KEY"] = st.text_input("API Key", type="password")

                # Validate API key
                if not self.user_controls["GROQ_API_KEY"]:
                    st.warning("Please enter your GROQ API key to proceed. Dont't have? refer : https://console.groq.com/keys")
                
            # usecase selection

            self.user_controls["selected_usecase"] = st.selectbox("Select Usecase" , options=usecase_options)

        return self.user_controls


                
        
        
        