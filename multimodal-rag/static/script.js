const messageInput = document.getElementById("messageInput");
const sendBtn = document.getElementById("sendBtn");
const messagesEl = document.getElementById("messages");
const sourcesEl = document.getElementById("sources");

messageInput.addEventListener("keypress", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

sendBtn.addEventListener("click", sendMessage);

async function sendMessage() {
    const message = messageInput.value.trim();
    if (!message) return;

    messageInput.value = "";
    setInputEnabled(false);
    clearSources();

    addBubble("user", escapeHtml(message));

    const loadingId = addBubble("assistant", "<span class='thinking'>Thinking…</span>");

    try {
        const res = await fetch("/api/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message })
        });

        const data = await res.json();

        if (!res.ok || data.error) throw new Error(data.error || `HTTP ${res.status}`);

        removeBubble(loadingId);
        addBubble("assistant", `<p>${escapeHtml(data.answer)}</p>`);

        if (data.references?.length) renderSources(data.references);

    } catch (err) {
        removeBubble(loadingId);
        addBubble("assistant", `<p style="color:#dc2626">Error: ${escapeHtml(err.message)}</p>`);
    } finally {
        setInputEnabled(true);
        messageInput.focus();
        scrollToBottom();
    }
}

function addBubble(role, html) {
    const id = `msg-${Date.now()}-${Math.random().toString(36).slice(2)}`;
    const wrapper = document.createElement("div");
    wrapper.className = `message ${role}`;
    wrapper.id = id;

    const bubble = document.createElement("div");
    bubble.className = "bubble";
    bubble.innerHTML = html;

    wrapper.appendChild(bubble);
    messagesEl.appendChild(wrapper);
    scrollToBottom();
    return id;
}

function removeBubble(id) {
    document.getElementById(id)?.remove();
}

function renderSources(refs) {
    sourcesEl.innerHTML = `<span class="sources-label">Sources</span>`;
    for (const ref of refs) {
        const score = `${(ref.score * 100).toFixed(0)}%`;
        const mediaUrl = `/media/${encodeURIComponent(ref.source)}`;
        let preview = "";
        if (ref.type === "image") {
            preview = `<a href="${mediaUrl}" target="_blank"><img class="source-thumb" src="${mediaUrl}" alt="${escapeHtml(ref.source)}" onerror="this.parentElement.style.display='none'"></a>`;
        } else if (ref.type === "video") {
            preview = `<video class="source-thumb" src="${mediaUrl}" controls muted preload="metadata" onerror="this.style.display='none'"></video>`;
        }
        sourcesEl.innerHTML += `
            <div class="source-item">
                <span class="badge ${ref.type}">${ref.type}</span>
                ${preview}
                <span>${escapeHtml(ref.source)}</span>
                <span>${score}</span>
            </div>`;
    }
    sourcesEl.classList.add("visible");
}

function clearSources() {
    sourcesEl.innerHTML = "";
    sourcesEl.classList.remove("visible");
}

function setInputEnabled(enabled) {
    messageInput.disabled = !enabled;
    sendBtn.disabled = !enabled;
}

function scrollToBottom() {
    messagesEl.scrollTop = messagesEl.scrollHeight;
}

function escapeHtml(text) {
    const d = document.createElement("div");
    d.textContent = text;
    return d.innerHTML;
}
