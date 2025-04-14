# modules/database.py
import sqlite3
from datetime import datetime

def init_db(db_path='proxy_metrics.db'):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS requests
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  timestamp TEXT,
                  model TEXT,
                  prompt TEXT,
                  response TEXT,
                  tokens_used INTEGER,
                  query_tokens INTEGER,
                  response_tokens INTEGER,
                  completion_time REAL,
                  response_time REAL)''')
    conn.commit()
    conn.close()

def store_metrics(db_path, model, prompt, response, tokens_used, query_tokens, response_tokens, completion_time, response_time):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''INSERT INTO requests (timestamp, model, prompt, response, tokens_used, query_tokens, response_tokens, completion_time, response_time)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
              (datetime.now().isoformat(), model, prompt, response, tokens_used, query_tokens, response_tokens, completion_time, response_time))
    conn.commit()
    conn.close()