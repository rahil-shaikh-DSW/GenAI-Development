import os
from sentence_transformers import SentenceTransformer
from PyPDF2 import PdfReader
import torch
from tqdm import tqdm  # Already imported, we'll use it more
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_postgres import PGVector
from langchain.docstore.document import Document
from langchain.embeddings.base import Embeddings

# Database connection parameters
CONNECTION_STRING = "postgresql+psycopg2://postgres:123456@localhost:5432/vector_db"
COLLECTION_NAME = "chsbc"

# PDF path
pdf_path = r'bare.pdf'

# Initialize SentenceTransformer model with GPU support
device = 'cuda' if torch.cuda.is_available() else 'cpu'
model = SentenceTransformer('Alibaba-NLP/gte-large-en-v1.5', trust_remote_code=True, device=device)

# Custom Embeddings class for SentenceTransformer
class SentenceTransformerEmbeddings(Embeddings):
    def __init__(self, model):
        self.model = model

    def embed_documents(self, texts):
        """Generate embeddings for a list of documents with progress."""
        return self.model.encode(texts, convert_to_numpy=True, show_progress_bar=True).tolist()

    def embed_query(self, text):
        """Generate embedding for a single query."""
        return self.model.encode(text, convert_to_numpy=True).tolist()

def process_pdf_and_store_embeddings():
    try:
        # Read the PDF file
        print(f"Processing file: {pdf_path}")
        reader = PdfReader(pdf_path)
        pdf_text = "".join([page.extract_text() for page in tqdm(reader.pages, desc="Extracting PDF Pages") 
                           if page.extract_text()])

        if not pdf_text.strip():
            print(f"Warning: No text extracted from '{pdf_path}'. Skipping.")
            return

        # Split text into chunks with progress
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=3072, chunk_overlap=512)
        print("Splitting text into chunks...")
        texts = text_splitter.split_text(pdf_text)
        print(f"Created {len(texts)} chunks")

        # Create Document objects for LangChain with progress
        documents = [Document(page_content=text, metadata={"source": f"{COLLECTION_NAME}-{i}"}) 
                     for i, text in enumerate(tqdm(texts, desc="Creating Documents"))]

        # Initialize the custom embeddings
        embeddings = SentenceTransformerEmbeddings(model)

        # Initialize PGVector store
        vector_store = PGVector(
            collection_name=COLLECTION_NAME,
            connection=CONNECTION_STRING,
            embeddings=embeddings,
        )

        # Add documents to the vector store with progress
        print("Storing embeddings in PGVector...")
        batch_size = 100  # Adjust batch size based on your system
        for i in tqdm(range(0, len(documents), batch_size), desc="Storing Embeddings"):
            batch = documents[i:i + batch_size]
            vector_store.add_documents(batch)
        
        print(f"Added {len(documents)} embeddings to collection '{COLLECTION_NAME}'")

    except FileNotFoundError:
        print(f"Error: The specified file '{pdf_path}' was not found.")
    except Exception as e:
        print(f"Error processing and storing embeddings: {e}")

if __name__ == "__main__":
    process_pdf_and_store_embeddings()