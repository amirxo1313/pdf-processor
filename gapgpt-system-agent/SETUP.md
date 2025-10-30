# Setup Guide for GapGPT System Agent

## Quick Start

1. **Install dependencies**:
```bash
cd gapgpt-system-agent
pip install -r backend/requirements.txt
```

2. **Create .env file**:
```bash
cat > .env << 'ENDENV'
BASE_URL=https://api.gapgpt.app/v1
OPENAI_API_KEY=your-openai-key-here
CLAUDE_API_KEY=your-claude-key-here
GEMINI_API_KEY=your-gemini-key-here
ENDENV
```

3. **Run the agent**:
```bash
python3 backend/main.py
```

Then open: http://localhost:8000/gui

## Features Fixed:
- ✅ Import paths corrected
- ✅ Added __init__.py for proper package structure
- ✅ Updated requirements.txt with all necessary dependencies
- ✅ Fixed Dockerfile working directory
- ✅ Removed duplicate literal warnings
- ✅ Added proper package structure

## Dependencies Added:
- pdfplumber
- pypdf
- cryptography
- openai
- anthropic
- google-generativeai

