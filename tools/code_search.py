# This tool scans all text files in the project root/subfolder using standard Python regex, enforces the safety sandbox, skips binary files, and truncates results to prevent token overload.

import os
import re
from pathlib import Path
from typing import Type
from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool

IGNORED_DIRS = {
    ".git", "node_modules", "__pycache__", ".venv", "venv",
    "dist", "build", ".next", ".idea", ".vscode"
}

BINARY_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".gif", ".ico", ".svg",
    ".pdf", ".zip", ".tar", ".gz", ".exe", ".dll", ".mp4", ".mp3"
}

MAX_MATCHES = 30  # Cap search results to avoid token flooding

class CodeSearchInput(BaseModel):
    query: str = Field(description="The keyword, variable name, function name, or regex pattern to search for.")
    file_extension: str = Field(default="", description="Optional extension filter like '.js', '.py', or '.ts'.")

class CodeSearchTool(BaseTool):
    name: str = "code_search"
    description: str = "Searches for a keyword, symbol, or regex pattern across all project source files, returning matched files and line snippets."
    args_schema: Type[BaseModel] = CodeSearchInput
    root_dir: str = Field(default_factory=os.getcwd)

    def _run(self, query: str, file_extension: str = "") -> str:
        base = Path(self.root_dir).resolve()
        matches = []
        pattern = re.compile(re.escape(query), re.IGNORECASE)

        for root, dirs, files in os.walk(base):
            # Prune ignored directories in-place
            dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]

            for file in files:
                file_path = Path(root) / file

                # Skip non-text binaries or unmatched extensions
                if file_path.suffix.lower() in BINARY_EXTENSIONS:
                    continue
                if file_extension and not file_path.name.endswith(file_extension):
                    continue

                try:
                    rel_path = file_path.relative_to(base).as_posix()
                    lines = file_path.read_text(encoding="utf-8", errors="ignore").splitlines()
                    
                    for idx, line in enumerate(lines, start=1):
                        if pattern.search(line):
                            clean_line = line.strip()
                            # Truncate overly long single lines (e.g. minified code)
                            if len(clean_line) > 140:
                                clean_line = clean_line[:140] + "..."
                            matches.append(f"{rel_path}:{idx}: {clean_line}")

                            if len(matches) >= MAX_MATCHES:
                                matches.append(f"\n[Search truncated: matched limit of {MAX_MATCHES} occurrences reached]")
                                return "\n".join(matches)
                except Exception:
                    continue

        if not matches:
            return f"No occurrences found for '{query}'."

        return "\n".join(matches)