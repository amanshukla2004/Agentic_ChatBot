import streamlit as st
import streamlit.components.v1 as components
import json
import plotly.express as px
import pandas as pd

def render_live_mermaid(mermaid_code: str, active_node: str = None, completed_nodes: list = None, failed_node: str = None, height: int = 500):
    """
    Renders a Mermaid diagram dynamically by injecting style nodes.
    - active_node: cyan glow (fill:#22D3EE)
    - completed_nodes: green (fill:#34D399)
    - failed_node: red (fill:#F87171)
    """
    if completed_nodes is None:
        completed_nodes = []
        
    style_lines = []
    
    # Add styling for completed nodes
    for node in completed_nodes:
        if node != active_node and node != failed_node:
            style_lines.append(f"style {node} fill:#34D399,stroke:#059669,stroke-width:2px,color:#000")
            
    # Add styling for failed node
    if failed_node:
        style_lines.append(f"style {failed_node} fill:#F87171,stroke:#DC2626,stroke-width:2px,color:#fff")
        
    # Add styling for active node
    if active_node:
        style_lines.append(f"style {active_node} fill:#22D3EE,stroke:#0891B2,stroke-width:3px,color:#000")
        
    if style_lines:
        mermaid_code += "\n" + "\n".join(style_lines)

    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <script type="module">
            import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
            mermaid.initialize({{ 
                startOnLoad: true, 
                theme: 'dark', 
                securityLevel: 'loose' 
            }});
        </script>
        <style>
            body {{ background-color: transparent; display: flex; justify-content: center; align-items: center; margin: 0; padding: 0; height: {height}px; overflow: hidden; }}
            .mermaid {{ width: 100%; height: 100%; display: flex; justify-content: center; align-items: center; }}
        </style>
    </head>
    <body>
        <div class="mermaid">
            {mermaid_code}
        </div>
    </body>
    </html>
    """
    components.html(html_code, height=height, scrolling=True)

def render_state_inspector(state_dict: dict):
    """
    Renders the live state dictionary using st.json.
    """
    st.markdown("### 🧩 Live State")
    if not state_dict:
        st.info("State is empty or not yet initialized.")
        return

    # Filter out overly long messages list to keep it readable, just showing counts or last message
    display_state = {}
    for k, v in state_dict.items():
        if k == "messages" and isinstance(v, list):
            display_state[k] = f"List of {len(v)} messages (Last: {v[-1].__class__.__name__ if v else 'None'})"
        else:
            display_state[k] = v
            
    st.json(display_state, expanded=True)

def render_timeline(events_data: list):
    """
    Renders a Gantt chart timeline of node execution.
    events_data should be a list of dicts with:
    {'Task': node_name, 'Start': start_time, 'Finish': end_time}
    """
    st.markdown("### ⏱️ Execution Timeline")
    if not events_data:
        st.info("No timeline data yet.")
        return
        
    df = pd.DataFrame(events_data)
    
    # Ensure start and finish are datetime objects
    df['Start'] = pd.to_datetime(df['Start'])
    df['Finish'] = pd.to_datetime(df['Finish'])

    fig = px.timeline(df, x_start="Start", x_end="Finish", y="Task", color="Task", 
                      title="Node Execution Duration", template="plotly_dark")
    fig.update_yaxes(autorange="reversed")
    fig.update_layout(showlegend=False, margin=dict(l=0, r=0, t=30, b=0), height=200)
    st.plotly_chart(fig, use_container_width=True)
