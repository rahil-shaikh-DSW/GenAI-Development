import os
import psycopg2
from sentence_transformers import SentenceTransformer
from PyPDF2 import PdfReader
import torch
from tqdm import tqdm

# Database connection parameters
db_params = {
    "host": "localhost",
    "port": "5432",
    "database": "vector_db",
    "user": "postgres",
    "password": "123456"
}

# PDF path and collection name
pdf_path = r'merged_output.pdf'
collection_name = "chsbc"

# Initialize SentenceTransformer model with GPU support
device = 'cuda' if torch.cuda.is_available() else 'cpu'
model = SentenceTransformer('Alibaba-NLP/gte-large-en-v1.5', trust_remote_code=True, device=device)
#all-MiniLM-L6-v2
def setup_database():
    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()

        # Enable pgvector extension
        cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        
        # Create table for embeddings (1024 is the dimension of gte-large-en-v1.5 embeddings)
        table_name = f"embeddings_{collection_name}"
        cur.execute(f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                id SERIAL PRIMARY KEY,
                source TEXT NOT NULL,
                content TEXT NOT NULL,
                embedding VECTOR(1024)
            );
        """)

        conn.commit()
        print(f"Database setup complete. Table '{table_name}' created.")
        return conn, cur, table_name

    except Exception as e:
        print(f"Database setup error: {e}")
        return None, None, None

def create_embeddings(conn, cur, table_name):
    try:
        # Read the PDF file
        print(f"Processing file: {pdf_path}")
        reader = PdfReader(pdf_path)
        pdf_text = "".join([page.extract_text() for page in reader.pages if page.extract_text()])

        if not pdf_text.strip():
            print(f"Warning: No text extracted from '{pdf_path}'. Skipping.")
            return

        # Split text into chunks
        from langchain.text_splitter import RecursiveCharacterTextSplitter
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=3072, chunk_overlap=512)
        texts = text_splitter.split_text(pdf_text)

        # Generate embeddings
        print("Generating embeddings...")
        embeddings = [model.encode(text) for text in tqdm(texts, desc="Embedding Progress")]

        # Insert into database
        for i, (text, embedding) in enumerate(zip(texts, embeddings)):
            source = f"{collection_name}-{i}"
            cur.execute(f"""
                INSERT INTO {table_name} (source, content, embedding)
                VALUES (%s, %s, %s);
            """, (source, text, embedding.tolist()))

        conn.commit()
        print(f"Added {len(texts)} embeddings to table '{table_name}'")

    except FileNotFoundError:
        print(f"Error: The specified file '{pdf_path}' was not found.")
    except Exception as e:
        print(f"Embedding creation error: {e}")

    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    # Setup database and create table
    conn, cur, table_name = setup_database()
    if conn and cur and table_name:
        # Create and store embeddings
        create_embeddings(conn, cur, table_name)