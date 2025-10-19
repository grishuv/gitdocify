from lib.git_utils import clone_repo, iter_commits
from lib.diff_parser import summarize_diff_hunks

repo_url = ""
repo_path = clone_repo(repo_url)

# Get latest commit
commit = next(iter_commits(repo_path, max_count=1))

# Use git command to get proper unified diff
repo = commit.repo
if commit.parents:
    parent_sha = commit.parents[0].hexsha
else:
    parent_sha = None

if parent_sha:
    diff_text = repo.git.diff(parent_sha, commit.hexsha, unified=3)
else:
    # First commit (no parent)
    diff_text = repo.git.show(commit.hexsha, unified=3)

diff_summary = summarize_diff_hunks(diff_text)

print("\nDiff Summary:\n", diff_summary["summary"])
print("\nSnippets:")
for f in diff_summary["file_snippets"]:
    print(f"File: {f['file']}\n{f['snippet']}\n{'-'*40}")
