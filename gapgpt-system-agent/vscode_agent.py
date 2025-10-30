#!/usr/bin/env python3
"""
VSCode GapGPT Agent - A real system agent that can execute tasks
Uses GapGPT API for AI-powered task execution
"""
import os
import sys
import json
import subprocess
import requests
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment
load_dotenv()

class GapGPTAgent:
    """Real GapGPT System Agent"""

    def __init__(self):
        self.base_url = os.getenv("BASE_URL", "https://api.gapgpt.app/v1")
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.claude_key = os.getenv("CLAUDE_API_KEY")

    def execute_command(self, command: str) -> Dict[str, Any]:
        """
        Execute a system command directly

        Args:
            command: Command to execute

        Returns:
            Dict with output, error, and exit_code
        """
        try:
            print(f"🔧 Executing: {command}")

            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )

            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr,
                "exit_code": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "output": "",
                "error": "Command timed out",
                "exit_code": -1
            }
        except Exception as e:
            return {
                "success": False,
                "output": "",
                "error": str(e),
                "exit_code": -1
            }

    def ask_ai(self, prompt: str, model: str = "gpt-4o") -> str:
        """
        Ask AI using GapGPT API

        Args:
            prompt: User's prompt
            model: AI model to use

        Returns:
            AI response
        """
        try:
            print(f"🤖 Asking {model}...")

            headers = {
                "Authorization": f"Bearer {self.openai_key}",
                "Content-Type": "application/json"
            }

            data = {
                "model": model,
                "messages": [
                    {"role": "system", "content": "You are a helpful system assistant with full access to the system."},
                    {"role": "user", "content": prompt}
                ]
            }

            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=data,
                timeout=60
            )

            response.raise_for_status()
            result = response.json()

            if "choices" in result and len(result["choices"]) > 0:
                return result["choices"][0]["message"]["content"]
            else:
                return f"Unexpected response: {json.dumps(result, indent=2)}"

        except Exception as e:
            return f"❌ Error: {str(e)}"

    def process_task(self, user_input: str) -> str:
        """
        Process user input and determine action

        Args:
            user_input: User's request

        Returns:
            Response
        """
        user_input_lower = user_input.lower()

        # Check if it's a direct command
        is_command = (
            len(user_input.split()) <= 5 and  # Short inputs
            not any(q in user_input for q in ['؟', '?', 'چیست', 'چطور', 'چرا', 'کجا']) and  # No questions
            not user_input_lower.startswith('explain') and
            not user_input_lower.startswith('what is') and
            not user_input_lower.startswith('how to')
        )

        if is_command:
            # Execute directly
            print(f"⚡ Detected as direct command, executing...")
            result = self.execute_command(user_input)

            if result["success"]:
                return f"✅ Executed successfully:\n{result['output']}"
            else:
                return f"❌ Error (code {result['exit_code']}):\n{result['error']}"

        else:
            # Ask AI and get intelligent response
            print(f"🤔 Detected as question, consulting AI...")
            ai_response = self.ask_ai(user_input)

            # Check if AI suggests executing a command
            if "run:" in ai_response or "execute:" in ai_response.lower():
                # Extract command if present
                lines = ai_response.split('\n')
                for line in lines:
                    if "run:" in line or "execute:" in line.lower():
                        cmd = line.split(":")[1].strip()
                        if cmd:
                            return self.process_task(cmd)  # Recursive execution

            return ai_response

    def run_interactive(self):
        """Run in interactive mode"""
        print("🧠 GapGPT System Agent - Ready")
        print("="*60)
        print("💡 Tips:")
        print("  - Direct commands: 'ls', 'docker ps', 'df -h'")
        print("  - Questions: 'What is Docker?', 'Show system info'")
        print("  - Type 'quit' or 'exit' to stop")
        print("="*60)
        print()

        while True:
            try:
                user_input = input("🤖 You: ").strip()

                if not user_input:
                    continue

                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("👋 Goodbye!")
                    break

                print("\n" + "─"*60)
                result = self.process_task(user_input)
                print(f"🤖 Agent: {result}")
                print("─"*60 + "\n")

            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}\n")


def main():
    """Main entry point"""
    agent = GapGPTAgent()

    # Check for command line arguments
    if len(sys.argv) > 1:
        # Execute single command
        result = agent.process_task(" ".join(sys.argv[1:]))
        print(result)
    else:
        # Run in interactive mode
        agent.run_interactive()


if __name__ == "__main__":
    main()


