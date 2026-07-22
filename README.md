# FinplotAI
CrewAI-based Financial Assistant with 5 AI agents for expense analysis, financial health assessment, savings planning, investment education, and personalized recommendations.

## Setup & Installation

1. Clone/download the repository and open a terminal in the project root.

2. Create and activate a virtual environment:
```bash
   python -m venv venv
```
   Then activate it:
```bash
   # Windows
   venv\Scripts\activate

   # Mac/Linux
   source venv/bin/activate
```

3. Install dependencies:
```bash
   pip install -r requirements.txt
```

4. Copy `.env.example` to `.env` and add your Gemini API key under both:
   GOOGLE_API_KEY=your_gemini_api_key_here
   GEMINI_API_KEY=your_gemini_api_key_here

5. Run the pre-flight check to confirm every agent, package, and the API key are wired correctly:
```bash
   python scripts/preflight_check.py
```

6. Start the server:
```bash
   uvicorn agent5.main:app --reload --port 8000
```

7. Open [http://localhost:8000/](http://localhost:8000/) in a browser — the frontend is served directly by the same FastAPI app, so no separate frontend server is needed.
