from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import tempfile
from pathlib import Path
import shutil
import asyncio

from lib.git_utils import clone_repo, iter_commits
from lib.diff_parser import summarize_diff_hunks
from lib.gemini_client import GemClient

app = FastAPI()

# Allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class RepoRequest(BaseModel):
    repo_url: str
    max_commits: int = 10

# Store last seen commit hashes per repo
repo_latest_commit = {}

# -----------------------------
# Helper Functions
# -----------------------------
def extract_before_after(diff_text):
    before_lines, after_lines = [], []
    current_file = None
    result = []
    for line in diff_text.splitlines():
        if line.startswith("diff --git"):
            if current_file and (before_lines or after_lines):
                result.append({
                    "file": current_file,
                    "before": "\n".join(before_lines),
                    "after": "\n".join(after_lines),
                })
            before_lines, after_lines = [], []
            parts = line.split(" ")
            if len(parts) >= 3:
                current_file = parts[2].replace("a/", "")
        elif line.startswith("---") or line.startswith("+++"):
            continue
        elif line.startswith("-"):
            before_lines.append(line[1:])
        elif line.startswith("+"):
            after_lines.append(line[1:])
    if current_file and (before_lines or after_lines):
        result.append({
            "file": current_file,
            "before": "\n".join(before_lines),
            "after": "\n".join(after_lines),
        })
    return result

async def process_commit(commit, client, sem):
    sha = commit.hexsha[:7]
    repo = commit.repo
    if commit.parents:
        parent_sha = commit.parents[0].hexsha
        diff_text = repo.git.diff(parent_sha, commit.hexsha, unified=3)
    else:
        diff_text = repo.git.show(commit.hexsha, unified=3)

    hunks = summarize_diff_hunks(diff_text)
    file_changes = extract_before_after(diff_text)

    file_snippets_text = ""
    for f in hunks["file_snippets"]:
        snippet = f["snippet"].replace("```", "'")
        file_snippets_text += f"File: {f['file']}\n{snippet}\n\n"

    prompt = f"""
You are an expert software engineer and technical writer.
Given commit metadata and code snippets, produce JSON like:
{{
  "summary": "A short, clear summary of what changed",
  "code_notes": "- bullet points about functions and changes"
}}

Commit metadata:
SHA: {sha}
Author: {commit.author.name} <{commit.author.email}>
Date: {commit.committed_datetime}
Message: {commit.message.strip()}

Changed files:
{file_snippets_text}
"""

    async with sem:
        ai_response = await asyncio.to_thread(client.generate_text, prompt)

    return {
        "sha": sha,
        "author": commit.author.name,
        "email": commit.author.email,
        "date": str(commit.committed_datetime),
        "message": commit.message.strip(),
        "summary": ai_response.get("summary", ""),
        "code_notes": ai_response.get("code_notes", ""),
        "files": file_changes
    }

# -----------------------------
# POST /generate_docs
# -----------------------------
@app.post("/generate_docs")
async def generate_docs(request: RepoRequest):
    repo_url = request.repo_url
    max_commits = request.max_commits
    tmp_dir = None
    try:
        tmp_dir = Path(tempfile.mkdtemp())
        repo_path = clone_repo(repo_url)
        client = GemClient()
        commits_list = list(iter_commits(repo_path, max_count=max_commits))

        # Semaphore limits concurrent AI calls
        sem = asyncio.Semaphore(5)
        tasks = [process_commit(commit, client, sem) for commit in commits_list]
        commits_data = await asyncio.gather(*tasks)

        if commits_data:
            repo_latest_commit[repo_url] = commits_data[0]["sha"]

        return {"status": "success", "commits": commits_data}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if tmp_dir:
            shutil.rmtree(tmp_dir, ignore_errors=True)

# -----------------------------
# WEBSOCKET /live_updates
# -----------------------------
@app.websocket("/live_updates")
async def websocket_live_updates(websocket: WebSocket):
    await websocket.accept()
    repo_url = None
    try:
        data = await websocket.receive_json()
        repo_url = data.get("repo_url")

        if not repo_url:
            await websocket.send_json({"error": "No repo_url provided"})
            await websocket.close()
            return

        print(f"🔌 Client connected for live updates: {repo_url}")

        # Initialize latest commit if not tracked
        if repo_url not in repo_latest_commit:
            tmp_dir = Path(tempfile.mkdtemp())
            repo_path = clone_repo(repo_url)
            commits = list(iter_commits(repo_path, max_count=1))
            if commits:
                repo_latest_commit[repo_url] = commits[0].hexsha[:7]
            shutil.rmtree(tmp_dir, ignore_errors=True)

        # Continuous check every 10 seconds
        while True:
            tmp_dir = Path(tempfile.mkdtemp())
            repo_path = clone_repo(repo_url)
            commits = list(iter_commits(repo_path, max_count=1))
            if commits:
                latest_commit = commits[0]
                latest_sha = latest_commit.hexsha[:7]
                if latest_sha != repo_latest_commit.get(repo_url):
                    print(f"🚀 New commit detected: {latest_sha}")
                    repo_latest_commit[repo_url] = latest_sha
                    await websocket.send_json({
                        "message": "New commit detected",
                        "sha": latest_sha,
                        "author": latest_commit.author.name,
                        "message_text": latest_commit.message.strip()
                    })
            shutil.rmtree(tmp_dir, ignore_errors=True)
            await asyncio.sleep(10)

    except WebSocketDisconnect:
        print("🔌 WebSocket disconnected")
    except Exception as e:
        await websocket.send_json({"error": str(e)})
