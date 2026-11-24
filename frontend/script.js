/* =========================================================
   Finplot AI — frontend logic
   Connected to Agent 5's real FastAPI server on Render.
   ========================================================= */

const API_BASE_URL = "https://finplotai-api.onrender.com";
const CHAT_ENDPOINT = `${API_BASE_URL}/chat/async`;     // POST { session_id, message } -> { job_id, status }
const UPLOAD_ENDPOINT = `${API_BASE_URL}/upload/async`; // POST multipart/form-data -> { job_id, status }
const JOB_ENDPOINT = `${API_BASE_URL}/jobs`;
const RESET_ENDPOINT = `${API_BASE_URL}/reset`;   // POST ?session_id=... -> clears that session's memory

// Agent 5 keeps conversation state in memory, keyed by session_id.
// We generate one per browser tab and reuse it for every message
// until "New entry" is clicked.
let sessionId = crypto.randomUUID();

const chatLog = document.getElementById("chatLog");
const emptyState = document.getElementById("emptyState");
const composerForm = document.getElementById("composerForm");
const messageInput = document.getElementById("messageInput");
const sendBtn = document.getElementById("sendBtn");
const plusBtn = document.getElementById("plusBtn");
const attachMenu = document.getElementById("attachMenu");
const uploadFileOption = document.getElementById("uploadFileOption");
const manualEntryOption = document.getElementById("manualEntryOption");
const fileInput = document.getElementById("fileInput");
const attachmentRow = document.getElementById("attachmentRow");
const newChatBtn = document.getElementById("newChatBtn");

const modalOverlay = document.getElementById("modalOverlay");
const modalCloseBtn = document.getElementById("modalCloseBtn");
const manualEntryForm = document.getElementById("manualEntryForm");
const txRows = document.getElementById("txRows");
const addRowBtn = document.getElementById("addRowBtn");
const txRowTemplate = document.getElementById("txRowTemplate");

let entryList = null;        // holder for the message list once chat starts
let pendingAttachments = [];  // files / manual entries waiting to be sent with the next message

// ---------- helpers ----------

function ensureEntryList() {
  if (entryList) return entryList;
  emptyState.remove();
  entryList = document.createElement("div");
  entryList.className = "entry-list";
  chatLog.appendChild(entryList);
  return entryList;
}

function scrollToBottom() {
  chatLog.scrollTop = chatLog.scrollHeight;
}

function addMessage({ role, text, cardHTML }) {
  const list = ensureEntryList();
  const entry = document.createElement("div");
  entry.className = `entry ${role}`;

  const rule = document.createElement("div");
  rule.className = "entry-rule";

  const body = document.createElement("div");
  body.className = "entry-body";

  const label = document.createElement("div");
  label.className = "entry-label";
  label.textContent = role === "assistant" ? "Finplot AI" : "You";

  const textEl = document.createElement("div");
  textEl.className = "entry-text";
  if (text) textEl.textContent = text;
  if (cardHTML) textEl.insertAdjacentHTML("beforeend", cardHTML);

  body.appendChild(label);
  body.appendChild(textEl);
  entry.appendChild(rule);
  entry.appendChild(body);
  list.appendChild(entry);

  scrollToBottom();
  return entry;
}

function addTypingIndicator() {
  const entry = addMessage({ role: "assistant", text: "" });
  const textEl = entry.querySelector(".entry-text");
  textEl.innerHTML = `<div class="typing-dots"><span></span><span></span><span></span></div>`;
  return entry;
}

function setEntryText(entry, text) {
  entry.querySelector(".entry-text").textContent = text;
}

function attachmentCardHTML(att) {
  if (att.type === "file") {
    return `
      <div class="entry-card">
        <div class="card-title">📎 ${att.name}</div>
        <dl><dt>Type</dt><dd>${att.fileType.toUpperCase()}</dd></dl>
      </div>`;
  }
  if (att.type === "manual") {
    const t = att.data;
    return `
      <div class="entry-card">
        <div class="card-title">🖊 Manual entry</div>
        <dl>
          <dt>date</dt><dd>${t.date}</dd>
          <dt>merchant</dt><dd>${t.merchant}</dd>
          <dt>amount</dt><dd>${t.amount}</dd>
          <dt>type</dt><dd>${t.type}</dd>
          <dt>category</dt><dd>${t.category}</dd>
        </dl>
      </div>`;
  }
  return "";
}

// ---------- attachment chips (shown above composer before sending) ----------

function renderAttachmentChips() {
  attachmentRow.innerHTML = "";
  pendingAttachments.forEach((att, i) => {
    const chip = document.createElement("div");
    chip.className = "attachment-chip";
    const label = att.type === "file" ? att.name : `Manual: ${att.data.merchant}`;
    chip.innerHTML = `<span>${att.type === "file" ? "📎" : "🖊"} ${label}</span>`;
    const removeBtn = document.createElement("button");
    removeBtn.innerHTML = "&times;";
    removeBtn.title = "Remove";
    removeBtn.addEventListener("click", () => {
      pendingAttachments.splice(i, 1);
      renderAttachmentChips();
    });
    chip.appendChild(removeBtn);
    attachmentRow.appendChild(chip);
  });
}

// ---------- + menu ----------

function closeAttachMenu() {
  attachMenu.classList.remove("open");
  plusBtn.setAttribute("aria-expanded", "false");
}

plusBtn.addEventListener("click", (e) => {
  e.stopPropagation();
  const isOpen = attachMenu.classList.toggle("open");
  plusBtn.setAttribute("aria-expanded", String(isOpen));
});

document.addEventListener("click", (e) => {
  if (!attachMenu.contains(e.target) && e.target !== plusBtn) closeAttachMenu();
});

uploadFileOption.addEventListener("click", () => {
  closeAttachMenu();
  fileInput.click();
});

// Accepts multiple files at once (statements as PDF/CSV, or photos of a passbook/receipt as images)
fileInput.addEventListener("change", () => {
  const files = Array.from(fileInput.files || []);
  files.forEach((file) => {
    if (file.size > 10 * 1024 * 1024) {
      addMessage({ role: "assistant", text: `${file.name} is larger than the 10 MB upload limit.` });
      return;
    }
    const ext = file.name.split(".").pop().toLowerCase();
    pendingAttachments.push({ type: "file", name: file.name, fileType: ext, file });
  });
  renderAttachmentChips();
  fileInput.value = "";
});

// ---------- manual entry modal (repeatable rows) ----------

function makeTxRow() {
  const fragment = txRowTemplate.content.cloneNode(true);
  const row = fragment.querySelector(".tx-row");
  row.querySelector(".tx-row-remove").addEventListener("click", () => {
    if (txRows.querySelectorAll(".tx-row").length <= 1) return; // keep at least one row
    row.remove();
    renumberRows();
  });
  return row;
}

function renumberRows() {
  txRows.querySelectorAll(".tx-row").forEach((row, i) => {
    row.querySelector(".tx-row-index").textContent = `Entry ${i + 1}`;
  });
}

function resetTxRows() {
  txRows.innerHTML = "";
  txRows.appendChild(makeTxRow());
  renumberRows();
}

addRowBtn.addEventListener("click", () => {
  txRows.appendChild(makeTxRow());
  renumberRows();
  txRows.lastElementChild.scrollIntoView({ block: "nearest", behavior: "smooth" });
});

manualEntryOption.addEventListener("click", () => {
  closeAttachMenu();
  resetTxRows();
  modalOverlay.classList.add("open");
  txRows.querySelector(".tx-date").focus();
});

function closeModal() {
  modalOverlay.classList.remove("open");
}

modalCloseBtn.addEventListener("click", closeModal);
modalOverlay.addEventListener("click", (e) => {
  if (e.target === modalOverlay) closeModal();
});

manualEntryForm.addEventListener("submit", (e) => {
  e.preventDefault();

  const rows = Array.from(txRows.querySelectorAll(".tx-row"));
  rows.forEach((row) => {
    const data = {
      date: row.querySelector(".tx-date").value,
      merchant: row.querySelector(".tx-merchant").value,
      amount: row.querySelector(".tx-amount").value,
      type: row.querySelector(".tx-type").value,
      category: row.querySelector(".tx-category").value,
    };
    pendingAttachments.push({ type: "manual", data });
  });

  renderAttachmentChips();
  closeModal();
});

// ---------- suggestions ----------

document.querySelectorAll(".suggestion").forEach((btn) => {
  btn.addEventListener("click", () => {
    messageInput.value = btn.dataset.prompt;
    messageInput.focus();
    autoGrow();
  });
});

// ---------- new chat ----------

newChatBtn.addEventListener("click", async () => {
  // Best-effort: clear this session's memory server-side too, so a
  // stray late reply can't land in a chat that looks empty.
  try {
    await fetch(`${RESET_ENDPOINT}?session_id=${encodeURIComponent(sessionId)}`, { method: "POST" });
  } catch (err) {
    console.error("Failed to reset session on the server:", err);
  }

  sessionId = crypto.randomUUID();
  chatLog.innerHTML = "";
  chatLog.appendChild(emptyState);
  entryList = null;
  pendingAttachments = [];
  renderAttachmentChips();
});

// ---------- textarea auto-grow ----------

function autoGrow() {
  messageInput.style.height = "auto";
  messageInput.style.height = Math.min(messageInput.scrollHeight, 160) + "px";
}
messageInput.addEventListener("input", autoGrow);
messageInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    composerForm.requestSubmit();
  }
});

// ---------- send ----------
//
// Agent 5's backend is conversational and stateful, not a single
// request/response call — so a "send" here can turn into several
// real requests:
//
//   1. Each uploaded file goes to POST /upload on its own. Agent 5
//      treats every upload as its own conversational turn (it may
//      immediately run the full analysis, or ask a follow-up
//      question) — so each file gets its own reply, in order.
//   2. Manual transaction entries aren't a separate upload type on
//      the backend — Agent 5 reads them as plain text typed in
//      chat. So manual entries get folded into the message text
//      and sent to POST /chat.
//   3. Typed text with no attachments just goes straight to /chat.

composerForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const text = messageInput.value.trim();
  if (!text && pendingAttachments.length === 0) return;

  const attachmentsToSend = [...pendingAttachments];

  let cardHTML = "";
  attachmentsToSend.forEach((att) => { cardHTML += attachmentCardHTML(att); });
  addMessage({ role: "user", text: text || undefined, cardHTML: cardHTML || undefined });

  messageInput.value = "";
  autoGrow();
  pendingAttachments = [];
  renderAttachmentChips();
  sendBtn.disabled = true;

  try {
    const files = attachmentsToSend.filter((a) => a.type === "file");
    for (const att of files) {
      const typingEntry = addTypingIndicator();
      try {
        const reply = await uploadFile(att.file);
        setEntryText(typingEntry, reply);
      } catch (err) {
        console.error(err);
        setEntryText(typingEntry, `Couldn't process ${att.name}. Check that the backend is running.`);
      }
    }

    const manualEntries = attachmentsToSend.filter((a) => a.type === "manual");
    const combinedMessage = buildCombinedMessage(text, manualEntries);

    if (combinedMessage) {
      const typingEntry = addTypingIndicator();
      try {
        const reply = await sendChatMessage(combinedMessage);
        setEntryText(typingEntry, reply);
      } catch (err) {
        console.error(err);
        setEntryText(typingEntry, "Something went wrong reaching Finplot AI. Check that the backend is running.");
      }
    }
  } finally {
    sendBtn.disabled = false;
  }
});

function buildCombinedMessage(text, manualEntries) {
  const lines = [];
  if (text) lines.push(text);
  manualEntries.forEach((att) => {
    const t = att.data;
    lines.push(`Transaction: ${t.date}, ${t.merchant}, amount ${t.amount}, type ${t.type}, category ${t.category}`);
  });
  return lines.join("\n");
}

async function uploadFile(file) {
  const formData = new FormData();
  formData.append("session_id", sessionId);
  formData.append("file", file);

  const res = await fetchWithTimeout(UPLOAD_ENDPOINT, { method: "POST", body: formData }, 30000);
  if (!res.ok) throw new Error(await responseError(res, "Upload"));
  const data = await res.json();
  return await waitForJob(data.job_id);
}

async function sendChatMessage(message) {
  const res = await fetchWithTimeout(CHAT_ENDPOINT, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ session_id: sessionId, message }),
  }, 30000);
  if (!res.ok) throw new Error(await responseError(res, "Chat"));
  const data = await res.json();
  return await waitForJob(data.job_id);
}

async function waitForJob(jobId) {
  const deadline = Date.now() + 300000;
  while (Date.now() < deadline) {
    const res = await fetchWithTimeout(`${JOB_ENDPOINT}/${encodeURIComponent(jobId)}`, {}, 30000);
    if (!res.ok) throw new Error(await responseError(res, "Processing"));
    const job = await res.json();
    if (job.status === "completed") return job.result.text;
    if (job.status === "failed") throw new Error(job.error || "Processing failed.");
    await new Promise((resolve) => setTimeout(resolve, 1000));
  }
  throw new Error("Processing took too long. Please try again.");
}

async function fetchWithTimeout(url, options, timeoutMs) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);
  try {
    return await fetch(url, { ...options, signal: controller.signal });
  } catch (err) {
    if (err && err.name === "AbortError") {
      throw new Error("The request timed out. The server may be starting or busy; please try again.");
    }
    throw new Error("Could not connect to the backend. Check your internet connection and try again.");
  } finally {
    clearTimeout(timer);
  }
}

async function responseError(res, operation) {
  let detail = "";
  try {
    const data = await res.json();
    detail = typeof data.detail === "string" ? data.detail : JSON.stringify(data.detail);
  } catch (_) {}
  return `${operation} failed (${res.status})${detail ? `: ${detail}` : "."}`;
}