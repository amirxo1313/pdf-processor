#!/usr/bin/env python3
"""
Test GapGPT Agent with various commands
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_command(cmd, description):
    """Test a system command"""
    print(f"\n{'='*60}")
    print(f"📋 Test: {description}")
    print(f"💻 Command: {cmd}")
    print(f"{'='*60}")

    try:
        response = requests.post(
            f"{BASE_URL}/system/run",
            json={"cmd": cmd},
            timeout=10
        )
        data = response.json()

        if data.get("exit_code") == 0:
            print(f"✅ Success!")
            print(f"📄 Output:\n{data.get('output', 'No output')[:500]}")
        else:
            print(f"⚠️  Exit code: {data.get('exit_code')}")
            print(f"📄 Output:\n{data.get('output', 'No output')}")
            if data.get("error"):
                print(f"❌ Error: {data.get('error')}")
    except Exception as e:
        print(f"❌ Exception: {e}")

def main():
    print("\n🤖 GapGPT Agent - System Command Tests")
    print("="*60)

    # Test basic commands
    test_command("uname -a", "System Information")
    test_command("df -h", "Disk Space")
    test_command("free -h", "Memory Usage")
    test_command("ls -la /app", "List Files")
    test_command("docker ps", "Docker Containers")
    test_command("ps aux | head -10", "Running Processes")

    print("\n" + "="*60)
    print("✅ All tests completed!")
    print("="*60)

if __name__ == "__main__":
    main()


