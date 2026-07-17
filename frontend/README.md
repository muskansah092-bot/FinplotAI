# Finplot AI — Frontend

A minimal chat interface for talking to **Agent 5** (the orchestrator). No
build step, no framework, no login — three files, drop them in and open
`index.html`.

```
frontend/
├── index.html   structure
├── style.css    "digital passbook" theme — ledger-line messages, brass ink accent
├── script.js    chat logic + the two spots where you plug in FastAPI
└── README.md
```

## What it does right now

- A chat log styled like ledger entries (not chat bubbles) — matches the
  passbook/statement theme of the rest of the product.
- A `+` button next to the input with two actions:
  - **Upload statement** — accepts `.pdf` / `.csv`, matches Agent 1's input.
  - **Enter transaction manually** — a small form (date, merchant, amount,
    type, category) matching Agent 1's output schema from your notes.
- Sends are currently mocked (`sendToAgent5()` in `script.js` returns a
  canned response after a short delay) so you can click through the whole
  flow before the backend exists.

## Connecting it to your FastAPI orchestrator

Everything you need to change lives at the top and bottom of `script.js`,
inside the block marked `BACKEND INTEGRATION POINT`.

1. **Point it at your server.** Edit the constants near the top:

   ```js
   const API_BASE_URL = "http://localhost:8000";
   const CHAT_ENDPOINT = `${API_BASE_URL}/api/agent5/chat`;
   const UPLOAD_ENDPOINT = `${API_BASE_URL}/api/agent5/upload`;
   ```

2. **Expose Agent 5 over HTTP.** In your FastAPI app (e.g. `crew/main.py`
   or wherever your orchestrator lives), add something like:

   ```python
   from fastapi import FastAPI, UploadFile, File
   from fastapi.middleware.cors import CORSMiddleware
   from pydantic import BaseModel

   app = FastAPI()

   app.add_middleware(
       CORSMiddleware,
       allow_origins=["*"],  # tighten this once you're not on localhost
       allow_methods=["*"],
       allow_headers=["*"],
   )

   class ChatRequest(BaseModel):
       message: str
       manual_entries: list[dict] = []

   @app.post("/api/agent5/chat")
   async def chat(req: ChatRequest):
       reply = run_agent5(req.message, req.manual_entries)  # your orchestrator call
       return {"reply": reply}

   @app.post("/api/agent5/upload")
   async def upload(file: UploadFile = File(...)):
       contents = await file.read()
       result = run_agent1(contents, file.filename)  # passbook/statement parser
       return {"reply": result}
   ```

3. **Swap the mock for the real call.** In `script.js`, inside
   `sendToAgent5()`, uncomment the "Real implementation" block and delete
   (or comment out) the "Mock implementation" block below it.

4. **Serve the frontend.** Easiest option while developing: open
   `index.html` directly in the browser, or serve the folder with:

   ```bash
   python -m http.server 5500 --directory frontend
   ```

   Later, if you'd rather serve it straight from FastAPI, mount it as
   static files:

   ```python
   from fastapi.staticfiles import StaticFiles
   app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
   ```

## Notes / things you'll likely want to tweak

- The manual-entry categories (`shopping`, `food`, `subscription`, `emi`,
  `bnpl`, `other`) mirror the categories in `agent2`'s
  `summarize_transactions` — update both together if that list changes.
- Right now a file upload and a chat message can be sent together (the file
  becomes an attachment chip above the composer). If you'd rather force
  file uploads to be their own step, remove the `attachment-chip-row` flow
  and call `UPLOAD_ENDPOINT` directly from the `+` menu instead.
- Currency is hardcoded to `₹` in the manual-entry summary card in
  `script.js` (`attachmentCardHTML`) — change if needed.
