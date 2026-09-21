import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from core.git_service import GitService
from core.tool_registry import ToolRegistry
from core.agent_factory import create_codebase_agent, MODEL_NAME
from tools.tree_tool import DirectoryTreeTool

load_dotenv()

app = FastAPI(title="Source Code Analyzer API", version="1.0.0")

# Enable CORS for Vite frontend (typically running on port 5173)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

CLONE_DIR = os.getenv("CLONE_DIR", r"E:\Analyzed-Repositories")
git_service = GitService(CLONE_DIR)

# ─── Pydantic Schemas (Frozen API Contracts) ─────────────────────────
class RepoCloneRequest(BaseModel):
    github_url: str

class ChatQueryRequest(BaseModel):
    repo_path: str
    selected_subfolder: Optional[str] = ""
    query: str

class FolderTreeRequest(BaseModel):
    repo_path: str
    selected_subfolder: Optional[str] = "."


def extract_message_text(content) -> str:
    if isinstance(content, str):
        return content
    elif isinstance(content, list):
        text_parts = [
            item.get("text", "") 
            for item in content 
            if isinstance(item, dict) and item.get("type") == "text"
        ]
        return "\n".join(text_parts)
    return str(content)

# ─── API Endpoints ───────────────────────────────────────────────────

@app.get("/api/health")
def get_health():
    """Sidebar connectivity status for LLM and Model."""
    has_api_key = bool(os.getenv("GOOGLE_API_KEY"))
    return {
        "status": "online" if has_api_key else "missing_credentials",
        "model": MODEL_NAME,
        "api_key_configured": has_api_key
    }

@app.get("/api/tools")
def get_tools():
    """Sidebar status listing all registered tools."""
    return {
        "tools": ToolRegistry.list_available_tools()
    }

@app.post("/api/repo/tree")
def get_folder_tree(req: FolderTreeRequest):
    """Returns the visual directory tree for the selected focus folder."""
    target_dir = Path(req.repo_path)
    if req.selected_subfolder and req.selected_subfolder != ".":
        target_dir = target_dir / req.selected_subfolder

    if not target_dir.exists():
        raise HTTPException(status_code=404, detail="Folder does not exist.")

    tree_tool = DirectoryTreeTool(root_dir=str(target_dir))
    tree_content = tree_tool.invoke({})
    return {"tree": tree_content}

@app.post("/api/repo/analyze")
async def analyze_repo(req: RepoCloneRequest):
    """Fetches GitHub stats, clones to external folder, and returns sub-folders."""
    try:
        owner, repo_name = git_service.parse_github_url(req.github_url)
        metadata = await git_service.get_github_metadata(owner, repo_name)
        
        # Clone repo
        local_path = git_service.clone_repository(req.github_url, repo_name)
        
        # Discover sub-folders
        subfolders = git_service.get_top_level_folders(local_path)

        return {
            "status": "success",
            "metadata": metadata,
            "local_path": local_path,
            "subfolders": subfolders
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/chat")
def chat_with_codebase(req: ChatQueryRequest):
    """Executes queries against the selected repository or subfolder."""
    target_dir = Path(req.repo_path)
    if req.selected_subfolder and req.selected_subfolder != ".":
        target_dir = target_dir / req.selected_subfolder

    if not target_dir.exists():
        raise HTTPException(status_code=404, detail="Target repository path not found.")

    try:
        agent = create_codebase_agent(str(target_dir))
        inputs = {"messages": [("user", req.query)]}

        final_message = None
        for step in agent.stream(inputs, stream_mode="values"):
            final_message = step["messages"][-1]

        answer = extract_message_text(final_message.content) if final_message else "No response generated."

        return {
            "status": "success",
            "target_path": str(target_dir),
            "answer": answer
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))