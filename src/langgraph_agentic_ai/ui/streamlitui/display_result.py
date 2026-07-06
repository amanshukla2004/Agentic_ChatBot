import streamlit as st 
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
import os

class DisplayResultStreamlit:
    def __init__(self, graph, user_message, visualizer_container):
        self.graph = graph
        self.user_message = user_message
        self.visualizer_container = visualizer_container

    def display_result_on_ui(self):
        graph = self.graph
        user_message = self.user_message
        
        initial_state = {"messages": [user_message]}
        
        # We will keep track of the final result as we stream
        full_state = {"messages": [initial_state["messages"][0]]}
        workflow_steps = []
        
        with self.visualizer_container:
            with st.status("Agent Workflow Steps", expanded=True) as status:
                try:
                    # Use .stream instead of .invoke to get live step updates
                    for event in graph.stream(initial_state, {"recursion_limit": 15}):
                        for node_name, node_state in event.items():
                            st.write(f"🔄 **Executing Node:** `{node_name}`")
                            workflow_steps.append(node_name)
                            
                            if node_state is None:
                                node_state = {}
                            
                            # Accumulate the state manually since stream yields updates
                            if "route" in node_state:
                                full_state["route"] = node_state["route"]
                            if "summary" in node_state:
                                full_state["summary"] = node_state["summary"]
                            
                            msgs = []
                            if "messages" in node_state and node_state["messages"]:
                                msgs = node_state["messages"]
                                if not isinstance(msgs, list):
                                    msgs = [msgs]
                                full_state["messages"].extend(msgs)
                            
                    status.update(label="Workflow Complete!", state="complete", expanded=False)
                except Exception as e:
                    status.update(label="Workflow Failed", state="error", expanded=True)
                    st.error(f"Graph execution failed or timed out: {e}")
                    return
        
        # --- UPDATE GLOBAL STATE FOR MAIN UI ---
        route = full_state.get("route", "basic_chat")
        summary = full_state.get("summary")
        
        # Ensure route is correctly identified if bypassed via UI news button
        if summary and route != "news_request":
            route = "news_request"
            
        st.session_state.last_tool_used = route
        st.session_state.workflow_steps = workflow_steps
        
        if route == "news_request" or summary:
            if summary:
                st.session_state.news_summary = summary
                # Fix infinite loop: We must append an assistant message to change the last message role!
                st.session_state.messages.append({"role": "assistant", "content": "I've fetched the latest AI news for you! See the summary card above."})
            else:
                st.session_state.messages.append({"role": "assistant", "content": "Could not generate news summary."})
        else:
            # Parse Langchain messages back to dictionaries for main.py to render cleanly
            messages_list = full_state["messages"]
            for i, message in enumerate(messages_list):
                # We skip the very first message because it's just the user_message we already appended in main.py
                if type(message) == HumanMessage and message.content == self.user_message:
                    continue
                
                if type(message) == HumanMessage:
                    st.session_state.messages.append({"role": "user", "content": message.content})
                elif type(message) == ToolMessage:
                    is_youtube = "[![YouTube Video Thumbnail]" in message.content
                    if is_youtube:
                        # Render natively without an expander so the thumbnails are front and center
                        st.session_state.messages.append({
                            "role": "assistant", 
                            "content": f"🎥 **Here are the YouTube videos I found:**\n\n{message.content}"
                        })
                    else:
                        st.session_state.messages.append({
                            "role": "assistant",
                            "expander_title": f"🔧 :green[**Tool fetched data** (Length: {len(message.content)} chars)]",
                            "content": message.content
                        })
                elif type(message) == AIMessage and message.content:
                    # If the preceding message was a youtube tool fetch, skip this AI message 
                    # because smaller models tend to hallucinate channel names/video titles.
                    prev_msg = messages_list[i-1] if i > 0 else None
                    if prev_msg and type(prev_msg) == ToolMessage and "[![YouTube Video Thumbnail]" in prev_msg.content:
                        continue
                        
                    # Fix math formatting for Streamlit (Streamlit expects $, $$ instead of \(, \[)
                    content = message.content
                    content = content.replace(r"\(", "$").replace(r"\)", "$")
                    content = content.replace(r"\[", "$$").replace(r"\]", "$$")
                        
                    st.session_state.messages.append({"role": "assistant", "content": content})