
---

### Resources
- **Docker**:
  - [docs.docker.com](https://docs.docker.com) (web:0,4).
  - [Docker Hub](https://hub.docker.com) (web:7).
- **Docker Compose**:
  - [docs.docker.com/compose](https://docs.docker.com/compose) (web:9,12).
- **Tutorials**:
  - “Docker for Beginners” [freecodecamp.org](https://www.freecodecamp.org) (web:3).
  - “Compose Multi-Container Apps” [datacamp.com](https://www.datacamp.com) (web:10).
- **Community**: Docker Discord, Stack Overflow.


---

### 1. What is Docker?

- **Definition**: Docker is an open-source platform for **containerization**, allowing you to package applications and their dependencies into lightweight, portable **containers** that run consistently across environments (local, cloud, or servers).
- **Why It Matters**:
  - **Portability**: Run apps anywhere (e.g., Ubuntu, macOS, AWS) without “it works on my machine” issues (per web:0,3).
  - **Isolation**: Containers share the host OS but run in isolated environments, reducing conflicts (per web:1,5).
  - **Efficiency**: Lighter than VMs, using less CPU/memory (e.g., ~100MB vs. ~GB for VMs) (per web:2).
  - **DevOps**: Simplifies CI/CD, microservices, and scaling (per web:6,11).
- **Key Components**:
  - **Image**: A read-only template (e.g., `nginx:latest`) with app code, libraries, and OS (per web:4).
  - **Container**: A running instance of an image, like a lightweight VM (per web:4).
  - **Dockerfile**: Script to build images (e.g., `FROM python:3.12`).
  - **Registry**: Stores images (e.g., Docker Hub, `docker.io`) (per web:7).
  - **Daemon**: `dockerd` manages containers on the host (per web:5).
- **Use Cases**:
  - Run a web server (e.g., Nginx).
  - Deploy a Python app with dependencies.
  - Test databases (e.g., PostgreSQL) without local installs.

---

### 2. What is Docker Compose?

- **Definition**: Docker Compose is a tool for defining and running **multi-container applications** using a single YAML file (`docker-compose.yml`), orchestrating services, networks, and volumes (per web:9,12).
- **Why It Matters**:
  - **Simplifies Complexity**: Manage multiple containers (e.g., app + database) with one command (per web:10).
  - **Development-Friendly**: Spin up entire stacks (e.g., web server, API, cache) locally (per web:13).
  - **Reproducible**: Share YAML files for consistent setups (per web:9).
- **Key Components**:
  - **Services**: Containers (e.g., `web`, `db`) defined in YAML.
  - **Networks**: Isolated communication channels (e.g., `frontend`, `backend`).
  - **Volumes**: Persistent storage for data (e.g., database files).
- **Use Cases**:
  - Run a web app with Nginx, Flask, and Redis.
  - Test microservices with interdependent containers.
  - Simulate production environments locally.

---

### 3. Docker: Installation and Usage

#### 3.1 Installation

- **Ubuntu**:
  ```bash
  sudo apt update
  sudo apt install -y docker.io docker-compose
  sudo usermod -aG docker $USER
  newgrp docker
  sudo systemctl enable docker
  sudo systemctl start docker
  ```
  - Verify: `docker --version` (e.g., `Docker version 27.3.1`).
- **macOS**:
  - Download [Docker Desktop](https://www.docker.com/products/docker-desktop).
  - Install, enable Docker Desktop in System Preferences.
  - Verify: `docker --version`.
- **Windows**:
  - Install Docker Desktop with WSL2 backend (Windows 10/11 Pro).
  - Enable WSL2, Hyper-V, and Containers in Windows Features.
  - Verify: `docker --version`.
- **Security**:
  - Restrict Docker socket:
    ```bash
    sudo chmod 660 /var/run/docker.sock
    ```
  - Scan images:
    ```bash
    docker scan nginx:latest
    ```

#### 3.2 Basic Usage

- **Run a Container**:
  ```bash
  docker run --name my-nginx -d -p 8080:80 nginx:latest
  ```
  - `-d`: Detached mode.
  - `-p 8080:80`: Map host port 8080 to container port 80.
  - Access: `http://localhost:8080` (Nginx welcome page).
- **List Containers**:
  ```bash
  docker ps  # Running
  docker ps -a  # All
  ```
- **Stop/Remove Container**:
  ```bash
  docker stop my-nginx
  docker rm my-nginx
  ```
- **Pull an Image**:
  ```bash
  docker pull python:3.12
  ```
- **Run Interactive Shell**:
  ```bash
  docker run -it python:3.12 bash
  # Inside container
  python --version
  exit
  ```
- **Build an Image** (Dockerfile):
  ```dockerfile
  # Dockerfile
  FROM python:3.12-slim
  WORKDIR /app
  COPY app.py .
  RUN pip install flask
  EXPOSE 5000
  CMD ["python", "app.py"]
  ```
  ```python
  # app.py
  from flask import Flask
  app = Flask(__name__)

  @app.route('/')
  def hello():
      return "Hello, Docker!"
  
  if __name__ == "__main__":
      app.run(host="0.0.0.0", port=5000)
  ```
  ```bash
  docker build -t my-flask-app .
  ```
- **Run Custom Image**:
  ```bash
  docker run --name flask-app -d -p 5000:5000 my-flask-app
  ```
  - Access: `http://localhost:5000` (“Hello, Docker!”).
- **Logs**:
  ```bash
  docker logs flask-app
  ```
- **Security**:
  - Run as non-root:
    ```dockerfile
    RUN useradd -m appuser
    USER appuser
    ```
  - Limit resources:
    ```bash
    docker run ... --memory="512m" --cpus="1"
    ```

#### 3.3 Common Commands
- **Images**:
  ```bash
  docker images  # List
  docker rmi nginx:latest  # Remove
  ```
- **Volumes** (persistent data):
  ```bash
  docker volume create my-data
  docker run -v my-data:/data my-app
  ```
- **Networks**:
  ```bash
  docker network create my-net
  docker run --network my-net ...
  ```
- **Clean Up**:
  ```bash
  docker system prune -f  # Remove unused
  ```

---

### 4. Docker Compose: Installation and Usage

#### 4.1 Installation

- **Ubuntu** (Docker Compose V2 included with Docker):
  ```bash
  docker compose version  # Should be ~2.29.2
  ```
  - If missing:
    ```bash
    sudo apt install docker-compose-plugin
    ```
- **macOS/Windows**: Included with Docker Desktop.
- **Manual Install** (if needed):
  ```bash
  sudo curl -L "https://github.com/docker/compose/releases/download/v2.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
  sudo chmod +x /usr/local/bin/docker-compose
  ```

#### 4.2 Basic Usage

- **Create `docker-compose.yml`**:
  ```yaml
  version: "3.9"
  services:
    web:
      image: nginx:latest
      ports:
        - "8080:80"
      volumes:
        - web-data:/usr/share/nginx/html
      networks:
        - my-net
    app:
      build:
        context: .
        dockerfile: Dockerfile
      ports:
        - "5000:5000"
      environment:
        - FLASK_ENV=production
      depends_on:
        - web
      networks:
        - my-net
  volumes:
    web-data:
  networks:
    my-net:
      driver: bridge
  ```
- **Directory Structure**:
  ```
  .
  ├── docker-compose.yml
  ├── Dockerfile
  └── app.py
  ```
- **Start Services**:
  ```bash
  docker compose up -d
  ```
  - Access: `http://localhost:8080` (Nginx), `http://localhost:5000` (Flask).
- **View Services**:
  ```bash
  docker compose ps
  ```
- **Logs**:
  ```bash
  docker compose logs app
  ```
- **Stop/Remove**:
  ```bash
  docker compose down
  docker compose down -v  # Remove volumes
  ```
- **Scale Services**:
  ```bash
  docker compose up -d --scale app=3
  ```
- **Security**:
  - Use secrets:
    ```yaml
    services:
      app:
        secrets:
          - api_key
    secrets:
      api_key:
        file: ./api_key.txt
    ```
    ```bash
    echo "my-secret-key" > api_key.txt
    ```
  - Isolate networks:
    ```yaml
    networks:
      my-net:
        internal: true
    ```

#### 4.3 Example: Multi-Container App

Build a **web app** (Flask) with a **database** (PostgreSQL) and **cache** (Redis).

- **docker-compose.yml**:
  ```yaml
  version: "3.9"
  services:
    db:
      image: postgres:16
      environment:
        POSTGRES_USER: appuser
        POSTGRES_PASSWORD: appsecret
        POSTGRES_DB: myapp
      volumes:
        - db-data:/var/lib/postgresql/data
      networks:
        - backend
    redis:
      image: redis:7
      networks:
        - backend
    app:
      build: .
      ports:
        - "5000:5000"
      environment:
        - DATABASE_URL=postgresql://appuser:appsecret@db/myapp
        - REDIS_URL=redis://redis:6379
      depends_on:
        - db
        - redis
      networks:
        - backend
        - frontend
  volumes:
    db-data:
  networks:
    backend:
      internal: true
    frontend:
  ```
- **Dockerfile**:
  ```dockerfile
  FROM python:3.12-slim
  WORKDIR /app
  COPY requirements.txt .
  RUN pip install -r requirements.txt
  COPY app.py .
  CMD ["python", "app.py"]
  ```
- **requirements.txt**:
  ```
  flask
  psycopg2-binary
  redis
  ```
- **app.py**:
  ```python
  from flask import Flask
  import psycopg2
  import redis
  import os

  app = Flask(__name__)
  db_url = os.getenv("DATABASE_URL")
  redis_url = os.getenv("REDIS_URL")

  @app.route('/')
  def home():
      try:
          conn = psycopg2.connect(db_url)
          cur = conn.cursor()
          cur.execute("CREATE TABLE IF NOT EXISTS visits (id SERIAL PRIMARY KEY, count INT)")
          cur.execute("INSERT INTO visits (count) VALUES (1) ON CONFLICT DO NOTHING")
          cur.execute("SELECT SUM(count) FROM visits")
          db_count = cur.fetchone()[0] or 0
          cur.close()
          conn.close()
      except Exception as e:
          db_count = f"DB Error: {e}"

      cache = redis.Redis.from_url(redis_url)
      cache.incr("visits")
      redis_count = cache.get("visits").decode()

      return f"DB Visits: {db_count}, Redis Visits: {redis_count}"

  if __name__ == "__main__":
      app.run(host="0.0.0.0", port=5000)
  ```
- **Run**:
  ```bash
  docker compose up -d --build
  ```
- **Access**: `http://localhost:5000` (“DB Visits: 1, Redis Visits: 1”).
- **Security**:
  - Validate env vars:
    ```python
    if not db_url:
        raise ValueError("DATABASE_URL missing")
    ```
  - Restrict ports:
    ```yaml
    db:
      ports:
        - "127.0.0.1:5432:5432"  # Local only
    ```

---

### 5. Key Concepts

- **Docker**:
  - **Images vs. Containers**: Image is a blueprint; container is a running instance (per web:4).
  - **Layers**: Images are cached layers (e.g., `RUN pip install` adds a layer) (per web:5).
  - **Volumes**: Persist data outside containers (e.g., `/var/lib/postgresql/data`).
  - **Networks**: Bridge (default), host, or custom for isolation (per web:8).
- **Docker Compose**:
  - **Services**: Define containers with images or builds (per web:9).
  - **Depends_On**: Startup order (e.g., app waits for db) (per web:12).
  - **Environment**: Pass configs (e.g., `POSTGRES_PASSWORD`) (per web:10).
  - **Healthchecks**:
    ```yaml
    db:
      healthcheck:
        test: ["CMD", "pg_isready", "-U", "appuser"]
        interval: 10s
        retries: 5
    ```
- **Performance**:
  - Cache builds: `docker compose build --no-cache`.
  - Optimize images:
    ```dockerfile
    FROM python:3.12-slim  # Smaller base
    RUN pip install --no-cache-dir ...
    ```

---

### 6. Common Pitfalls and Fixes

- **Docker**:
  - **Image Pull Fails**:
    - Fix: Check Docker Hub:
      ```bash
      docker pull nginx:latest
      ```
  - **Port Conflict**:
    - Fix: Free port or remap:
      ```bash
      docker run -p 8081:80 ...
      ```
  - **Permission Denied**:
    - Fix: Add user to docker group:
      ```bash
      sudo usermod -aG docker $USER
      ```
- **Docker Compose**:
  - **Service Won’t Start**:
    - Fix: Check logs:
      ```bash
      docker compose logs db
      ```
  - **Network Issues**:
    - Fix: Ensure services on same network:
      ```yaml
      networks:
        - my-net
      ```
  - **Volume Not Persisting**:
    - Fix: Use named volume:
      ```yaml
      volumes:
        db-data:
      ```

#### Security Fixes
- **Exposed Ports**:
  ```bash
  ufw deny 8080
  docker run -p 127.0.0.1:8080:80 ...
  ```
- **Vulnerable Images**:
  ```bash
  docker scan python:3.12
  docker pull python:3.12-slim  # Use minimal
  ```
- **Root Access**:
  ```dockerfile
  USER appuser
  ```

---

### 7. Hands-On Challenge
To master Docker and Docker Compose:
1. **Single Container**:
   - Run a Python container, execute `print("Hello, Docker!")`.
   - Map port 5000, access a Flask app.
2. **Custom Image**:
   - Write a Dockerfile for a Flask app (`/hello` → “Hi!”).
   - Build and run it.
3. **Docker Compose**:
   - Create a `docker-compose.yml` with:
     - Nginx (port 8080).
     - Flask app (port 5000).
     - Redis (internal).
   - Ensure Flask increments a Redis counter per visit.
4. **Security**:
   - Run Flask as non-root.
   - Log requests to `app.log`.
5. Share code/output, and I’ll review!

**Starter Code**:
```dockerfile
# Dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY app.py .
CMD ["python", "app.py"]
```
```python
# app.py
print("Hello, Docker!")
```
```yaml
# docker-compose.yml
version: "3.9"
services:
  app:
    build: .
    # Add more
```

---

### 8. Advanced Tips

- **Multi-Stage Builds** (smaller images):
  ```dockerfile
  FROM python:3.12 AS builder
  WORKDIR /app
  COPY requirements.txt .
  RUN pip install --user -r requirements.txt

  FROM python:3.12-slim
  WORKDIR /app
  COPY --from=builder /root/.local /root/.local
  COPY app.py .
  ENV PATH=/root/.local/bin:$PATH
  CMD ["python", "app.py"]
  ```
- **Healthchecks**:
  ```yaml
  app:
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000"]
      interval: 30s
  ```
- **Logging**:
  ```yaml
  app:
    logging:
      driver: json-file
      options:
        max-size: "10m"
  ```
  ```python
  with open("app.log", "a") as f:
      f.write("Request received\n")
  ```
- **Swarm Mode** (scaling):
  ```bash
  docker swarm init
  docker stack deploy -c docker-compose.yml myapp
  ```
- **Security**:
  - Use Distroless images:
    ```dockerfile
    FROM gcr.io/distroless/python3
    ```
  - Audit containers:
    ```bash
    docker inspect my-flask-app
    ```


---
