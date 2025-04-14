
---

### Resources
- **Docs**: [langfuse.com/docs](https://langfuse.com/docs) (per web:1,5).
- **GitHub**: [github.com/langfuse/langfuse](https://github.com/langfuse/langfuse) (per web:6).
- **Tutorials**:
  - “Langfuse with LangChain” (web:9).
  - “Tracing RAG with LlamaIndex” (web:23).
  - Medium: “LLM Tracing with Langfuse” (web:14).
- **Community**: Langfuse Discord, GitHub Discussions (per web:12).
- **Installation**:
  ```bash
  pip install langfuse
  docker compose up -d
  ```

---

### 1. What is Langfuse?

- **Definition**: Langfuse is an **open-source LLM engineering platform** designed for **observability**, **prompt management**, and **evaluation** of LLM applications, offering tools for **prompt registry** (versioning, caching, and deployment) and **inference tracing** (logging inputs/outputs, latency, costs, and errors).
- **Why It Matters**:
  - **Prompt Registry**: Centralizes prompt storage, versioning, and retrieval, decoupling prompts from code for easy updates and rollbacks (per web:0,5,8,9).
  - **Inference Tracing**: Captures detailed execution flows (API calls, prompts, responses, embeddings) to debug, optimize, and monitor LLM apps (per web:1,2,6,15,21).
  - Aligns with your **privacy/security focus**: Self-hostable, open-source (MIT-licensed core), and integrates with private LLM deployments (e.g., vLLM, TGI) (per web:5,6,24).
  - Supports **production-grade apps** with low-latency prompt caching and high-performance tracing (per web:0,2).
  - **Community Sentiment**: Praised for debugging complex LLM workflows and cost tracking (per post:1,2,4).
- **Key Features**:
  - **Prompt Management**:
    - Version control with labels (e.g., `production`, `staging`, `latest`) (per web:0).
    - UI, API, or SDK for collaborative editing (per web:0,9).
    - Caching (default 60s TTL, customizable) for low-latency retrieval (per web:0).
    - Playground for testing prompts (per web:1,6).
  - **Inference Tracing**:
    - Nested traces for LLM calls, retrievals, agents, and embeddings (per web:2,17).
    - Metrics: latency, cost, token usage, and quality scores (per web:1,2,15).
    - Session tracking for multi-turn chats (per web:2,23).
    - Visual dashboard for debugging (per web:2,21).
  - **Evaluations**: LLM-as-a-judge, user feedback, manual labeling, or custom pipelines (per web:1,24).
  - **Integrations**: OpenAI, LangChain, LlamaIndex, LiteLLM, vLLM, TGI, Ollama, and more (per web:5,6,12).
  - **Multi-Modal**: Traces text, images, and embeddings (per web:1,12).
  - **Deployment**: Cloud (langfuse.com), self-hosted (Docker, Kubernetes), or serverless (per web:6,18,20).
- **Use Cases**:
  - Version and deploy prompts for a vLLM-hosted Llama model.
  - Trace inference in a TGI-based RAG app to debug latency.
  - Monitor costs in a LiteLLM-proxied multi-model setup.
  - Build a chatbot UI with Chainlit, tracing via Langfuse (per our prior Chainlit chat).
- **Comparison to Prior Frameworks**:
  - **vLLM/TGI**: Host LLMs with high throughput; Langfuse adds observability and prompt management, not hosting (per web:12).
  - **Ollama**: Local LLM runner; Langfuse traces Ollama calls for debugging (per web:12).
  - **LiteLLM**: Proxies LLM APIs; Langfuse traces inputs/outputs and manages prompts (per web:10).
  - **Chainlit**: UI for apps; Langfuse provides backend tracing.

---

### 2. Core Components of Langfuse

Langfuse organizes functionality around **prompt management**, **tracing**, and **integrations**:

- **Prompt Registry**:
  - **Storage**: Prompts stored as text or chat templates (e.g., `[{"role": "system", "content": "..."}]`) (per web:0).
  - **Versioning**: Assign versions (e.g., `1`, `2`) or labels (`production`, `staging`) (per web:0,9).
  - **Retrieval**: SDKs cache prompts locally (TTL customizable) (per web:0).
  - **API**: Create, update, or fetch via `/prompts` endpoint (per web:0,8).
- **Inference Tracing**:
  - **Traces**: Top-level records of app execution (e.g., a chat session) (per web:16,20).
  - **Spans**: Time-bound operations (e.g., retrieval, API call) (per web:16).
  - **Generations**: LLM calls with metadata (prompt, response, tokens, cost) (per web:16,20).
  - **Events**: Discrete actions (e.g., logging a decision) (per web:20).
  - **Sessions**: Group traces for multi-turn interactions (per web:2,23).
  - **Scores**: Evaluate outputs (e.g., 0-1 for quality) (per web:1,16).
- **SDKs/Integrations**:
  - Python/JS SDKs for manual tracing (per web:4,20).
  - Framework hooks: LangChain, LlamaIndex, OpenAI, LiteLLM (per web:1,12).
  - Decorators: `@observe()` for custom Python apps (per web:6,17).
- **Dashboard**: Visualizes traces, metrics, and prompt versions (per web:2,21).

---

### 3. Using Langfuse for Prompt Registry

Langfuse’s **prompt registry** decouples prompts from code, enabling versioning, testing, and deployment.

#### 3.1 Setup
- **Cloud**:
  - Sign up at [langfuse.com](https://langfuse.com).
  - Create a project, get API keys (`pk-lf-...`, `sk-lf-...`) from settings (per web:4,15).
- **Self-Hosted** (per web:6,20):
  ```bash
  git clone https://github.com/langfuse/langfuse
  cd langfuse
  docker compose up -d
  ```
  - Access: `http://localhost:3000`.
  - Keys: Generate via UI.
- **Install SDK**:
  ```bash
  pip install langfuse
  ```
- **Configure**:
  ```python
  from langfuse import Langfuse

  langfuse = Langfuse(
      public_key="pk-lf-...",
      secret_key="sk-lf-...",
      host="https://cloud.langfuse.com"  # or "http://localhost:3000"
  )
  ```

#### 3.2 Create and Version Prompts
- **Create via SDK** (per web:0,9):
  ```python
  langfuse.create_prompt(
      name="movie-critic",
      prompt="You are a {criticlevel} movie critic. Review {movie}.",
      labels=["production"],
      version=1
  )
  ```
- **Create Chat Prompt**:
  ```python
  langfuse.create_prompt(
      name="movie-critic-chat",
      prompt=[
          {"role": "system", "content": "You are a {criticlevel} movie critic"},
          {"role": "user", "content": "Do you like {movie}?"}
      ],
      type="chat",
      labels=["staging"],
      version=1
  )
  ```
- **Update Labels**:
  ```python
  langfuse.update_prompt(
      name="movie-critic",
      version=1,
      new_labels=["staging", "experiment-a"]
  )
  ```

#### 3.3 Retrieve and Use Prompts
- **Fetch Prompt** (per web:0):
  ```python
  prompt = langfuse.get_prompt(
      name="movie-critic",
      label="production",
      cache_ttl_seconds=300
  )
  compiled = prompt.compile(criticlevel="expert", movie="Dune 2")
  print(compiled)
  # Output: "You are an expert movie critic. Review Dune 2."
  ```
- **Fetch Chat Prompt**:
  ```python
  chat_prompt = langfuse.get_prompt(
      name="movie-critic-chat",
      type="chat",
      label="staging"
  )
  compiled_chat = chat_prompt.compile(criticlevel="expert", movie="Dune 2")
  print(compiled_chat)
  # Output: [
  #   {"role": "system", "content": "You are an expert movie critic"},
  #   {"role": "user", "content": "Do you like Dune 2?"}
  # ]
  ```
- **Security**:
  - Validate inputs:
    ```python
    if "hack" in criticlevel.lower():
        raise ValueError("Unsafe input")
    ```
  - Restrict access:
    ```bash
    docker compose -f docker-compose.yml up -d --scale web=1
    ufw allow from <trusted-ip> to any port 3000
    ```

#### 3.4 Test in Playground
- Access: Langfuse UI → Prompts → Select `movie-critic` → Playground.
- Input: `criticlevel="expert", movie="Dune 2"`.
- Output: Preview compiled prompt.
- **Security**: Use read-only API keys for testing (per web:18).

---

### 4. Using Langfuse for Inference Tracing

Langfuse’s **inference tracing** logs LLM calls, retrievals, and app logic for debugging and optimization.

#### 4.1 Trace a vLLM/TGI-Hosted Model
Integrate Langfuse with a vLLM or TGI server (per our prior chats).

- **Run vLLM/TGI**:
  ```bash
  vllm serve mistralai/Mistral-7B-Instruct-v0.3 --host 127.0.0.1 --port 8000
  # OR
  docker run --gpus all -p 8080:80 ghcr.io/huggingface/text-generation-inference:2.2.0 \
    --model-id mistralai/Mistral-7B-Instruct-v0.3
  ```
- **Trace with Langfuse**:
  ```python
  from langfuse.decorators import observe
  from openai import OpenAI

  client = OpenAI(base_url="http://localhost:8000/v1", api_key="-")  # vLLM/TGI

  @observe()
  def llm_call(prompt):
      if "hack" in prompt.lower():
          raise ValueError("Unsafe prompt")
      response = client.chat.completions.create(
          model="mistralai/Mistral-7B-Instruct-v0.3",
          messages=[{"role": "user", "content": prompt}],
          temperature=0.7
      )
      return response.choices[0].message.content

  @observe()
  def main():
      prompt = langfuse.get_prompt("movie-critic-chat", type="chat")
      compiled = prompt.compile(criticlevel="expert", movie="Dune 2")
      response = llm_call(compiled)
      with open("audit.log", "a") as f:
          f.write(f"Prompt: {compiled}\nResponse: {response}\n")
      return response

  print(main())
  ```
- **Output**:
  ```
  [{"role": "system", "content": "You are an expert movie critic"}, {"role": "user", "content": "Do you like Dune 2?"}] -> "Dune 2 is a cinematic triumph..."
  ```
- **Dashboard**:
  - Access: `https://cloud.langfuse.com` or `http://localhost:3000`.
  - View: Trace with prompt, response, latency, and tokens.

#### 4.2 Trace with LiteLLM Proxy
Use Langfuse with LiteLLM (per our LiteLLM chat, web:10).

- **Config** (`config.yaml`):
  ```yaml
  model_list:
    - model_name: mistral
      litellm_params:
        model: openai/mistral
        api_base: http://localhost:8000/v1
  ```
- **Run Proxy**:
  ```bash
  docker run -v $(pwd)/config.yaml:/app/config.yaml -p 4000:4000 ghcr.io/berriai/litellm:main-latest --config /app/config.yaml
  ```
- **Trace**:
  ```python
  from langfuse import Langfuse
  from openai import OpenAI

  langfuse = Langfuse(public_key="pk-lf-...", secret_key="sk-lf-...")
  client = OpenAI(base_url="http://localhost:4000", api_key="anything")

  trace = langfuse.trace(name="movie-review")
  generation = trace.generation(
      name="mistral-call",
      model="mistral",
      input=langfuse.get_prompt("movie-critic-chat").compile(criticlevel="expert", movie="Dune 2")
  )

  response = client.chat.completions.create(
      model="mistral",
      messages=generation.input
  )
  output = response.choices[0].message.content

  generation.end(output=output)
  print(output)
  ```
- **Security**:
  - Mask sensitive data:
    ```python
    import re
    output = re.sub(r'\b[\w\.-]+@[\w\.-]+\.\w+\b', '[REDACTED]', output)
    ```
  - Rate limits:
    ```yaml
    general_settings:
      rpm_limit_per_key: 100
    ```

#### 4.3 Trace LangChain/LlamaIndex Apps
- **LangChain** (per web:3,7,9):
  ```python
  from langchain_openai import ChatOpenAI
  from langchain.prompts import ChatPromptTemplate
  from langfuse.callback import CallbackHandler

  langfuse_handler = CallbackHandler(public_key="pk-lf-...", secret_key="sk-lf-...")
  prompt = ChatPromptTemplate.from_template(
      langfuse.get_prompt("movie-critic").compile(criticlevel="expert", movie="Dune 2")
  )
  model = ChatOpenAI(model="gpt-4o")
  chain = prompt | model

  response = chain.invoke({}, config={"callbacks": [langfuse_handler]})
  print(response.content)
  ```
- **LlamaIndex** (per web:23):
  ```python
  from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, set_global_handler

  set_global_handler("langfuse", public_key="pk-lf-...", secret_key="sk-lf-...")
  documents = SimpleDirectoryReader("data").load_data()
  index = VectorStoreIndex.from_documents(documents)
  query_engine = index.as_query_engine()
  response = query_engine.query(
      langfuse.get_prompt("movie-critic").compile(criticlevel="expert", movie="Dune 2")
  )
  print(response)
  ```

---

### 5. Key Concepts
- **Prompt Registry**:
  - **Labels**: `production`, `staging`, `latest`, or custom (e.g., `tenant-1`) (per web:0).
  - **Caching**: Reduces latency; default TTL 60s (per web:0).
  - **Versioning**: Tracks changes, supports rollbacks (per web:8).
- **Inference Tracing**:
  - **Traces**: Hierarchical logs of app execution (per web:16,17).
  - **Generations**: LLM-specific spans with token/cost data (per web:20).
  - **Sessions**: Group multi-turn interactions (per web:2).
  - **Scores**: Quality metrics (e.g., relevance, hallucination) (per web:1,24).
- **Performance**: Asynchronous SDKs with batched requests (per web:2,6).
- **Security**: Self-hosting, API key isolation, and data export (per web:5,19,24).

---

### 6. When to Use Langfuse
- **Prompt Registry**:
  - Manage prompts for vLLM/TGI-hosted models across environments.
  - Enable non-technical teams to edit prompts via UI (per web:24).
- **Inference Tracing**:
  - Debug latency in RAG apps (e.g., LlamaIndex with vLLM).
  - Monitor costs in multi-model setups (e.g., LiteLLM proxy).
  - Analyze quality in production (e.g., hallucination detection).
- **Compared to Prior Frameworks**:
  - **vLLM/TGI**: Host LLMs; Langfuse traces their inference and manages prompts.
  - **Ollama**: Local hosting; Langfuse adds observability (per web:12).
  - **LiteLLM**: Proxies APIs; Langfuse logs calls and versions prompts (per web:10).
  - **Chainlit**: UI; Langfuse traces backend logic.

---

### 7. Common Pitfalls and Fixes
- **Prompt Registry**:
  - **Issue**: Prompt not found.
    - **Fix**: Verify name/label:
      ```python
      prompt = langfuse.get_prompt("movie-critic", label="production")
      ```
  - **Issue**: High latency.
    - **Fix**: Extend cache:
      ```python
      langfuse.get_prompt(..., cache_ttl_seconds=300)
      ```
- **Inference Tracing**:
  - **Issue**: No traces in dashboard (per web:4,18).
    - **Fix**: Flush events:
      ```python
      langfuse.flush()
      ```
    - Check keys:
      ```python
      langfuse.auth_check()
      ```
  - **Issue**: Missing metrics.
    - **Fix**: Add metadata:
      ```python
      trace.generation(..., model="mistral", usage={"input_tokens": 50, "output_tokens": 100})
      ```
- **Security**:
  - **Issue**: Exposed keys.
    - **Fix**: Use env variables:
      ```bash
      export LANGFUSE_PUBLIC_KEY="pk-lf-..."
      export LANGFUSE_SECRET_KEY="sk-lf-..."
      ```
  - **Issue**: Data leaks.
    - **Fix**: Mask outputs:
      ```python
      from llm_guard.output_scanners import Anonymize
      scanner = Anonymize()
      sanitized, _ = scanner.scan(response)
      ```

---

### 8. Hands-On Challenge
To master Langfuse:
1. **Prompt Registry**:
   - Create a prompt `chatbot` with a chat template.
   - Version it (`production`, `v1`).
   - Fetch and compile with variables (`topic="AI"`).
2. **Inference Tracing**:
   - Trace a vLLM/TGI call (e.g., Mistral-7B) using the prompt.
   - Log to Langfuse, view in dashboard.
3. **LiteLLM Integration**:
   - Proxy vLLM/TGI via LiteLLM, trace with Langfuse.
   - Query: “What’s AI?”
4. **Security**:
   - Block “hack” prompts, log to `langfuse.log`.
5. Share code/output, and I’ll review!

**Starter Code**:
```python
from langfuse import Langfuse

langfuse = Langfuse(public_key="pk-lf-...", secret_key="sk-lf-...")

def create_prompt():
    langfuse.create_prompt(
        name="chatbot",
        prompt="Tell me about {topic}.",
        labels=["production"],
        version=1
    )

def trace_llm():
    # Add tracing code
```

---

### 9. Advanced Tips
- **Prompt A/B Testing** (per web:11):
  ```python
  prompt_a = langfuse.get_prompt("chatbot", label="experiment-a")
  prompt_b = langfuse.get_prompt("chatbot", label="experiment-b")
  trace = langfuse.trace(name="ab-test")
  trace.generation(name="prompt-a", input=prompt_a.compile(topic="AI"))
  trace.generation(name="prompt-b", input=prompt_b.compile(topic="AI"))
  ```
- **RAG with LlamaIndex** (per web:23):
  ```python
  from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
  from langfuse import Langfuse

  langfuse = Langfuse()
  set_global_handler("langfuse", public_key="pk-lf-...", secret_key="sk-lf-...")
  prompt = langfuse.get_prompt("chatbot").compile(topic="AI")
  documents = SimpleDirectoryReader("data").load_data()
  index = VectorStoreIndex.from_documents(documents)
  print(index.as_query_engine().query(prompt))
  ```
- **Chainlit UI**:
  ```python
  import chainlit as cl
  from langfuse import Langfuse
  from openai import AsyncOpenAI

  langfuse = Langfuse()
  client = AsyncOpenAI(base_url="http://localhost:8000/v1", api_key="-")

  @cl.on_message
  async def main(message: cl.Message):
      trace = langfuse.trace(name="chatbot")
      prompt = langfuse.get_prompt("chatbot-chat", type="chat").compile(topic=message.content)
      generation = trace.generation(name="llm", input=prompt)
      response = await client.chat.completions.create(
          model="mistralai/Mistral-7B-Instruct-v0.3",
          messages=prompt,
          stream=True
      )
      msg = cl.Message(content="")
      await msg.send()
      async for chunk in response:
          if chunk.choices[0].delta.content:
              await msg.stream_token(chunk.choices[0].delta.content)
      generation.end(output=msg.content)
      await msg.update()
  ```
- **Evaluations** (per web:24):
  ```python
  trace.score(name="quality", value=0.9, comment="Relevant response")
  ```
- **Security**:
  - Input guardrails:
    ```python
    from llm_guard.input_scanners import PromptInjection
    scanner = PromptInjection()
    if scanner.scan(prompt)[1]:
        raise ValueError("Injection detected")
    ```
  - Export traces:
    ```python
    traces = langfuse.fetch_traces()
    with open("traces.json", "w") as f:
        json.dump(traces, f)
    ```



---

