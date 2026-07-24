from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from openai import OpenAI

client = OpenAI(api_key="")

def proccess_query(query:str):
    embeddint_model = OpenAIEmbeddings(model="text-embedding-3-large")
 
    vector_db = QdrantVectorStore.from_existing_collection(
        embedding=embeddint_model,
        url="http://localhost:6333",
        collection_name="demo_pdf_collection"
    )

    search_result = vector_db.similarity_search(query=query)

    context = "\n\n\n".join([f"Page Content: {result.page_content}\nPage Number:{result.metadata['page_label']}\nFile Location:{result.metadata['source']}" for result in search_result])

    system_prompt = f"""
        You are a helpfull AI assistant who answers user query based on available context retrived from a PDF file along with page_content and page number.

        You should only ans the user based on the following context and navigate the user to open the right page number to know more.

        Context:{context}
    """

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query}
        ]
    )

    print(response.choices[0].message.content)