from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent
from core.tool_registry import ToolRegistry

MODEL_NAME = "gemini-2.5-flash"

SYSTEM_INSTRUCTION = (
    "You are an expert codebase assistant with local filesystem tools.\n\n"
    "OPERATING RULES:\n"
    "1. DISCOVERY: Call 'directory_tree_tool' first if you need to map out folders to find relevant files.\n"
    "2. BATCH READING: Inspect files using 'read_files' in a single call with a list of relative paths. "
    "Do not speculate on code behavior without reading the code.\n"
    "3. PATH HANDLING: Relative paths must omit root directory names.\n"
    "4. EVIDENCE-BASED: Base answers strictly on the retrieved source code.\n\n"
    "RESPONSE RULES:\n"
    "- Address the user's specific question directly in the opening sentence.\n"
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