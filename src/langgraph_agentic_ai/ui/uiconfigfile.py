from configparser import ConfigParser

class Config:
    def __init__(self, config_file="src/langgraph_agentic_ai/ui/uiconfigfile.ini"):
        self.config = ConfigParser()
        self.config.read(config_file)

    def get_llm_options(self):
        return self.config["DEFAULT"].get("LLM_OPTIONS").split(", ") 

    def get_usecase_options(self):
        return self.config["DEFAULT"].get("USECASE_OPTIONS").split(", ")

    def get_groq_model_options(self):
        return self.config["DEFAULT"].get("GROQ_MODEL_OPTIONS").split(", ")

    def get_page_title(self):
        return self.config["DEFAULT"].get("PAGE_TITLE")

    






# --------------------------------------------
'''
# configparser
To read a .ini file in Python, you can use the configparser module, which is a built-in module in Python's standard library.

'''