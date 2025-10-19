from lib.git_utils import clone_repo, iter_commits

# Replace with a small public repo for testing
repo_url = ""

repo_path = clone_repo(repo_url)

print("\nRecent commits:")
for commit in iter_commits(repo_path, max_count=5):
    print(f"{commit.hexsha[:7]} | {commit.author.name} | {commit.committed_datetime} | {commit.message.strip()}")
