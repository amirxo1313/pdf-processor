#!/usr/bin/env python3
"""
GapGPT System Agent - API Test Script
Test all endpoints of the agent
"""
import requests
import json
from typing import Dict

BASE_URL = "http://localhost:8000"


def test_endpoint(method: str, endpoint: str, data: Dict = None) -> None:
    """Test an API endpoint"""
    url = f"{BASE_URL}{endpoint}"

    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        else:
            print(f"❌ Unknown method: {method}")
            return

        print(f"\n{'='*60}")
        print(f"📍 {method} {endpoint}")
        print(f"{'='*60}")

        if response.status_code == 200:
            print("✅ Status: OK")
            result = response.json()
            print(f"📊 Response:\n{json.dumps(result, indent=2, ensure_ascii=False)}")
        else:
            print(f"❌ Status: {response.status_code}")
            print(f"Error: {response.text}")

    except requests.exceptions.ConnectionError:
        print(f"❌ Connection Error: Is the server running on {BASE_URL}?")
    except Exception as e:
        print(f"❌ Error: {str(e)}")


def main():
    """Run all API tests"""
    print("🚀 GapGPT System Agent - API Test Suite")
    print("=" * 60)

    # Health Check
    test_endpoint("GET", "/health")

    # About
    test_endpoint("GET", "/about")

    # Ask AI (auto model selection)
    test_endpoint("POST", "/ask", {
        "prompt": "What is Docker and how does it work?",
        "model": "auto"
    })

    # System command
    test_endpoint("POST", "/system/run", {
        "cmd": "uname -a"
    })

    # Docker containers
    test_endpoint("POST", "/docker/containers")

    # Network local IP
    test_endpoint("GET", "/net/local-ip")

    # File list (try /tmp as it's usually accessible)
    test_endpoint("POST", "/file/list", {
        "directory_path": "/tmp"
    })

    print("\n" + "=" * 60)
    print("✨ Test suite completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()


