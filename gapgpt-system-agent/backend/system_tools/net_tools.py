"""
Network Tools
Network diagnostics and management utilities
"""
import subprocess
import socket
from typing import Dict


def check_port(host: str, port: int) -> Dict:
    """
    Check if a port is open

    Args:
        host: Hostname or IP
        port: Port number

    Returns:
        Dict with 'open' and 'error' fields
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((host, port))
        sock.close()

        return {
            "open": result == 0,
            "error": None
        }
    except Exception as e:
        return {
            "open": False,
            "error": str(e)
        }


def ping_host(host: str, count: int = 4) -> Dict:
    """
    Ping a host

    Args:
        host: Hostname or IP
        count: Number of ping packets

    Returns:
        Dict with 'output' and 'error' fields
    """
    cmd = f"ping -c {count} {host}"

    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return {
        "output": result.stdout,
        "error": result.stderr,
        "exit_code": result.returncode
    }


def get_local_ip() -> Dict:
    """Get local IP address"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()

        return {
            "ip": ip,
            "error": None
        }
    except Exception as e:
        return {
            "ip": None,
            "error": str(e)
        }


