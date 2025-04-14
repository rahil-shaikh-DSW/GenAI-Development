# inference_module.py
import sqlite3
import time
import os
from litellm import completion
from datetime import datetime

# Database setup
DB_PATH = "proxy_metrics.db"

def init_db():
    """Initialize or update the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Create table if it doesn't exist
    c.execute('''CREATE TABLE IF NOT EXISTS requests
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  timestamp TEXT,
                  model TEXT,
                  prompt TEXT,
                  response TEXT,
                  query_tokens INTEGER,
                  response_tokens INTEGER,
                  total_tokens INTEGER,
                  completion_time REAL,
                  response_time REAL)''')
    
    # Check if provider column exists and add it if not
    c.execute("PRAGMA table_info(requests)")
    columns = [col[1] for col in c.fetchall()]
    if "provider" not in columns:
        c.execute("ALTER TABLE requests ADD COLUMN provider TEXT")
        # Optionally set a default provider for existing rows
        c.execute("UPDATE requests SET provider = 'unknown' WHERE provider IS NULL")
    
    conn.commit()
    conn.close()

# Ensure database is initialized/updated
init_db()

def run_inference(prompt, model="gemini/gemini-pro", provider="gemini", api_key=None):
    """
    Run inference using LiteLLM with any supported provider and log metrics.
    
    Args:
        prompt (str): Input prompt
        model (str): Model name (e.g., "gemini/gemini-pro", "groq/llama-70b", "ollama/llama2")
        provider (str): LLM provider (e.g., "gemini", "groq", "ollama", "xai")
        api_key (str): Optional API key for the provider (falls back to env var)
    
    Returns:
        dict: Response data including text, tokens, and timing
    """
    start_time = time.time()
    
    # Set API key based on provider
    env_key = f"{provider.upper()}_API_KEY"
    if api_key:
        os.environ[env_key] = api_key
    elif env_key not in os.environ:
        raise ValueError(f"{env_key} not set in environment or provided as argument")
    
    try:
        # Adjust model format if needed
        full_model = model if "/" in model else f"{provider}/{model}"
        
        # Get completion via LiteLLM
        response = completion(
            model=full_model,
            messages=[{"role": "user", "content": prompt}]
        )
        
        end_time = time.time()
        response_time = end_time - start_time
        
        # Calculate tokens (approximation)
        query_tokens = len(prompt.split())
        response_text = response.choices[0].message.content
        response_tokens = len(response_text.split())
        total_tokens = query_tokens + response_tokens
        
        # Store metrics in database
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''INSERT INTO requests (timestamp, model, provider, prompt, response, query_tokens, response_tokens, total_tokens, completion_time, response_time)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                  (datetime.now().isoformat(), model, provider, prompt, response_text,
                   query_tokens, response_tokens, total_tokens, response_time, response_time))
        conn.commit()
        conn.close()
        
        return {
            "response": response_text,
            "query_tokens": query_tokens,
            "response_tokens": response_tokens,
            "total_tokens": total_tokens,
            "response_time": response_time,
            "model": model,
            "provider": provider
        }
    
    except Exception as e:
        return {"error": str(e)}

def get_metrics():
    """Retrieve aggregated metrics from the database."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    metrics = {}
    
    c.execute("SELECT COUNT(*) FROM requests")
    metrics["total_requests"] = c.fetchone()[0] or 0
    
    c.execute("SELECT AVG(response_time) FROM requests")
    metrics["avg_response_time"] = c.fetchone()[0] or 0.0
    
    c.execute("SELECT SUM(query_tokens), SUM(response_tokens), SUM(total_tokens) FROM requests")
    qt, rt, tt = c.fetchone()
    metrics["query_tokens"] = qt or 0
    metrics["response_tokens"] = rt or 0
    metrics["total_tokens"] = tt or 0
    
    c.execute("SELECT prompt, response, query_tokens, response_tokens, total_tokens, response_time, model, provider FROM requests ORDER BY id DESC LIMIT 1")
    last_request = c.fetchone()
    metrics["last_request"] = last_request if last_request else None
    
    c.execute("SELECT provider || '/' || model, COUNT(*) FROM requests GROUP BY provider, model")
    metrics["model_usage"] = dict(c.fetchall())
    
    c.execute("SELECT timestamp, response_time, total_tokens FROM requests ORDER BY timestamp LIMIT 50")
    metrics["recent_data"] = c.fetchall()
    
    conn.close()
    return metrics