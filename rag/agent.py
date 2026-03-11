from dotenv import load_dotenv
import warnings

warnings.filterwarnings("ignore")
load_dotenv()

# Updated imports
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage, AIMessage  # for memory

# Embedding model
embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# Vector DB
vector_db = Chroma(
    persist_directory="vector_db",
    embedding_function=embedding_model
)

retriever = vector_db.as_retriever(search_kwargs={"k": 4})

# LLM
llm = ChatMistralAI(
    model="mistral-small-latest",
    temperature=0.2
)

# Memory — stores conversation turns as a plain list
chat_history: list = []

# Prompt — now includes {chat_history}
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an AI assistant that helps users find Indian government schemes."),
    ("human",
"""
Using ONLY the context below, return scheme details in this format.

Scheme Name:
Description:
Benefits:
Eligibility:
Application Process:
Required Documents:
State:
Link:

Conversation History:
{chat_history}

Context:
{context}

Question:
{question}
""")
])

# Convert documents to text
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

# Format chat_history list into a readable string for the prompt
def get_chat_history(_):
    if not chat_history:
        return "No previous conversation."
    lines = []
    for msg in chat_history:
        if isinstance(msg, HumanMessage):
            lines.append(f"User: {msg.content}")
        elif isinstance(msg, AIMessage):
            lines.append(f"Assistant: {msg.content}")
    return "\n".join(lines)

# RAG Chain
chain = (
    {
        "context":      retriever | format_docs,
        "question":     lambda x: x,
        "chat_history": get_chat_history,
    }
    | prompt
    | llm
    | StrOutputParser()
)

# Ask function
def ask_agent(question: str) -> str:
    result = chain.invoke(question)

    # Save this turn to memory
    chat_history.append(HumanMessage(content=question))
    chat_history.append(AIMessage(content=result))

    return result


# # Test
# if __name__ == "__main__":
#     print(ask_agent("schemes for farmers in Gujarat"))