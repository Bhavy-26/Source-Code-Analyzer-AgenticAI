# This tool reads files in batches and handles non-text files, massive files, and missing paths gracefully.

from pathlib import Path
from typing import List
from langchain_core.tools import tool

# Block non-text/binary formats to prevent corrupted tokens
BINARY_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".gif", ".ico", ".svg",
    ".pdf", ".zip", ".tar", ".gz", ".exe", ".dll", ".mp4", ".mp3"
}

# Max character limit per file (approx 12,000 tokens) to protect LLM context
MAX_CHAR_LIMIT = 50_000 

def make_file_reader(base_dir: str):
    base = Path(base_dir).resolve()

    @tool
    def read_files(file_paths: List[str]) -> str:
        """Reads one or multiple files in a single turn using relative paths."""
        results = []

        for path_str in file_paths:
            try:
                clean_path = path_str.strip().lstrip("./").lstrip("/\\")
                target = (base / clean_path).resolve()

                # ERROR HANDLING 1: Path Traversal Attack Check
                try:
                    target.relative_to(base)
                except ValueError:
                    results.append(f"=== {path_str} ===\nError: Security Violation. Path escapes repository root.")
                    continue

                # ERROR HANDLING 2: Non-Existent File Check
                if not target.exists():
                    results.append(f"=== {path_str} ===\nError: File does not exist. Check directory_tree_tool for exact filename.")
                    continue

                # ERROR HANDLING 3: Directory Passed Instead of File
                if target.is_dir():
                    results.append(f"=== {path_str} ===\nError: '{clean_path}' is a directory, not a readable file.")
                    continue

                # ERROR HANDLING 4: Binary File Check
                if target.suffix.lower() in BINARY_EXTENSIONS:
                    results.append(f"=== {path_str} ===\nError: Cannot read binary asset '{target.name}' as text.")
                    continue

                # Read content safely with UTF-8 fallback
                content = target.read_text(encoding="utf-8", errors="replace")

                # ERROR HANDLING 5: File Size / Token Overflow Guard
                if len(content) > MAX_CHAR_LIMIT:
                    truncated = content[:MAX_CHAR_LIMIT]
                    results.append(
                        f"=== {clean_path} (Truncated: exceeded {MAX_CHAR_LIMIT} chars) ===\n"
                        f"{truncated}\n\n[Warning: File truncated to avoid context window overflow.]"
                    )
                else:
                    results.append(f"=== {clean_path} ===\n{content}")

            except PermissionError:
                results.append(f"=== {path_str} ===\nError: Permission denied when reading file.")
            except Exception as e:
                results.append(f"=== {path_str} ===\nUnexpected Error: {str(e)}")

        return "\n\n".join(results)

    return read_files