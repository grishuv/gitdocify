from dotenv import load_dotenv
import os

load_dotenv()  # load .env

api_key = os.getenv("GEMINI_API_KEY")
print("GEMINI_API_KEY found:", bool(api_key))
