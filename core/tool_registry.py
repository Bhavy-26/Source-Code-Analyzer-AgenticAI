# This file dynamically registers all tools and initializes them with the selected repository path without touching your existing code in tools/tree_tool.py and tools/file_reader.py

from typing import List, Dict, Any
from langchain_core.tools import BaseTool
from tools.tree_tool import DirectoryTreeTool
from tools.file_reader import make_file_reader
from tools.code_search import CodeSearchTool  # Import the new tool

class ToolRegistry:
    """Manages dynamic registration and binding of codebase tools."""

    @staticmethod
    def get_tools_for_path(repo_path: str) -> List[BaseTool]:
        """Instantiates all registered tools bound to a specific target repository path."""
        tree_tool = DirectoryTreeTool(root_dir=repo_path)
        file_reader_tool = make_file_reader(repo_path)

        # Future tools can easily be appended here:
        # e.g., git_log_tool = make_git_log_tool(repo_path)
        return [tree_tool, file_reader_tool]

    @staticmethod
    def list_available_tools() -> List[Dict[str, Any]]:
        """Returns metadata for all available tools to display in the frontend sidebar."""
        # Temporary instance to inspect schema
        dummy_tree = DirectoryTreeTool()
        dummy_reader = make_file_reader(".")

        tool_instances = [dummy_tree, dummy_reader]
        
        return [
            {
                "name": t.name,
                "description": t.description,
                "status": "ready"
            }
            for t in tool_instances
        ]

    @staticmethod
    def get_tools_for_path(repo_path: str) -> List[BaseTool]:
        """Instantiates all registered tools bound to a specific target repository path."""
        tree_tool = DirectoryTreeTool(root_dir=repo_path)
        file_reader_tool = make_file_reader(repo_path)
        code_search_tool = CodeSearchTool(root_dir=repo_path)

        return [tree_tool, file_reader_tool, code_search_tool]

    @staticmethod
    def list_available_tools() -> List[Dict[str, Any]]:
        """Returns metadata for all available tools to display in the frontend sidebar."""
        dummy_tree = DirectoryTreeTool()
        dummy_reader = make_file_reader(".")
        dummy_search = CodeSearchTool()

        tool_instances = [dummy_tree, dummy_reader, dummy_search]
        
        return [
            {
                "name": t.name,
                "description": t.description,
                "status": "ready"
            }
            for t in tool_instances
        ]