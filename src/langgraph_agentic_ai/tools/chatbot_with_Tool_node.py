from src.langgraph_agentic_ai.state.state import State



class ChatbotWithToolNode:
    """
    Chatbot logic enhanced with tool integration.
    """
    def __init__(self, model):
        self.llm = model
    
    # not needed 
    def process(self, state: State) -> dict:
        """
            Processes the input state and generates a response with tool integration
        """
        user_input = state["messages"][-1] if state["messages"] else ""

        llm_response = self.llm.invoke([{"role": "user", "content": user_input}])

        # Simulate tool-specific logic
        tools_response= f"tool integration for '{user_input}' "

        return {"messages" : [llm_response, tools_response]}

    def create_chatbot(self, tools):
        ''' returns a chatbot node functionality '''

        llm_with_tools = self.llm.bind_tools(tools)
        
        def chatbot_node(state: State):
            '''
            chatbot logic for processing the input state and returning a response
            '''
            return {"messages" : [llm_with_tools.invoke(state["messages"])]}

        return chatbot_node