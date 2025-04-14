# inference_module.py
import sqlite3
import time
import os
from litellm import completion
from datetime import datetime

# Database setup
DB_PATH = "proxy_metrics.db"

def init_db():
    """Initialize the SQLite database if it doesn't exist."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
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
    conn.commit()
    conn.close()

# Ensure database is initialized
init_db()

def run_inference(prompt, model="gemini/gemini-pro", api_key=None):
    """
    Run inference using LiteLLM and log metrics to database.
    
    Args:
        prompt (str): Input prompt
        model (str): Model name (default: "gemini/gemini-pro")
        api_key (str): Optional API key (falls back to environment variable)
    
    Returns:
        dict: Response data including text, tokens, and timing
    """
    start_time = time.time()
    
    # Set API key
    if api_key:
        os.environ["GEMINI_API_KEY"] = api_key
    elif "GEMINI_API_KEY" not in os.environ:
        raise ValueError("GEMINI_API_KEY not set in environment or provided as argument")
    
    try:
        # Get completion from Gemini via LiteLLM
        response = completion(
            model=model,
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
        c.execute('''INSERT INTO requests (timestamp, model, prompt, response, query_tokens, response_tokens, total_tokens, completion_time, response_time)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                  (datetime.now().isoformat(), model, prompt, response_text,
                   query_tokens, response_tokens, total_tokens, response_time, response_time))
        conn.commit()
        conn.close()
        
        return {
            "response": response_text,
            "query_tokens": query_tokens,
            "response_tokens": response_tokens,
            "total_tokens": total_tokens,
            "response_time": response_time,
            "model": model
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
    
    c.execute("SELECT prompt, response, query_tokens, response_tokens, total_tokens, response_time, model FROM requests ORDER BY id DESC LIMIT 1")
    last_request = c.fetchone()
    metrics["last_request"] = last_request if last_request else None
    
    c.execute("SELECT model, COUNT(*) FROM requests GROUP BY model")
    metrics["model_usage"] = dict(c.fetchall())
    
    c.execute("SELECT timestamp, response_time, total_tokens FROM requests ORDER BY timestamp LIMIT 50")
    metrics["recent_data"] = c.fetchall()
    
    conn.close()
    return metrics