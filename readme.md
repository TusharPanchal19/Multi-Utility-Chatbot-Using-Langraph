Multi Utility LangGraph PDF Chatbot

A Multi Utility AI Chatbot built using LangGraph, LangChain, Streamlit, Ollama, FAISS, and SQLite.

The application supports:

💬 Conversational AI using a local Ollama model
📄 PDF upload and document question answering
🔍 Web search using DuckDuckGo
🧮 Calculator tool
📈 Stock price lookup using Alpha Vantage
🧠 Persistent conversation memory using SQLite
🗂️ Multiple chat threads
🔎 RAG-based document retrieval using FAISS
💻 Interactive Streamlit frontend
🚀 Features
💬 Local AI Chatbot

The chatbot uses a locally running Ollama model:

qwen2.5:3b

This allows the application to run the language model locally instead of sending normal chat requests to a cloud LLM.

📄 PDF Question Answering

Users can upload a PDF directly from the Streamlit sidebar.

The application then:

Reads the uploaded PDF.
Extracts text using PyPDFLoader.
Splits the document into smaller chunks.
Converts chunks into embeddings.
Stores embeddings in a FAISS vector database.
Retrieves relevant document chunks when the user asks a question.
Provides the retrieved context to the LLM.

Each PDF is associated with a specific chat thread.

🔎 RAG Pipeline

The application uses Retrieval-Augmented Generation (RAG).

PDF Upload
    ↓
PyPDFLoader
    ↓
Document Pages
    ↓
RecursiveCharacterTextSplitter
    ↓
Document Chunks
    ↓
HuggingFace Embeddings
    ↓
FAISS Vector Store
    ↓
Retriever
    ↓
Relevant PDF Context
    ↓
Ollama LLM
    ↓
Final Answer

The embedding model used is:

sentence-transformers/all-MiniLM-L6-v2
🔍 Web Search Tool

The chatbot can search the web using:

DuckDuckGoSearchRun

The LLM can decide when web search is required and call the search tool through LangGraph.

🧮 Calculator Tool

The chatbot includes a calculator tool supporting:

Addition
Subtraction
Multiplication
Division

Supported operations:

add
sub
mul
div

Example:

Calculate 25 × 40

The chatbot can call the calculator tool to perform the calculation.

📈 Stock Price Tool

The chatbot can fetch stock prices using the Alpha Vantage API.

Example queries:

What is the stock price of AAPL?
Get the latest price of TSLA

The tool sends a request to:

Alpha Vantage GLOBAL_QUOTE API
🧠 Persistent Chat Memory

The project uses SQLite for LangGraph checkpointing.

User Message
      ↓
LangGraph
      ↓
Checkpoint
      ↓
SQLite Database

This allows conversations to persist between application runs.

The database files include:

chatbot.db
chatbot.db-shm
chatbot.db-wal
🗂️ Multiple Chat Threads

Every new conversation receives a unique thread ID.

Example:

Thread ID
    ↓
UUID Generated
    ↓
Separate Conversation Memory
    ↓
Separate PDF Retriever

Users can:

Create new chats
Switch between previous conversations
Maintain separate conversation histories
Associate uploaded PDFs with specific chat threads
🏗️ Project Architecture
LangGraph Chatbot
│
├── Streamlit Frontend
│
│   ├── Chat Interface
│   ├── PDF Upload
│   ├── Thread Management
│   └── Conversation Display
│
├── LangGraph Backend
│
│   ├── Chat Node
│   ├── Tool Node
│   └── SQLite Checkpointer
│
├── Tools
│
│   ├── Web Search
│   ├── Calculator
│   ├── Stock Price
│   └── RAG Tool
│
├── RAG System
│
│   ├── PDF Loader
│   ├── Text Splitter
│   ├── HuggingFace Embeddings
│   └── FAISS Vector Store
│
└── Ollama LLM
    └── Qwen2.5 3B
🔄 Complete Application Workflow
1️⃣ Application Starts

The Streamlit application starts with:

streamlit run streamlit-frontend.py

The frontend imports the LangGraph backend components:

from local_model import (
    chatbot,
    ingest_pdf,
    retrieve_all_threads,
    thread_document_metadata,
)
2️⃣ A New Thread Is Created

When the user starts a new conversation, a unique UUID is generated.

thread_id = uuid.uuid4()

This thread ID is used to maintain:

Conversation memory
LangGraph checkpoints
PDF retrievers
PDF metadata
3️⃣ User Uploads a PDF

The user uploads a PDF from the Streamlit sidebar.

Upload PDF
     ↓
Read PDF Bytes
     ↓
ingest_pdf()

The PDF bytes are passed to:

ingest_pdf(
    uploaded_pdf.getvalue(),
    thread_id=thread_key,
    filename=uploaded_pdf.name
)
4️⃣ PDF Processing

Inside ingest_pdf():

Uploaded PDF
      ↓
Temporary PDF File
      ↓
PyPDFLoader
      ↓
Extract Pages
      ↓
RecursiveCharacterTextSplitter
      ↓
Create Chunks

The document is split using:

chunk_size = 1000
chunk_overlap = 200
5️⃣ Creating Embeddings

Each document chunk is converted into a vector embedding using:

sentence-transformers/all-MiniLM-L6-v2
Document Chunk
      ↓
HuggingFace Embeddings
      ↓
Vector Representation
6️⃣ FAISS Vector Database

The document embeddings are stored inside FAISS.

Embeddings
    ↓
FAISS Vector Store
    ↓
Retriever

The retriever is stored separately for each chat thread:

_THREAD_RETRIEVERS[thread_id]

This ensures that PDFs uploaded in one chat are associated with that particular thread.

💬 Chat Workflow

When the user sends a message:

User
  ↓
Streamlit Frontend
  ↓
HumanMessage
  ↓
LangGraph
  ↓
Chat Node

The message is sent to the graph using:

chatbot.stream(
    {"messages": [HumanMessage(content=user_input)]},
    config=CONFIG,
    stream_mode="messages"
)
🤖 LangGraph Workflow

The LangGraph structure is:

START
  ↓
chat_node
  ↓
tools_condition
  ├───────────────┐
  ↓               ↓
END            ToolNode
                  ↓
              chat_node
Workflow Explanation
Step 1: START

The graph starts from:

graph.add_edge(START, "chat_node")
Step 2: Chat Node

The chat_node sends the conversation to the Ollama model.

Conversation
      ↓
System Message
      ↓
LLM

The chat node also checks whether a PDF retriever exists for the current thread.

Step 3: PDF Context Retrieval

If a PDF exists for the current thread:

User Question
      ↓
FAISS Retriever
      ↓
Top Relevant Chunks
      ↓
PDF Context
      ↓
System Message
      ↓
LLM

The retrieved document content is added as context for the model.

Step 4: Tool Decision

The model can decide whether it needs a tool.

Possible tools:

DuckDuckGo Search
Calculator
Stock Price
RAG Tool

LangGraph checks this using:

tools_condition
Step 5: Tool Execution

If a tool is required:

LLM
 ↓
Tool Call
 ↓
ToolNode
 ↓
Tool Result
 ↓
chat_node

The model then receives the tool output and generates the final response.

🧰 Available Tools
🔍 Search Tool
DuckDuckGoSearchRun

Used when the chatbot needs web information.

🧮 Calculator Tool
calculator(
    first_num,
    second_num,
    operation
)

Example:

10 + 20

The LLM can call:

calculator

and return:

30
📈 Stock Price Tool
get_stock_price(symbol)

Example:

AAPL
TSLA
MSFT

The tool uses the Alpha Vantage API.

📄 RAG Tool
rag_tool(query)

The RAG tool:

Gets the current thread ID.
Finds the thread's retriever.
Searches the FAISS vector database.
Retrieves relevant PDF chunks.
Returns document context and metadata.
🗃️ Conversation Memory

LangGraph checkpoints are stored in SQLite.

conn = sqlite3.connect(
    database="chatbot.db",
    check_same_thread=False
)

The SQLite checkpointer is created using:

checkpointer = SqliteSaver(conn=conn)

The graph is compiled with:

chatbot = graph.compile(
    checkpointer=checkpointer
)

This allows previous conversations to be retrieved later.

📁 Project Structure
LangGraph-Chatbot/
│
├── streamlit-frontend.py
│
├── local_model.py
│
├── .env
│
├── chatbot.db
│
├── chatbot.db-shm
│
├── chatbot.db-wal
│
├── __pycache__/
│
└── README.md
Important Files
streamlit-frontend.py

Contains:

Streamlit user interface
PDF upload functionality
Chat interface
Thread creation
Conversation switching
Response streaming
local_model.py

Contains:

Ollama LLM configuration
LangGraph workflow
Tools
RAG pipeline
FAISS retriever
SQLite checkpointing
⚙️ Installation
1. Clone the Repository
git clone YOUR_GITHUB_REPOSITORY_URL
cd LangGraph-Chatbot
2. Create a Virtual Environment
Windows
python -m venv venv

Activate it:

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
🤖 Install Ollama

Install Ollama and make sure the Ollama service is running.

Then download the model:

ollama pull qwen2.5:3b

You can verify the installation with:

ollama list

Run Ollama if necessary:

ollama serve
🔐 Environment Variables

Create a .env file:

HF_TOKEN=your_huggingface_token

If you move your Alpha Vantage API key into environment variables, you can also use:

ALPHA_VANTAGE_API_KEY=your_alpha_vantage_api_key

⚠️ Never upload your .env file to GitHub.

▶️ Running the Application

First ensure Ollama is running:

ollama serve

Then start Streamlit:

streamlit run streamlit-frontend.py

Open the local Streamlit URL shown in your terminal.

🔐 Recommended .gitignore

Create a .gitignore file containing:

# Environment variables
.env

# Python cache
__pycache__/
*.pyc

# SQLite database
*.db
*.db-shm
*.db-wal

# Virtual environment
venv/
.venv/

# Streamlit
.streamlit/secrets.toml

This prevents sensitive information and unnecessary local files from being uploaded to GitHub.

🛠️ Technologies Used
Technology	Purpose
Python	Core programming language
Streamlit	Frontend user interface
LangGraph	Agent workflow orchestration
LangChain	LLM and tool integration
Ollama	Local LLM runtime
Qwen2.5 3B	Language model
FAISS	Vector database
HuggingFace Embeddings	Document embeddings
PyPDF	PDF text extraction
SQLite	Persistent chat memory
DuckDuckGo	Web search
Alpha Vantage	Stock market data
🔮 Future Improvements

Possible future improvements include:

 Support multiple PDFs in one chat
 Persistent FAISS vector databases
 Source citations for PDF answers
 Document preview
 Support DOCX and TXT files
 Better RAG retrieval strategies
 Conversation export
 Human approval before sensitive tool execution
 Markdown report generation
 PDF report generation
 MCP tool integration
 Better error handling
 Streaming tool responses
 Authentication and user accounts
👨‍💻 Author

Tushar Panchal

⭐ Project Summary

This project demonstrates how multiple AI components can be combined into a single application:

                ┌─────────────────┐
                │    Streamlit    │
                │    Frontend     │
                └────────┬────────┘
                         │
                         ▼
                ┌─────────────────┐
                │    LangGraph    │
                │     Workflow    │
                └────────┬────────┘
                         │
          ┌──────────────┼──────────────┐
          ▼              ▼              ▼
      Ollama LLM      Tool System    SQLite Memory
          │              │
          │       ┌──────┼──────┐
          │       ▼      ▼      ▼
          │    Search Calculator Stock API
          │
          ▼
      PDF RAG System
          │
          ▼
   HuggingFace Embeddings
          │
          ▼
         FAISS

The chatbot combines local LLM inference, RAG, web search, utility tools, persistent memory, and a Streamlit interface into one LangGraph-based application.