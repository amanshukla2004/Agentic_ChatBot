from src.langgraph_agentic_ai.state.state import State
from datetime import datetime
from langchain_core.messages import SystemMessage

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

        print("chatbot with tools is invoked")
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
            print("\n--- [NODE: Chatbot With Tools] Executing ---")
            
            messages = state.get("messages", [])
            current_date = datetime.now().strftime("%Y-%m-%d")
            
            # Inject system message if not present
            if not messages or not isinstance(messages[0], SystemMessage):
                sys_msg = SystemMessage(content=f"You are a helpful assistant. Today's date is {current_date}. You have access to tools. If you have already called a tool and received the results, DO NOT call the exact same tool again. Synthesize the final answer immediately based on the tool results. ALWAYS use the standard tool calling API to invoke tools. NEVER use <function=...> XML tags to call tools. IMPORTANT: Do not include raw image markdown, thumbnails, or raw URLs from tool outputs in your final response, as the UI will render them automatically. Just summarize the findings.")
                messages = [sys_msg] + messages
                
            # Prevent infinite tool loops: if the last action was a tool execution, force a text response by unbinding tools.
            from langchain_core.messages import ToolMessage, AIMessage
            
            last_was_tool = False
            for msg in reversed(messages):
                if isinstance(msg, AIMessage):
                    break
                if isinstance(msg, ToolMessage):
                    last_was_tool = True
                    break
                    
            if last_was_tool:
                response = self.llm.invoke(messages)
            else:
                response = llm_with_tools.invoke(messages)
            
            # --- FALLBACK: Parse XML Tool Calls ---
            # Smaller models like llama-3.1-8b sometimes hallucinate XML tool calls instead of using the API natively.
            if not response.tool_calls and isinstance(response.content, str) and "<" in response.content:
                import re
                import json
                from langchain_core.messages import AIMessage
                # Look for <tool_name>{"arg": "val"}</tool_name>
                match = re.search(r'<([a-zA-Z0-9_]+)>\s*({.*?})\s*(?:</\1>)?', response.content, re.DOTALL)
                if match:
                    tool_name = match.group(1)
                    try:
                        import uuid
                        args = json.loads(match.group(2))
                        # Replace the response with a correctly formatted tool call message, keeping any other text
                        response = AIMessage(
                            content=response.content.replace(match.group(0), ""),
                            tool_calls=[{"name": tool_name, "args": args, "id": "call_" + str(uuid.uuid4().hex[:8])}]
                        )
                        print(f"Fallback parser activated! Converted XML to tool call: {tool_name}")
                    except Exception as e:
                        print("Fallback parser failed to parse JSON:", e)
                        
            return {"messages" : [response]}

        return chatbot_node
