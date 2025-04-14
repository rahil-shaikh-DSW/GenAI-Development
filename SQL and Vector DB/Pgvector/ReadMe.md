Let’s walk through how to use `pgvector` with PostgreSQL and `pgAdmin` to create embeddings from your PDF, store them in a PostgreSQL database, and visualize them in `pgAdmin`. I’ll simplify the process step-by-step, covering Docker setup, Python scripting for database creation and embedding generation, and how to use `pgAdmin`. I'll also ensure it’s easy to extend for additional collections.

---

### Step 1: Docker Compose Setup
We’ll use a `docker-compose.yml` file to set up PostgreSQL with `pgvector` and `pgAdmin`. Since the default `postgres` image doesn’t include `pgvector`, we’ll use the `pgvector/pgvector` image instead.

Here’s the updated `docker-compose.yml`:

```yaml
version: '3'

services:
  db:
    image: pgvector/pgvector:pg16  # Use pgvector-enabled PostgreSQL image
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: 123456
      POSTGRES_DB: vector_db  # Default database name
    volumes:
      - C:/postgres/postgres-data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  pgadmin:
    image: dpage/pgadmin4
    environment:
      PGADMIN_DEFAULT_EMAIL: rahilshaikhada424@gmail.com
      PGADMIN_DEFAULT_PASSWORD: root
    ports:
      - "8080:80"
    depends_on:
      - db
```

#### Explanation:
- **`pgvector/pgvector:pg16`**: This image includes PostgreSQL 16 with `pgvector` pre-installed.
- **`POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`**: Sets up the database credentials and a default database.
- **`volumes`**: Persists PostgreSQL data on your local machine.
- **`pgadmin`**: Runs `pgAdmin` for a web-based interface to manage the database.

#### Run Docker Compose:
1. Save the above content in a file named `docker-compose.yml` in your project directory.
2. Open a terminal in that directory and run:
   ```bash
   docker-compose up -d
   ```
3. This starts the PostgreSQL and `pgAdmin` containers in the background. Wait a minute for them to initialize.

---

### Step 2: Python Script for Database Setup and Embedding Creation
Below is a Python script that:
- Connects to the PostgreSQL database.
- Enables the `pgvector` extension.
- Creates a table for storing embeddings.
- Processes your PDF and generates embeddings.
- Stores them in the database.

#### Prerequisites:
Install the required Python packages:
```bash
pip install psycopg2-binary sentence-transformers PyPDF2 tqdm torch
```

#### Python Script (`setup_and_embed.py`):
```python
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
```

#### Explanation:
- **`db_params`**: Connection details matching your Docker setup.
- **`setup_database`**: Connects to the database, enables `pgvector`, and creates a table with a `VECTOR(1024)` column (the embedding size for `gte-large-en-v1.5`).
- **`create_embeddings`**: Reads the PDF, splits it into chunks, generates embeddings, and stores them in the table.
- **Dynamic Table Name**: Uses `embeddings_{collection_name}` so you can create more collections by changing `collection_name`.

#### Run the Script:
1. Save the script as `setup_and_embed.py`.
2. Ensure `merged_output.pdf` is in the same directory (or adjust the path).
3. Run:
   ```bash
   python setup_and_embed.py
   ```

---

### Step 3: Using `pgAdmin` Step-by-Step
`pgAdmin` is a web-based tool to manage your PostgreSQL database. Here’s how to set it up and view your embeddings:

#### 1. Access `pgAdmin`
- Open your browser and go to `http://localhost:8080`.
- Log in with:
  - **Email**: `rahilshaikhada424@gmail.com`
  - **Password**: `root`

#### 2. Register the PostgreSQL Server
1. On the left sidebar, right-click **Servers** > **Register** > **Server**.
2. In the pop-up:
   - **General Tab**:
     - Name: `MyVectorDB` (or any name you like)
   - **Connection Tab**:
     - Host: `db` (the service name from Docker Compose)
     - Port: `5432`
     - Database: `vector_db`
     - Username: `postgres`
     - Password: `123456`
3. Click **Save**. You’ll see `MyVectorDB` appear under **Servers**.

#### 3. View Your Data
1. Expand **Servers** > **MyVectorDB** > **Databases** > **vector_db** > **Schemas** > **public** > **Tables**.
2. Right-click `embeddings_chsbc` (or your table name) > **View/Edit Data** > **All Rows**.
3. You’ll see columns: `id`, `source`, `content`, and `embedding`. The `embedding` column will show vectors like `[0.123, -0.456, ...]`.

#### 4. Run a Simple Query (Optional)
1. In `pgAdmin`, click **Tools** > **Query Tool**.
2. Run this SQL to see your data:
   ```sql
   SELECT * FROM embeddings_chsbc LIMIT 5;
   ```
3. Results appear in the bottom pane.

---

### Step 4: Adding More Collections
To create another collection (e.g., `new_collection`):
1. Update `collection_name = "new_collection"` in the Python script.
2. Change `pdf_path` to a different PDF if needed.
3. Run the script again. It’ll create a new table (`embeddings_new_collection`) without affecting the existing one.
4. In `pgAdmin`, refresh the **Tables** list to see the new table.

---

### Key Notes:
- **Simplicity**: The script uses a single table per collection. You can extend it by adding more tables or modifying the schema.
- **pgAdmin Basics**: It’s just a GUI for PostgreSQL. Use the left sidebar to navigate, and the **Query Tool** for custom SQL.
- **Embedding Size**: `gte-large-en-v1.5` outputs 1024-dimensional vectors. If you switch models, adjust the `VECTOR(1024)` size in the table creation.

Now you’re set! You’ve got a working setup with Docker, Python, and `pgAdmin` to create and manage embeddings. Let me know if you need further clarification!