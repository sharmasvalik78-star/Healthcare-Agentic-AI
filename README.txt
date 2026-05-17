Healthcare Agentic AI (Educational)

What this is
- A Streamlit web app that provides educational symptom support.
- It uses a simple, safe heuristic implementation of “agents” (triage + diet guidance + medication safety education + consolidated report).
- This app does NOT diagnose and is not medical advice.

Setup
1) Create a virtual environment (recommended)

   python -m venv .venv
   .venv\Scripts\activate

2) Install dependencies

   pip install -r requirements.txt

3) Configure API key (optional for now)
- The current implementation works without an LLM.
- If you later wire Gemini/LLM features, create a `.env` file in the project root:

   GOOGLE_API_KEY=your_key_here

Run the app
- Start Streamlit:

   python -m streamlit run app.py

Notes
- Never paste real personal health identifiers into public/shared logs.
- If you feel seriously unwell or have emergency warning signs, seek urgent/emergency medical help.

