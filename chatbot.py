import ollama

from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

# Load embedding model
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# Load FAISS vector store
vectorstore = FAISS.load_local(
    "vectorstore",
    embeddings,
    allow_dangerous_deserialization=True
)

# Create retriever
retriever = vectorstore.as_retriever()

# Chatbot function
def ask_chatbot(question):

    # Retrieve relevant documents
    docs = retriever.invoke(question)

    # Combine document contents
    context = "\n".join([doc.page_content for doc in docs])

    # Prompt for AI
    prompt = f"""
You are an Industrial Maintenance AI Assistant.

Use the following knowledge base to answer the question.

Knowledge Base:
{context}

Question:
{question}

Answer:
"""

    # Generate response using Ollama
    response = ollama.chat(
        model="tinyllama",   # Changed from llama3
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    # Return answer
    return response["message"]["content"]