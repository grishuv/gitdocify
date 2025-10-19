# 🧠 GitDocify — AI-Powered Git Commit Documentation Generator

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![React](https://img.shields.io/badge/React-18.2.0-blue.svg)](https://reactjs.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

GitDocify is an **AI-powered Git documentation generator** that automatically analyzes commit history, summarizes code changes, and creates **beautiful, professional project documentation** — including downloadable PDFs with code diffs, summaries, and commit insights.  

It helps developers, teams, and open-source maintainers **save hours** by generating clean and structured documentation directly from their repository’s history.

---

## 🌟 Features

✅ Fetch commits directly from any GitHub repository  
✅ AI-based summaries of each commit  
✅ Before & After code comparison view  
✅ Real-time commit updates using WebSockets  
✅ Professional, well-spaced PDF export with colors & bold headers  
✅ Sleek dark-themed minimal React interface  

---

## 🏗️ Project Architecture

```
gitdocify/
├── app.py                 # FastAPI backend (main server)
├── lib/                   # Helper utilities (git, AI, diff parser)
├── frontend/              # React web interface
│   ├── src/
│   │   ├── App.js         # Main frontend logic
│   │   ├── components/    # UI components
│   │   └── utils/         # PDF & styling utilities
├── requirements.txt       # Backend dependencies
└── README.md
```

---

## ⚙️ Step-by-Step Installation & Setup

Follow the steps below to set up and run **GitDocify** locally 👇

### 🧩 Step 1: Clone the Repository

```bash
git clone https://github.com/your-username/gitdocify.git
cd gitdocify
```

### ⚙️ Step 2: Set Up the Backend (FastAPI)

#### 1️⃣ Create and activate a virtual environment:

```bash
# Create virtual environment
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate

# Activate (macOS / Linux)
source .venv/bin/activate
```

#### 2️⃣ Install dependencies:

```bash
pip install -r requirements.txt
```

#### 3️⃣ Run the backend:

```bash
uvicorn app:app --reload
```

✅ The backend will run at:  
**http://127.0.0.1:8000**

---

### 💻 Step 3: Set Up the Frontend (React)

#### 1️⃣ Move to the frontend directory:

```bash
cd frontend
```

#### 2️⃣ Install dependencies:

```bash
npm install
```

#### 3️⃣ Start the React app:

```bash
npm start
```

✅ The frontend will be available at:  
**http://localhost:3000**

---

### ⚡ Step 4: Generate Documentation

1️⃣ Enter your GitHub repo URL in the text field, e.g.  
```
https://github.com/user/repo.git
```

2️⃣ Click **Generate Docs**  
   → It will fetch the latest commits and display:  
   - Commit SHA  
   - Author name  
   - Summary  
   - Before & After code comparison  

3️⃣ Click **Download PDF**  
   → It exports all commits into a **formatted PDF document** with:  
   - Bold headers  
   - Colored text highlights  
   - Proper spacing and line padding  

---

### 🔁 Step 5: Real-Time Live Updates

GitDocify automatically tracks new commits pushed to your GitHub repo.  
When a new commit is detected:
- A **WebSocket event** is triggered.
- The app **fetches only the new commit**.
- The UI updates instantly — no page reload required!  

---

## 🎨 UI Overview

| Section | Description |
|----------|-------------|
| **Project Header** | Displays repo title, AI-generated short description, and total commits |
| **Commits Section** | Accordion-style expandable commits list |
| **Code View** | Split view showing “Before” and “After” code side by side |
| **Dark Theme** | Clean, minimalistic UI for professional readability |
| **PDF Export** | Generates documentation with colors, bold fonts, and spacing |

---

## 🧾 Example PDF Features

- 🧠 **AI Summary:** Each commit summarized clearly  
- 💬 **Message & Notes:** Developer notes and commit message  
- 🔀 **Before / After Diff:** Clean formatted code comparison  
- ✨ **Design:**  
  - Bold commit headers  
  - Line spacing & margin adjustments  
  - Color-coded file names & code  

---

## 📦 Tech Stack

| Layer | Technology |
|-------|-------------|
| **Frontend** | React, Axios, Bootstrap, jsPDF |
| **Backend** | FastAPI, GitPython, AsyncIO |
| **AI** | Gemini / LangChain (optional integration) |
| **Language** | Python 3.10+, JavaScript (ES6) |

---

## 🧰 Dependencies

### Backend
```
fastapi
uvicorn
gitpython
aiofiles
pydantic
```

### Frontend
```
react
axios
react-bootstrap
react-syntax-highlighter
jspdf
```

---

## 🧠 How It Works

1. The backend clones the given repo temporarily.  
2. Fetches and parses recent commit diffs.  
3. Optionally analyzes them using an AI model (LangChain or Gemini).  
4. Sends structured JSON to the React frontend.  
5. The frontend displays commit details with syntax highlighting.  
6. When “Download PDF” is clicked → the app generates a clean, spaced PDF.  

---

## 💡 Tips

- Make sure your repo is **public**, or configure a GitHub token if private.  
- You can change the number of commits fetched via `max_commits` in the backend.  
- For large repos, initial fetch may take longer.  

---

## 🧾 License

This project is licensed under the **MIT License**.  
See the [LICENSE](LICENSE) file for full details.

---

## 🤝 Contributing

We welcome contributions!  
To contribute:

```bash
# 1. Fork the repo
# 2. Create a new branch
git checkout -b feature-name

# 3. Commit your changes
git commit -m "Added new feature"

# 4. Push your branch
git push origin feature-name
```

Then open a Pull Request 🚀  

---

## 👩‍💻 Author

**👤 Grishma Dhawale**  
📧 grishudhawale02@gmail.com

---

## 🏁 Final Notes

✨ **GitDocify** helps developers generate clean, readable, and AI-powered documentation straight from their Git commits.  
It’s ideal for portfolios, internal reports, or project submissions.  

> _“Stop writing commit documentation manually — let GitDocify do it for you.”_ 🚀  

**Built with ❤️ and ☕ by Grishma Dhawale**
