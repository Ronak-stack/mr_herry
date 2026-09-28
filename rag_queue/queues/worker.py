import os
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from openai import OpenAI

# Load environment variables from .env
load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

# Initialize embeddings and database client once at module load
embedding_model = OpenAIEmbeddings(
    model="text-embedding-3-large",
    api_key=api_key
)

vector_db = QdrantVectorStore.from_existing_collection(
    embedding=embedding_model,
    url=os.getenv("QDRANT_URL", "http://localhost:6333"),
    collection_name="demo_pdf_collection"
)

def process_query(query: str) -> str:
    # 1. Retrieve relevant chunks (default k=4)
    search_results = vector_db.similarity_search(query=query, k=4)

    # 2. Build context string safely
    context_chunks = []
    for res in search_results:
        page_num = res.metadata.get("page_label", res.metadata.get("page", "N/A"))
        source = res.metadata.get("source", "Unknown file")
        context_chunks.append(
            f"Page Content: {res.page_content}\n"
            f"Page Number: {page_num}\n"
            f"File Location: {source}"
        )

    context = "\n\n---\n\n".join(context_chunks)

    # 3. Construct system prompt
    system_prompt = f"""You are a helpful AI assistant that answers user queries strictly based on the provided context retrieved from a PDF document.

Always:
1. Answer using only the provided context. If the answer cannot be found in the context, state that clearly.
2. Direct the user to the specific page number(s) and file location to learn more.

Context:
{context}"""

    # 4. Generate response
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query}
        ],
        temperature=0.2
    )

    answer = response.choices[0].message.content
    print(answer)
    return answer

if __name__ == "__main__":
    test_query = "What is the primary topic of the document?"
    process_query(test_query)