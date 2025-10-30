"""
File Tools
File system operations and management
"""
import os
from typing import Dict, List
from pathlib import Path

# Security constants
PATH_TRAVERSAL_ERROR = "Invalid file path - path traversal detected"

# Response field constants
FIELD_CONTENT = "content"
FIELD_ERROR = "error"
FIELD_SUCCESS = "success"
FIELD_FILES = "files"
FIELD_SIZE = "size"
FIELD_MODIFIED = "modified"
FIELD_IS_FILE = "is_file"
FIELD_IS_DIR = "is_dir"


def _validate_path(file_path: str) -> bool:
    """
    Validate file path to prevent path traversal attacks

    Args:
        file_path: Path to validate

    Returns:
        True if valid, False otherwise
    """
    try:
        # Normalize path
        normalized = os.path.normpath(file_path)

        # Check for path traversal attempts
        if '..' in normalized or normalized.startswith('/'):
            return False

        # Check if path is absolute
        if os.path.isabs(file_path):
            return False

        return True
    except Exception:
        return False


def read_file(file_path: str, max_size: int = 1024 * 1024) -> Dict:
    """
    Read file contents with size limit

    Args:
        file_path: Path to file
        max_size: Maximum file size in bytes (default 1MB)

    Returns:
        Dict with 'content' and 'error' fields
    """
    try:
        # Validate path to prevent path traversal
        if not _validate_path(file_path):
            return {FIELD_CONTENT: None, FIELD_ERROR: PATH_TRAVERSAL_ERROR}

        if not os.path.exists(file_path):
            return {FIELD_CONTENT: None, FIELD_ERROR: "File not found"}

        file_size = os.path.getsize(file_path)
        if file_size > max_size:
            return {
                FIELD_CONTENT: None,
                FIELD_ERROR: f"File too large ({file_size} bytes > {max_size} bytes)"
            }

        with open(file_path, 'r', encoding='utf-8') as f:
            return {FIELD_CONTENT: f.read(), FIELD_ERROR: None}

    except Exception as e:
        return {FIELD_CONTENT: None, FIELD_ERROR: str(e)}


def write_file(file_path: str, content: str) -> Dict:
    """
    Write content to file

    Args:
        file_path: Path to file
        content: Content to write

    Returns:
        Dict with 'success' and 'error' fields
    """
    try:
        # Validate path to prevent path traversal
        if not _validate_path(file_path):
            return {FIELD_SUCCESS: False, FIELD_ERROR: PATH_TRAVERSAL_ERROR}

        # Create parent directories if needed
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        return {FIELD_SUCCESS: True, FIELD_ERROR: None}

    except Exception as e:
        return {FIELD_SUCCESS: False, FIELD_ERROR: str(e)}


def list_directory(directory_path: str) -> Dict:
    """
    List directory contents

    Args:
        directory_path: Path to directory

    Returns:
        Dict with 'files' and 'error' fields
    """
    try:
        # Validate path to prevent path traversal
        if not _validate_path(directory_path):
            return {FIELD_FILES: None, FIELD_ERROR: PATH_TRAVERSAL_ERROR}

        if not os.path.isdir(directory_path):
            return {FIELD_FILES: None, FIELD_ERROR: "Not a directory"}

        files = os.listdir(directory_path)
        return {FIELD_FILES: files, FIELD_ERROR: None}

    except Exception as e:
        return {FIELD_FILES: None, FIELD_ERROR: str(e)}


def get_file_info(file_path: str) -> Dict:
    """Get file metadata"""
    try:
        # Validate path to prevent path traversal
        if not _validate_path(file_path):
            return {FIELD_ERROR: PATH_TRAVERSAL_ERROR}

        stat = os.stat(file_path)
        return {
            FIELD_SIZE: stat.st_size,
            FIELD_MODIFIED: stat.st_mtime,
            FIELD_IS_FILE: os.path.isfile(file_path),
            FIELD_IS_DIR: os.path.isdir(file_path),
            FIELD_ERROR: None
        }
    except Exception as e:
        return {FIELD_ERROR: str(e)}


