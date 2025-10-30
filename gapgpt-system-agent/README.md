# GapGPT System Agent — Secure Edition

🧠 A full-featured AI system automation agent with secure API key management and intelligent model selection.

## 🔐 Security Notice

**⚠️ IMPORTANT**: Never share your API tokens publicly or expose them in client code.

- Tokens are stored **server-side only** in the `.env` file
- Never commit `.env` to version control
- Always use environment variables for API keys

### Official GapGPT API Endpoints

Choose one of these base URLs:
- `https://api.gapgpt.app/v1`
- `https://api.gapapi.com/v1`

## 🎯 Features

- **Multiple AI Models**: GPT-4o, GPT-5, Claude Opus 4, Gemini 2.5 Pro
- **Intelligent Auto-Selection**: Automatically chooses the best model for each task
- **System Command Execution**: Safe command execution with timeouts
- **Docker Management**: Full container orchestration
- **File System Operations**: Read, write, list, and inspect files
- **Network Diagnostics**: Port checking, pinging, and IP detection
- **Secure Token Management**: All API keys handled server-side

## 📁 Project Structure

```
gapgpt-system-agent/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── agent_manager.py      # Model selection logic
│   ├── models.py             # GapGPT API integration
│   ├── requirements.txt      # Python dependencies
│   └── system_tools/
│       ├── exec_tools.py     # Command execution
│       ├── docker_tools.py   # Docker operations
│       ├── file_tools.py     # File operations
│       └── net_tools.py      # Network utilities
├── Dockerfile
├── docker-compose.yml
├── .env                     # Environment variables (secure)
└── README.md
```

## 🚀 Quick Start

### 1. Configure Environment

Edit `.env` file with your API tokens:

```bash
BASE_URL=https://api.gapgpt.app/v1
OPENAI_API_KEY=sk-your-key-here
CLAUDE_API_KEY=sk-your-key-here
GEMINI_API_KEY=sk-your-key-here
```

### 2. Build and Run

```bash
# Build and start the container
docker compose up --build -d

# View logs
docker compose logs -f

# Stop the container
docker compose down
```

### 3. Test the API

```bash
# Health check
curl http://localhost:8000/health

# Ask the agent
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Show all Docker containers", "model": "auto"}'

# Execute system command
curl -X POST http://localhost:8000/system/run \
  -H "Content-Type: application/json" \
  -d '{"cmd": "uname -a"}'

# List files
curl -X POST http://localhost:8000/file/list \
  -H "Content-Type: application/json" \
  -d '{"directory_path": "/hostfs/var/log"}'
```

## 🧠 Model Selection Logic

The agent automatically selects the best model based on your prompt:

| Task Type | Model | Use Case |
|-----------|-------|----------|
| Docker/System | **GPT-5** | Container management, system commands |
| Legal/Analysis | **Claude Opus 4** | Document review, formal analysis |
| Image/Vision | **Gemini 2.5 Pro** | Image processing, visual tasks |
| General | **GPT-4o** | Default balanced model |

You can also specify a model manually:

```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Explain quantum computing", "model": "gpt-4o"}'
```

## 📊 API Endpoints

### AI Agent

- `POST /ask` - Ask the AI agent (auto-selects best model)
- `GET /about` - Get agent information

### System Commands

- `POST /system/run` - Execute a system command

### Docker Operations

- `POST /docker/containers` - List containers
- `POST /docker/inspect` - Inspect a container
- `POST /docker/logs` - Get container logs
- `POST /docker/start` - Start a container
- `POST /docker/stop` - Stop a container

### File System

- `POST /file/read` - Read file contents
- `POST /file/write` - Write to file
- `POST /file/info` - Get file metadata
- `POST /file/list` - List directory

### Network

- `POST /net/check` - Check if port is open
- `POST /net/ping` - Ping a host
- `GET /net/local-ip` - Get local IP

### Health

- `GET /` - Status check
- `GET /health` - Health check

## 🔑 API Tokens (Current Balance)

| Token | Balance | Status |
|-------|---------|--------|
| Main Key | 7.186 USDT | ✅ Active |
| Gift Key | 0.5 USDT | ✅ Active |

## 🛡️ Security Best Practices

1. **Never expose tokens in**: 
   - Frontend code
   - Browser JavaScript
   - Public repositories
   - Client-side applications

2. **Always use**:
   - `.env` file for configuration
   - Environment variables at runtime
   - Server-side token handling
   - Secure API endpoints

3. **File permissions**:
   ```bash
   chmod 600 .env  # Secure .env file
   ```

## 🐳 Docker Configuration

The container runs with:
- **Privileged mode**: Full system access
- **Host network**: Direct network access
- **Volume mount**: Root filesystem mounted at `/hostfs`
- **Docker socket**: Access to Docker daemon

## 📝 Example Usage

### 1. Ask the AI

```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "How can I optimize Docker container performance?",
    "model": "auto"
  }'
```

### 2. Execute Commands

```bash
curl -X POST http://localhost:8000/system/run \
  -H "Content-Type: application/json" \
  -d '{"cmd": "df -h"}'
```

### 3. Docker Operations

```bash
# List containers
curl -X POST http://localhost:8000/docker/containers

# Get logs
curl -X POST http://localhost:8000/docker/logs \
  -H "Content-Type: application/json" \
  -d '{"container_id": "my-container"}'
```

## 🚧 Next Phase

- [ ] Add `/event/watch` endpoint using Watchdog for real-time filesystem monitoring
- [ ] Implement task scheduling and automation
- [ ] Add webhook support for external integrations
- [ ] Create web dashboard for monitoring

## 📄 License

Private project - All rights reserved

## 🤝 Support

For issues or questions, contact the project maintainer.

---

**⚠️ Remember**: Keep your API tokens secure and never expose them publicly!
