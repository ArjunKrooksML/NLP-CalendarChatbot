import os
from dotenv import load_dotenv

load_dotenv()

MODEL = os.getenv("LLM_MODEL","mistralai/Mistral-7B-Instruct-v0.1")
CREDENTIALS = os.getenv("CREDENTIALS_FILE", "Credentials.json")
TOKENS = os.getenv("TOKEN_FILE", "token.json")
SCOPES_STRING = os.getenv("GOOGLE_SCOPES", "https://www.googleapis.com/auth/calendar.events")
SCOPES = [SCOPES_STRING] if SCOPES_STRING else ['https://www.googleapis.com/auth/calendar.events']


print("Configuration loaded:")
print(f"  LLM Model: {MODEL}")
print(f"  Credentials File: {CREDENTIALS}")
print(f"  Token File: {TOKENS}")
print(f"  API Scopes: {SCOPES}")

