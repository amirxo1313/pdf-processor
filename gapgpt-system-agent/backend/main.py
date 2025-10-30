"""
GapGPT System Agent - Main FastAPI Application
Secure AI agent with system-wide access and multiple model support
"""
from fastapi import FastAPI, HTTPException, Body
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional
import os
from dotenv import load_dotenv

from agent_manager import run_agent
from system_tools.exec_tools import safe_run
from system_tools.docker_tools import (
    list_containers,
    inspect_container,
    container_logs,
    start_container,
    stop_container
)
from system_tools.file_tools import read_file, write_file, list_directory, get_file_info
from system_tools.net_tools import check_port, ping_host, get_local_ip

# Load environment variables
load_dotenv()

# Constants
APP_NAME = "GapGPT System Agent"
APP_VERSION = "1.0.0"

# Initialize FastAPI app
app = FastAPI(
    title=APP_NAME,
    description="Full-access AI system automation agent with secure API key management",
    version=APP_VERSION
)


# Request/Response Models
class AskRequest(BaseModel):
    prompt: str
    model: Optional[str] = "auto"


class SystemRunRequest(BaseModel):
    cmd: str


class FileReadRequest(BaseModel):
    file_path: str


class FileWriteRequest(BaseModel):
    file_path: str
    content: str


class DirListRequest(BaseModel):
    directory_path: str


class ContainerRequest(BaseModel):
    container_id: str


class NetworkCheckRequest(BaseModel):
    host: str
    port: int


# === API Endpoints ===

@app.get("/")
async def root():
    """Root endpoint - Status check"""
    return {
        "status": "OK",
        "agent": APP_NAME,
        "security": "Tokens kept server-side only",
        "version": APP_VERSION,
        "web_gui": "Visit /gui for web interface"
    }

@app.get("/gui", response_class=HTMLResponse)
async def web_gui():
    """Serve the web GUI"""
    html_content = """
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🧠 GapGPT System Agent</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
            direction: rtl;
        }
        .container {
            max-width: 900px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        .header h1 { font-size: 28px; margin-bottom: 10px; }
        .header p { opacity: 0.9; font-size: 14px; }
        .status-bar {
            background: #f8f9fa;
            padding: 15px 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid #e0e0e0;
        }
        .status-dot {
            width: 10px;
            height: 10px;
            border-radius: 50%;
            background: #28a745;
            animation: pulse 2s infinite;
        }
        @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
        .chat-area {
            height: 400px;
            overflow-y: auto;
            padding: 20px;
            background: #f8f9fa;
        }
        .message {
            margin-bottom: 15px;
            animation: slideIn 0.3s ease;
        }
        @keyframes slideIn {
            from { opacity: 0; transform: translateY(-10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .message.user { text-align: right; }
        .message.assistant { text-align: left; }
        .message-bubble {
            display: inline-block;
            max-width: 70%;
            padding: 12px 16px;
            border-radius: 18px;
            word-wrap: break-word;
        }
        .message.user .message-bubble {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .message.assistant .message-bubble {
            background: white;
            border: 1px solid #e0e0e0;
            color: #333;
        }
        .input-area {
            padding: 20px;
            background: white;
            border-top: 1px solid #e0e0e0;
        }
        .input-container {
            display: flex;
            gap: 10px;
        }
        input[type="text"] {
            flex: 1;
            padding: 15px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            font-size: 16px;
            outline: none;
        }
        input[type="text"]:focus { border-color: #667eea; }
        button {
            padding: 15px 30px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
        }
        button:hover { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4); }
        button:disabled { opacity: 0.6; cursor: not-allowed; }
        .model-selector { margin-bottom: 10px; }
        .model-selector label { font-size: 14px; color: #666; margin-left: 10px; }
        select { padding: 8px 15px; border: 2px solid #e0e0e0; border-radius: 8px; font-size: 14px; }
        .quick-actions {
            display: flex;
            gap: 10px;
            padding: 10px;
            flex-wrap: wrap;
        }
        .quick-btn {
            padding: 8px 15px;
            background: #f0f0f0;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 12px;
        }
        .quick-btn:hover { background: #e0e0e0; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧠 GapGPT System Agent</h1>
            <p>دستیار هوشمند با دسترسی کامل به سیستم</p>
        </div>

        <div class="status-bar">
            <div class="status" style="display: flex; align-items: center; gap: 8px;">
                <div class="status-dot"></div>
                <span>متصل</span>
            </div>
            <div style="font-size: 12px; color: #666;">Port: 8000</div>
        </div>

        <div class="chat-area" id="chatArea">
            <div class="message assistant">
                <div class="message-bubble">
                    سلام! من GapGPT System Agent هستم 🤖<br>
                    <strong>من یک Agent کامل هستم و می‌تونم دستورات رو مستقیماً اجرا کنم!</strong><br><br>
                    <strong>💡 نحوه استفاده:</strong><br>
                    • برای دستورات: فقط بنویس "ls" یا "docker ps" یا هر دستور دیگه<br>
                    • برای سوالات: بنویس "Docker چیست؟" یا "چطور..."<br><br>
                    <strong>مثال دستورات:</strong> ls, df -h, docker ps, uname -a
                </div>
            </div>
        </div>

        <div class="quick-actions">
            <button class="quick-btn" onclick="sendQuickMessage('docker ps')">🐳 Docker Containers</button>
            <button class="quick-btn" onclick="sendQuickMessage('df -h')">💾 فضای دیسک</button>
            <button class="quick-btn" onclick="sendQuickMessage('uname -a')">💻 وضعیت سیستم</button>
            <button class="quick-btn" onclick="sendQuickMessage('ps aux | head -10')">📊 فرآیندها</button>
            <button class="quick-btn" onclick="sendQuickMessage('Docker چیست؟')">❓ سوال از AI</button>
        </div>

        <div class="input-area">
            <div class="model-selector">
                <label for="modelSelect">مدل:</label>
                <select id="modelSelect">
                    <option value="auto">🤖 خودکار (توصیه می‌شود)</option>
                    <option value="gpt-4o">GPT-4o</option>
                    <option value="gpt-5">GPT-5</option>
                    <option value="claude-opus-4">Claude Opus 4</option>
                    <option value="gemini-2.5-pro">Gemini 2.5 Pro</option>
                </select>
            </div>

            <div class="input-container">
                <input type="text" id="userInput" placeholder="پیام خود را بنویسید..." onkeypress="handleKeyPress(event)">
                <button onclick="sendMessage()">📤 ارسال</button>
            </div>
        </div>
    </div>

    <script>
        const chatArea = document.getElementById('chatArea');
        const userInput = document.getElementById('userInput');
        const sendButton = document.querySelector('button[onclick="sendMessage()"]');

        function handleKeyPress(event) { if (event.key === 'Enter') sendMessage(); }

        function sendQuickMessage(message) { userInput.value = message; sendMessage(); }

        async function sendMessage() {
            const message = userInput.value.trim();
            const model = document.getElementById('modelSelect').value;
            if (!message) return;
            userInput.value = '';
            addMessage('user', message);
            sendButton.disabled = true;

            try {
                // چک کردن اینکه آیا دستور سیستم هست یا سوال
                const isSystemCommand = isLikelyCommand(message);

                let response;
                if (isSystemCommand) {
                    // اجرای مستقیم دستور
                    response = await fetch('/system/run', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({cmd: message})
                    });
                    const data = await response.json();
                    const output = data.output || data.error || 'بدون خروجی';
                    addMessage('assistant', `📋 خروجی دستور:\n${output}`);
                } else {
                    // سوال از AI
                    response = await fetch('/ask', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({prompt: message, model: model})
                    });
                    const data = await response.json();

                    if (data.result && data.result.choices && data.result.choices[0]) {
                        addMessage('assistant', data.result.choices[0].message.content);
                    } else {
                        addMessage('assistant', JSON.stringify(data, null, 2));
                    }
                }
            } catch (error) {
                addMessage('assistant', `❌ خطا: ${error.message}`);
            } finally {
                sendButton.disabled = false;
                userInput.focus();
            }
        }

        function isLikelyCommand(message) {
            const cmd = message.toLowerCase().trim();

            // اگر با "اجرا کن" یا "exec" شروع بشه
            if (cmd.startsWith('اجرا کن:') || cmd.startsWith('exec:')) {
                return true;
            }

            // دستورات سیستم رایج
            const systemCommands = [
                'ls', 'pwd', 'cd', 'mkdir', 'rm', 'cp', 'mv', 'cat', 'head', 'tail',
                'grep', 'find', 'ps', 'top', 'kill', 'df', 'du', 'free', 'uptime',
                'docker', 'git', 'npm', 'pip', 'python', 'node', 'curl', 'wget'
            ];

            // چک کردن اینکه یک دستور لینوکس ساده هست یا نه
            const firstWord = cmd.split(' ')[0].replace(/[^a-z]/g, '');
            if (systemCommands.some(c => firstWord.includes(c))) {
                return true;
            }

            // اگر فقط یک کلمه یا کمی توکن باشه (احتمالاً دستور هست)
            const wordCount = cmd.split(/\\s+/).length;
            if (wordCount <= 3 && !cmd.includes('؟') && !cmd.includes('?') && !cmd.includes('چیست') && !cmd.includes('چطور')) {
                return true;
            }

            return false;
        }

        function addMessage(type, content) {
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${type}`;
            messageDiv.innerHTML = `<div class="message-bubble">${content.replace(/\\n/g, '<br>')}</div>`;
            chatArea.appendChild(messageDiv);
            chatArea.scrollTop = chatArea.scrollHeight;
        }
    </script>
</body>
</html>
    """
    return html_content


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "tokens_configured": bool(os.getenv("OPENAI_API_KEY"))
    }


@app.post("/ask")
async def ask_endpoint(request: AskRequest):
    """
    Ask the AI agent a question

    Model auto-selection logic:
    - docker/system tasks → gpt-5
    - legal/analysis → claude-opus-4
    - image/vision → gemini-2.5-pro
    - default → gpt-4o
    """
    try:
        result = run_agent(request.prompt, request.model)
        return {
            "model": request.model,
            "result": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/system/run")
async def system_run_endpoint(request: SystemRunRequest):
    """Execute a system command safely"""
    result = safe_run(request.cmd)
    return {
        "command": request.cmd,
        "output": result["output"],
        "error": result["error"],
        "exit_code": result["exit_code"]
    }


# === Docker Endpoints ===

@app.post("/docker/containers")
async def docker_list_containers(all_containers: bool = False):
    """List Docker containers"""
    result = list_containers(all_containers)
    return result


@app.post("/docker/inspect")
async def docker_inspect_endpoint(request: ContainerRequest):
    """Inspect a Docker container"""
    result = inspect_container(request.container_id)
    return result


@app.post("/docker/logs")
async def docker_logs_endpoint(request: ContainerRequest, tail: int = 100):
    """Get container logs"""
    result = container_logs(request.container_id, tail)
    return result


@app.post("/docker/start")
async def docker_start_endpoint(request: ContainerRequest):
    """Start a Docker container"""
    result = start_container(request.container_id)
    return result


@app.post("/docker/stop")
async def docker_stop_endpoint(request: ContainerRequest):
    """Stop a Docker container"""
    result = stop_container(request.container_id)
    return result


# === File System Endpoints ===

@app.post("/file/read")
async def file_read_endpoint(request: FileReadRequest):
    """Read file contents"""
    result = read_file(request.file_path)
    return result


@app.post("/file/write")
async def file_write_endpoint(request: FileWriteRequest):
    """Write content to file"""
    result = write_file(request.file_path, request.content)
    return result


@app.post("/file/info")
async def file_info_endpoint(request: FileReadRequest):
    """Get file metadata"""
    result = get_file_info(request.file_path)
    return result


@app.post("/file/list")
async def file_list_endpoint(request: DirListRequest):
    """List directory contents"""
    result = list_directory(request.directory_path)
    return result


# === Network Endpoints ===

@app.post("/net/check")
async def network_check_endpoint(request: NetworkCheckRequest):
    """Check if a port is open"""
    result = check_port(request.host, request.port)
    return result


@app.post("/net/ping")
async def network_ping_endpoint(request: ContainerRequest, count: int = 4):
    """Ping a host"""
    result = ping_host(request.container_id, count)
    return result


@app.get("/net/local-ip")
async def network_local_ip():
    """Get local IP address"""
    result = get_local_ip()
    return result


# === About Endpoint ===
@app.get("/about")
async def about():
    """Get information about the agent"""
    return {
        "name": APP_NAME,
        "description": "Full-access AI system automation with secure token management",
        "features": [
            "Multiple AI model support (GPT-4o, GPT-5, Claude Opus 4, Gemini 2.5 Pro)",
            "Intelligent auto model selection",
            "System command execution",
            "Docker container management",
            "File system operations",
            "Network diagnostics",
            "Secure API key handling"
        ],
        "base_url_options": [
            "https://api.gapgpt.app/v1",
            "https://api.gapapi.com/v1"
        ],
        "security": {
            "tokens": "Server-side only",
            "env_file": ".env",
            "warning": "Never expose API keys in client code or browser environments"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

