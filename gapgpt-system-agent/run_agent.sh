#!/bin/bash
# Run GapGPT VSCode Agent

echo "🧠 Starting GapGPT System Agent..."
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found!"
    echo "   Please make sure you're in the gapgpt-system-agent directory"
    exit 1
fi

# Run the agent
python3 vscode_agent.py "$@"


