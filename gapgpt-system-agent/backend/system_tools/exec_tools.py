"""
Execution Tools
Safe command execution with timeout and output limiting
"""
import subprocess
from typing import Dict


def safe_run(cmd: str, timeout: int = 30, max_output: int = 4000) -> Dict[str, str]:
    """
    Safely execute shell commands with timeout and output limiting

    Args:
        cmd: Command to execute
        timeout: Timeout in seconds
        max_output: Maximum output length to return

    Returns:
        Dict with 'output' and 'error' fields
    """
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout
        )

        output = result.stdout[:max_output] if result.stdout else ""
        error = result.stderr[:max_output] if result.stderr else ""

        return {
            "output": output,
            "error": error,
            "exit_code": result.returncode
        }
    except subprocess.TimeoutExpired:
        return {
            "output": "",
            "error": f"Command timed out after {timeout} seconds",
            "exit_code": -1
        }
    except Exception as e:
        return {
            "output": "",
            "error": str(e),
            "exit_code": -1
        }


