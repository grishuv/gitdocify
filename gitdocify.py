import sys
from pathlib import Path
from lib.git_utils import clone_repo, iter_commits
from lib.diff_parser import summarize_diff_hunks
from lib.gemini_client import GemClient

# Output directories
OUT = Path("output")
COMMIT_DOCS = OUT / "commit_docs"

# Ensure output folder exists
OUT.mkdir(exist_ok=True)

# Ensure commit_docs folder exists safely
if COMMIT_DOCS.exists():
    if COMMIT_DOCS.is_file():
        COMMIT_DOCS.unlink()  # delete file if same name exists
        COMMIT_DOCS.mkdir()
else:
    COMMIT_DOCS.mkdir()


# -------------------------------------------------------
# Helper to extract before/after code from a unified diff
# -------------------------------------------------------
def extract_before_after(diff_text):
    """Extract before/after code sections from unified diff text."""
    before_lines = []
    after_lines = []
    current_file = None
    result = []

    for line in diff_text.splitlines():
        if line.startswith("diff --git"):
            # save previous file's diff
            if current_file and (before_lines or after_lines):
                result.append({
                    "file": current_file,
                    "before": "\n".join(before_lines),
                    "after": "\n".join(after_lines)
                })
            before_lines = []
            after_lines = []
            parts = line.split(" ")
            if len(parts) >= 3:
                current_file = parts[2].replace("a/", "")
        elif line.startswith("---") or line.startswith("+++"):
            continue
        elif line.startswith("-"):
            before_lines.append(line[1:])
        elif line.startswith("+"):
            after_lines.append(line[1:])

    # save last file
    if current_file and (before_lines or after_lines):
        result.append({
            "file": current_file,
            "before": "\n".join(before_lines),
            "after": "\n".join(after_lines)
        })

    return result


# -------------------------------------------------------
# Main logic
# -------------------------------------------------------
def main(repo_url_or_path, max_commits=50):
    print(f"\n🔹 Cloning repo or using local path: {repo_url_or_path}")
    repo_path = clone_repo(repo_url_or_path)

    print("🔹 Initializing Gemini client...")
    client = GemClient()

    summary_lines = []

    print("\n🔹 Iterating commits...\n")
    for i, commit in enumerate(iter_commits(repo_path, max_count=max_commits), 1):
        sha = commit.hexsha[:7]
        print(f"[{i}] Processing commit {sha} - {commit.message.strip()}")

        repo = commit.repo
        if commit.parents:
            parent_sha = commit.parents[0].hexsha
            diff_text = repo.git.diff(parent_sha, commit.hexsha, unified=3)
        else:
            diff_text = repo.git.show(commit.hexsha, unified=3)

        # Summarize diff hunks
        hunks = summarize_diff_hunks(diff_text)

        # Extract before/after changes for visualization
        file_changes = extract_before_after(diff_text)

        # Prepare snippets for Gemini
        file_snippets_text = ""
        for f in hunks["file_snippets"]:
            snippet = f["snippet"].replace("```", "'")  # avoid Markdown code interference
            file_snippets_text += f"File: {f['file']}\n{snippet}\n\n"

        # Build Gemini prompt
        prompt = f"""
You are an expert software engineer and technical writer.
Given commit metadata and code snippets, produce JSON like:
{{
  "summary": "A 1-2 sentence high-level summary of what the commit does and why",
  "code_notes": "- bullet1\\n- bullet2 (function names and reason)"
}}

Commit metadata:
SHA: {sha}
Author: {commit.author.name} <{commit.author.email}>
Date: {commit.committed_datetime}
Message: {commit.message.strip()}

Changed files and code snippets:
{file_snippets_text}

Focus: Be concise, avoid hallucination. Return JSON only.
"""

        # Call Gemini API
        response = client.generate_text(prompt)

        # Write commit-level Markdown
        md = f"# Commit {sha}\n\n"
        md += f"**Author:** {commit.author.name} <{commit.author.email}>\n\n"
        md += f"**Date:** {commit.committed_datetime}\n\n"
        md += f"**Summary:**\n{response.get('summary','')}\n\n"
        md += f"**Code notes:**\n{response.get('code_notes','')}\n\n"
        md += f"**Files changed:**\n{hunks['summary']}\n"

        # Include before/after code sections
        for fc in file_changes:
            md += f"\n### {fc['file']}\n"
            md += f"**Before:**\n```diff\n{fc['before']}\n```\n"
            md += f"**After:**\n```diff\n{fc['after']}\n```\n"

        (COMMIT_DOCS / f"{sha}.md").write_text(md, encoding="utf-8")
        summary_lines.append(f"- {sha}: {response.get('summary','')}")

    # Write overall changelog
    (OUT / "summary.md").write_text("\n".join(summary_lines), encoding="utf-8")
    print(f"\n✅ Documentation generated in {OUT.resolve()}\n")


# -------------------------------------------------------
# CLI Entrypoint
# -------------------------------------------------------
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python gitdocify.py <repo_url_or_local_path> [max_commits]")
    else:
        repo_arg = sys.argv[1]
        max_c = int(sys.argv[2]) if len(sys.argv) > 2 else 50
        main(repo_arg, max_c)
