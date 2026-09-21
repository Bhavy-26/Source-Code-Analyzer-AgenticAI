import React, { useState, useEffect, useRef } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { 
  FolderGit2, 
  Search, 
  Terminal, 
  CheckCircle2, 
  AlertCircle, 
  Star, 
  GitFork, 
  Folder, 
  Cpu, 
  Wrench,
  Loader2,
  ChevronDown,
  ChevronRight,
  User,
  Bot
} from "lucide-react";

const BACKEND_URL = "http://localhost:8000/api";

export default function App() {
  // Global System State
  const [health, setHealth] = useState(null);
  const [tools, setTools] = useState([]);

  // Repo State
  const [githubUrl, setGithubUrl] = useState("");
  const [isCloning, setIsCloning] = useState(false);
  const [repoData, setRepoData] = useState(null);
  const [selectedSubfolder, setSelectedSubfolder] = useState(".");

  // Folder Tree Explorer State
  const [folderTree, setFolderTree] = useState("");
  const [isTreeOpen, setIsTreeOpen] = useState(true);
  const [isLoadingTree, setIsLoadingTree] = useState(false);

  // Chat / Q&A State
  const [messages, setMessages] = useState([]); // [{ sender: "user" | "bot", text: "", scope: "" }]
  const [query, setQuery] = useState("");
  const [isAnswering, setIsAnswering] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");

  const chatEndRef = useRef(null);

  useEffect(() => {
    fetchHealthAndTools();
  }, []);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isAnswering]);

  const fetchHealthAndTools = async () => {
    try {
      const [resHealth, resTools] = await Promise.all([
        fetch(`${BACKEND_URL}/health`),
        fetch(`${BACKEND_URL}/tools`)
      ]);
      setHealth(await resHealth.json());
      const dataTools = await resTools.json();
      setTools(dataTools.tools || []);
    } catch (err) {
      console.error("Backend error:", err);
    }
  };

  // Fetch Tree for currently chosen folder
  const fetchFolderTree = async (repoPath, folder) => {
    setIsLoadingTree(true);
    try {
      const res = await fetch(`${BACKEND_URL}/repo/tree`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ repo_path: repoPath, selected_subfolder: folder })
      });
      const data = await res.json();
      if (res.ok) setFolderTree(data.tree);
    } catch (e) {
      console.error("Failed to load tree:", e);
    } finally {
      setIsLoadingTree(false);
    }
  };

  // 1. Analyze / Clone Repository
  const handleCloneRepo = async (e) => {
    e.preventDefault();
    if (!githubUrl.trim()) return;

    setIsCloning(true);
    setErrorMsg("");
    setMessages([]);
    setRepoData(null);
    setFolderTree("");

    try {
      const res = await fetch(`${BACKEND_URL}/repo/analyze`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ github_url: githubUrl.trim() })
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Failed to clone repository.");

      setRepoData(data);
      setSelectedSubfolder(".");
      fetchFolderTree(data.local_path, ".");
    } catch (err) {
      setErrorMsg(err.message);
    } finally {
      setIsCloning(false);
    }
  };

  // 2. Switch Subfolder
  const handleSelectFolder = (folder) => {
    setSelectedSubfolder(folder);
    if (repoData) {
      fetchFolderTree(repoData.local_path, folder);
    }
  };

  // 3. Ask Question (Chat Thread Mode)
  const handleAskQuestion = async (e) => {
    e.preventDefault();
    if (!query.trim() || !repoData || isAnswering) return;

    const userQuestion = query.trim();
    setQuery(""); // Instantly clear input
    setErrorMsg("");

    // Append user message immediately
    setMessages((prev) => [
      ...prev,
      { sender: "user", text: userQuestion }
    ]);

    setIsAnswering(true);

    try {
      const res = await fetch(`${BACKEND_URL}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          repo_path: repoData.local_path,
          selected_subfolder: selectedSubfolder,
          query: userQuestion
        })
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Analysis failed.");

      setMessages((prev) => [
        ...prev,
        { sender: "bot", text: data.answer, scope: data.target_path }
      ]);
    } catch (err) {
      setErrorMsg(err.message);
      setMessages((prev) => [
        ...prev,
        { sender: "bot", text: `⚠️ Error: ${err.message}`, isError: true }
      ]);
    } finally {
      setIsAnswering(false);
    }
  };

  return (
    <div className="flex h-screen flex-col bg-zinc-950 text-zinc-100 font-sans">
      
      {/* ─── TOP BAR ───────────────────────────────────────────────────────────── */}
      <header className="border-b border-zinc-800 bg-zinc-900/60 p-4 backdrop-blur-md">
        <form onSubmit={handleCloneRepo} className="max-w-4xl mx-auto flex gap-3">
          <div className="relative flex-1">
            <FolderGit2 className="absolute left-3.5 top-3 h-5 w-5 text-zinc-400" />
            <input
              type="text"
              placeholder="Paste GitHub Repository URL (e.g., https://github.com/owner/repo)..."
              value={githubUrl}
              onChange={(e) => setGithubUrl(e.target.value)}
              className="w-full rounded-xl border border-zinc-700 bg-zinc-800/80 py-2.5 pl-11 pr-4 text-sm text-zinc-100 placeholder-zinc-400 focus:border-cyan-500 focus:outline-none focus:ring-1 focus:ring-cyan-500 transition-all"
            />
          </div>
          <button
            type="submit"
            disabled={isCloning}
            className="flex items-center gap-2 rounded-xl bg-cyan-600 px-5 py-2.5 text-sm font-medium hover:bg-cyan-500 disabled:opacity-50 transition-colors shadow-lg shadow-cyan-900/20"
          >
            {isCloning ? <Loader2 className="h-4 w-4 animate-spin" /> : "Analyze Repo"}
          </button>
        </form>
      </header>

      {/* ─── MAIN WORKSPACE ────────────────────────────────────────────────────── */}
      <div className="flex flex-1 overflow-hidden">
        
        {/* LEFT SIDEBAR: STATUS & TOOLS */}
        <aside className="w-72 border-r border-zinc-800 bg-zinc-900/30 p-5 flex flex-col gap-6 overflow-y-auto shrink-0">
          <div>
            <h3 className="text-xs font-semibold uppercase tracking-wider text-zinc-400 mb-3 flex items-center gap-2">
              <Cpu className="h-4 w-4 text-cyan-400" /> Model Connectivity
            </h3>
            <div className="rounded-xl border border-zinc-800 bg-zinc-900/80 p-3.5">
              <div className="flex items-center justify-between">
                <span className="text-xs text-zinc-400">Status</span>
                <span className="flex items-center gap-1.5 text-xs font-medium text-emerald-400">
                  <CheckCircle2 className="h-3.5 w-3.5" /> {health?.status || "Connecting..."}
                </span>
              </div>
              <div className="mt-2 text-sm font-semibold text-zinc-200">
                {health?.model || "Gemini"}
              </div>
            </div>
          </div>

          <div className="flex-1">
            <h3 className="text-xs font-semibold uppercase tracking-wider text-zinc-400 mb-3 flex items-center gap-2">
              <Wrench className="h-4 w-4 text-cyan-400" /> Tools Present ({tools.length})
            </h3>
            <div className="flex flex-col gap-2.5">
              {tools.map((t) => (
                <div key={t.name} className="rounded-xl border border-zinc-800/80 bg-zinc-900/50 p-3 hover:border-zinc-700 transition-colors">
                  <div className="flex items-center justify-between">
                    <span className="font-mono text-xs font-semibold text-cyan-300">{t.name}</span>
                    <span className="h-2 w-2 rounded-full bg-emerald-400"></span>
                  </div>
                  <p className="mt-1 text-xs text-zinc-400 line-clamp-2">{t.description}</p>
                </div>
              ))}
            </div>
          </div>
        </aside>

        {/* CENTER STAGE: REPO STATS + FOLDER TREE + CHAT THREAD */}
        <main className="flex-1 overflow-y-auto p-6">
          <div className="max-w-4xl mx-auto flex flex-col gap-6">
            
            {errorMsg && (
              <div className="flex items-center gap-2.5 rounded-xl border border-red-500/30 bg-red-950/40 p-4 text-sm text-red-300">
                <AlertCircle className="h-5 w-5 shrink-0" />
                <span>{errorMsg}</span>
              </div>
            )}

            {/* GitHub Overview Card */}
            {repoData && (
              <div className="rounded-2xl border border-zinc-800 bg-zinc-900/60 p-6 shadow-xl">
                <div className="flex items-start justify-between">
                  <div>
                    <h2 className="text-xl font-bold tracking-tight text-white flex items-center gap-2">
                      <FolderGit2 className="h-5 w-5 text-cyan-400" />
                      {repoData.metadata.owner} / {repoData.metadata.repo_name}
                    </h2>
                    <p className="mt-1 text-sm text-zinc-400">{repoData.metadata.description || "No description provided."}</p>
                  </div>
                  <div className="flex gap-4 text-xs text-zinc-300 font-medium">
                    <span className="flex items-center gap-1"><Star className="h-4 w-4 text-amber-400" /> {repoData.metadata.stars}</span>
                    <span className="flex items-center gap-1"><GitFork className="h-4 w-4 text-zinc-400" /> {repoData.metadata.forks}</span>
                  </div>
                </div>

                {repoData.metadata.languages?.length > 0 && (
                  <div className="mt-4 flex flex-wrap gap-1.5">
                    {repoData.metadata.languages.map((lang) => (
                      <span key={lang} className="rounded-md bg-zinc-800 px-2.5 py-1 text-xs text-zinc-300">
                        {lang}
                      </span>
                    ))}
                  </div>
                )}

                {/* Subfolder Scroll Strip */}
                <div className="mt-5 border-t border-zinc-800/80 pt-4">
                  <label className="text-xs font-semibold uppercase tracking-wider text-zinc-400 flex items-center gap-1.5 mb-2.5">
                    <Folder className="h-3.5 w-3.5" /> Target Sub-Project / Focus Folder ({repoData.subfolders.length}):
                  </label>
                  
                  {/* Scrollable folder badges row */}
                  <div className="flex gap-2 overflow-x-auto pb-2 scrollbar-thin scrollbar-thumb-zinc-700">
                    {repoData.subfolders?.map((folder) => (
                      <button
                        key={folder}
                        onClick={() => handleSelectFolder(folder)}
                        className={`shrink-0 rounded-lg px-3 py-1.5 text-xs font-medium transition-all ${
                          selectedSubfolder === folder
                            ? "bg-cyan-500 text-zinc-950 font-bold shadow-md shadow-cyan-500/20"
                            : "bg-zinc-800 text-zinc-300 hover:bg-zinc-700"
                        }`}
                      >
                        {folder === "." ? "Root (Whole Project)" : folder}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Selected Folder Directory Tree Viewer */}
                <div className="mt-4 border border-zinc-800/80 rounded-xl bg-zinc-950/60 overflow-hidden">
                  <button 
                    onClick={() => setIsTreeOpen(!isTreeOpen)}
                    className="w-full flex items-center justify-between px-3.5 py-2 text-xs font-mono text-zinc-400 hover:bg-zinc-900/60 transition-colors"
                  >
                    <span className="flex items-center gap-2">
                      {isTreeOpen ? <ChevronDown className="h-3.5 w-3.5 text-cyan-400" /> : <ChevronRight className="h-3.5 w-3.5 text-cyan-400" />}
                      Folder Structure: <span className="text-zinc-200">{selectedSubfolder === "." ? "Root" : selectedSubfolder}</span>
                    </span>
                    <span className="text-[11px] text-zinc-500">{isTreeOpen ? "Click to collapse" : "Click to view tree"}</span>
                  </button>

                  {isTreeOpen && (
                    <div className="p-3 border-t border-zinc-800/60 bg-black/40 text-xs font-mono text-cyan-200/80 overflow-x-auto max-h-48 scrollbar-thin">
                      {isLoadingTree ? (
                        <div className="flex items-center gap-2 py-2 text-zinc-500">
                          <Loader2 className="h-3.5 w-3.5 animate-spin" /> Loading folder tree...
                        </div>
                      ) : (
                        <pre className="leading-tight">{folderTree || "No tree generated."}</pre>
                      )}
                    </div>
                  )}
                </div>

              </div>
            )}

            {/* Conversational Chat Thread */}
            <div className="flex flex-col gap-4">
              {messages.length === 0 && !repoData && (
                <div className="flex flex-col items-center justify-center p-12 text-center text-zinc-500 border border-dashed border-zinc-800 rounded-2xl">
                  <Terminal className="h-10 w-10 mb-3 stroke-[1.5]" />
                  <p className="text-sm">Clone a repository above to explore code and start asking questions.</p>
                </div>
              )}

              {messages.map((msg, index) => (
                <div key={index} className="flex flex-col">
                  {msg.sender === "user" ? (
                    // User Question Bubble (Right aligned)
                    <div className="flex justify-end items-start gap-2.5 mb-2">
                      <div className="max-w-2xl rounded-2xl rounded-tr-sm bg-cyan-600 px-4 py-3 text-sm text-white shadow-md">
                        {msg.text}
                      </div>
                      <div className="rounded-full bg-cyan-800 p-1.5 shrink-0">
                        <User className="h-4 w-4 text-white" />
                      </div>
                    </div>
                  ) : (
                    // Bot Answer Bubble (Left aligned with full Markdown)
                    <div className="flex justify-start items-start gap-3 mb-4">
                      <div className="rounded-full bg-zinc-800 p-2 shrink-0 border border-zinc-700">
                        <Bot className="h-4 w-4 text-cyan-400" />
                      </div>
                      <div className="max-w-3xl flex-1 rounded-2xl rounded-tl-sm border border-zinc-800 bg-zinc-900/60 p-5 shadow-lg">
                        {msg.scope && (
                          <div className="pb-3 mb-3 border-b border-zinc-800 text-[11px] font-mono text-zinc-400">
                            Scope: {msg.scope}
                          </div>
                        )}
                        <div className="prose prose-invert max-w-none text-sm leading-relaxed text-zinc-200">
                          <ReactMarkdown remarkPlugins={[remarkGfm]}>
                            {msg.text}
                          </ReactMarkdown>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              ))}

              {isAnswering && (
                <div className="flex justify-start items-start gap-3">
                  <div className="rounded-full bg-zinc-800 p-2 shrink-0 border border-zinc-700">
                    <Bot className="h-4 w-4 text-cyan-400" />
                  </div>
                  <div className="flex items-center gap-3 p-4 rounded-2xl border border-zinc-800 bg-zinc-900/40">
                    <Loader2 className="h-4 w-4 animate-spin text-cyan-400" />
                    <span className="text-xs text-zinc-400">Agent reading source files and reasoning...</span>
                  </div>
                </div>
              )}
              <div ref={chatEndRef} />
            </div>

          </div>
        </main>
      </div>

      {/* ─── BOTTOM BAR: QUESTION INPUT ────────────────────────────────────────── */}
      <footer className="border-t border-zinc-800 bg-zinc-900/60 p-4 backdrop-blur-md">
        <form onSubmit={handleAskQuestion} className="max-w-4xl mx-auto flex gap-3">
          <div className="relative flex-1">
            <Search className="absolute left-3.5 top-3 h-5 w-5 text-zinc-400" />
            <input
              type="text"
              disabled={!repoData || isAnswering}
              placeholder={repoData ? `Ask anything about ${selectedSubfolder === "." ? "the repository" : selectedSubfolder}...` : "Clone a repository first to ask questions"}
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              className="w-full rounded-xl border border-zinc-700 bg-zinc-800/80 py-2.5 pl-11 pr-4 text-sm text-zinc-100 placeholder-zinc-400 focus:border-cyan-500 focus:outline-none focus:ring-1 focus:ring-cyan-500 transition-all disabled:opacity-50"
            />
          </div>
          <button
            type="submit"
            disabled={!repoData || isAnswering || !query.trim()}
            className="flex items-center gap-2 rounded-xl bg-cyan-600 px-6 py-2.5 text-sm font-medium hover:bg-cyan-500 disabled:opacity-50 transition-colors shadow-lg shadow-cyan-900/20"
          >
            {isAnswering ? <Loader2 className="h-4 w-4 animate-spin" /> : "Ask Agent"}
          </button>
        </form>
      </footer>

    </div>
  );
}