# NLP-Powered Calendar Scheduling Chatbot

A Python chatbot that uses the Mistral 7B LLM to understand natural language commands and schedule events in Google Calendar. It extracts event details (title, date, time), confirms with the user, and uses the Google Calendar API.

# Features

* Parses natural language for event scheduling.
* Extracts Title, Date, Start Time, End Time using Mistral 7B LLM.
* Handles relative dates (e.g., "tomorrow") and defaults duration (1hr).
* Confirms details with the user before creating the event.
* Integrates directly with Google Calendar API (OAuth 2.0).


# Technologies Used


* Hugging Face `transformers`, `torch`, `accelerate`, `sentencepiece`, `huggingface_hub`
* Google `google-api-python-client`, `google-auth-oauthlib`
* Utilities: `python-dateutil`, `tzlocal`, `python-dotenv`

# Setup Instructions

1.  **Clone/Download:** Get the project files.
2.  **Environment:** Create and activate a Python virtual environment (e.g., `python3 -m venv .venv && source .venv/bin/activate`).
3.  **Install Dependencies:**
    ```bash
    pip install --upgrade transformers torch google-api-python-client google-auth-oauthlib python-dateutil tzlocal python-dotenv huggingface_hub sentencepiece accelerate
    ```
    *(Or `pip install -r requirements.txt` if provided)*
4.  **Google Calendar API:**
    * Enable the Google Calendar API in Google Cloud Console.
    * Create OAuth 2.0 Credentials for a "Desktop app".
    * Download the credentials JSON file and save it as `credentials.json` in the project root.
5.  **Hugging Face:**
    * Create an account and get an Access Token ([Settings -> Access Tokens](https://huggingface.co/settings/tokens)).
    * Accept the terms for `mistralai/Mistral-7B-Instruct-v0.1` on its [model page](https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.1).
    * Log in via terminal: `huggingface-cli login` (paste your token when prompted).
6.  **Create `.env` File:** Create a file named `.env` in the project root with the following (adjust `HUGGINGFACE_TOKEN` only if *not* using CLI login):
    ```dotenv
    LLM_MODEL_NAME="mistralai/Mistral-7B-Instruct-v0.1"
    # HUGGINGFACE_TOKEN="hf_YOUR_TOKEN_HERE" # Usually not needed after CLI login
    GOOGLE_CREDENTIALS_FILE="credentials.json"
    GOOGLE_TOKEN_FILE="token.json" # Will be created
    GOOGLE_API_SCOPES="[https://www.googleapis.com/auth/calendar.events](https://www.googleapis.com/auth/calendar.events)"
    ```
    *Ensure `.env` is in your `.gitignore`!*

## Running the Application

1.  Activate your virtual environment (`source .venv/bin/activate`).
2.  Run the main script:
    ```bash
    python main.py
    ```
3.  Follow the prompts for Google authentication (first run) and wait for the LLM to load (first run).

# Usage

Type scheduling requests naturally at the `>` prompt. Confirm (`yes`/`y`) or deny (`no`/`n`) the chatbot's interpretation. Type `quit` or `exit` to stop.

**Examples:**

* `Schedule "Review Meeting" next Monday 11am-11:30am`
* `Book dentist appointment tomorrow 4pm`

