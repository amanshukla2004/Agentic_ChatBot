from src.langgraph_agentic_ai.graph.graph_builder import GraphBuilder
import streamlit as st 
from src.langgraph_agentic_ai.ui.streamlitui.loadui import LoadStreamlitUI
from src.langgraph_agentic_ai.LLMS.groqllm import GroqLLM
from src.langgraph_agentic_ai.ui.streamlitui.display_result import DisplayResultStreamlit

def load_langgraph_agenticai_app():
    """
        Loads and runs the langgraph agentic ai application with streamlit ui
    """
    ui = LoadStreamlitUI()
    user_input = ui.load_streamlit_ui()
    if not user_input:
        st.error("UI failed to load properly.")
        return
    
# --- EXTENSIBLE FEATURE REGISTRY ---
def render_ai_news_panel():
    st.info("📰 **AI News Workflow**\n\nSuccessfully compiled and summarized the latest AI articles.")

def render_web_search_panel():
    st.info("🔧 **Web / Media Search**\n\nThe agent utilized external search tools to answer your query.")

def render_default_panel():
    st.info("💬 **Standard Chat Mode**\n\nBasic conversation active. No external tools were utilized.")

TOOL_PANELS = {
    "ai_news": {
        "label": "📰 AI News",
        "icon": "📰",
        "render": render_ai_news_panel,
        "active_when": lambda last_tool: last_tool == "news_request"
    },
    "web_search": {
        "label": "🔧 Web Search",
        "icon": "🔧",
        "render": render_web_search_panel,
        "active_when": lambda last_tool: last_tool == "web_search"
    },
    "default": {
        "label": "💬 Chat Mode",
        "icon": "💬",
        "render": render_default_panel,
        "active_when": lambda last_tool: last_tool not in ["news_request", "web_search"]
    }
}

def load_langgraph_agenticai_app():
    """
        Loads and runs the langgraph agentic ai application with streamlit ui
    """
    ui = LoadStreamlitUI()
    user_input = ui.load_streamlit_ui()
    if not user_input:
        st.error("UI failed to load properly.")
        return
        
    if not user_input.get("GROQ_API_KEY") or not user_input.get("TAVILY_API_KEY"):
        st.info("👋 Welcome to Agentic AI Workflow! Please enter your **GROQ API Key** and **TAVILY API Key** in the sidebar to get started.")
        return
        
    # --- STATE INITIALIZATION ---
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "last_tool_used" not in st.session_state:
        st.session_state.last_tool_used = "basic_chat"
    if "news_summary" not in st.session_state:
        st.session_state.news_summary = None
        
    # --- HITL CHECKPOINTER ---
    from langgraph.checkpoint.memory import MemorySaver
    import uuid
    if "checkpointer" not in st.session_state:
        st.session_state.checkpointer = MemorySaver()
    if "thread_id" not in st.session_state:
        st.session_state.thread_id = str(uuid.uuid4())
    # --- SIDEBAR COMPONENTS ---
    with st.sidebar:
        st.write("---")
        
        # If there are cached workflow steps from the last execution, render them persistently
        if "workflow_steps" in st.session_state and st.session_state.workflow_steps:
            with st.expander("Agent Workflow Steps (Completed)", expanded=False):
                for step in st.session_state.workflow_steps:
                    st.write(f"✅ **Executed Node:** `{step}`")
        
        st.write("---")
        
        # --- NEW: Sidebar Tabs for 'Under the Hood' ---
        st.markdown("#### 🧠 Agent Diagnostics")
        tab_mermaid, tab_state, tab_timeline = st.tabs(["Graph", "State", "Timeline"])
        
        with tab_mermaid:
            mermaid_container = st.empty()
            if "final_mermaid" in st.session_state:
                with mermaid_container:
                    from src.langgraph_agentic_ai.ui.streamlitui.visualizer import render_live_mermaid
                    render_live_mermaid(st.session_state.final_mermaid, active_node=None, completed_nodes=st.session_state.get("workflow_steps", []))
                    
        with tab_state:
            state_container = st.empty()
            if "final_state" in st.session_state:
                with state_container:
                    from src.langgraph_agentic_ai.ui.streamlitui.visualizer import render_state_inspector
                    render_state_inspector(st.session_state.final_state)
                    
        with tab_timeline:
            timeline_container = st.empty()
            if "final_timeline" in st.session_state:
                with timeline_container:
                    from src.langgraph_agentic_ai.ui.streamlitui.visualizer import render_timeline
                    render_timeline(st.session_state.final_timeline)
        
        st.write("---")
        
        # Render the persistent dynamic tool panel
        st.markdown("#### 🔧 Tools Explorer")
        st.caption("The agent evaluates your prompt and automatically routes it to the appropriate tool:")
        st.markdown(
            """
            - 🌐 **Web Search:** Real-time web info (Tavily)
            - 🎥 **YouTube Search:** Find video tutorials
            - 📰 **AI News:** Curated industry updates
            """
        )
        
        st.markdown("#### ⚡ Active State")
        panel_rendered = False
        for key, panel in TOOL_PANELS.items():
            if panel["active_when"](st.session_state.last_tool_used):
                panel["render"]()
                panel_rendered = True
                break
        if not panel_rendered:
            TOOL_PANELS["default"]["render"]()
                
        st.write("---")
        
        # Persistent Quick Actions at the bottom
        st.markdown("#### 📰 AI News")
        st.session_state["timeframe"] = st.radio("News Timeframe", ["Daily", "Weekly", "Monthly"], horizontal=True, label_visibility="collapsed")
        if st.button("📰 Fetch AI News Now", use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": "give me the latest ai news"})
            st.session_state.news_summary = None
            st.rerun()

    # --- MAIN CHAT AREA ---
    # Empty State
    if not st.session_state.messages:
            st.markdown(
                """
                <div style="text-align: center; margin-top: 40px; margin-bottom: 40px; color: #9CA3AF;">
                    <img src="https://fonts.gstatic.com/s/e/notoemoji/latest/1f916/512.gif" alt="🤖" width="80" height="80" style="margin-bottom: 10px;">
                    <h1 style="color: #E5E7EB; font-weight: 700; font-size: 2.5rem; letter-spacing: -0.025em; margin-bottom: 10px;">Agentic AI Workflow</h1>
                    <p style="font-size: 1.1rem; max-width: 600px; margin: 0 auto; line-height: 1.5;">I am a stateful, intelligent routing agent equipped with multiple tools and dynamic workflows.</p>
                </div>
                """, 
                unsafe_allow_html=True
            )
            st.caption("💡 Hint: Try asking *'Find a YouTube video on LangGraph'*, *'Check the weather in Paris'*, or *'Give me the latest AI news'*.")
    
    # Render persistent chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            if "expander_title" in msg:
                with st.expander(msg["expander_title"]):
                    st.markdown(msg["content"])
            else:
                st.markdown(msg["content"])
            
    # If there's a stored news summary, render it as a system message card
    if st.session_state.news_summary:
        st.markdown(f'<div class="news-card">{st.session_state.news_summary}</div>', unsafe_allow_html=True)

    # --- INITIALIZE GRAPH EARLY TO CHECK FOR INTERRUPTS ---
    obj_llm_configure = GroqLLM(user_controls_input = user_input)
    model = obj_llm_configure.get_llm_model()
    if not model:
        st.error("LLM configuration failed.")
        return
        
    graph_builder_instance = GraphBuilder(model)
    graph = graph_builder_instance.setup_graph(checkpointer=st.session_state.checkpointer)
    config = {"configurable": {"thread_id": st.session_state.thread_id}}
    
    config = {"configurable": {"thread_id": st.session_state.thread_id}}

    # --- CHAT INPUT & EXECUTION ---
    user_message = st.chat_input("Ask a question, request web search, or ask for AI News...")
    
    if user_message:
        # Immediately display user message in the UI before processing
        st.session_state.messages.append({"role": "user", "content": user_message})
        # Clear any previous news summary when a new chat starts
        st.session_state.news_summary = None
        # Rerun to update the UI with the user message
        st.rerun()

    # Process the last message if it's from the user
    if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
        latest_user_msg = st.session_state.messages[-1]["content"]
        try:
            # We can determine if it's news based on exact match or let router handle it
            usecase = "news" if latest_user_msg.lower().strip() == "give me the latest ai news" else None
            # Re-setup graph with specific usecase entry point if needed
            new_graph_builder_instance = GraphBuilder(model)
            graph = new_graph_builder_instance.setup_graph(usecase=usecase, checkpointer=st.session_state.checkpointer)
            
            # Setup real-time feedback UI
            with st.chat_message("assistant"):
                with st.spinner("🧠 Agent is analyzing and routing your request..."):
                    stream_container = st.empty()
                    
            # Pass the visualizer containers and stream container to display_result
            DisplayResultStreamlit(graph, latest_user_msg, st.session_state.thread_id, mermaid_container, state_container, timeline_container, stream_container).display_result_on_ui()
            
            # After graph finishes, rerun to flush states and lock UI
            st.rerun()

        except Exception as e:
                import traceback
                traceback.print_exc()
                st.error(f"Error: Failed to setup the graph. {e}")
                return

        except Exception as e:
            st.error(f"Error: Graph setup failed - {e}")
            return
