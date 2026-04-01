/**
 * Applies inline markdown styling to selected text.
 */
function applyStyle(style) {
    const textarea = document.getElementById("content");
    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    const selectedText = textarea.value.substring(start, end);

    if (selectedText.length > 0) {
        let openTag = "";
        let closeTag = "";

        switch (style) {
            case "bold": openTag = closeTag = "**"; break;
            case "italic": openTag = closeTag = "*"; break;
            case "underline": openTag = closeTag = "_"; break;
            case "strikethrough": openTag = closeTag = "~~"; break;
            case "inlinecode": openTag = closeTag = "`"; break;
            case "superscript": 
                openTag = "[^"; 
                closeTag = "]"; 
                break;
            case "subscript": 
                openTag = "[_"; 
                closeTag = "]"; 
                break;
            default: return;
        }

        const newText = `${openTag}${selectedText}${closeTag}`;
        textarea.value = textarea.value.substring(0, start) + newText + textarea.value.substring(end);
        textarea.focus();
        textarea.setSelectionRange(start + openTag.length, start + openTag.length + selectedText.length);
    }
}

/**
 * Applies block-level or line-based markdown styling.
 */
function applyLineStyle(style) {
    const textarea = document.getElementById("content");
    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    const selectedText = textarea.value.substring(start, end);

    if (selectedText.length > 0) {
        let newText = "";
        switch (style) {
            case "blockquote":
                newText = selectedText.split('\n').map(line => `> ${line}`).join('\n');
                break;
            case "codeblock":
                newText = `\`\`\`\n${selectedText}\n\`\`\``;
                break;
            case "html":
                newText = `{html}\n${selectedText}\n{/html}`;
                break;
            case "h1": newText = `# ${selectedText}`; break;
            case "h2": newText = `## ${selectedText}`; break;
            case "h3": newText = `### ${selectedText}`; break;
            case "unordered":
                newText = selectedText.split('\n').map(line => `- ${line}`).join('\n');
                break;
            default: return;
        }

        textarea.value = textarea.value.substring(0, start) + newText + textarea.value.substring(end);
        textarea.focus();
    }
}

function applyColor() {
    const color = prompt("Enter Hex Color (e.g., #ff0000):", "#");
    if (color && color.startsWith("#")) {
        const textarea = document.getElementById("content");
        const start = textarea.selectionStart;
        const end = textarea.selectionEnd;
        const selectedText = textarea.value.substring(start, end);
        
        const newText = `{color:${color}}${selectedText || "text"}{/color}`;
        textarea.value = textarea.value.substring(0, start) + newText + textarea.value.substring(end);
    }
}

function applyAlignment(pos) {
    const textarea = document.getElementById("content");
    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    const selectedText = textarea.value.substring(start, end);
    
    const newText = `{align:${pos}}${selectedText || "text"}{/align}`;
    textarea.value = textarea.value.substring(0, start) + newText + textarea.value.substring(end);
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

/**
 * Toggles between Editor and Preview modes. 
 * Includes CSRF token for backend validation.
 */
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
                "X-CSRFToken": csrfToken // Essential for preventing 400 errors [^2]
            }
        })
        .then(response => {
            if (!response.ok) throw new Error('Preview failed');
            return response.text();
        })
        .then(html => { outputDiv.innerHTML = html; })
        .catch(err => { 
            console.error(err);
            outputDiv.innerHTML = "<p style='color:red;'>Could not render preview. Check console for details.</p>"; 
        });
    }
}

function addAuthor() {
    const container = document.getElementById("author-list");
    const div = document.createElement("div");
    div.classList.add("dynamic-input");
    div.innerHTML = `
        <input name="authors[]" type="text" placeholder="Author Name" required>
        <button type="button" class="btn-remove-author" onclick="this.parentElement.remove()" title="Remove">
            <i class="fas fa-times"></i>
        </button>
    `;
    container.appendChild(div);
}

/**
 * Toggles the visibility of the scheduling group based on blog status
 */
function toggleScheduling() {
    const status = document.getElementById('blog-status');
    const schedulingGroup = document.getElementById('scheduling-group');
    
    if (status && schedulingGroup) {
        if (status.value === 'draft') {
            schedulingGroup.classList.add('active');
        } else {
            schedulingGroup.classList.remove('active');
        }
    }
}

function initScheduling() {
    const statusSelect = document.getElementById('blog-status');
    const scheduledDateInput = document.getElementById('scheduled-date');
    
    // Set minimum date to today
    if (scheduledDateInput) {
        const today = new Date().toISOString().split('T')[0];
        scheduledDateInput.min = today;
    }
    
    // Add event listener for status changes
    if (statusSelect) {
        statusSelect.addEventListener('change', toggleScheduling);
        // Initial toggle on page load
        toggleScheduling();
    }
}

// Global Event Listeners
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
    
    // Initialize scheduling
    initScheduling();
});

