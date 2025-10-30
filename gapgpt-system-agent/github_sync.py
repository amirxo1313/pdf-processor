#!/usr/bin/env python3
"""
Safe GitHub synchronization script for background agent
"""
import os
import subprocess
import requests
from dotenv import load_dotenv

load_dotenv()

def safe_git_fetch():
    """Safely fetch from GitHub"""
    try:
        result = subprocess.run(
            ["git", "fetch", "origin"],
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def check_github_status():
    """Check GitHub repository status"""
    try:
        token = os.getenv("GITHUB_TOKEN")
        if not token:
            return False, "No GitHub token configured"
        
        headers = {"Authorization": f"token {token}"}
        response = requests.get(
            "https://api.github.com/user",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            return True, f"Connected as {response.json()['login']}"
        else:
            return False, f"GitHub API error: {response.status_code}"
    except Exception as e:
        return False, str(e)

if __name__ == "__main__":
    print("🧠 GapGPT GitHub Sync Agent")
    print("=" * 40)
    
    # Check GitHub connection
    github_ok, github_msg = check_github_status()
    print(f"GitHub Status: {'✅' if github_ok else '❌'} {github_msg}")
    
    # Perform safe git fetch
    fetch_ok, fetch_out, fetch_err = safe_git_fetch()
    print(f"Git Fetch: {'✅' if fetch_ok else '❌'}")
    if fetch_out:
        print(f"Output: {fetch_out.strip()}")
    if fetch_err:
        print(f"Error: {fetch_err.strip()}")
