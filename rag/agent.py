from dotenv import load_dotenv
import warnings

warnings.filterwarnings("ignore")
load_dotenv()

# Vector DB + Embeddings
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

# LLM
from langchain_mistralai import ChatMistralAI

# LangChain Core
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

# -------------------------------------------------
# Embedding model
# -------------------------------------------------

embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# -------------------------------------------------
# Vector Database
# -------------------------------------------------

vector_db = Chroma(
    persist_directory="vector_db",
    embedding_function=embedding_model
)

retriever = vector_db.as_retriever(search_kwargs={"k": 3})

# -------------------------------------------------
# LLM
# -------------------------------------------------

llm = ChatMistralAI(
    model="mistral-small-latest",
    temperature=0.2
)

# -------------------------------------------------
# Prompt
# -------------------------------------------------

prompt = ChatPromptTemplate.from_messages([
    ("system",
     "You are an AI assistant that helps users find Indian government schemes."),

    ("placeholder", "{chat_history}"),

    ("human",
"""
Using ONLY the context below, return scheme details.

Context:
{context}

Question:
{question}
""")
])

# -------------------------------------------------
# Format documents
# -------------------------------------------------

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

# -------------------------------------------------
# Rewrite question using history
# -------------------------------------------------

def rewrite_question(question, chat_history):

    if not chat_history:
        return question

    history_text = "\n".join([msg.content for msg in chat_history])

    rewrite_prompt = f"""
Rewrite the follow-up question into a standalone search query.

Conversation:
{history_text}

Follow-up question:
{question}

Standalone search query:
"""

    response = llm.invoke(rewrite_prompt)
    return response.content

# -------------------------------------------------
# Retrieve context
# -------------------------------------------------

def get_context(x):

    question = x["question"]
    chat_history = x["chat_history"]

    standalone_question = rewrite_question(question, chat_history)

    docs = retriever.invoke(standalone_question)

    return format_docs(docs)

# -------------------------------------------------
# RAG Chain
# -------------------------------------------------

chain = (
    {
        "context": get_context,
        "question": lambda x: x["question"],
        "chat_history": lambda x: x["chat_history"],
    }
    | prompt
    | llm
    | StrOutputParser()
)

# -------------------------------------------------
# Memory Store
# -------------------------------------------------

store = {}

def get_session_history(session_id: str):

    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()

    return store[session_id]

# -------------------------------------------------
# Chain with Memory
# -------------------------------------------------

chain_with_memory = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="question",
    history_messages_key="chat_history",
)

# -------------------------------------------------
# Ask function
# -------------------------------------------------

def ask_agent(question: str, session_id="user_1"):

    return chain_with_memory.invoke(
        {"question": question},
        config={"configurable": {"session_id": session_id}}
    )

# -------------------------------------------------
# CLI Test
# -------------------------------------------------

if __name__ == "__main__":

    print("\nAI Government Scheme Assistant")
    print("Type 'exit' to stop\n")

    while True:

        q = input("Ask: ")

        if q.lower() == "exit":
            break

        answer = ask_agent(q)

        print("\nAI:", answer)