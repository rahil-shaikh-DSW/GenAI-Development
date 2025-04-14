
---

###  Resources
- **Docs**:
  - [vLLM Docs](https://docs.vllm.ai): Quickstart and API.
  - [GitHub](https://github.com/vllm-project/vllm): Examples, issues.
- **Tutorials**:
  - Medium: “Deploying LLMs with vLLM” (web:3,9,19).
  - DataCamp: “vLLM on Cloud” (web:13).
  - X: `#vLLM #LLM` (post:1,2,4,6).
- **Community**:
  - Slack: [slack.vllm.ai](https://slack.vllm.ai) (per web:0).
  - Discord: vLLM community.
- **Installation**:
  ```bash
  pip install vllm
  docker pull vllm/vllm-openai:latest
  ```

---

### 1. What is vLLM?

- **Definition**: vLLM is an **open-source, high-performance inference and serving engine** for hosting large language models (LLMs) on GPU hardware, optimized for **high throughput** and **memory efficiency** using techniques like **PagedAttention** and **continuous batching**.
- **Why It Matters**:
  - Designed for **production-grade LLM hosting**, delivering up to **24x higher throughput** than Hugging Face Transformers (per web:19, post:0,4).
  - Supports **OpenAI-compatible APIs**, making it a drop-in replacement for cloud services (e.g., OpenAI, Anthropic).
  - Ideal for **self-hosted LLMs** on-premises or cloud, aligning with your privacy/security focus (vs. Ollama’s local focus or LiteLLM’s proxy role).
  - Handles **large-scale workloads** (e.g., chatbots, RAG apps) with low latency.
- **Key Features**:
  - **PagedAttention**: Efficient memory management for attention keys/values, reducing GPU memory waste (per web:12,16,19).
  - **Continuous Batching**: Dynamically groups requests to maximize GPU utilization (per web:12,24).
  - **Model Support**: Llama 3.1, Mistral, Gemma, Phi-3, and more (50+ models, per web:0).
  - **APIs**: `/v1/completions`, `/v1/chat/completions`, `/v1/embeddings` (OpenAI format).
  - **GPU Optimization**: Tensor parallelism, FP8 quantization, and pipeline parallelism (per web:0,5,7).
  - **Streaming**: Real-time output for interactive apps (per web:7,15).
  - **Multimodal**: Supports vision-language models like Pixtral (per web:2,5).
  - **Integrations**: Works with LangChain, LlamaIndex, LiteLLM, and FastAPI.
- **Use Cases**:
  - Host a private chatbot (e.g., Llama 3.1 for internal use).
  - Serve RAG apps with embeddings (like our LlamaIndex chat).
  - Deploy APIs for real-time inference (e.g., code generation).
- **Comparison to Prior Frameworks**:
  - **Ollama**: Local, CPU/GPU hosting for smaller setups; vLLM is GPU-focused, production-scale.
  - **LiteLLM**: Proxy for unified API access; vLLM hosts models directly with better throughput.
  - **Chainlit**: UI layer; vLLM provides the inference backend.
  - **Hugging Face TGI**: Similar GPU serving, but vLLM has lower latency under load (per web:2).

---

### 2. Core Components of vLLM

vLLM organizes LLM hosting around **models**, **servers**, and **optimizations**:

- **Models**: Pre-trained LLMs from Hugging Face (e.g., `meta-llama/Llama-3.1-8B-Instruct`) or local weights.
  - Stored in `~/.cache/huggingface` or custom paths.
  - Sizes: 8B (16GB VRAM), 70B (80GB VRAM with multi-GPU).
- **Server**: Runs at `http://localhost:8000` by default, exposing OpenAI-compatible endpoints.
  - CLI: `vllm serve`.
  - Python: `vllm.entrypoints.openai.api_server`.
- **Optimizations**:
  - **PagedAttention**: Splits attention cache into pages, reducing memory fragmentation (per web:12,16).
  - **Continuous Batching**: Processes requests as they arrive, avoiding fixed batch delays (per web:24).
  - **Quantization**: Supports FP8, 4-bit (e.g., AWQ), shrinking model size (per web:5,19).
  - **Tensor Parallelism**: Splits models across GPUs for large models (per web:7).
- **CLI**: Commands like `vllm serve`, `python -m vllm.entrypoints`.
- **Docker**: Official images (`vllm/vllm-openai:latest`) for containerized hosting (per web:5,13).

---

### 3. Hosting LLMs with vLLM

Hosting an LLM with vLLM involves **installation**, **model selection**, **server setup**, and **integration**. Below are steps for local and cloud/server setups, with examples.

#### 3.1 Installation
- **Requirements**:
  - **OS**: Linux preferred; macOS/Windows via Docker/WSL2.
  - **Hardware**:
    - GPU: NVIDIA (Compute Capability ≥7.0, e.g., V100, A100, RTX 3060); AMD ROCm experimental.
    - VRAM: 16GB (8B models), 40GB+ (70B models).
    - CPU fallback: Limited support, slow (per web:13).
  - **Software**: Python 3.8+, CUDA 12.1+, PyTorch 2.1+.
  - **Storage**: Models range from 5GB (Gemma-2B) to 150GB (Llama-70B).
- **Install**:
  ```bash
  pip install vllm==0.7.2
  ```
  - Recommended: Use `uv` for faster setup (per web:4):
    ```bash
    uv venv myenv --python 3.12
    source myenv/bin/activate
    uv pip install vllm
    ```
  - Docker (GPU):
    ```bash
    docker pull vllm/vllm-openai:latest
    ```
- **Verify**:
  ```bash
  python -c "import vllm; print(vllm.__version__)"
  ```

#### 3.2 Pull a Model
- **Source**: Hugging Face (requires `HF_TOKEN` for gated models like Llama).
  ```bash
  export HF_TOKEN="your-huggingface-token"
  ```
- **Example**: Use `meta-llama/Llama-3.1-8B-Instruct` (8B, ~16GB VRAM).
  - vLLM auto-downloads during serving (no explicit pull needed).
- **Check Models**:
  ```bash
  ls ~/.cache/huggingface/hub
  ```

#### 3.3 Run Locally (CLI)
- **Command**:
  ```bash
  vllm serve meta-llama/Llama-3.1-8B-Instruct --host 127.0.0.1 --port 8000
  ```
- **Output**:
  ```
  INFO: Started server at http://127.0.0.1:8000
  ```
- **Test API**:
  ```bash
  curl http://localhost:8000/v1/chat/completions -H "Content-Type: application/json" -d '{
    "model": "meta-llama/Llama-3.1-8B-Instruct",
    "messages": [{"role": "user", "content": "What is Python?"}]
  }'
  ```
- **Response** (JSON):
  ```json
  {
    "choices": [{"message": {"role": "assistant", "content": "Python is a programming language..."}}]
  }
  ```
- **Security**:
  - Restrict host:
    ```bash
    vllm serve ... --host 127.0.0.1
    ```
  - API key:
    ```bash
    export VLLM_API_KEY="my-secret-key"
    vllm serve ... --api-key $VLLM_API_KEY
    ```
  - Input validation:
    ```bash
    if [[ $input == *"hack"* ]]; then echo "Blocked"; exit 1; fi
    ```

#### 3.4 Run as Python API
Use vLLM’s Python interface for custom apps.

```python
from vllm import LLM, SamplingParams

def query_vllm(prompt, model="meta-llama/Llama-3.1-8B-Instruct"):
    if "hack" in prompt.lower():
        raise ValueError("Unsafe prompt")
    llm = LLM(model=model, gpu_memory_utilization=0.9)
    params = SamplingParams(temperature=0.7, max_tokens=100)
    outputs = llm.generate([prompt], params)
    return outputs[0].outputs[0].text

print(query_vllm("What is Python used for?"))
```

**Output**:
```
Python is used for AI, web development, automation, and more.
```

**How It Works**:
- **LLM**: Loads model into GPU memory.
- **SamplingParams**: Controls generation (temperature, tokens).
- **Security**:
  - Redact outputs:
    ```python
    import re
    output = re.sub(r'\b[\w\.-]+@[\w\.-]+\.\w+\b', '[REDACTED]', response)
    ```
  - Limit tokens:
    ```python
    params = SamplingParams(..., max_tokens=500)
    ```

#### 3.5 Run with Docker
For containerized hosting (per web:5,7,15).

- **Command**:
  ```bash
  docker run --runtime nvidia --gpus all \
    -v ~/.cache/huggingface:/root/.cache/huggingface \
    -e "HUGGING_FACE_HUB_TOKEN=$HF_TOKEN" \
    -e "VLLM_API_KEY=my-secret-key" \
    -p 8000:8000 \
    vllm/vllm-openai:latest \
    --model meta-llama/Llama-3.1-8B-Instruct \
    --host 0.0.0.0 --port 8000
  ```
- **Access**: `http://localhost:8000/v1/chat/completions`.
- **Security**:
  - Network isolation:
    ```bash
    docker network create vllm-net
    docker run ... --network vllm-net
    ```
  - Audit logs:
    ```bash
    docker logs vllm-container > audit.log
    ```

---

### 4. Hosting on a Server/Cloud

For production or multi-user access (per web:6,9,13,16,17).

#### 4.1 Bare Metal (e.g., Local GPU Server)
- **Setup**:
  - Server: NVIDIA A100 (40GB) or RTX 4090 (24GB).
  - OS: Ubuntu 22.04.
  - Install CUDA 12.1, PyTorch, vLLM:
    ```bash
    pip install torch vllm
    ```
- **Run**:
  ```bash
  vllm serve mistralai/Mixtral-8x7B-Instruct-v0.1 \
    --host 0.0.0.0 --port 8000 \
    --gpu-memory-utilization 0.9 \
    --tensor-parallel-size 2
  ```
- **Access**: `http://<server-ip>:8000`.
- **Security**:
  - Firewall:
    ```bash
    ufw allow from <trusted-ip> to any port 8000
    ```
  - HTTPS (via Caddy, per web:7,15):
    ```bash
    sudo apt install caddy
    echo "<domain>:80 {
      reverse_proxy localhost:8000
      encode gzip
      tls <email>
    }" > /etc/caddy/Caddyfile
    sudo systemctl restart caddy
    ```

#### 4.2 Cloud (e.g., AWS, Google Cloud, Koyeb)
- **AWS EC2 (per web:9)**:
  - Instance: `g5.4xlarge` (A10G, 24GB VRAM).
  - Setup:
    ```bash
    sudo apt update
    pip install vllm
    export HF_TOKEN="your-token"
    vllm serve meta-llama/Llama-3.1-8B-Instruct
    ```
  - Access: `http://<ec2-public-ip>:8000`.
- **Google Cloud (per web:13,24)**:
  - Instance: A100 80GB.
  - Use Vertex AI’s vLLM (optimized, per web:24):
    ```bash
    gcloud ai endpoints deploy-model \
      --model=meta-llama/Llama-3.1-8B \
      --region=us-central1 \
      --accelerator=type=NVIDIA_A100_80GB,count=1
    ```
- **Koyeb (per web:6)**:
  - Dockerfile:
    ```dockerfile
    FROM pytorch/pytorch:2.1.2-cuda12.1-cudnn8-devel
    RUN pip install vllm==0.7.2
    ENTRYPOINT ["vllm", "serve", "google/gemma-2b-it", "--host", "0.0.0.0", "--port", "80"]
    ```
  - Deploy:
    ```bash
    koyeb app deploy --docker vllm-app --env HF_TOKEN=$HF_TOKEN
    ```
- **Security**:
  - API key:
    ```bash
    export VLLM_API_KEY="secure-key"
    ```
  - VPC:
    ```bash
    aws ec2 create-security-group --group-name vllm-sg --description "vLLM access"
    aws ec2 authorize-security-group-ingress --group-name vllm-sg --protocol tcp --port 8000 --cidr <trusted-ip>/32
    ```

#### 4.3 Kubernetes (per web:1,11, post:1)
- **Helm Chart** (per post:1):
  ```bash
  helm repo add vllm https://vllm.ai/helm
  helm install vllm vllm/vllm \
    --set model=meta-llama/Llama-3.1-8B-Instruct \
    --set gpus=2
  ```
- **Config**:
  ```yaml
  apiVersion: apps/v1
  kind: Deployment
  metadata:
    name: vllm
  spec:
    replicas: 1
    template:
      spec:
        containers:
        - name: vllm
          image: vllm/vllm-openai:latest
          args:
          - "--model=meta-llama/Llama-3.1-8B-Instruct"
          - "--tensor-parallel-size=2"
          resources:
            limits:
              nvidia.com/gpu: 2
  ```
- **Security**:
  - RBAC:
    ```yaml
    apiVersion: rbac.authorization.k8s.io/v1
    kind: Role
    rules:
    - apiGroups: [""]
      resources: ["pods"]
      verbs: ["get", "list"]
    ```
  - Network policy:
    ```yaml
    apiVersion: networking.k8s.io/v1
    kind: NetworkPolicy
    spec:
      podSelector:
        matchLabels:
          app: vllm
      ingress:
      - from:
        - ipBlock:
            cidr: <trusted-ip>/32
        ports:
        - port: 8000
    ```

---

### 5. Integrating with LiteLLM Proxy

Use vLLM with LiteLLM for unified access (per our LiteLLM chat).

- **Config** (`config.yaml`):
  ```yaml
  model_list:
    - model_name: llama3
      litellm_params:
        model: openai/llama3
        api_base: http://<vllm-host>:8000
        api_key: my-secret-key
  ```
- **Run Proxy**:
  ```bash
  docker run -v $(pwd)/config.yaml:/app/config.yaml -p 4000:4000 ghcr.io/berriai/litellm:main-latest --config /app/config.yaml
  ```
- **Query**:
  ```python
  import openai

  client = openai.OpenAI(base_url="http://localhost:4000", api_key="anything")
  response = client.chat.completions.create(
      model="llama3",
      messages=[{"role": "user", "content": "What is Python?"}]
  )
  print(response.choices[0].message.content)
  ```
- **Output**:
  ```
  Python is a programming language...
  ```
- **Security**:
  - Virtual keys:
    ```bash
    curl -X POST 'http://localhost:4000/key/generate' -d '{"models": ["llama3"]}'
    ```
  - Rate limits:
    ```yaml
    general_settings:
      rpm_limit_per_key: 100
    ```

**Why It’s Effective**:
- Combines vLLM’s high-throughput hosting with LiteLLM’s proxy features.
- Scales to multiple apps/users.
- Integrates with Chainlit for UI (per our Chainlit chat).

---

### 6. Example: Chat with Streaming
Host Llama 3.1 with streaming for a chatbot.

- **Run Server**:
  ```bash
  vllm serve meta-llama/Llama-3.1-8B-Instruct --host 127.0.0.1
  ```
- **Python Client**:
  ```python
  import openai

  client = openai.OpenAI(base_url="http://localhost:8000", api_key="my-secret-key")
  stream = client.chat.completions.create(
      model="meta-llama/Llama-3.1-8B-Instruct",
      messages=[{"role": "user", "content": "Tell a short story"}],
      stream=True
  )
  for chunk in stream:
      if chunk.choices[0].delta.content:
          print(chunk.choices[0].delta.content, end="")
  ```
- **Output** (live):
  ```
  Once a robot dreamed of stars...
  ```
- **Security**:
  - Sanitize input:
    ```python
    if "hack" in messages[0]["content"].lower():
        raise ValueError("Blocked")
    ```
  - Log requests:
    ```python
    with open("audit.log", "a") as f:
        f.write(f"Request: {messages}\n")
    ```

---

### 7. Key Concepts
- **PagedAttention**: Manages attention cache in pages, reducing memory use (per web:12,16).
- **Continuous Batching**: Dynamically adjusts batch size for throughput (per web:24).
- **Tensor Parallelism**: Splits model across GPUs (e.g., `--tensor-parallel-size 4` for 4 GPUs).
- **Quantization**: FP8 or 4-bit (e.g., `llama3:8b-q4_0`) for smaller footprint (per web:5).
- **API Endpoints**:
  - `/v1/chat/completions`: Conversational tasks.
  - `/v1/completions`: Text generation.
  - `/v1/embeddings`: Vector outputs for RAG.
- **Scaling**:
  - Multi-GPU: `--tensor-parallel-size N`.
  - Kubernetes: Helm charts (per post:1).

---

### 8. When to Use vLLM
- **Hosting**:
  - Production apps needing high throughput (e.g., customer support bots).
  - GPU clusters for large models (e.g., Mixtral 8x7B).
- **Compared to Prior Frameworks**:
  - **Ollama**: Better for local, small-scale; vLLM for production GPU.
  - **LiteLLM**: Proxy layer; vLLM is the hosting engine.
  - **Chainlit**: vLLM as backend for Chainlit’s UI.
- **Use Cases**:
  - Replace OpenAI APIs with self-hosted Llama.
  - Serve RAG apps (like our LlamaIndex setup).
  - Handle 1000s of concurrent users (per web:8,21).

---

### 9. Common Pitfalls and Fixes
- **Hosting**:
  - **Issue**: GPU OOM.
    - **Fix**: Reduce memory usage:
      ```bash
      vllm serve ... --gpu-memory-utilization 0.8 --max-model-len 2048
      ```
    - Or quantize:
      ```bash
      vllm serve ... --quantization awq
      ```
  - **Issue**: Slow startup.
    - **Fix**: Pre-download model:
      ```bash
      python -c "from huggingface_hub import snapshot_download; snapshot_download('meta-llama/Llama-3.1-8B-Instruct')"
      ```
- **API**:
  - **Issue**: Model not found.
    - **Fix**: Verify Hugging Face ID and token:
      ```bash
      export HF_TOKEN="your-token"
      ```
  - **Issue**: High latency.
    - **Fix**: Enable continuous batching:
      ```bash
      vllm serve ... --enable-chunked-prefill
      ```
- **Security**:
  - **Issue**: Exposed API.
    - **Fix**: Use Caddy for HTTPS (per web:15):
      ```bash
      caddy run --config Caddyfile
      ```
  - **Issue**: Data leaks.
    - **Fix**: Redact outputs:
      ```python
      from llm_guard.output_scanners import Anonymize
      scanner = Anonymize()
      sanitized, _ = scanner.scan(response)
      ```

---

### 10. Hands-On Challenge
To master vLLM:
1. **Host Locally**:
   - Install vLLM, serve `google/gemma-2b-it`.
   - Query via curl: “What’s AI?”
2. **Python App**:
   - Write a script for streaming chat with Gemma.
   - Test: “Write a poem.”
3. **LiteLLM Proxy**:
   - Run vLLM server, proxy with LiteLLM.
   - Query via OpenAI client.
4. **Security**:
   - Add API key, block “hack” prompts.
   - Log responses to `vllm.log`.
5. Share code/output, and I’ll review!

**Starter Code**:
```python
from vllm import LLM, SamplingParams

def query_vllm(prompt):
    if "hack" in prompt.lower():
        raise ValueError("Unsafe prompt")
    # Add inference code
```

---

### 11. Advanced Tips
- **Multimodal Models** (per web:5):
  ```bash
  vllm serve mistralai/Pixtral-12B-2409 --limit-mm-per-prompt 'image=4'
  ```
- **RAG with LlamaIndex**:
  ```python
  from llama_index.llms.vllm import VLLM
  from llama_index.core import VectorStoreIndex, SimpleDirectoryReader

  llm = VLLM(model="meta-llama/Llama-3.1-8B-Instruct", api_url="http://localhost:8000")
  documents = SimpleDirectoryReader("data").load_data()
  index = VectorStoreIndex.from_documents(documents)
  print(index.as_query_engine(llm=llm).query("What’s in the docs?"))
  ```
- **Chainlit UI**:
  ```python
  import chainlit as cl
  from openai import AsyncOpenAI

  client = AsyncOpenAI(base_url="http://localhost:8000", api_key="my-secret-key")
  @cl.on_message
  async def main(message: cl.Message):
      response = await client.chat.completions.create(
          model="meta-llama/Llama-3.1-8B-Instruct",
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
- **Scaling**:
  - Multi-GPU:
    ```bash
    vllm serve ... --tensor-parallel-size 4
    ```
  - Autoscaling (Kubernetes):
    ```yaml
    apiVersion: autoscaling/v2
    kind: HorizontalPodAutoscaler
    spec:
      scaleTargetRef:
        kind: Deployment
        name: vllm
      minReplicas: 1
      maxReplicas: 10
      metrics:
      - type: Resource
        resource:
          name: cpu
          target:
            type: Utilization
            averageUtilization: 70
    ```
- **Security**:
  - Audit logs:
    ```bash
    vllm serve ... --uvicorn-log-level info >> vllm.log
    ```
  - Input guardrails:
    ```python
    from llm_guard.input_scanners import PromptInjection
    scanner = PromptInjection()
    if scanner.scan(prompt)[1]:
        raise ValueError("Injection detected")
    ```



---
