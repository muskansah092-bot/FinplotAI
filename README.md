# FinplotAI

CrewAI-based financial assistant with five AI agents for expense analysis,
financial health assessment, savings planning, investment education, and
personalized recommendations.

## Free deployment

- Deploy the FastAPI backend on Render using `render.yaml`.
- Deploy the files in `frontend/` as a Hugging Face Static Space.
- Set `GEMINI_API_KEY` as a secret in Render. Do not commit API keys.
- Set `API_BASE_URL` in `frontend/script.js` to the Render service URL.

The free backend uses temporary storage. Uploaded statements and generated
files may be lost when the service restarts; avoid uploading sensitive data.
