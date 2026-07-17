/* =========================================================
   Finplot AI — frontend logic
   Everything under "BACKEND INTEGRATION POINTS" is where you
   wire this up to your FastAPI orchestrator (Agent 5). Until
   then, sendToAgent5() returns a mocked response so you can
   demo the UI end to end.
   ========================================================= */

// ---------------------------------------------------------
// BACKEND INTEGRATION POINTS — edit these two constants and
// the sendToAgent5() function once your FastAPI server is up.
// ---------------------------------------------------------
const API_BASE_URL = "http://localhost:8000"; // your FastAPI base URL
const CHAT_ENDPOINT = `${API_BASE_URL}/api/agent5/chat`;       // expects { message, attachments } -> { reply }
const UPLOAD_ENDPOINT = `${API_BASE_URL}/api/agent5/upload`;   // expects multipart/form-data with "file"

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

let entryList = null;       // holder for the message list once chat starts
let pendingAttachments = []; // files / manual entries waiting to be sent with the next message

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

fileInput.addEventListener("change", () => {
  const file = fileInput.files[0];
  if (!file) return;
  const ext = file.name.split(".").pop().toLowerCase();
  pendingAttachments.push({ type: "file", name: file.name, fileType: ext, file });
  renderAttachmentChips();
  fileInput.value = "";
});

// ---------- manual entry modal ----------

manualEntryOption.addEventListener("click", () => {
  closeAttachMenu();
  modalOverlay.classList.add("open");
  document.getElementById("txDate").focus();
});

function closeModal() {
  modalOverlay.classList.remove("open");
  manualEntryForm.reset();
}

modalCloseBtn.addEventListener("click", closeModal);
modalOverlay.addEventListener("click", (e) => {
  if (e.target === modalOverlay) closeModal();
});

manualEntryForm.addEventListener("submit", (e) => {
  e.preventDefault();
  const data = {
    date: document.getElementById("txDate").value,
    merchant: document.getElementById("txMerchant").value,
    amount: document.getElementById("txAmount").value,
    type: document.getElementById("txType").value,
    category: document.getElementById("txCategory").value,
  };
  pendingAttachments.push({ type: "manual", data });
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

newChatBtn.addEventListener("click", () => {
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

composerForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const text = messageInput.value.trim();
  if (!text && pendingAttachments.length === 0) return;

  const attachmentsToSend = [...pendingAttachments];

  // Render the user's message, with a small card per attachment
  let cardHTML = "";
  attachmentsToSend.forEach((att) => { cardHTML += attachmentCardHTML(att); });
  addMessage({ role: "user", text: text || undefined, cardHTML: cardHTML || undefined });

  messageInput.value = "";
  autoGrow();
  pendingAttachments = [];
  renderAttachmentChips();
  sendBtn.disabled = true;

  const typingEntry = addTypingIndicator();

  try {
    const reply = await sendToAgent5({ message: text, attachments: attachmentsToSend });
    typingEntry.querySelector(".entry-text").textContent = reply;
  } catch (err) {
    typingEntry.querySelector(".entry-text").textContent =
      "Something went wrong reaching Finplot AI. Check that the backend is running.";
    console.error(err);
  } finally {
    sendBtn.disabled = false;
  }
});

// ---------------------------------------------------------
// BACKEND INTEGRATION POINT
// Replace the mocked body below with real calls to your
// FastAPI orchestrator once Agent 5 is exposed over HTTP.
//
// Suggested contract:
//   POST /api/agent5/chat        { message: string }        -> { reply: string }
//   POST /api/agent5/upload      multipart/form-data "file"  -> { reply: string }
// If you'd rather send everything (text + files + manual
// entries) in one request, switch CHAT_ENDPOINT to accept
// multipart/form-data instead and build a FormData below.
// ---------------------------------------------------------
async function sendToAgent5({ message, attachments }) {
  // ---- Real implementation (uncomment and adjust once FastAPI is ready) ----
  //
  // // 1) Upload any files first
  // for (const att of attachments.filter(a => a.type === "file")) {
  //   const formData = new FormData();
  //   formData.append("file", att.file);
  //   await fetch(UPLOAD_ENDPOINT, { method: "POST", body: formData });
  // }
  //
  // // 2) Send the chat message (+ any manual entries) to Agent 5
  // const manualEntries = attachments.filter(a => a.type === "manual").map(a => a.data);
  // const res = await fetch(CHAT_ENDPOINT, {
  //   method: "POST",
  //   headers: { "Content-Type": "application/json" },
  //   body: JSON.stringify({ message, manual_entries: manualEntries }),
  // });
  // if (!res.ok) throw new Error(`Agent 5 returned ${res.status}`);
  // const data = await res.json();
  // return data.reply;

  // ---- Mock implementation (demo only — remove once wired up) ----
  await new Promise((resolve) => setTimeout(resolve, 900 + Math.random() * 600));

  if (attachments.some((a) => a.type === "file")) {
    const f = attachments.find((a) => a.type === "file");
    return `Got your ${f.fileType.toUpperCase()} statement (${f.name}). Once the backend is connected, Agent 1 will parse this and Agent 5 will use it to answer your question.`;
  }
  if (attachments.some((a) => a.type === "manual")) {
    const t = attachments.find((a) => a.type === "manual").data;
    return `Logged: ${t.merchant} — ₹${t.amount} (${t.category}) on ${t.date}. This is a placeholder reply — connect Agent 5 to generate a real response.`;
  }
  return `This is a placeholder reply from Finplot AI. Once your FastAPI endpoint is live, this message will come from Agent 5 instead.`;
}
