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
const txRows = document.getElementById("txRows");
const addRowBtn = document.getElementById("addRowBtn");
const txRowTemplate = document.getElementById("txRowTemplate");

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

// Accepts multiple files at once (statements as PDF/CSV, or photos of a passbook/receipt as images)
fileInput.addEventListener("change", () => {
  const files = Array.from(fileInput.files || []);
  files.forEach((file) => {
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
  // scroll the new row into view within the scrollable form
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
//   POST /api/agent5/chat        { message, manual_entries }  -> { reply: string }
//   POST /api/agent5/upload      multipart/form-data "file"   -> { reply: string }
// Files are uploaded one at a time (one request per file) so
// each can be routed to Agent 1 individually; manual entries
// are batched and sent together with the chat message.
// ---------------------------------------------------------
async function sendToAgent5({ message, attachments }) {
  // ---- Real implementation (uncomment and adjust once FastAPI is ready) ----
  //
  // // 1) Upload any files first (one request per file)
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

  const files = attachments.filter((a) => a.type === "file");
  const manualEntries = attachments.filter((a) => a.type === "manual");

  if (files.length && manualEntries.length) {
    return `Got ${files.length} file${files.length > 1 ? "s" : ""} and ${manualEntries.length} manual ${manualEntries.length > 1 ? "entries" : "entry"}. Once the backend is connected, Agent 1 will parse the files and Agent 5 will fold everything into its answer.`;
  }
  if (files.length) {
    if (files.length === 1) {
      return `Got your ${files[0].fileType.toUpperCase()} file (${files[0].name}). Once the backend is connected, Agent 1 will parse this and Agent 5 will use it to answer your question.`;
    }
    return `Got ${files.length} files (${files.map((f) => f.name).join(", ")}). Once the backend is connected, Agent 1 will parse each of these and Agent 5 will use them to answer your question.`;
  }
  if (manualEntries.length) {
    if (manualEntries.length === 1) {
      const t = manualEntries[0].data;
      return `Logged: ${t.merchant} — ₹${t.amount} (${t.category}) on ${t.date}. This is a placeholder reply — connect Agent 5 to generate a real response.`;
    }
    const total = manualEntries
      .reduce((sum, a) => sum + (parseFloat(a.data.amount) || 0), 0)
      .toFixed(2);
    return `Logged ${manualEntries.length} transactions totalling ₹${total}. This is a placeholder reply — connect Agent 5 to generate a real response.`;
  }
  return `This is a placeholder reply from Finplot AI. Once your FastAPI endpoint is live, this message will come from Agent 5 instead.`;
}
