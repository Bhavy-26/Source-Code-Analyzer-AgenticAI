from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent
from core.tool_registry import ToolRegistry

MODEL_NAME = "gemini-3.1-flash-lite"

SYSTEM_INSTRUCTION = (
    "You are an expert codebase assistant equipped with local filesystem tools.\n\n"
    "TOOL USAGE STRATEGY:\n"
    "1. SPECIFIC KEYWORDS / SYMBOLS: If the user asks about a specific route, variable, function, or keyword, "
    "call 'code_search' FIRST. This is the fastest way to pinpoint exact files and lines.\n"
    "2. BROAD STRUCTURE: If you need an overall architectural map, call 'directory_tree_tool'.\n"
    "3. DEEP INSPECTION: Once candidate files are identified, batch-read them in ONE call using 'read_files'.\n"
    "4. EVIDENCE-BASED: Base answers strictly on the retrieved source code without speculating.\n\n"
    "RESPONSE RULES:\n"
    "- Directly answer the user's specific question in the opening sentence.\n"
    "- Use clean Markdown: bold headers, tables, and formatted code blocks."
)

def create_codebase_agent(target_path: str):
    """Creates an agent executor bound to the specified repository path."""
    tools = ToolRegistry.get_tools_for_path(target_path)
    
    llm = ChatGoogleGenerativeAI(
        model=MODEL_NAME,
        temperature=0
    )

    agent = create_agent(
        model=llm,
        tools=tools,
        system_prompt=SYSTEM_INSTRUCTION
    )
    
    return agent