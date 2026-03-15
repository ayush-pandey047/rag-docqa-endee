// DocMind - app.js

const indexedDocs = [];

document.getElementById("docText").addEventListener("input", function () {
    const count = this.value.length;
    document.getElementById("charCount").textContent =
        count.toLocaleString() + " character" + (count !== 1 ? "s" : "");
});

function setStatus(id, message, type, showSpinner) {
    const el = document.getElementById(id);
    el.className = "status-bar " + (type || "");
    if (showSpinner) {
        el.innerHTML = '<div class="spinner"></div>' + message;
    } else {
        el.textContent = message;
    }
}

function showToast(message) {
    const toast = document.getElementById("toast");
    toast.textContent = message;
    toast.classList.add("show");
    setTimeout(() => toast.classList.remove("show"), 3000);
}

async function uploadDocument() {
    const text = document.getElementById("docText").value.trim();
    const name = document.getElementById("docName").value.trim() || "document";
    const btn  = document.getElementById("uploadBtn");

    if (!text) {
        setStatus("uploadStatus", "Please paste some document text first.", "error");
        return;
    }

    btn.disabled = true;
    setStatus("uploadStatus", "Chunking and indexing into Endee...", "loading", true);

    try {
        const response = await fetch("/upload", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text, source_name: name })
        });

        const data = await response.json();

        if (response.ok) {
            setStatus("uploadStatus", data.chunks_created + " chunks stored in Endee.", "success");
            indexedDocs.push({ name, chunks: data.chunks_created });
            renderIndexedList();
            document.getElementById("docText").value = "";
            document.getElementById("charCount").textContent = "0 characters";
            showToast("Document indexed successfully.");
        } else {
            setStatus("uploadStatus", data.detail || "Upload failed.", "error");
        }
    } catch {
        setStatus("uploadStatus", "Could not connect to the server.", "error");
    }

    btn.disabled = false;
}

function renderIndexedList() {
    const container = document.getElementById("indexedList");
    const items     = document.getElementById("indexedItems");
    container.style.display = "block";
    items.innerHTML = indexedDocs.map(doc => `
        <div class="indexed-item">
            <svg width="13" height="13" viewBox="0 0 13 13" fill="none">
                <circle cx="6.5" cy="6.5" r="5.5" stroke="currentColor" stroke-width="1.4"/>
                <path d="M4 6.5l2 2 3-3" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            ${doc.name} &mdash; ${doc.chunks} chunks
        </div>
    `).join("");
}

async function askQuestion() {
    const question = document.getElementById("questionInput").value.trim();
    const btn      = document.getElementById("askBtn");

    if (!question) {
        setStatus("askStatus", "Please type a question first.", "error");
        return;
    }

    btn.disabled = true;
    document.getElementById("answerSection").style.display  = "none";
    document.getElementById("sourcesSection").style.display = "none";
    document.getElementById("emptyState").style.display     = "none";
    setStatus("askStatus", "Searching Endee and generating answer...", "loading", true);

    try {
        const response = await fetch("/ask", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ question })
        });

        const data = await response.json();

        if (response.ok) {
            setStatus("askStatus", "", "");

            const answerSection = document.getElementById("answerSection");
            const answerBody    = document.getElementById("answerBody");
            answerBody.textContent = "";
            answerSection.style.display = "block";

            typeWriter(answerBody, data.answer, 12);

            if (data.sources && data.sources.length > 0) {
                setTimeout(() => renderSources(data.sources), data.answer.length * 12 + 300);
            }
        } else {
            setStatus("askStatus", data.detail || "Something went wrong.", "error");
            document.getElementById("emptyState").style.display = "flex";
        }
    } catch {
        setStatus("askStatus", "Could not connect to the server.", "error");
        document.getElementById("emptyState").style.display = "flex";
    }

    btn.disabled = false;
}

function typeWriter(element, text, speed) {
    let i = 0;
    const interval = setInterval(() => {
        if (i < text.length) {
            element.textContent += text[i];
            i++;
        } else {
            clearInterval(interval);
        }
    }, speed);
}

function renderSources(sources) {
    const section = document.getElementById("sourcesSection");
    const list    = document.getElementById("sourcesList");

    list.innerHTML = sources.map((s, idx) => `
        <div class="source-chip" style="animation-delay:${idx * 0.07}s">
            <div class="source-name">${s.source}</div>
            <div class="source-text">${s.text}</div>
        </div>
    `).join("");

    section.style.display = "block";
}

function handleFileUpload(event) {
    const file = event.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = function(e) {
        document.getElementById("docText").value = e.target.result;
        document.getElementById("docName").value = file.name.replace(/\.[^/.]+$/, "");
        const count = e.target.result.length;
        document.getElementById("charCount").textContent = count.toLocaleString() + " characters";
    };
    reader.readAsText(file);
    document.getElementById("fileNameDisplay").textContent = file.name;
}