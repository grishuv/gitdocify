from git import Repo
import tempfile
import os

def clone_repo(url_or_path):
    """
    Clone a Git repo if a URL is given. 
    If a local path exists, just return it.
    Returns the local path of the repo.
    """
    if os.path.exists(url_or_path):
        print(f"Using local repo at: {url_or_path}")
        return url_or_path

    # Create a temporary folder for cloning
    tmp_dir = tempfile.mkdtemp(prefix="gitdocify_")
    print(f"Cloning {url_or_path} into {tmp_dir} ...")
    Repo.clone_from(url_or_path, tmp_dir)
    print("Clone completed.")
    return tmp_dir


def iter_commits(repo_path, max_count=50):
    """
    Iterate over recent commits of the default branch.
    Returns a generator of commit objects.
    """
    repo = Repo(repo_path)

    # Get the default branch (main or master)
    try:
        branch = repo.active_branch
    except TypeError:
        # Detached HEAD fallback
        branch = repo.head.reference

    print(f"Iterating commits on branch: {branch}")
    for i, commit in enumerate(repo.iter_commits(branch, max_count=max_count)):
        yield commit
