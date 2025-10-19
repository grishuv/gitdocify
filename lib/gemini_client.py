import os
from google import genai
import json
import re
from dotenv import load_dotenv

# Load .env for GEMINI_API_KEY
load_dotenv()


class GemClient:
    def __init__(self):
        # Initialize Gemini client
        # It will automatically read GEMINI_API_KEY from environment
        self.client = genai.Client()

    def generate_text(self, prompt, model="gemini-2.5-flash"):
        """
        Send prompt to Gemini and return structured output as dict:
        { "summary": "...", "code_notes": "..." }
        """
        # Generate response from Gemini
        try:
            resp = self.client.models.generate_content(model=model, contents=prompt)
            text = resp.text if hasattr(resp, "text") else str(resp)

            # Remove ```json ... ``` or ``` ... ``` fences
            text = re.sub(r"```(?:json)?\s*", "", text)
            text = re.sub(r"```", "", text).strip()

            # Try to parse JSON
            try:
                return json.loads(text)
            except Exception:
                # Fallback split
                parts = text.strip().split("\n\n", 1)
                return {
                    "summary": parts[0],
                    "code_notes": parts[1] if len(parts) > 1 else ""
                }
        except Exception as e:
            print("Error calling Gemini API:", e)
            return {"summary": "Error generating summary", "code_notes": ""}