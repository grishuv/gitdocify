from lib.gemini_client import GemClient

client = GemClient()

prompt = """
You are an expert software engineer.
Given the commit metadata and code snippets, produce JSON like:
{
  "summary": "A 1-2 sentence high-level summary of what the commit does and why",
  "code_notes": "- bullet1\\n- bullet2 (function names and reason)"
}

Commit metadata:
Commit SHA: abc123
Author: John Doe
Date: 2025-10-18
Message: Fixed bug in login validation

Changed files and code snippets:
File: login.js
function validateLogin(user) {
    ...
}

Focus: Be concise, avoid hallucination.
"""

response = client.generate_text(prompt)
print(response)
