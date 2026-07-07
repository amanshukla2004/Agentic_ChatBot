import streamlit as st 
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
import asyncio
from datetime import datetime
from src.langgraph_agentic_ai.ui.streamlitui.visualizer import render_live_mermaid, render_state_inspector, render_timeline

class DisplayResultStreamlit:
    def __init__(self, graph, user_message, thread_id, mermaid_container=None, state_container=None, timeline_container=None, stream_container=None):
        self.graph = graph
        self.user_message = user_message
        self.thread_id = thread_id
        self.mermaid_container = mermaid_container
        self.state_container = state_container
        self.timeline_container = timeline_container
        self.stream_container = stream_container

    async def _async_display(self, stream_input, config):
        full_state = {"messages": []}
        workflow_steps = []
        events_data = []
        node_start_times = {}
        completed_nodes = []
        failed_node = None
        streamed_content = ""
        
        try:
            base_mermaid = self.graph.get_graph().draw_mermaid()
        except:
            base_mermaid = "graph TD\n  Start --> End"
            
        async for event in self.graph.astream_events(stream_input, config, version="v2"):
            kind = event["event"]
            if kind == "on_chain_start":
                node_name = event["name"]
                if node_name and node_name not in ["__start__", "LangGraph", "Pregel", "RunnableSequence"]:
                    node_start_times[node_name] = datetime.now()
                    
                    if self.mermaid_container:
                        with self.mermaid_container:
                            render_live_mermaid(base_mermaid, active_node=node_name, completed_nodes=completed_nodes)
                            
            elif kind == "on_chain_end":
                node_name = event["name"]
                if node_name in node_start_times:
                    start_time = node_start_times[node_name]
                    end_time = datetime.now()
                    events_data.append({"Task": node_name, "Start": start_time, "Finish": end_time})
                    completed_nodes.append(node_name)
                    workflow_steps.append(node_name)
                    
                    # Update State Inspector
                    output = event["data"].get("output")
                    if output and isinstance(output, dict):
                        if "route" in output:
                            full_state["route"] = output["route"]
                        if "summary" in output:
                            full_state["summary"] = output["summary"]
                        if "messages" in output and output["messages"]:
                            msgs = output["messages"]
                            if not isinstance(msgs, list):
                                msgs = [msgs]
                            full_state["messages"].extend(msgs)
                            
                        if self.state_container:
                            with self.state_container:
                                render_state_inspector(output)
                                
                    if self.mermaid_container:
                        with self.mermaid_container:
                            render_live_mermaid(base_mermaid, active_node=None, completed_nodes=completed_nodes)
                            
                    if self.timeline_container:
                        with self.timeline_container:
                            render_timeline(events_data)
                            
            elif kind == "on_chain_error":
                node_name = event["name"]
                failed_node = node_name
                if self.mermaid_container:
                    with self.mermaid_container:
                        render_live_mermaid(base_mermaid, active_node=None, completed_nodes=completed_nodes, failed_node=failed_node)
                        
            elif kind == "on_chat_model_stream":
                if self.stream_container:
                    chunk = event["data"].get("chunk")
                    if chunk and hasattr(chunk, "content") and chunk.content and isinstance(chunk.content, str):
                        streamed_content += chunk.content
                        self.stream_container.markdown(streamed_content + " ▌")

        st.session_state.final_mermaid = base_mermaid
        st.session_state.final_state = full_state
        st.session_state.final_timeline = events_data
        return full_state, workflow_steps

    def display_result_on_ui(self, resume_command=None):
        config = {"recursion_limit": 15, "configurable": {"thread_id": self.thread_id}}
        
        if resume_command:
            stream_input = resume_command
            full_state = {"messages": []}
            workflow_steps = st.session_state.get("workflow_steps", [])
        else:
            initial_state = {"messages": [self.user_message]}
            stream_input = initial_state
            full_state = {"messages": [initial_state["messages"][0]]}
            workflow_steps = []
            
        try:
            new_state, steps = asyncio.run(self._async_display(stream_input, config))
            for k, v in new_state.items():
                if k == "messages":
                    full_state["messages"].extend(v)
                else:
                    full_state[k] = v
            workflow_steps.extend(steps)
        except Exception as e:
            st.error(f"Graph execution failed: {e}")
            return False

        # --- UPDATE GLOBAL STATE FOR MAIN UI ---
        route = full_state.get("route", "basic_chat")
        summary = full_state.get("summary")
        
        if summary and route != "news_request":
            route = "news_request"
            
        st.session_state.last_tool_used = route
        st.session_state.workflow_steps = workflow_steps
        
        config = {"configurable": {"thread_id": self.thread_id}}
        state_snapshot = self.graph.get_state(config)
        is_interrupted = len(state_snapshot.next) > 0
        
        if is_interrupted:
            return False
            
        if route == "news_request" or summary:
            if summary:
                st.session_state.news_summary = summary
                st.session_state.messages.append({"role": "assistant", "content": "I've fetched the latest AI news for you! See the summary card above."})
            else:
                st.session_state.messages.append({"role": "assistant", "content": "Could not generate news summary."})
        else:
            all_graph_messages = state_snapshot.values.get("messages", [])
            last_human_idx = -1
            for i in range(len(all_graph_messages) - 1, -1, -1):
                if isinstance(all_graph_messages[i], HumanMessage):
                    last_human_idx = i
                    break
                    
            if last_human_idx != -1:
                new_messages = all_graph_messages[last_human_idx + 1:]
                for i, message in enumerate(new_messages):
                    if type(message) == ToolMessage:
                        is_youtube = "[![YouTube Video Thumbnail]" in message.content
                        if is_youtube:
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
                        continue
                    elif isinstance(message, AIMessage) and message.content:
                        content = message.content
                        if content:
                            content = content.replace(r"\(", "$").replace(r"\)", "$")
                            content = content.replace(r"\[", "$$").replace(r"\]", "$$")
                            st.session_state.messages.append({"role": "assistant", "content": content})
                    
        return True