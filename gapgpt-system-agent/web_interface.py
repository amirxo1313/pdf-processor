#!/usr/bin/env python3
"""
GapGPT System Agent - Web GUI Interface
یک رابط گرافیکی ساده برای ارتباط با Agent
"""
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi import FastAPI, Request
from pathlib import Path
import uvicorn

app = FastAPI(title="GapGPT Agent GUI")

# Mount static files
static_dir = Path(__file__).parent / "static"
static_dir.mkdir(exist_ok=True)

@app.get("/", response_class=HTMLResponse)
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
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

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

        .header h1 {
            font-size: 28px;
            margin-bottom: 10px;
        }

        .header p {
            opacity: 0.9;
            font-size: 14px;
        }

        .status-bar {
            background: #f8f9fa;
            padding: 15px 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid #e0e0e0;
        }

        .status {
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .status-dot {
            width: 10px;
            height: 10px;
            border-radius: 50%;
            background: #28a745;
            animation: pulse 2s infinite;
        }

        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }

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
            from {
                opacity: 0;
                transform: translateY(-10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .message.user {
            text-align: right;
        }

        .message.assistant {
            text-align: left;
        }

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
            margin-right: auto;
            margin-left: auto;
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
            transition: all 0.3s;
        }

        input[type="text"]:focus {
            border-color: #667eea;
        }

        button {
            padding: 15px 30px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s;
        }

        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }

        button:active {
            transform: translateY(0);
        }

        button:disabled {
            opacity: 0.6;
            cursor: not-allowed;
        }

        .model-selector {
            margin-bottom: 10px;
        }

        .model-selector label {
            font-size: 14px;
            color: #666;
            margin-left: 10px;
        }

        select {
            padding: 8px 15px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 14px;
            outline: none;
            cursor: pointer;
        }

        .loading {
            display: none;
            text-align: center;
            color: #666;
            font-style: italic;
        }

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
            transition: all 0.3s;
        }

        .quick-btn:hover {
            background: #e0e0e0;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧠 GapGPT System Agent</h1>
            <p>دستیار هوشمند با دسترسی کامل به سیستم</p>
        </div>

        <div class="status-bar">
            <div class="status">
                <div class="status-dot"></div>
                <span>متصل</span>
            </div>
            <div style="font-size: 12px; color: #666;">Port: 8000</div>
        </div>

        <div class="chat-area" id="chatArea">
            <div class="message assistant">
                <div class="message-bubble">
                    سلام! من GapGPT System Agent هستم 🤖<br>
                    می‌تونم بهت کمک کنم تا دستورات سیستم رو اجرا کنی، از Docker استفاده کنی، یا سوال بپرسی!<br><br>
                    مثال: "نشان بده Docker containers"
                </div>
            </div>
        </div>

        <div class="quick-actions">
            <button class="quick-btn" onclick="sendQuickMessage('docker ps')">🐳 لیست Docker</button>
            <button class="quick-btn" onclick="sendQuickMessage('نشان بده وضعیت سیستم')">💻 وضعیت سیستم</button>
            <button class="quick-btn" onclick="sendQuickMessage('فضای دیسک چقدر آزاده؟')">💾 فضای دیسک</button>
            <button class="quick-btn" onclick="sendQuickMessage('Docker چیست؟')">❓ درباره Docker</button>
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
                <input type="text" id="userInput" placeholder="پیام خود را بنویسید..."
                       onkeypress="handleKeyPress(event)">
                <button onclick="sendMessage()">📤 ارسال</button>
            </div>

            <div class="loading" id="loading">در حال پردازش...</div>
        </div>
    </div>

    <script>
        const chatArea = document.getElementById('chatArea');
        const userInput = document.getElementById('userInput');
        const loading = document.getElementById('loading');
        const sendButton = document.querySelector('button[onclick="sendMessage()"]');

        function handleKeyPress(event) {
            if (event.key === 'Enter') {
                sendMessage();
            }
        }

        function sendQuickMessage(message) {
            userInput.value = message;
            sendMessage();
        }

        async function sendMessage() {
            const message = userInput.value.trim();
            const model = document.getElementById('modelSelect').value;

            if (!message) return;

            // Clear input
            userInput.value = '';

            // Add user message
            addMessage('user', message);

            // Show loading
            loading.style.display = 'block';
            sendButton.disabled = true;

            try {
                // Check if it's a system command
                const isSystemCommand = message.toLowerCase().startsWith('اجرا کن:') ||
                                        message.toLowerCase().startsWith('exec:');

                let response;
                if (isSystemCommand) {
                    const cmd = message.replace(/^(اجرا کن:|exec:)\s*/i, '');
                    response = await fetch('/system/run', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({cmd: cmd})
                    });
                } else {
                    // AI Chat
                    response = await fetch('/ask', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({prompt: message, model: model})
                    });
                }

                const data = await response.json();

                let responseText;
                if (isSystemCommand) {
                    responseText = `📋 خروجی دستور:\n${data.output || data.error || 'بدون خروجی'}`;
                } else {
                    // Extract AI response
                    if (data.result && data.result.choices && data.result.choices[0]) {
                        responseText = data.result.choices[0].message.content;
                    } else {
                        responseText = JSON.stringify(data, null, 2);
                    }
                }

                addMessage('assistant', responseText);

            } catch (error) {
                addMessage('assistant', `❌ خطا: ${error.message}`);
            } finally {
                loading.style.display = 'none';
                sendButton.disabled = false;
                userInput.focus();
            }
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


if __name__ == "__main__":
    print("🚀 Starting GapGPT Agent Web GUI on http://localhost:8001")
    print("📱 Open your browser and visit: http://localhost:8001")
    uvicorn.run(app, host="0.0.0.0", port=8001)


