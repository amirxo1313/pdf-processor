"""
Docker Tools
Container management and orchestration utilities
"""
import subprocess
from typing import Dict, List


def list_containers(all_containers: bool = False) -> Dict:
    """List Docker containers"""
    flag = "-a" if all_containers else ""
    cmd = f"docker ps {flag}"

    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return {
        "output": result.stdout,
        "error": result.stderr,
        "exit_code": result.returncode
    }


def inspect_container(container_id: str) -> Dict:
    """Inspect a Docker container"""
    cmd = f"docker inspect {container_id}"

    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return {
        "output": result.stdout,
        "error": result.stderr,
        "exit_code": result.returncode
    }


def container_logs(container_id: str, tail: int = 100) -> Dict:
    """Get container logs"""
    cmd = f"docker logs --tail {tail} {container_id}"

    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return {
        "output": result.stdout,
        "error": result.stderr,
        "exit_code": result.returncode
    }


def start_container(container_id: str) -> Dict:
    """Start a Docker container"""
    cmd = f"docker start {container_id}"

    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return {
        "output": result.stdout,
        "error": result.stderr,
        "exit_code": result.returncode
    }


def stop_container(container_id: str) -> Dict:
    """Stop a Docker container"""
    cmd = f"docker stop {container_id}"

    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return {
        "output": result.stdout,
        "error": result.stderr,
        "exit_code": result.returncode
    }


