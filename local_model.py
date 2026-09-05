from langgraph.graph import StateGraph,START, END
from typing import TypedDict, Literal, Annotated, Any, Dict, Optional
from langchain_huggingface import ChatHuggingFace,HuggingFaceEndpoint
import operator
import sqlite3
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.tools import tool
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph.message import add_messages
from langchain_core.messages import (
    BaseMessage,
    SystemMessage,
    HumanMessage
)
from dotenv import load_dotenv
import os
import requests
import tempfile
from langchain_ollama import ChatOllama
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings


load_dotenv()

hf_token = os.getenv("HF_TOKEN")

if not hf_token:
    raise ValueError("HF_TOKEN was not found in the .env file")


llm = ChatOllama(
    model="qwen2.5:3b",
    temperature=0.5,
    num_predict=2048
)

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)


_THREAD_RETRIEVERS: Dict[str, Any] = {}
_THREAD_METADATA: Dict[str, dict] = {}
CURRENT_THREAD_ID = {}


def _get_retriever(thread_id: Optional[str]):
    if thread_id and str(thread_id) in _THREAD_RETRIEVERS:
        return _THREAD_RETRIEVERS[str(thread_id)]
    return None


def ingest_pdf(file_bytes: bytes, thread_id: str, filename: Optional[str] = None) -> dict:
    if not file_bytes:
        raise ValueError("No bytes received for ingestion.")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
        temp_file.write(file_bytes)
        temp_path = temp_file.name

    try:
        loader = PyPDFLoader(temp_path)
        docs = loader.load()

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", " ", ""]
        )

        chunks = splitter.split_documents(docs)

        vector_store = FAISS.from_documents(chunks, embeddings)

        retriever = vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 4}
        )

        _THREAD_RETRIEVERS[str(thread_id)] = retriever

        _THREAD_METADATA[str(thread_id)] = {
            "filename": filename or os.path.basename(temp_path),
            "documents": len(docs),
            "chunks": len(chunks),
        }

        return {
            "filename": filename or os.path.basename(temp_path),
            "documents": len(docs),
            "chunks": len(chunks),
        }

    finally:
        try:
            os.remove(temp_path)
        except OSError:
            pass


search_tool = DuckDuckGoSearchRun(region="us-en")


@tool
def calculator(first_num: float, second_num: float, operation: str) -> dict:
    """
    Perform a basic arithmetic operation on two numbers.
    Supported operations: add, sub, mul, div
    """
    try:
        if operation == "add":
            result = first_num + second_num
        elif operation == "sub":
            result = first_num - second_num
        elif operation == "mul":
            result = first_num * second_num
        elif operation == "div":
            if second_num == 0:
                return {"error": "Division by zero is not allowed"}
            result = first_num / second_num
        else:
            return {"error": f"Unsupported operation '{operation}'"}
        
        return {"first_num": first_num, "second_num": second_num, "operation": operation, "result": result}
    except Exception as e:
        return {"error": str(e)}


@tool
def get_stock_price(symbol: str) -> dict:
    """
    Fetch latest stock price for a given symbol (e.g. 'AAPL', 'TSLA') 
    using Alpha Vantage with API key in the URL.
    """
    url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={"your api key"}
    r = requests.get(url)
    return r.json()


@tool
def rag_tool(query: str) -> dict:
    """
    Retrieve relevant information from the uploaded PDF for this chat thread.
    """
    thread_id = CURRENT_THREAD_ID.get("thread_id")

    retriever = _get_retriever(thread_id)

    if retriever is None:
        return {
            "error": "No document indexed for this chat. Upload a PDF first.",
            "query": query,
        }

    result = retriever.invoke(query)

    context = [doc.page_content for doc in result]
    metadata = [doc.metadata for doc in result]

    return {
        "query": query,
        "context": context,
        "metadata": metadata,
        "source_file": _THREAD_METADATA.get(str(thread_id), {}).get("filename"),
    }


tools = [search_tool, get_stock_price, calculator, rag_tool]
llm_with_tools = llm.bind_tools(tools)


class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


def chat_node(state: ChatState, config=None):
    thread_id = None

    if config:
        thread_id = config.get(
            "configurable",
            {}
        ).get("thread_id")

    if not thread_id and config:
        thread_id = config.get(
            "metadata",
            {}
        ).get("thread_id")

    thread_id = str(thread_id)

    CURRENT_THREAD_ID["thread_id"] = thread_id

    retriever = _get_retriever(thread_id)

    pdf_context = ""

    if retriever and state["messages"]:
        last_message = state["messages"][-1]

        if isinstance(last_message, HumanMessage):
            result = retriever.invoke(last_message.content)

            pdf_context = "\n\n".join(
                doc.page_content for doc in result
            )

    if pdf_context:
        document_instruction = (
            "An uploaded PDF exists for this chat. "
            "You MUST use the DOCUMENT CONTEXT below to answer questions about it. "
            "Do not say that the user has not uploaded a document.\n\n"
            "DOCUMENT CONTEXT:\n"
            f"{pdf_context}"
        )
    else:
        document_instruction = (
            "No PDF context is currently available. "
            "Only tell the user to upload a PDF if they specifically ask about a document."
        )

    system_message = SystemMessage(
        content=(
            "You are a helpful multi-utility assistant. "
            + document_instruction +
            "\n\nUse the calculator tool for calculations. "
            "Use the search tool when web search is needed. "
            "Use the stock price tool when the user asks for stock prices."
        )
    )

    messages = [
        system_message,
        *state["messages"]
    ]

    response = llm_with_tools.invoke(messages)

    return {"messages": [response]}

tool_node = ToolNode(tools)


# Checkpointer save into sqlite db
conn = sqlite3.connect(database='chatbot.db', check_same_thread=False)
# Checkpointer
checkpointer = SqliteSaver(conn=conn)

graph = StateGraph(ChatState)
graph.add_node("chat_node", chat_node)
graph.add_node("tools", tool_node)

graph.add_edge(START, "chat_node")

graph.add_conditional_edges("chat_node",tools_condition)
graph.add_edge('tools', 'chat_node')

chatbot = graph.compile(checkpointer=checkpointer)


def retrieve_all_threads():
    all_threads = set()
    for checkpoint in checkpointer.list(None):
        all_threads.add(checkpoint.config['configurable']['thread_id'])

    return list(all_threads)


def thread_has_document(thread_id: str) -> bool:
    return str(thread_id) in _THREAD_RETRIEVERS


def thread_document_metadata(thread_id: str) -> dict:
    return _THREAD_METADATA.get(str(thread_id), {})