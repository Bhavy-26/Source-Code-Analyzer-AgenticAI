# This service fetches GitHub metadata using public REST APIs (stars, forks, languages, branches) and clones the repository into destination of CLONE_DIR.

import os
import re
from pathlib import Path
from typing import Dict, Any, List
import git
import httpx

class GitService:
    def __init__(self, base_clone_dir: str):
        self.base_clone_dir = Path(base_clone_dir).resolve()
        self.base_clone_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def parse_github_url(url: str) -> tuple[str, str]:
        """Extracts owner and repo name from URLs like https://github.com/owner/repo"""
        match = re.search(r"github\.com/([^/]+)/([^/]+?)(?:\.git)?/?$", url.strip())
        if not match:
            raise ValueError("Invalid GitHub URL format. Example: https://github.com/owner/repo")
        return match.group(1), match.group(2)

    async def get_github_metadata(self, owner: str, repo: str) -> Dict[str, Any]:
        """Fetches public stats from the GitHub REST API without cloning."""
        api_url = f"https://api.github.com/repos/{owner}/{repo}"
        async with httpx.AsyncClient() as client:
            res = await client.get(api_url, headers={"User-Agent": "FastAPI-Analyzer"})
            if res.status_code != 200:
                raise ValueError(f"GitHub repository not found or rate-limited ({res.status_code})")
            data = res.json()

            # Fetch language breakdown
            lang_res = await client.get(data.get("languages_url", ""), headers={"User-Agent": "FastAPI-Analyzer"})
            languages = list(lang_res.json().keys()) if lang_res.status_code == 200 else []

            return {
                "owner": owner,
                "repo_name": repo,
                "description": data.get("description", "No description provided."),
                "stars": data.get("stargazers_count", 0),
                "forks": data.get("forks_count", 0),
                "default_branch": data.get("default_branch", "main"),
                "languages": languages
            }

    def clone_repository(self, url: str, repo_name: str) -> str:
        """Clones repo into E:\\Analyzed-Repositories\\<repo_name> or pulls if already exists."""
        target_path = self.base_clone_dir / repo_name
        
        if (target_path / ".git").exists():
            # Already cloned, fetch updates
            repo = git.Repo(target_path)
            repo.remotes.origin.pull()
        else:
            git.Repo.clone_from(url, target_path, depth=1)

        return str(target_path)

    @staticmethod
    def get_top_level_folders(repo_path: str) -> List[str]:
        """Lists sub-projects/folders in the root so the user can select one."""
        p = Path(repo_path)
        ignored = {".git", ".github", ".venv", "venv", "node_modules", "dist", "build"}
        folders = [item.name for item in p.iterdir() if item.is_dir() and item.name not in ignored]
        return ["."] + sorted(folders)  # '.' represents root