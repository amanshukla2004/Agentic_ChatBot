from src.langgraph_agentic_ai.graph.graph_builder import GraphBuilder
import streamlit as st 
from src.langgraph_agentic_ai.ui.streamlitui.loadui import LoadStreamlitUI
from src.langgraph_agentic_ai.LLMS.groqllm import GroqLLM
from src.langgraph_agentic_ai.ui.streamlitui.display_result import DisplayResultStreamlit



def load_langgraph_agenticai_app():
    """
        Loads and run the langgraph agentic ai application with streamlit ui
        this function initializes the ui, handles user input, configures the llm model, sets up the graph based on the selected use case and displays the output while implementing exception handling for robustness.
    """

    # load ui

    ui = LoadStreamlitUI()
    user_input = ui.load_streamlit_ui()
    if not user_input:
        st.error("No input received from the user")
        return
    
    user_message = st.chat_input("Enter your message")

    if user_message:
        try:
            # configure llm
            obj_llm_configure = GroqLLM(user_controls_input = user_input)
            model = obj_llm_configure.get_llm_model()

            if not model:
                st.error("LLM configuration failed. Please check your API key and model selection.")
                return
            
            # initialise and set up the graph based on use case

            usecase = user_input.get('selected_usecase')
            if not usecase:
                st.error("Error: No use case selected. ")
                return
            graph_builder_instance = GraphBuilder(model)
            try:
                graph = graph_builder_instance.setup_graph(usecase)
                DisplayResultStreamlit(usecase, graph, user_message).display_result_on_ui()

            except Exception as e:
                import traceback
                traceback.print_exc()
                st.error(f"Error: Failed to setup the graph. {e}")
                return

        except Exception as e:
            # raise ValueError(f"{e}")

            st.error(f"Error: Graph set p failed - {e}")
            return


            












# -------------------------------------------------------
