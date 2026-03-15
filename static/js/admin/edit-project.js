function applyStyle(style) {
    const textarea = document.getElementById("content");
    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    const selectedText = textarea.value.substring(start, end);

    if (selectedText.length > 0) {
        let openTag = ""; let closeTag = "";
        switch (style) {
            case "bold": openTag = closeTag = "**"; break;
            case "italic": openTag = closeTag = "*"; break;
            case "underline": openTag = closeTag = "_"; break;
            case "strikethrough": openTag = closeTag = "~~"; break;
            case "inlinecode": openTag = closeTag = "`"; break;
            default: return;
        }
        const newText = `${openTag}${selectedText}${closeTag}`;
        textarea.value = textarea.value.substring(0, start) + newText + textarea.value.substring(end);
        textarea.focus();
    }
}

function applyLineStyle(style) {
    const textarea = document.getElementById("content");
    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    const selectedText = textarea.value.substring(start, end);

    if (selectedText.length > 0) {
        let newText = "";
        switch (style) {
            case "codeblock": newText = `\`\`\`\n${selectedText}\n\`\`\``; break;
            default: return;
        }
        textarea.value = textarea.value.substring(0, start) + newText + textarea.value.substring(end);
        textarea.focus();
    }
}

function addLink() {
    const url = prompt("Enter the URL:");
    if (url) {
        const textarea = document.getElementById("content");
        const start = textarea.selectionStart;
        const end = textarea.selectionEnd;
        const selectedText = textarea.value.substring(start, end);
        const linkText = `[${selectedText || "Link Text"}](${url})`;
        textarea.value = textarea.value.substring(0, start) + linkText + textarea.value.substring(end);
    }
}

function toggleView() {
    const sourceTextarea = document.getElementById("content");
    const outputDiv = document.getElementById("preview-output");
    const toggleViewButton = document.getElementById("toggle-view-button");
    const csrfToken = document.getElementById("csrf_token").value;

    if (sourceTextarea.style.display === "none") {
        toggleViewButton.innerHTML = "<i class='fas fa-eye'></i> Preview";
        sourceTextarea.style.display = "block";
        outputDiv.style.display = "none";
    } else {
        toggleViewButton.innerHTML = "<i class='fa-solid fa-pen'></i> Edit";
        sourceTextarea.style.display = "none";
        outputDiv.innerHTML = "<p><em>Rendering...</em></p>";
        outputDiv.style.display = "block";

        fetch("/api/markdown-to-html/", {
            method: "POST",
            body: JSON.stringify({ data: sourceTextarea.value }),
            headers: { 
                "Content-Type": "application/json",
                "X-CSRFToken": csrfToken
            }
        })
        .then(response => response.text())
        .then(html => { outputDiv.innerHTML = html; })
        .catch(err => console.error(err));
    }
}

function addTech() {
    const container = document.getElementById("tech-list");
    const div = document.createElement("div");
    div.classList.add("dynamic-input");
    div.innerHTML = `
        <input name="tech_stack[]" type="text" placeholder="e.g. Python, React" required>
        <button type="button" class="btn-remove-author" onclick="this.parentElement.remove()" title="Remove">
            <i class="fas fa-times"></i>
        </button>
    `;
    container.appendChild(div);
}

document.addEventListener("DOMContentLoaded", () => {
    const thumbUpload = document.getElementById("thumbnail-upload");
    const dropZone = document.getElementById("drop-zone");

    if (thumbUpload && dropZone) {
        dropZone.addEventListener("click", () => thumbUpload.click());
        thumbUpload.addEventListener("change", (e) => {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = (ev) => {
                    document.getElementById("thumbnail-preview").innerHTML = 
                        `<img src="${ev.target.result}" style="max-width:100%; border-radius:8px;">`;
                };
                reader.readAsDataURL(file);
            }
        });
    }
});