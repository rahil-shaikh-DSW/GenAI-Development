import os
import psycopg2
from sentence_transformers import SentenceTransformer
import litellm
from litellm import completion
import torch

# Database connection parameters
db_params = {
    "host": "localhost",
    "port": "5432",
    "database": "vector_db",
    "user": "postgres",
    "password": "123456"
}

# Collection name (table created earlier)
collection_name = "chsbc"
table_name = f"embeddings_{collection_name}"

# Initialize SentenceTransformer model
device = 'cuda' if torch.cuda.is_available() else 'cpu'
model = SentenceTransformer('Alibaba-NLP/gte-large-en-v1.5', trust_remote_code=True, device=device)

# LiteLLM configuration (replace with your Gemini API key)
os.environ["GEMINI_API_KEY"] = "AIzaSyD4r52F6L76Q8t0E9AtVPJdafy7DDm-bpI"  # Replace with actual key
litellm.api_key = os.environ["GEMINI_API_KEY"]

def connect_to_db():
    try:
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()
        return conn, cur
    except Exception as e:
        print(f"Database connection error: {e}")
        return None, None

def retrieve_context(query, conn, cur, top_k=3):
    # Generate embedding for the query
    query_embedding = model.encode(query).tolist()

    # Query the database for top-k similar embeddings
    cur.execute(f"""
        SELECT content, embedding <-> %s::vector AS distance
        FROM {table_name}
        ORDER BY distance
        LIMIT %s;
    """, (query_embedding, top_k))

    results = cur.fetchall()
    return [row[0] for row in results]  # Return the content of the top-k matches

def generate_response(query, context):
    # Combine query and context into a prompt
    context_str = "\n".join(context)
    prompt = f"""
    You are a helpful chatbot. Use the following context to answer the user's query.
    If the context doesn't fully answer the query, use your knowledge to provide a complete response.

    Context:
    {context_str}

    Query:
    {query}
    """

    # Call Gemini via LiteLLM
    response = completion(
        model="gemini/gemini-2.0-flash",  # Replace with exact Gemini model name if different
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=500
    )

    return response.choices[0].message.content

def chatbot():
    print("Welcome to the Chatbot! Type 'exit' to quit.")
    conn, cur = connect_to_db()
    if not conn or not cur:
        print("Failed to connect to the database. Exiting.")
        return

    while True:
        query = input("You: ")
        if query.lower() == "exit":
            break

        # Retrieve relevant context from the database
        context = retrieve_context(query, conn, cur)
        if not context:
            print("Bot: No relevant context found. I'll try to answer anyway.")
            context = [""]

        # Generate response using Gemini
        response = generate_response(query, context)
        print(f"Bot: {response}")

    # Cleanup
    cur.close()
    conn.close()
    print("Goodbye!")

if __name__ == "__main__":
    chatbot()