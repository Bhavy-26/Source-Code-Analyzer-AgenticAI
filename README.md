
# Source Code Analyzer

An agentic codebase exploration and analysis tool powered by **Google Gemini**, **LangChain / LangGraph**, **FastAPI**, and a **Vite + React + Tailwind CSS** frontend.  
The system clones GitHub repositories into an isolated storage workspace, extracts repository metadata, inspects directory layouts dynamically, batches file reading turns, and answers architectural, security, and feature-related questions using LLM reasoning[cite: 1, 2].

---

## 🚀 Get Started

### Step 1: Clone the Repository

```bash
git clone [https://github.com/](https://github.com/)<your-username>/Source-Code-Analyzer.git
cd Source-Code-Analyzer

```

---

### Step 2: Backend Setup

1. **Create and activate a virtual environment:**
* **Windows (PowerShell):**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1

```


* **Linux/macOS:**
```bash
python3 -m venv .venv
source .venv/bin/activate

```




2. **Install Python dependencies:**
```bash
pip install -r requirements.txt

```


3. **Configure Environment Variables:**
Create a `.env` file in the root directory:
```env
GOOGLE_API_KEY="your_actual_google_api_key_here"
CLONE_DIR="E:\Analyzed-Repositories or wherever you want to set"

```


> **Note for Windows users:** Ensure the directory specified in `CLONE_DIR` exists or let the application create it automatically.
> 
> 


4. **Start the FastAPI Backend:**
```bash
uvicorn main:app --reload --port 8000

```


The backend will run at `http://localhost:8000`. You can inspect interactive API documentation at `http://localhost:8000/docs`.

---

### Step 3: Frontend Setup

1. **Open a separate terminal and navigate to the frontend directory:**
```bash
cd frontend

```


2. **Install Node dependencies:**
```bash
npm install

```


3. **Start the Vite development server:**
```bash
npm run dev

```


The application interface will be accessible at `http://localhost:5173`.

---

## 🖥️ How to Use

* **Clone & Analyze:** Paste a public GitHub URL (e.g., `https://github.com/owner/repository`) into the top input bar and click **Analyze Repo**.


* **Focus Sub-Project:** If the project contains multiple workspaces or packages, select the target folder badge to narrow the analysis scope.


* **Inspect Directory Layout:** Expand the **Folder Structure** preview box to view the directory tree.


* **Ask Questions:** Use the bottom search input to query route configurations, architecture patterns, dependencies, or security logic.



```

```
