#!/usr/bin/env python3
"""
Quick test for GapGPT Agent
"""
from vscode_agent import GapGPTAgent

agent = GapGPTAgent()

# Test 1: Direct command
print("🧪 Test 1: Direct Command (ls)")
result = agent.process_task("ls -la")
print(result)
print()

# Test 2: System info
print("🧪 Test 2: System Info")
result = agent.process_task("uname -a")
print(result)
print()

# Test 3: Docker
print("🧪 Test 3: Docker Containers")
result = agent.process_task("docker ps")
print(result)


