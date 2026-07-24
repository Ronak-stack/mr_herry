from dotenv import load_dotenv
from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader

from langchain_text_splitters import RecursiveCharacterTextSplitter

from langchain_openai import OpenAIEmbeddings

from langchain_qdrant import QdrantVectorStore

load_dotenv()

file_path = Path(__file__).parent / "demo.pdf"

# Load pdf with all set of pages using langchain

loader = PyPDFLoader(file_path=file_path)

set_of_pages_after_loading_the_pdf = loader.load()

# how to access seperate page from a pdf after loaded
# print(set_of_pages_after_loading_the_pdf[0])

# start chunking
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=400)

chunks = text_splitter.split_documents(documents=set_of_pages_after_loading_the_pdf)

# Vectory embedding
embeddint_model = OpenAIEmbeddings(
    model="text-embedding-3-large"
)

# store data in vector db
vector_store = QdrantVectorStore.from_documents(
    documents=chunks,
    embedding=embeddint_model,
    url="http://localhost:6333",
    collection_name="demo_pdf_collection"
)

print("Vector store successfully....done")