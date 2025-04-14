# gui_monitor.py
import tkinter as tk
from tkinter import ttk
import sqlite3
import time
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import threading
from inference_module import DB_PATH

class MonitoringApp:
    def __init__(self, root):
        self.root = root
        self.root.title("LLM Inference Monitor")
        self.root.geometry("1000x800")
        
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(pady=10, expand=True, fill='both')
        
        self.stats_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.stats_frame, text="Statistics")
        
        self.graphs_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.graphs_frame, text="Graphs")
        
        self.setup_stats_tab()
        self.setup_graphs_tab()
        
        self.running = True
        self.update_thread = threading.Thread(target=self.update_stats)
        self.update_thread.daemon = True
        self.update_thread.start()
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def setup_stats_tab(self):
        stats_main = ttk.LabelFrame(self.stats_frame, text="Detailed Metrics", padding=10)
        stats_main.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.total_requests = ttk.Label(stats_main, text="Total Requests: 0")
        self.total_requests.grid(row=0, column=0, padx=5, pady=5, sticky='w')
        
        self.avg_response_time = ttk.Label(stats_main, text="Avg Response Time: 0.00s")
        self.avg_response_time.grid(row=1, column=0, padx=5, pady=5, sticky='w')
        
        self.total_tokens = ttk.Label(stats_main, text="Total Tokens: 0")
        self.total_tokens.grid(row=2, column=0, padx=5, pady=5, sticky='w')
        
        self.query_tokens = ttk.Label(stats_main, text="Total Query Tokens: 0")
        self.query_tokens.grid(row=3, column=0, padx=5, pady=5, sticky='w')
        
        self.response_tokens = ttk.Label(stats_main, text="Total Response Tokens: 0")
        self.response_tokens.grid(row=4, column=0, padx=5, pady=5, sticky='w')
        
        self.avg_tokens_per_request = ttk.Label(stats_main, text="Avg Tokens/Request: 0")
        self.avg_tokens_per_request.grid(row=5, column=0, padx=5, pady=5, sticky='w')
        
        load_frame = ttk.LabelFrame(stats_main, text="Model Usage", padding=10)
        load_frame.grid(row=0, column=1, rowspan=6, padx=10, pady=5, sticky='n')
        
        self.model_usage_label = ttk.Label(load_frame, text="Model Usage:")
        self.model_usage_label.pack(pady=5)
        
        self.model_usage_list = tk.Text(load_frame, height=5, width=30)
        self.model_usage_list.pack(pady=5)
        
        detail_frame = ttk.LabelFrame(stats_main, text="Last Request", padding=10)
        detail_frame.grid(row=6, column=0, columnspan=2, padx=5, pady=5, sticky='we')
        
        self.last_prompt = ttk.Label(detail_frame, text="Prompt: N/A", wraplength=400)
        self.last_prompt.pack(pady=2)
        self.last_response = ttk.Label(detail_frame, text="Response: N/A", wraplength=400)
        self.last_response.pack(pady=2)
        self.last_metrics = ttk.Label(detail_frame, text="Metrics: N/A")
        self.last_metrics.pack(pady=2)
    
    def setup_graphs_tab(self):
        self.rt_fig = Figure(figsize=(5, 3), dpi=100)
        self.rt_ax = self.rt_fig.add_subplot(111)
        self.rt_canvas = FigureCanvasTkAgg(self.rt_fig, master=self.graphs_frame)
        self.rt_canvas.get_tk_widget().pack(side=tk.LEFT, padx=5, pady=5)
        
        self.token_fig = Figure(figsize=(5, 3), dpi=100)
        self.token_ax = self.token_fig.add_subplot(111)
        self.token_canvas = FigureCanvasTkAgg(self.token_fig, master=self.graphs_frame)
        self.token_canvas.get_tk_widget().pack(side=tk.RIGHT, padx=5, pady=5)
    
    def update_stats(self):
        from inference_module import get_metrics
        while self.running:
            try:
                metrics = get_metrics()
                
                self.total_requests.config(text=f"Total Requests: {metrics['total_requests']}")
                self.avg_response_time.config(text=f"Avg Response Time: {metrics['avg_response_time']:.2f}s")
                self.total_tokens.config(text=f"Total Tokens: {metrics['total_tokens']}")
                self.query_tokens.config(text=f"Total Query Tokens: {metrics['query_tokens']}")
                self.response_tokens.config(text=f"Total Response Tokens: {metrics['response_tokens']}")
                avg_tokens = metrics['total_tokens'] / metrics['total_requests'] if metrics['total_requests'] > 0 else 0
                self.avg_tokens_per_request.config(text=f"Avg Tokens/Request: {avg_tokens:.1f}")
                
                self.model_usage_list.delete(1.0, tk.END)
                for model, count in metrics['model_usage'].items():
                    self.model_usage_list.insert(tk.END, f"{model}: {count}\n")
                
                if metrics['last_request']:
                    prompt, response, qt, rt, tt, rtime, model = metrics['last_request']
                    self.last_prompt.config(text=f"Prompt: {prompt[:50]}..." if len(prompt) > 50 else f"Prompt: {prompt}")
                    self.last_response.config(text=f"Response: {response[:50]}..." if len(response) > 50 else f"Response: {response}")
                    self.last_metrics.config(text=f"Metrics: {tt} tokens (Q:{qt}, R:{rt}), {rtime:.2f}s")
                
                if metrics['recent_data']:
                    times, responses, tokens = zip(*metrics['recent_data'])
                    
                    self.rt_ax.clear()
                    self.rt_ax.plot(responses, label="Response Time")
                    self.rt_ax.set_title("Response Time Trend")
                    self.rt_ax.set_ylabel("Seconds")
                    self.rt_ax.legend()
                    self.rt_canvas.draw()
                    
                    self.token_ax.clear()
                    self.token_ax.plot(tokens, label="Tokens Used", color='orange')
                    self.token_ax.set_title("Token Usage Trend")
                    self.token_ax.set_ylabel("Tokens")
                    self.token_ax.legend()
                    self.token_canvas.draw()
                
            except Exception as e:
                print(f"Error updating stats: {e}")
            
            time.sleep(5)
    
    def on_closing(self):
        self.running = False
        self.update_thread.join(timeout=1.0)
        self.root.quit()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = MonitoringApp(root)
    root.mainloop()