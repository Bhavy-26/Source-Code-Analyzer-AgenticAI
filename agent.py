# This is the control center that assembles the tools, configures Gemini, and executes the user query.


from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent
from rich.console import Console
from rich.markdown import Markdown

# Import custom tools from the tools folder
from tools.tree_tool import DirectoryTreeTool
from tools.file_reader import make_file_reader

load_dotenv()

# 1. Point to your target repository
TARGET_REPO_PATH = r"E:\Complete AUTH\Server"

# 2. Initialize tools
tree_tool = DirectoryTreeTool(root_dir=TARGET_REPO_PATH)
file_reader_tool = make_file_reader(TARGET_REPO_PATH)
tools = [tree_tool, file_reader_tool]

# 3. Setup Gemini Model
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0
)

# 4. General, Adaptive System Prompt
system_instruction = (
    "You are an expert codebase assistant.\n\n"
    "WORKFLOW RULES:\n"
    "1. DISCOVERY: Always call 'directory_tree_tool' first to locate relevant files unless the user provided exact file paths.\n"
    "2. BATCH READING: Inspect files using 'read_files' in a single call with a list of relative paths. Do not guess what code does.\n"
    "3. ERROR RECOVERY: If a file returns 'File does not exist', inspect the tree again to self-correct the path.\n"
    "4. EVIDENCE-BASED: Base your response directly on the fetched file content.\n\n"
    "RESPONSE RULES:\n"
    "- Directly answer the user's specific question in your first sentence.\n"
    "- If the requested feature/file does not exist in the project, explicitly state that it is not present."
)

agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt=system_instruction
)

console = Console()

def extract_message_text(content) -> str:
    """Extracts clean text from strings or multimodal block lists."""
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

if __name__ == "__main__":
    query = "What dependencies and external libraries does this project rely on, and what are their purposes?"
    inputs = {"messages": [("user", query)]}

    final_message = None
    for step in agent.stream(inputs, stream_mode="values"):
        final_message = step["messages"][-1]

    if final_message:
        raw_text = extract_message_text(final_message.content)
        console.print("\n")
        console.rule("[bold cyan]Analysis Result[/bold cyan]")
        console.print(Markdown(raw_text))