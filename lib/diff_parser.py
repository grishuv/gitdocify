from unidiff import PatchSet
import io

def summarize_diff_hunks(unified_diff_text):
    """
    Parse a unified diff string and summarize changes.
    
    Returns a dict:
    {
        "summary": "filename1: +x/-y\nfilename2: +x/-y",
        "file_snippets": [
            {"file": filename, "snippet": first_hunk_snippet}
        ]
    }
    """
    # If diff is a list (GitPython sometimes returns a list), join to string
    if isinstance(unified_diff_text, list):
        unified_diff_text = "\n".join(unified_diff_text)
    
    patches = PatchSet(io.StringIO(unified_diff_text))
    
    summary_lines = []
    file_snippets = []

    for patched_file in patches:
        filename = patched_file.path

        # Count added and removed lines
        added = sum(1 for h in patched_file for l in h if l.is_added)
        removed = sum(1 for h in patched_file for l in h if l.is_removed)
        summary_lines.append(f"{filename}: +{added} / -{removed}")

        # Take first hunk snippet (small sample)
        if patched_file:
            first_hunk = next(iter(patched_file), None)
            if first_hunk:
                snippet = "".join([l.value for l in first_hunk if l.is_added or l.is_context])
                # Limit snippet size to 1000 chars
                file_snippets.append({"file": filename, "snippet": snippet[:1000]})

    return {
        "summary": "\n".join(summary_lines),
        "file_snippets": file_snippets
    }
