
---

### Resources
- **Docs**:
  - [LiteLLM Docs](https://docs.litellm.ai): Proxy and SDK guide.[](https://docs.litellm.ai/)
  - [GitHub](https://github.com/BerriAI/litellm): Examples and config.[](https://github.com/BerriAI/litellm)
- **Tutorials**:
  - Medium: “Streamlining LLM Apps with LiteLLM Proxy.”[](https://medium.com/%40thinhda/streamlining-llm-applications-with-litellm-proxy-a-comprehensive-guide-875122c00974)
  - X: Unified inference with LiteLLM.
- **Community**:
  - Discord: LiteLLM community.
  - X posts: Search `#LiteLLM #LLMProxy`.
- **Installation**:
  ```bash
  pip install litellm
  docker pull ghcr.io/berriai/litellm:main-latest
  ```

---

### 1. Understanding LLM Hosting, Inference, and Proxy

#### LLM Hosting
- **Definition**: Hosting an LLM involves deploying a large language model on infrastructure (cloud, on-premises, or edge) to serve requests for tasks like text generation, embeddings, or tool calling.
- **Types**:
  - **Cloud Providers**: AWS Bedrock, Azure AI, Google Vertex AI, OpenAI.
  - **Self-Hosted**: Run models like Llama 3 or Mistral on servers using frameworks (e.g., Hugging Face, vLLM).
  - **Inference Endpoints**: Managed services like Hugging Face Inference Endpoints or Replicate.
- **Considerations**:
  - **Compute**: GPUs/TPUs for efficiency (e.g., NVIDIA A100).
  - **Cost**: Pay-per-use (cloud) vs. fixed (self-hosted).
  - **Scalability**: Load balancing for high traffic.
  - **Security**: Protect model weights, APIs, and data (e.g., encrypt keys, restrict access).

#### LLM Inference
- **Definition**: Inference is the process of generating outputs (e.g., text, embeddings) from an LLM given an input (e.g., prompt). It’s the “runtime” phase after training.
- **Key Aspects**:
  - **Endpoints**: APIs like `/chat/completions` (OpenAI format) or `/generate` (Hugging Face).
  - **Latency**: Depends on model size, hardware, and optimization (e.g., quantization).
  - **Tasks**: Chat, embeddings, image generation, transcription.
  - **Optimization**:
    - **Batching**: Process multiple requests together.
    - **Quantization**: Reduce model size (e.g., 4-bit Llama).
    - **Streaming**: Return partial outputs for real-time apps.
- **Challenges**:
  - High compute cost for large models (e.g., GPT-4o, Llama 70B).
  - Provider-specific APIs complicate integration.
  - Error handling (e.g., rate limits, timeouts).

#### LLM Proxy
- **Definition**: An LLM proxy is middleware that unifies access to multiple LLM providers (e.g., OpenAI, Anthropic, Hugging Face) through a standardized API, simplifying integration and adding features like load balancing, caching, and cost tracking.
- **Benefits**:
  - **Unified Interface**: Use one API (e.g., OpenAI’s) for all models.
  - **Abstraction**: Switch providers without code changes.
  - **Management**: Track usage, set budgets, and handle errors.
  - **Security**: Centralize API key management and auditing.
- **Use Cases**:
  - Route requests to the cheapest/fastest model.
  - Fallback to secondary providers if one fails.
  - Monitor costs across teams or projects.

---

### 2. What is LiteLLM?

- **Definition**: LiteLLM is an **open-source Python library and proxy server** that provides a unified OpenAI-compatible API to call over **100+ LLMs** from providers like OpenAI, Azure, Anthropic, Hugging Face, Bedrock, and Ollama. It simplifies **LLM inference** and acts as a **proxy** for hosting and managing LLM requests.[](https://github.com/BerriAI/litellm)
- **Why It Matters**:
  - Abstracts provider-specific APIs, reducing integration complexity.
  - Supports **chat completions**, **embeddings**, **image generation**, and more in OpenAI format.
  - Offers **proxy features**: load balancing, cost tracking, virtual keys, and retries.
  - Lightweight and scalable, handling 1.5k+ requests/second in tests.[](https://docs.litellm.ai/docs/proxy/quick_start)
  - Aligns with your security interest: encrypts keys, logs interactions, and supports rate limits.
- **Key Features**:
  - **Unified API**: Call GPT-4o, Claude 3, Llama, or Mistral with the same code.
  - **Proxy Server**: Run as a gateway (`http://localhost:4000`) for apps or frameworks (e.g., LangChain, Chainlit).
  - **Load Balancing**: Distribute requests across models/deployments.
  - **Cost Tracking**: Monitor token usage and budgets per key/project.
  - **Error Handling**: Retries, fallbacks (e.g., Azure → OpenAI).[](https://docs.litellm.ai/)
  - **Streaming**: Real-time responses for interactive apps.
  - **Observability**: Logs to Langfuse, Prometheus, or S3.[](https://aws.amazon.com/marketplace/pp/prodview-gdm3gswgjhgjo)
  - **Local Support**: Run Ollama models for on-premises inference.
- **Use Cases**:
  - Build a chatbot accessing multiple LLMs (e.g., GPT-4o, Claude).
  - Create a RAG app with embeddings from Hugging Face and chat from OpenAI.
  - Manage enterprise LLM usage with budgets and virtual keys.
- **Comparison to Prior Frameworks**:
  - **OpenAI SDK** (per our chat): Low-level inference; LiteLLM unifies providers.
  - **LlamaIndex**: Data-centric RAG/agents; LiteLLM handles inference backend.
  - **Chainlit**: UI for conversational apps; LiteLLM provides LLM proxy for Chainlit’s backend.
  - **LangChain/AutoGen**: Workflow-focused; LiteLLM simplifies their LLM calls.

---

### 3. Setting Up LiteLLM

1. **Install LiteLLM**:
   ```bash
   pip install litellm
   ```
   - Requires Python 3.8+, `openai>=1.0.0`, `pydantic>=2.0.0`.[](https://github.com/BerriAI/litellm)

2. **Set Environment Variables**:
   - For providers (e.g., OpenAI, Hugging Face):
     ```bash
     export OPENAI_API_KEY="your-openai-key"
     export HUGGINGFACE_API_KEY="your-hf-key"
     ```
   - Store securely (e.g., `.env` file).

3. **Run LiteLLM Proxy** (optional for server mode):
   ```bash
   litellm --model openai/gpt-4o
   ```
   - Starts proxy at `http://localhost:4000`.
   - Use a config for multiple models (see below).

---

### 4. LiteLLM for LLM Inference

LiteLLM supports inference via its **Python SDK** or **proxy server**. Below are examples for key tasks: chat completions, embeddings, streaming, and tool calling.

#### Example 1: Chat Completions (SDK)
Call GPT-4o-mini and Claude 3 with the same code.

```python
from litellm import completion
import os

os.environ["OPENAI_API_KEY"] = "your-openai-key"
os.environ["ANTHROPIC_API_KEY"] = "your-anthropic-key"

# OpenAI GPT-4o-mini
response = completion(
    model="openai/gpt-4o-mini",
    messages=[{"role": "user", "content": "What is Python used for?"}]
)
print("GPT-4o-mini:", response.choices[0].message.content)

# Anthropic Claude 3 Sonnet
response = completion(
    model="anthropic/claude-3-sonnet-20240229",
    messages=[{"role": "user", "content": "What is Python used for?"}]
)
print("Claude 3:", response.choices[0].message.content)
```

**Output** (approximate):
```
GPT-4o-mini: Python is used for AI, web development, automation, and more.
Claude 3: Python supports data science, machine learning, web apps, and scripting.
```

**How It Works**:
- **Model**: Prefix with provider (e.g., `openai/`, `anthropic/`).
- **Messages**: OpenAI-compatible format (`role`, `content`).
- **Security**:
  - Validate input:
    ```python
    if "hack" in messages[0]["content"].lower():
        raise ValueError("Unsafe prompt")
    ```
  - Encrypt keys:
    ```python
    os.environ["LITELLM_SALT_KEY"] = "random-salt"  # For proxy encryption
    ```

#### Example 2: Embeddings (SDK)
Generate embeddings with Hugging Face.

```python
from litellm import embedding
import os

os.environ["HUGGINGFACE_API_KEY"] = "your-hf-key"

response = embedding(
    model="huggingface/sentence-transformers/all-MiniLM-L6-v2",
    input=["Python is cool", "Java is enterprise-ready"],
    api_base="https://api-inference.huggingface.co/models/sentence-transformers/all-MiniLM-L6-v2"
)
embeddings = [item["embedding"] for item in response.data]
print("Embeddings:", [e[:5] for e in embeddings])  # First 5 dimensions
```

**Output**:
```
Embeddings: [[0.123, -0.456, 0.789, -0.234, 0.567], ...]
```

**How It Works**:
- **Model**: Specifies Hugging Face model.
- **Input**: List of texts for vectorization.
- **Use Case**: Feed to RAG (like our LlamaIndex chat).
- **Security**:
  - Limit input size:
    ```python
    if len(input_text) > 10000:
        raise ValueError("Input too long")
    ```

#### Example 3: Streaming via Proxy
Run a proxy and stream responses.

```bash
# Terminal: Start proxy
litellm --model openai/gpt-4o-mini
```

```python
import openai

client = openai.OpenAI(
    api_key="anything",  # Proxy key (or LITELLM_MASTER_KEY)
    base_url="http://localhost:4000"
)

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Tell a short story"}],
    stream=True
)

for chunk in response:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="")
```

**Output** (live stream):
```
Once a robot dreamed of stars...
```

**How It Works**:
- **Proxy**: Runs at `localhost:4000`, routes to GPT-4o-mini.
- **Streaming**: Returns chunks for real-time UI (like Chainlit).
- **Security**:
  - Restrict proxy access:
    ```bash
    litellm --config config.yaml --host 127.0.0.1
    ```
  - Log requests:
    ```python
    os.environ["LITELLM_LOGGING"] = "true"
    ```

#### Example 4: Tool Calling via Proxy
Use a calculator tool with Claude.

```bash
# config.yaml
model_list:
  - model_name: claude
    litellm_params:
      model: anthropic/claude-3-sonnet-20240229
      api_key: os.environ/ANTHROPIC_API_KEY
```

```bash
litellm --config config.yaml
```

```python
import openai
import json

client = openai.OpenAI(base_url="http://localhost:4000", api_key="anything")

response = client.chat.completions.create(
    model="claude",
    messages=[{"role": "user", "content": "Calculate 5 * 3 - 2"}],
    tools=[
        {
            "type": "function",
            "function": {
                "name": "calculator",
                "description": "Evaluates math expressions",
                "parameters": {
                    "type": "object",
                    "properties": {"expression": {"type": "string"}},
                    "required": ["expression"]
                }
            }
        }
    ]
)

tool_call = response.choices[0].message.tool_calls[0]
if tool_call.function.name == "calculator":
    args = json.loads(tool_call.function.arguments)
    from sympy import sympify
    result = str(sympify(args["expression"]))
    print(f"Result: {result}")
```

**Output**:
```
Result: 13
```

**How It Works**:
- **Config**: Defines `claude` model in proxy.
- **Tool**: Claude calls `calculator` for math.
- **Security**:
  - Sanitize expressions:
    ```python
    if ";" in args["expression"]:
        raise ValueError("Invalid expression")
    ```

---

### 5. LiteLLM Proxy Setup

For production, run LiteLLM as a proxy with a config to manage multiple models.

**Config Example** (`config.yaml`):
```yaml
model_list:
  - model_name: gpt
    litellm_params:
      model: openai/gpt-4o-mini
      api_key: os.environ/OPENAI_API_KEY
  - model_name: claude
    litellm_params:
      model: anthropic/claude-3-sonnet-20240229
      api_key: os.environ/ANTHROPIC_API_KEY
  - model_name: llama
    litellm_params:
      model: ollama/llama3
      api_base: http://localhost:11434
general_settings:
  master_key: sk-1234
  database_url: postgresql://user:password@host:port/dbname
```

**Run Proxy**:
```bash
docker run -v $(pwd)/config.yaml:/app/config.yaml -p 4000:4000 ghcr.io/berriai/litellm:main-latest --config /app/config.yaml
```

**Features**:
- **Models**: Access GPT-4o-mini, Claude, and Llama via `model=gpt`, `claude`, or `llama`.
- **Virtual Keys**:
  ```bash
  curl -X POST 'http://localhost:4000/key/generate' \
  -H 'Authorization: Bearer sk-1234' \
  -H 'Content-Type: application/json' \
  -d '{"models": ["gpt", "claude"]}'
  ```
- **Cost Tracking**: Logs token usage to database.
- **Security**:
  - Encrypt keys: Set `LITELLM_SALT_KEY`.
  - Restrict models per key.
  - Audit logs:
    ```yaml
    litellm_settings:
      callbacks: [langfuse]
    ```

---

### 6. Integration with Chainlit

Since you explored Chainlit for conversational UIs, here’s how to use LiteLLM as its inference backend.

```python
import chainlit as cl
import openai

client = openai.AsyncOpenAI(
    base_url="http://localhost:4000",
    api_key="sk-1234"
)

@cl.on_chat_start
async def start():
    await cl.Message(content="Welcome! Ask anything.").send()

@cl.on_message
async def main(message: cl.Message):
    response = await client.chat.completions.create(
        model="gpt",  # From config.yaml
        messages=[{"role": "user", "content": message.content}],
        stream=True
    )
    msg = cl.Message(content="")
    await msg.send()
    async for chunk in response:
        if chunk.choices[0].delta.content:
            await msg.stream_token(chunk.choices[0].delta.content)
    await msg.update()
```

**How It Works**:
- **LiteLLM Proxy**: Routes `gpt` to GPT-4o-mini.
- **Chainlit**: Provides ChatGPT-like UI (like our Chainlit chat).
- **Security**:
  - Filter inputs:
    ```python
    if "hack" in message.content.lower():
        await cl.Message(content="Blocked.").send()
        return
    ```

**Why It’s Effective**:
- Combines LiteLLM’s unified inference with Chainlit’s UI.
- Switches models (e.g., to `claude`) without code changes.

---

### 7. Key Concepts
- **SDK vs. Proxy**:
  - **SDK**: `litellm.completion()` for direct calls.
  - **Proxy**: `http://localhost:4000` for apps/frameworks.
- **Model Format**: `provider/model` (e.g., `openai/gpt-4o`, `huggingface/llama`).
- **Config**:
  - `model_list`: Defines models and credentials.
  - `general_settings`: Sets keys, database, retries.
- **Routing**:
  - Strategies: `simple-shuffle`, `least-busy`, `latency-based`.[](https://docs.litellm.ai/docs/proxy/configs)
- **Fallbacks**:
  - Example: If Claude fails, try GPT-4o.
    ```yaml
    fallbacks: [{"claude": ["gpt"]}]
    ```

---

### 8. When to Use LiteLLM
- **Inference**:
  - Need a single API for multiple LLMs.
  - Example: Chatbot with GPT-4o and Llama fallback.
- **Proxy**:
  - Centralize LLM access for apps (e.g., Chainlit, LangChain).
  - Example: Enterprise gateway with cost tracking.
- **Hosting**:
  - Use with Ollama for local models or cloud for scale.
- **Compared to Chainlit**:
  - **Chainlit**: Builds UI; uses LiteLLM for inference.
  - **LiteLLM**: Handles backend LLM calls, no UI.

---

### 9. Common Pitfalls and Fixes
- **Proxy**:
  - **Issue**: Proxy not starting.
    - **Fix**: Check config syntax:
      ```bash
      litellm --config config.yaml --detailed_debug
      ```
  - **Issue**: Rate limits.
    - **Fix**: Set virtual key limits:
      ```bash
      curl -X POST 'http://localhost:4000/key/generate' -d '{"rpm_limit": 10}'
      ```
- **Inference**:
  - **Issue**: Model not found.
    - **Fix**: Use correct prefix:
      ```python
      model="huggingface/mistralai/Mixtral-8x7B"
      ```
  - **Issue**: High latency.
    - **Fix**: Enable caching:
      ```yaml
      litellm_settings:
        cache: true
      ```
- **Security**:
  - **Issue**: Exposed proxy.
    - **Fix**: Restrict access:
      ```bash
      ufw allow from 127.0.0.1 to any port 4000
      ```
  - **Issue**: Data leaks.
    - **Fix**: Redact outputs:
      ```python
      from llm_guard.output_scanners import Anonymize
      scanner = Anonymize()
      sanitized, _ = scanner.scan(response.choices[0].message.content)
      ```

---

### 10. Hands-On Challenge
To master LiteLLM:
1. **Run Proxy**:
   - Create `config.yaml` with GPT-4o-mini and Ollama Llama3.
   - Start proxy: `litellm --config config.yaml`.
2. **Chat Completion**:
   - Query both models: “What’s AI?”
   - Use SDK and proxy.
3. **Tool Calling**:
   - Add a `double` function (input * 2).
   - Query: “Double 5.”
4. **Security**:
   - Block “hack” in prompts.
   - Log responses to a file.
5. Share code/output, and I’ll review!

**Starter Code**:
```python
from litellm import completion
import os

os.environ["OPENAI_API_KEY"] = "your-key"

def double(x: str) -> str:
    return str(int(x) * 2)

# Add inference code
```

---

### 11. Advanced Tips
- **Load Balancing**:
  ```yaml
  router_settings:
    routing_strategy: latency-based-routing
  ```
- **Caching**:
  ```python
  from litellm import completion
  response = completion(..., cache={"enabled": True})
  ```
- **Local Hosting**:
  ```bash
  ollama pull llama3
  litellm --model ollama/llama3 --api_base http://localhost:11434
  ```
- **Chainlit Integration**:
  - Add model switcher:
    ```python
    from chainlit.input_widget import Select
    await cl.ChatSettings([
        Select(id="model", label="Model", values=["gpt", "claude"])
    ]).send()
    ```
- **Security**:
  - Rate limits:
    ```yaml
    general_settings:
      rpm_limit_per_key: 100
    ```
  - Audit logs:
    ```python
    os.environ["LANGFUSE_PUBLIC_KEY"] = "your-key"
    ```



---
