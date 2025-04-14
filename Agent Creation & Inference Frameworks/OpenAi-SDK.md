
---

### Resources
- **Docs**:
  - [OpenAI API](https://platform.openai.com/docs): Official guide.
  - [Python SDK](https://github.com/openai/openai-python): GitHub and examples.
- **Tutorials**:
  - OpenAI Cookbook: “Getting Started with Chat Completions.”
  - FreeCodeCamp: “OpenAI SDK for Python.”
- **Community**:
  - GitHub: github.com/openai/openai-python
  - Stack Overflow for SDK errors.
  - X posts: Search `#OpenAI #GPT4o` for tips (e.g., @openai_dev).
- **Installation**:
  ```bash
  pip install openai
  ```

---

### 1. What is the OpenAI SDK?

- **Definition**: The OpenAI SDK is a Python (and JavaScript/TypeScript) library for interacting with OpenAI’s APIs, enabling **inference** with models like GPT-4, GPT-4o, and embeddings models (e.g., text-embedding-3-large) for tasks like text generation, chat, embeddings, and more.
- **Why It Matters**:
  - Provides direct access to OpenAI’s powerful LLMs for **inference** (generating outputs from inputs).
  - Simplifies API calls with a clean, typed interface (v1.0+ overhauled for clarity).
  - Supports diverse tasks: chatbots, embeddings for RAG, code generation, and more.
  - Integrates with frameworks like LangChain/AutoGen (per your prior chats) but is lower-level for fine-grained control.
- **Key Features**:
  - **Chat Completions**: Generate conversational responses (e.g., GPT-4o).
  - **Embeddings**: Convert text to vectors for semantic search (e.g., RAG).
  - **Tool Calling**: Structured outputs for functions (e.g., math, APIs).
  - **Streaming**: Real-time responses for interactive apps.
  - **Async Support**: Non-blocking calls for scalability.
- **Use Cases**:
  - Building chatbots or assistants.
  - Powering RAG systems (embeddings + chat).
  - Automating tasks (e.g., summarize text, generate code).
- **Security Note**: Aligns with your guardrails interest by requiring input/output validation to prevent misuse (e.g., prompt injection, PII leaks).

---

### 2. Inference with OpenAI Models

#### What is Inference?
- **Inference** is the process of generating outputs (e.g., text, embeddings) from inputs using a trained model.
- In the OpenAI SDK, inference involves calling APIs for:
  - **Chat Completions**: Conversational or task-oriented text (e.g., “Answer this question”).
  - **Embeddings**: Numerical vectors for text similarity (e.g., search, clustering).
  - **Completions** (legacy): Non-chat text generation (less common).

#### Supported Models
- **Chat Models** (as of April 2025):
  - **GPT-4o**: Multimodal (text, images), high performance.
  - **GPT-4o-mini**: Cost-effective, fast.
  - **GPT-3.5-turbo**: Affordable, good for simple tasks.
- **Embedding Models**:
  - **text-embedding-3-large**: High-dimensional vectors for accuracy.
  - **text-embedding-3-small**: Lightweight, cost-efficient.
  - **text-embedding-ada-002**: Legacy, still supported.
- **Other**:
  - **DALL-E** (image generation, not covered here).
  - **Whisper** (audio, via separate endpoints).

#### Key Components
- **API Key**: Authenticates requests (get from platform.openai.com).
- **Client**: SDK interface (`OpenAI` or `AsyncOpenAI`).
- **Endpoints**:
  - `/chat/completions`: For conversational tasks.
  - `/embeddings`: For vector generation.
- **Parameters**:
  - `model`: Specifies the model (e.g., `gpt-4o`).
  - `messages`: Chat history for context (role: `user`, `assistant`, `system`).
  - `temperature`: Controls randomness (0-2, default 1).
  - `max_tokens`: Limits output length.
  - `tools`: For structured function calls.

---

### 3. Setting Up the OpenAI SDK

1. **Install SDK**:
   ```bash
   pip install openai
   ```
   - Requires Python 3.7+.
   - Latest version: v1.0+ (simplified from v0.x).

2. **Set API Key**:
   ```python
   import os
   os.environ["OPENAI_API_KEY"] = "your-api-key"
   ```
   - Get key from OpenAI dashboard.
   - Store securely (e.g., `.env` file).

3. **Initialize Client**:
   ```python
   from openai import OpenAI
   client = OpenAI()  # Uses OPENAI_API_KEY from env
   ```
   - For async: `from openai import AsyncOpenAI; client = AsyncOpenAI()`.

---

### 4. Inference Examples

Below are practical examples covering key inference tasks: chat completions, tool calling, embeddings, and streaming. Each includes security tips per your guardrails interest.

#### Example 1: Chat Completions
Generate conversational responses using GPT-4o.

```python
from openai import OpenAI

client = OpenAI()

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": "You’re a helpful assistant."},
        {"role": "user", "content": "What is Python used for?"}
    ],
    temperature=0.7,
    max_tokens=100
)

print(response.choices[0].message.content)
```

**Output** (approximate):
```
Python is used for web development, AI, data science, automation, and more.
```

**How It Works**:
- **Model**: GPT-4o for high-quality responses.
- **Messages**: System sets tone; user asks question.
- **Parameters**: `temperature=0.7` balances creativity; `max_tokens=100` limits length.
- **Security**:
  - Validate input:
    ```python
    if "ignore" in messages[-1]["content"].lower():
        raise ValueError("Unsafe prompt")
    ```
  - Redact PII in output:
    ```python
    import re
    output = re.sub(r'\b[\w\.-]+@[\w\.-]+\.\w+\b', '[REDACTED]', response.choices[0].message.content)
    ```

#### Example 2: Tool Calling
Use structured tools for precise tasks (e.g., math).

```python
from openai import OpenAI
from pydantic import BaseModel

client = OpenAI()

# Define tool schema
class CalculatorInput(BaseModel):
    expression: str

def calculator(expression: str) -> str:
    from sympy import sympify
    return str(sympify(expression))  # Safe eval

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "user", "content": "What’s 15 * 3 - 7?"}
    ],
    tools=[
        {
            "type": "function",
            "function": {
                "name": "calculator",
                "description": "Evaluates math expressions",
                "parameters": CalculatorInput.schema()
            }
        }
    ],
    tool_choice="auto"
)

# Handle tool call
tool_call = response.choices[0].message.tool_calls[0]
if tool_call.function.name == "calculator":
    args = eval(tool_call.function.arguments)  # Parse JSON safely
    result = calculator(args["expression"])
    print(f"Result: {result}")
```

**Output**:
```
Result: 38
```

**How It Works**:
- **Tool**: `calculator` uses `sympy` for safe math.
- **Schema**: Pydantic ensures structured inputs.
- **Inference**: GPT-4o decides to call the tool.
- **Security**:
  - Avoid `eval` for args; use `json.loads`:
    ```python
    import json
    args = json.loads(tool_call.function.arguments)
    ```
  - Sanitize expressions:
    ```python
    if ";" in expression:
        raise ValueError("Invalid expression")
    ```

#### Example 3: Embeddings
Generate vectors for RAG or similarity tasks.

```python
from openai import OpenAI

client = OpenAI()

response = client.embeddings.create(
    model="text-embedding-3-small",
    input=["Python is a programming language.", "Java is for enterprise apps."]
)

embeddings = [data.embedding for data in response.data]
print(f"Embedding for Python: {embeddings[0][:5]}...")  # First 5 dimensions
```

**Output** (approximate):
```
Embedding for Python: [0.123, -0.456, 0.789, -0.234, 0.567]...
```

**How It Works**:
- **Model**: `text-embedding-3-small` for efficiency.
- **Input**: List of texts to vectorize.
- **Use Case**: Feed embeddings to FAISS for RAG (like our LangChain chat).
- **Security**:
  - Check input for sensitive data:
    ```python
    if "password" in input_text.lower():
        raise ValueError("Sensitive data detected")
    ```
  - Limit input size:
    ```python
    if len(input_text) > 10000:
        raise ValueError("Input too long")
    ```

#### Example 4: Streaming
Stream responses for real-time interaction.

```python
from openai import OpenAI

client = OpenAI()

stream = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "user", "content": "Tell me a short story."}
    ],
    stream=True
)

for chunk in stream:
    if chunk.choices[0].delta.content is not None:
        print(chunk.choices[0].delta.content, end="")
```

**Output** (live stream):
```
Once upon a time, a robot learned to dream...
```

**How It Works**:
- **Stream**: Returns chunks as generated.
- **Use Case**: Interactive apps (e.g., live chat).
- **Security**:
  - Monitor chunks for harmful content:
    ```python
    if "violence" in chunk.choices[0].delta.content.lower():
        break
    ```
  - Log for auditing:
    ```python
    with open("log.txt", "a") as f:
        f.write(chunk.choices[0].delta.content)
    ```

#### Example 5: Async Inference
Non-blocking calls for scalability.

```python
import asyncio
from openai import AsyncOpenAI

client = AsyncOpenAI()

async def get_response():
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": "What’s AI?"}
        ]
    )
    return response.choices[0].message.content

# Run async
print(asyncio.run(get_response()))
```

**Output**:
```
AI is intelligence exhibited by machines...
```

**How It Works**:
- **Async**: Handles multiple requests concurrently.
- **Use Case**: High-throughput apps (e.g., APIs).
- **Security**: Same as chat completions (validate inputs/outputs).

---

### 5. Key Concepts
- **Client Types**:
  - `OpenAI`: Synchronous for simple apps.
  - `AsyncOpenAI`: Asynchronous for scalability.
- **Endpoints**:
  - `/chat/completions`: Main for text generation.
  - `/embeddings`: For vector tasks.
- **Messages**:
  - Roles: `system` (behavior), `user` (input), `assistant` (output).
  - Example: `[{"role": "system", "content": "Be concise"}]`.
- **Tools**:
  - Structured functions with JSON schemas.
  - LLM decides when to call (like AutoGen tools).
- **Streaming**:
  - `stream=True` for real-time output.
- **Rate Limits**:
  - Managed via API key; check OpenAI dashboard.

---

### 6. When to Use OpenAI SDK
- **Direct Inference**:
  - Need raw access to GPT-4o or embeddings.
  - Example: Custom chatbot or RAG component.
- **Compared to LangChain/AutoGen** (per prior chats):
  - **OpenAI SDK**: Low-level, direct API calls; best for control.
  - **LangChain**: Higher-level for RAG/chains; abstracts SDK.
  - **AutoGen**: Multi-agent focus; uses SDK internally.
- **Use Case Fit**:
  - Use SDK for simple apps or integration into larger systems.
  - Use LangChain/AutoGen for complex workflows (agents, RAG).

---

### 7. Common Pitfalls and Fixes
- **Rate Limits**:
  - **Issue**: “Rate limit exceeded.”
    - **Fix**: Add retries:
      ```python
      from openai import OpenAI
      import time
      client = OpenAI(max_retries=3)
      ```
- **Token Limits**:
  - **Issue**: Truncated outputs.
    - **Fix**: Set `max_tokens` or summarize input:
      ```python
      max_tokens=500
      ```
- **Cost Overruns**:
  - **Issue**: High API usage.
    - **Fix**: Use `gpt-4o-mini` or cache responses locally:
      ```python
      import hashlib
      cache = {}
      def cached_call(messages):
          key = hashlib.md5(str(messages).encode()).hexdigest()
          if key in cache:
              return cache[key]
          response = client.chat.completions.create(...)
          cache[key] = response
          return response
      ```
- **Security** (per guardrails):
  - **Issue**: Prompt injection.
    - **Fix**: Filter inputs:
      ```python
      if "bypass" in prompt.lower():
          raise ValueError("Unsafe prompt")
      ```
  - **Issue**: PII leaks.
    - **Fix**: Use regex or LLM Guard (from our prior chat):
      ```python
      from llm_guard.output_scanners import Anonymize
      scanner = Anonymize()
      sanitized, _ = scanner.scan(response.choices[0].message.content)
      ```

---

### 8. Hands-On Challenge
To master the OpenAI SDK:
1. **Chat Completion**:
   - Query GPT-4o-mini: “What’s machine learning?”
   - Limit to 50 tokens, temperature 0.5.
2. **Tool Calling**:
   - Create a `double` function (input * 2).
   - Query: “Double 7.”
3. **Embeddings**:
   - Generate vectors for “AI is cool” and “ML is awesome.”
   - Compute cosine similarity (use numpy).
4. **Security**:
   - Add input filter (block “hack”).
   - Redact emails in outputs.
5. Share code/output, and I’ll review!

**Starter Code**:
```python
from openai import OpenAI
import re

client = OpenAI()

def double(x: str) -> str:
    return str(int(x) * 2)

# Add your inference code
```

---

### 9. Advanced Tips
- **Batch Processing**:
  - Process multiple inputs:
    ```python
    responses = [client.chat.completions.create(...) for _ in queries]
    ```
- **Caching**:
  - Use Redis for persistent cache:
    ```python
    import redis
    r = redis.Redis()
    def cached_call(messages):
        key = str(messages)
        if r.exists(key):
            return r.get(key)
        response = client.chat.completions.create(...)
        r.set(key, response)
        return response
    ```
- **Structured Outputs**:
  - Enforce JSON:
    ```python
    response_format={"type": "json_object"}
    ```
- **Security** (per guardrails):
  - Integrate Guardrails AI:
    ```python
    from guardrails import Guard
    guard = Guard().use(ToxicLanguage())
    guard.validate(response.choices[0].message.content)
    ```
  - Log for auditing:
    ```python
    with open("api_log.txt", "a") as f:
        f.write(f"Prompt: {prompt}, Response: {response}\n")
    ```



---
