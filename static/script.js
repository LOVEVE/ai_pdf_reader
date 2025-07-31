// Client‑side logic for the AI PDF Reader

document.addEventListener("DOMContentLoaded", () => {
    const uploadBtn = document.getElementById("uploadBtn");
    const pdfInput = document.getElementById("pdfFile");
    const uploadStatus = document.getElementById("upload-status");
    const previewSection = document.getElementById("preview-section");
    const previewText = document.getElementById("preview-text");
    const chatSection = document.getElementById("chat-section");
    const chatWindow = document.getElementById("chat-window");
    const questionInput = document.getElementById("questionInput");
    const sendBtn = document.getElementById("sendBtn");

    // Handle PDF upload
    uploadBtn.addEventListener("click", async () => {
        const file = pdfInput.files[0];
        if (!file) {
            uploadStatus.textContent = "請選擇一個 PDF 文件。";
            uploadStatus.style.color = "red";
            return;
        }
        uploadStatus.textContent = "正在上傳和解析…";
        uploadStatus.style.color = "#333";
        const formData = new FormData();
        formData.append("file", file);
        try {
            const res = await fetch("/upload", {
                method: "POST",
                body: formData,
            });
            const data = await res.json();
            if (!res.ok) {
                throw new Error(data.error || "上傳失敗");
            }
            uploadStatus.textContent = data.message;
            uploadStatus.style.color = "green";
            // Show preview and chat section
            previewSection.style.display = "block";
            chatSection.style.display = "block";
            previewText.textContent = data.preview;
            chatWindow.innerHTML = "";
        } catch (err) {
            uploadStatus.textContent = err.message;
            uploadStatus.style.color = "red";
        }
    });

    // Handle question sending
    async function sendQuestion() {
        const question = questionInput.value.trim();
        if (!question) {
            return;
        }
        // Display user's question in chat
        appendMessage("user", question);
        questionInput.value = "";
        sendBtn.disabled = true;
        try {
            const res = await fetch("/ask", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ question }),
            });
            const data = await res.json();
            if (!res.ok) {
                throw new Error(data.error || "提問失敗");
            }
            appendMessage("assistant", data.answer);
        } catch (err) {
            appendMessage("assistant", `錯誤：${err.message}`);
        } finally {
            sendBtn.disabled = false;
        }
    }

    sendBtn.addEventListener("click", sendQuestion);
    questionInput.addEventListener("keypress", (ev) => {
        if (ev.key === "Enter") {
            ev.preventDefault();
            sendQuestion();
        }
    });

    function appendMessage(role, content) {
        const msgDiv = document.createElement("div");
        msgDiv.classList.add("chat-message", role);
        msgDiv.textContent = content;
        chatWindow.appendChild(msgDiv);
        // Scroll to bottom
        chatWindow.scrollTop = chatWindow.scrollHeight;
    }
});
