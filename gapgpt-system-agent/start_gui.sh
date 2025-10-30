#!/bin/bash
# GapGPT Agent - Quick Start GUI Script
echo "🧠 GapGPT System Agent - Starting..."
echo ""
echo "✅ Agent is running on: http://localhost:8000"
echo "🌐 Opening web GUI in 3 seconds..."
echo ""
sleep 3

# Try to open in browser
if command -v xdg-open &> /dev/null; then
    xdg-open http://localhost:8000/gui
elif command -v gnome-open &> /dev/null; then
    gnome-open http://localhost:8000/gui
elif command -v open &> /dev/null; then
    open http://localhost:8000/gui
else
    echo "⚠️  Cannot auto-open browser. Please visit manually:"
    echo "   http://localhost:8000/gui"
fi

echo ""
echo "📝 یا می‌تونی مستقیماً بری این آدرس رو باز کنی:"
echo "   👉 http://localhost:8000/gui"
echo ""
echo "💡 برای توقف: Ctrl+C"


