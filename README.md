# 🤖 Graphite AI

<div align="center">

 
### *A multi-tool agent that reasons, routes, and remembers.*
 
[![Python Version](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Framework](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)
[![LangGraph](https://img.shields.io/badge/LangGraph-1C3C3C?style=for-the-badge&logo=langchain&logoColor=white)](https://langchain.com)
[![Groq](https://img.shields.io/badge/Groq-F55036?style=for-the-badge&logo=lightning&logoColor=white)](https://groq.com)
[![License](https://img.shields.io/badge/License-MIT-000000?style=for-the-badge)](https://opensource.org/licenses/MIT)
 
</div>
 
## ✨ Why Graphite AI?
 
Most LLM wrappers are stateless and boxed in by their training data. **Graphite AI** is different.
 
Built on **LangGraph**, it behaves as an intelligent router — evaluating every prompt before deciding how to answer it. Ask it a coding question, and it responds directly from the model. Ask it about current events, live weather, or a video tutorial, and it autonomously reaches out to the right tool, pulls real data, and folds that into its answer — no manual tool-picking required.
 
> 💡 **In short:** it's not a chatbot with a search button bolted on. Routing, tool use, and memory are native parts of how it thinks.
 
---
 
## 🚀 Core Capabilities
 
| Feature | Description |
| :--- | :--- |
| 🎥 **YouTube Search** | Finds and surfaces relevant video tutorials based on user intent |
| ☁️ **Weather Info** | Fetches real-time weather data for any global location |
| 📰 **AI News Aggregation** | Compiles and summarizes the latest AI industry updates into a cached, chronological report |
| 🔎 **Web Search** | Tavily-powered search augmentation for fast, accurate real-time answers |
| 🧠 **Dynamic Routing** | Evaluates prompts and routes them to the correct tool automatically |
| ⚡ **Real-Time Streaming** | Streams LLM responses token-by-token for a fast, responsive feel |
| 📊 **Agent Diagnostics** | An "Under the Hood" panel showing live Mermaid execution graphs + state JSON inspection |
 
---
 
## 🏗️ Architecture Flow
 
Graphite AI runs on a directed graph — every request moves through a router node that decides which tool (if any) gets called before the response is synthesized.
 
```mermaid
graph TD
    classDef router fill:#f9f,stroke:#333,stroke-width:4px,color:#000;
    classDef tool fill:#bbf,stroke:#333,stroke-width:2px,color:#000;
    classDef llm fill:#bfb,stroke:#333,stroke-width:2px,color:#000;
 
    User(["👤 User Input"]) --> Router{"Router Node"}:::router
 
    Router -->|News Intent| NewsTool["📰 AI News Tool"]:::tool
    Router -->|Web/General Intent| WebTool["🔎 Tavily Web Search"]:::tool
    Router -->|Weather Intent| WeatherTool["☁️ Weather API"]:::tool
    Router -->|Video Intent| YTTool["🎥 YouTube Search"]:::tool
    Router -->|No Tool Needed| LLM["💬 Groq LLM"]:::llm
 
    NewsTool --> Formatter["Response Synthesizer"]
    WebTool --> Formatter
    WeatherTool --> Formatter
    YTTool --> Formatter
    LLM --> Formatter
 
    Formatter --> Memory[("🧠 Memory Checkpointer")]
    Memory --> UI(["💻 Streamlit UI"])
```
 
---
 
## 🔍 Deep Dive Workflows
 
### 🔎 Web Search Augmentation
 
When a prompt needs live knowledge the model wasn't trained on, the router silently calls Tavily, injects the result as context, and *then* generates the answer.
 
```mermaid
graph LR
    classDef user fill:#e1bee7,stroke:#4a148c,stroke-width:2px,color:#000;
    classDef router fill:#ffcc80,stroke:#e65100,stroke-width:3px,color:#000;
    classDef tool fill:#bbdefb,stroke:#0d47a1,stroke-width:2px,color:#000;
    classDef llm fill:#c8e6c9,stroke:#1b5e20,stroke-width:2px,color:#000;
 
    U(["👤 User"]):::user -->|"Who won the game?"| R{"Router"}:::router
    R -->|"Requires live data"| T["🔎 Tavily API"]:::tool
    T -->|"Returns search results"| R
    R -->|"Injects context"| L["💬 Groq LLM"]:::llm
    L -->|"Streams answer"| U
```
 
### 📰 AI News Explorer
 
A dedicated multi-step pipeline: search → summarize → cache → render, so repeated visits don't re-trigger the same API calls.
 
```mermaid
graph LR
    classDef trigger fill:#ffcdd2,stroke:#b71c1c,stroke-width:2px,color:#000;
    classDef tool fill:#bbdefb,stroke:#0d47a1,stroke-width:2px,color:#000;
    classDef llm fill:#c8e6c9,stroke:#1b5e20,stroke-width:2px,color:#000;
    classDef file fill:#cfd8dc,stroke:#263238,stroke-width:2px,color:#000;
    classDef ui fill:#ffe082,stroke:#ff6f00,stroke-width:2px,color:#000;
 
    A(["🖱️ Click 'Fetch News'"]):::trigger --> B["📰 News Node"]:::tool
    B --> C["🔎 Tavily Search"]:::tool
    C --> D["💬 Groq Synthesizer"]:::llm
    D --> E[("📁 Save to .md")]:::file
    E --> F(["💻 Streamlit Cache"]):::ui
```
 
### 🎥 YouTube Tool Resolution
 
```mermaid
graph LR
    classDef user fill:#e1bee7,stroke:#4a148c,stroke-width:2px,color:#000;
    classDef router fill:#ffcc80,stroke:#e65100,stroke-width:3px,color:#000;
    classDef tool fill:#bbdefb,stroke:#0d47a1,stroke-width:2px,color:#000;
    classDef state fill:#d7ccc8,stroke:#3e2723,stroke-width:2px,color:#000;
 
    U(["👤 'Find a video on LangGraph'"]):::user --> R{"Router"}:::router
    R -->|"Video Intent"| Y["🎥 YouTube Tool"]:::tool
    Y -->|"Single tool call"| S[("State: append result once")]:::state
    S --> UI(["💻 Render in chat"])
```
 
---

 
---
 
## 🛠️ Tech Stack
 
| Layer | Technology |
| :--- | :--- |
| Agent Orchestration | LangGraph, LangChain |
| LLM Engine | Groq (Llama 3) |
| Search Infrastructure | Tavily API |
| Frontend | Streamlit |
| Memory Persistence | LangGraph `MemorySaver` |
 
---
 
## ⚡ Quick Start
 
Get Graphite AI running locally in under 2 minutes.
 
**1. Clone the repository**
```bash
git clone https://github.com/amanshukla2004/Agentic_ChatBot.git
cd Agentic_ChatBot
```
 
**2. Install dependencies**
```bash
pip install -r requirements.txt
```
 
**3. Configure API keys**
 
Enter them in the Streamlit UI, or export them to skip the prompt:
```bash
export GROQ_API_KEY="your-groq-api-key"
export TAVILY_API_KEY="your-tavily-api-key"
```
 
**4. Launch the app**
```bash
streamlit run app.py
```
 
---
 
## 📁 Project Structure
 
```text
Agentic_ChatBot/
├── app.py                     # Streamlit entry point
├── requirements.txt           # Project dependencies
└── src/
    └── langgraph_agentic_ai/
        ├── graph/             # LangGraph nodes & state schema
        ├── tools/             # YouTube, Weather, and News integrations
        ├── LLMS/              # Groq model configurations
        └── ui/                # Streamlit UI & Visualizer components
```
 
---
 
## 🗺️ Roadmap
 
- [ ] Support for local, offline LLMs via Ollama
- [ ] Multi-agent workflows (dedicated Researcher + Writer agents)
- [ ] Expand tool registry with GitHub and Jira integrations
- [ ] Persistent auth + PostgreSQL for long-term memory
- [ ] LangSmith tracing integration
---
 
<div align="center">
**Built with ❤️ by Aman Shukla**
 
[LinkedIn](https://www.linkedin.com/in/amanshukla-dev/) • [Email](mailto:work.amanshukla2004@gmail.com)
 
</div>
