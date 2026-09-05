🤖 Multi-Utility LangGraph PDF Chatbot

A multi-utility AI chatbot built with LangGraph, LangChain, Streamlit, Ollama, FAISS, and SQLite.

The application supports conversational AI, PDF-based question answering using RAG, web search, calculations, stock price lookup, persistent chat memory, and multiple conversation threads.

✨ Features
💬 Local AI chatbot powered by Ollama
📄 Upload and chat with PDF documents
🧠 RAG-based document retrieval using FAISS
🔍 Web search using DuckDuckGo
🧮 Built-in calculator tool
📈 Stock price lookup using Alpha Vantage
💾 Persistent conversation memory using SQLite
🗂️ Multiple chat threads
🔄 Streaming AI responses
📚 Thread-specific PDF retrieval
## 🏗️ Architecture

```mermaid
flowchart TD
    A[Streamlit Frontend] --> B[LangGraph Workflow]

    B --> C[Chat Node]
    B --> D[Tool Node]

    C --> E[Ollama - Qwen2.5 3B]

    D --> F[DuckDuckGo Search]
    D --> G[Calculator]
    D --> H[Stock Price API]
    D --> I[RAG Tool]

    I --> J[FAISS Vector Store]
    J --> K[HuggingFace Embeddings]

    B --> L[SQLite Memory]

### Application Workflow

```markdown
## 🔄 Application Workflow

```mermaid
flowchart TD
    A[User Opens Application] --> B[Streamlit Frontend]
    B --> C[Create or Load Thread ID]

    C --> D{Upload PDF?}

    D -->|Yes| E[PyPDFLoader]
    E --> F[Split Document into Chunks]
    F --> G[Create Embeddings]
    G --> H[Store in FAISS]

    D -->|No| I[User Sends Message]
    H --> I

    I --> J[LangGraph Chat Node]
    J --> K[Ollama LLM]

    K --> L{Tool Required?}

    L -->|No| M[Generate Response]

    L -->|Yes| N[Tool Node]
    N --> O[Execute Tool]
    O --> J

    M --> P[Display Response]

3. Tool Calling Workflow
                    ┌─────────────┐
                    │  Chat Node  │
                    └──────┬──────┘
                           │
                    tools_condition
                           │
              ┌────────────┴────────────┐
              │                         │
              ▼                         ▼
         Direct Answer               Tool Node
              │                         │
              ▼                         ▼
             END                    Tool Result
                                        │
                                        ▼
                                    Chat Node
                                        │
                                        ▼
                                      Answer

Available tools:

DuckDuckGo Search
Calculator
Stock Price Tool
RAG Tool
### RAG Workflow

```markdown
## 📄 PDF RAG Workflow

```mermaid
flowchart LR
    A[PDF Upload] --> B[PyPDFLoader]
    B --> C[Document Pages]
    C --> D[Text Splitter]
    D --> E[Document Chunks]
    E --> F[HuggingFace Embeddings]
    F --> G[FAISS Vector Store]
    G --> H[Retriever]
    H --> I[Relevant Context]
    I --> J[Ollama LLM]
    J --> K[Final Answer]

The document is stored separately for each conversation thread.

Thread ID
    │
    ├── Conversation Memory
    │
    └── PDF Retriever

This ensures that different chats can work with different documents.

🔎 Answering Questions From PDF

When the user asks a question:

User Question
      ↓
FAISS Retriever
      ↓
Relevant Document Chunks
      ↓
PDF Context
      ↓
Ollama LLM
      ↓
Final Answer

The application retrieves the most relevant PDF chunks and provides them as context to the language model.

🧰 Available Tools
🔍 Web Search

The chatbot uses DuckDuckGo for web searches.

DuckDuckGoSearchRun

The LLM can automatically decide when web search is required.

🧮 Calculator

Supports basic arithmetic operations:

add
sub
mul
div

Example:

Calculate 25 × 10
📈 Stock Price Lookup

The chatbot can retrieve stock prices using the Alpha Vantage API.

Examples:

What is the price of AAPL?
Get the latest TSLA stock price
📄 RAG Tool

The RAG tool retrieves relevant information from the PDF associated with the current chat thread.

User Query
     ↓
Thread Retriever
     ↓
FAISS Search
     ↓
Relevant Chunks
     ↓
LLM Context
💾 Persistent Memory

Conversation history is stored using SQLite and LangGraph Checkpoints.

Conversation
      ↓
LangGraph Checkpointer
      ↓
SQLite Database

This allows previous conversations to be loaded from the sidebar.

📁 Project Structure
LangGraph-Chatbot/
│
├── streamlit-frontend.py     # Streamlit user interface
├── local_model.py            # LangGraph backend and RAG system
│
├── chatbot.db                # SQLite conversation database
├── chatbot.db-shm
├── chatbot.db-wal
│
├── .env                      # Environment variables
├── .gitignore
├── README.md
│
└── __pycache__/
⚙️ Installation
1. Clone the Repository
git clone https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
cd YOUR_REPOSITORY
2. Create a Virtual Environment
Windows
python -m venv venv

Activate the environment:

venv\Scripts\activate
3. Install Dependencies
pip install streamlit
pip install langgraph
pip install langchain
pip install langchain-community
pip install langchain-ollama
pip install langchain-huggingface
pip install langchain-text-splitters
pip install sentence-transformers
pip install faiss-cpu
pip install pypdf
pip install python-dotenv
pip install requests
pip install duckduckgo-search
🤖 Ollama Setup

Install Ollama on your system.

Then download the model:

ollama pull qwen2.5:3b

Check available models:

ollama list

Start the Ollama server:

ollama serve

Make sure Ollama is running before starting the Streamlit application.

🔐 Environment Variables

Create a .env file in the project directory:

HF_TOKEN=your_huggingface_token

If you use an Alpha Vantage API key through environment variables:

ALPHA_VANTAGE_API_KEY=your_alpha_vantage_api_key

⚠️ Never upload your .env file to GitHub.

▶️ Run the Application

Start Ollama:

ollama serve

Then run Streamlit:

streamlit run streamlit-frontend.py

The application will open in your browser.

🔧 Technologies Used
Technology	Purpose
Python	Backend programming
Streamlit	Web interface
LangGraph	AI workflow orchestration
LangChain	LLM and tool integration
Ollama	Local LLM runtime
Qwen 2.5 3B	Language model
FAISS	Vector database
HuggingFace	Text embeddings
PyPDFLoader	PDF processing
SQLite	Persistent chat memory
DuckDuckGo	Web search
Alpha Vantage	Stock data

👨‍💻 Author

Tushar Panchal

⭐ If You Like This Project

Consider giving the repository a star ⭐ on GitHub.

<img width="1917" height="866" alt="image" src="https://github.com/user-attachments/assets/17cfc0ee-95c5-44d7-a4bb-2d4219f04bab" />
