# This tool scans the folder structure safely.

import os
from pathlib import Path
from typing import Type
from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool

IGNORED_DIRS = {
    ".git", "node_modules", "__pycache__", ".venv", "venv",
    "dist", "build", ".next", ".idea", ".vscode"
}

class DirectoryTreeInput(BaseModel):
    dir_path: str = Field(
        default="", 
        description="Relative path inside the repo. Leave empty to scan from root."
    )

class DirectoryTreeTool(BaseTool):
    name: str = "directory_tree_tool"
    description: str = "Returns the folder and file tree structure. Root is './'."
    args_schema: Type[BaseModel] = DirectoryTreeInput
    root_dir: str = Field(default_factory=os.getcwd)

    def _run(self, dir_path: str = "") -> str:
        base = Path(self.root_dir).resolve()
        clean_subpath = dir_path.strip().lstrip("/\\")
        target = (base / clean_subpath).resolve()

        # ERROR HANDLING 1: Directory Traversal Check (Security Sandbox)
        try:
            target.relative_to(base)
        except ValueError:
            return "Error: Access Denied. Cannot inspect directories outside the project root."

        # ERROR HANDLING 2: Folder Existence & Type Check
        if not target.exists():
            return f"Error: Directory '{dir_path}' does not exist."
        if not target.is_dir():
            return f"Error: '{dir_path}' is a file, not a directory. Use read_files instead."

        tree_lines = ["./"]
        self._build_tree(target, "", tree_lines, max_depth=4, current_depth=0)
        return "\n".join(tree_lines)

    def _build_tree(self, dir_path: Path, prefix: str, tree_lines: list, max_depth: int, current_depth: int):
        # ERROR HANDLING 3: Depth Guard (Prevents token-heavy infinite trees)
        if current_depth >= max_depth:
            return

        try:
            items = [p for p in dir_path.iterdir() if p.name not in IGNORED_DIRS]
            items.sort(key=lambda p: (not p.is_dir(), p.name.lower()))
        except (PermissionError, OSError) as e:
            tree_lines.append(f"{prefix}[Error: Access restricted - {e.strerror}]")
            return

        for index, item in enumerate(items):
            is_last = (index == len(items) - 1)
            connector = "└── " if is_last else "├── "
            tree_lines.append(f"{prefix}{connector}{item.name}")

            if item.is_dir():
                next_prefix = prefix + ("    " if is_last else "│   ")
                self._build_tree(item, next_prefix, tree_lines, max_depth, current_depth + 1)