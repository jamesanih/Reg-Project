const chatForm = document.getElementById("chatForm");
const questionInput = document.getElementById("questionInput");
const messagesDiv = document.getElementById("messages");
const sendBtn = document.getElementById("sendBtn");
const chatContainer = document.getElementById("chatContainer");

function scrollToBottom() {
  chatContainer.scrollTop = chatContainer.scrollHeight;
}

function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}

function formatAnswer(text) {
  // Convert markdown-style bold
  let html = escapeHtml(text);
  html = html.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");
  // Convert markdown lists
  html = html.replace(/^- (.+)$/gm, "<li>$1</li>");
  html = html.replace(/(<li>.*<\/li>\n?)+/g, "<ul>$&</ul>");
  // Convert newlines to paragraphs
  html = html
    .split(/\n\n+/)
    .map((p) => `<p>${p.trim()}</p>`)
    .join("");
  html = html.replace(/<p>\s*<ul>/g, "<ul>").replace(/<\/ul>\s*<\/p>/g, "</ul>");
  return html;
}

function createUserMessage(text) {
  return `
    <div class="message user-message">
      <div class="message-avatar">You</div>
      <div class="message-content">
        <p>${escapeHtml(text)}</p>
      </div>
    </div>`;
}

function createLoadingMessage() {
  return `
    <div class="message bot-message" id="loadingMsg">
      <div class="message-avatar">AI</div>
      <div class="message-content">
        <div class="loading">
          <div class="loading-dot"></div>
          <div class="loading-dot"></div>
          <div class="loading-dot"></div>
        </div>
      </div>
    </div>`;
}

function createBotMessage(data) {
  const msgId = "msg-" + Date.now();

  let citationsHtml = "";
  if (data.snippets && data.snippets.length > 0) {
    const cards = data.snippets
      .map(
        (s, i) => `
      <div class="citation-card visible" id="${msgId}-cite-${i}">
        <div class="citation-source">${escapeHtml(s.source)}</div>
        <div class="citation-section">${escapeHtml(s.section)}</div>
        <div class="citation-score">Relevance: ${(s.score * 100).toFixed(1)}%</div>
        <button class="snippet-toggle" onclick="toggleSnippet('${msgId}-snippet-${i}')">Show excerpt</button>
        <div class="citation-snippet" id="${msgId}-snippet-${i}">${escapeHtml(s.text)}</div>
      </div>`
      )
      .join("");

    citationsHtml = `
      <div class="citations-container">
        <div class="citations-header" onclick="toggleCitations('${msgId}')">
          <span class="arrow">&#9654;</span> Sources (${data.snippets.length} documents)
        </div>
        <div id="${msgId}-citations">${cards}</div>
      </div>`;
  }

  let latencyHtml = "";
  if (data.latency_seconds) {
    latencyHtml = `<div class="latency-badge">Response time: ${data.latency_seconds}s</div>`;
  }

  return `
    <div class="message bot-message">
      <div class="message-avatar">AI</div>
      <div class="message-content">
        ${formatAnswer(data.answer)}
        ${citationsHtml}
        ${latencyHtml}
      </div>
    </div>`;
}

function toggleCitations(msgId) {
  const header = event.currentTarget;
  const container = document.getElementById(msgId + "-citations");
  const cards = container.querySelectorAll(".citation-card");

  header.classList.toggle("expanded");
  cards.forEach((card) => card.classList.toggle("visible"));
}

function toggleSnippet(snippetId) {
  const snippet = document.getElementById(snippetId);
  const btn = snippet.previousElementSibling;
  snippet.classList.toggle("visible");
  btn.textContent = snippet.classList.contains("visible")
    ? "Hide excerpt"
    : "Show excerpt";
}

async function sendQuestion(question) {
  sendBtn.disabled = true;
  questionInput.disabled = true;

  // Add user message
  messagesDiv.insertAdjacentHTML("beforeend", createUserMessage(question));
  scrollToBottom();

  // Show loading
  messagesDiv.insertAdjacentHTML("beforeend", createLoadingMessage());
  scrollToBottom();

  try {
    const response = await fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question }),
    });

    const data = await response.json();

    // Remove loading
    const loadingMsg = document.getElementById("loadingMsg");
    if (loadingMsg) loadingMsg.remove();

    if (response.ok) {
      messagesDiv.insertAdjacentHTML("beforeend", createBotMessage(data));
    } else {
      messagesDiv.insertAdjacentHTML(
        "beforeend",
        createBotMessage({
          answer: data.error || "Sorry, something went wrong. Please try again.",
          snippets: [],
        })
      );
    }
  } catch (err) {
    const loadingMsg = document.getElementById("loadingMsg");
    if (loadingMsg) loadingMsg.remove();

    messagesDiv.insertAdjacentHTML(
      "beforeend",
      createBotMessage({
        answer:
          "Sorry, I couldn't connect to the server. Please check your connection and try again.",
        snippets: [],
      })
    );
  }

  scrollToBottom();
  sendBtn.disabled = false;
  questionInput.disabled = false;
  questionInput.focus();
}

chatForm.addEventListener("submit", (e) => {
  e.preventDefault();
  const question = questionInput.value.trim();
  if (!question) return;
  questionInput.value = "";
  sendQuestion(question);
});

// Focus input on load
questionInput.focus();
