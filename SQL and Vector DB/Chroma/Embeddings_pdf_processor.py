import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma  # Import Chroma vector store
from langchain.docstore.document import Document  # Import Document class
import chromadb
from sentence_transformers import SentenceTransformer
from PyPDF2 import PdfReader
import torch
from tqdm import tqdm

# Specify the path to your PDF file and collection name
pdf_path = r'merged_output.pdf'
collection_name = "chsbc"
db_path = r"bajajfinserve_agent\insurance_vdb3"

# Create db directory if it doesn't exist
if not os.path.exists(db_path):
    os.makedirs(db_path)
    print(f"Created directory: {db_path}")

try:
    # Initialize Chroma client with persistent storage settings
    client = chromadb.PersistentClient(path=db_path)

    # Create or get a collection
    collection = client.get_or_create_collection(name=collection_name)

    # Initialize SentenceTransformer model with GPU support
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    model = SentenceTransformer('Alibaba-NLP/gte-large-en-v1.5', trust_remote_code=True, device=device)

    # Read the PDF file
    print(f"Processing file: {pdf_path}")
    reader = PdfReader(pdf_path)
    pdf_text = "".join([page.extract_text() for page in reader.pages if page.extract_text()])

    if not pdf_text.strip():
        print(f"Warning: No text extracted from the file '{pdf_path}'. Skipping.")
    else:
        # Split the text into chunks
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=3072, chunk_overlap=512)
        texts = text_splitter.split_text(pdf_text)

        # Create metadata for each chunk
        metadatas = [{"source": f"chsbc-{i}"} for i in range(len(texts))]

        # Prepare documents for Chroma vector store
        documents = [Document(page_content=text, metadata=metadata) for text, metadata in zip(texts, metadatas)]

        # Generate embeddings using SentenceTransformer with progress bar
        print("Generating embeddings...")
        embedding_results = [model.encode(doc.page_content) for doc in tqdm(documents, desc="Embedding Progress")]

        # Add documents to the collection with their embeddings and metadata
        collection.add(documents=[doc.page_content for doc in documents],
                       metadatas=metadatas,
                       ids=[metadata['source'] for metadata in metadatas],
                       embeddings=embedding_results)

        print(f"Added {len(documents)} documents from '{pdf_path}' to collection: {collection_name}")

    # Verify creation by listing all collections and checking document count
    all_collections = client.list_collections()
    print("Existing collections:", all_collections)

    # Check document count in the collection
    document_count = collection.count()
    print(f"Total documents in '{collection_name}': {document_count}")

except FileNotFoundError:
    print(f"Error: The specified file '{pdf_path}' was not found.")
except ValueError as ve:
    print(f"Value Error: {ve}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")