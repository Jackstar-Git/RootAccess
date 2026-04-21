function getTargetTextarea(element) {
    if (!element) return document.getElementById("content");
    const editor = element.closest('.markdown-editor') || document.querySelector('.markdown-editor');
    return editor ? editor.querySelector('textarea') : document.getElementById("content");
}

function updateTextarea(textarea, start, end, newText) {
    const oldScrollTop = textarea.scrollTop;
    textarea.value = textarea.value.substring(0, start) + newText + textarea.value.substring(end);
    textarea.focus();
    
    const newEnd = start + newText.length;
    textarea.setSelectionRange(newEnd, newEnd);
    textarea.scrollTop = oldScrollTop;
}

function applyStyle(style) {
    const textarea = getTargetTextarea(document.activeElement);
    if (!textarea) return;

    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    const selectedText = textarea.value.substring(start, end);

    let openTag = "";
    let closeTag = "";

    switch (style) {
        case "bold": openTag = closeTag = "**"; break;
        case "italic": openTag = closeTag = "*"; break;
        case "underline": openTag = closeTag = "_"; break;
        case "strikethrough": openTag = closeTag = "~~"; break;
        case "inlinecode": openTag = closeTag = "`"; break;
        case "superscript": openTag = "[^"; closeTag = "]"; break;
        case "subscript": openTag = "[_"; closeTag = "]"; break;
        default: return;
    }

    const newText = `${openTag}${selectedText || "text"}${closeTag}`;
    updateTextarea(textarea, start, end, newText);
}

function applyLineStyle(style) {
    const textarea = getTargetTextarea(document.activeElement);
    if (!textarea) return;

    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    const selectedText = textarea.value.substring(start, end);

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
        case "image":
            const imgUrl = prompt("Enter Image URL:");
            if (imgUrl) {
                const alt = prompt("Enter Alt Text:", "image");
                newText = `![${alt}](${imgUrl})`;
            } else return;
            break;
        case "video":
            const vidUrl = prompt("Enter Video URL:");
            if (vidUrl) {
                newText = `[video(${vidUrl})]`;
            } else return;
            break;
        case "indent":
            newText = `{indent}\n${selectedText || "indented text"}\n{/indent}`;
            break;
        case "carousel":
            newText = `{carousel auto=true delay=5000}\n![Alt](/uploads/images/placeholder.jpg)\n{/carousel}`;
            break;
        default: return;
    }

    updateTextarea(textarea, start, end, newText);
}

function applyColor() {
    const color = prompt("Enter Hex Color:", "#");
    if (color && color.startsWith("#")) {
        const textarea = getTargetTextarea(document.activeElement);
        const start = textarea.selectionStart;
        const end = textarea.selectionEnd;
        const selectedText = textarea.value.substring(start, end);
        const newText = `{color:${color}}${selectedText || "text"}{/color}`;
        updateTextarea(textarea, start, end, newText);
    }
}

function applyAlignment(pos) {
    if (!pos) return;
    const textarea = getTargetTextarea(document.activeElement);
    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    const selectedText = textarea.value.substring(start, end);
    const newText = `{align:${pos}}${selectedText || "text"}{/align}`;
    updateTextarea(textarea, start, end, newText);
}

function addLink() {
    const url = prompt("Enter the URL:");
    if (url) {
        const textarea = getTargetTextarea(document.activeElement);
        const start = textarea.selectionStart;
        const end = textarea.selectionEnd;
        const selectedText = textarea.value.substring(start, end);
        const linkText = `[${selectedText || "Link Text"}](${url})`;
        updateTextarea(textarea, start, end, linkText);
    }
}

function toggleMarkdownPreview(buttonElement) {
    const editor = buttonElement.closest('.markdown-editor');
    const sourceTextarea = editor.querySelector('textarea');
    const previewDiv = editor.querySelector('.markdown-preview');
    const previewBody = previewDiv.querySelector('.markdown-body');
    const csrfToken = document.getElementById("csrf_token")?.value;

    if (sourceTextarea.style.display === "none") {
        buttonElement.innerHTML = "<i class='fas fa-eye'></i> Preview";
        sourceTextarea.style.display = "block";
        previewDiv.style.display = "none";
    } else {
        buttonElement.innerHTML = "<i class='fa-solid fa-pen'></i> Edit";
        sourceTextarea.style.display = "none";
        previewBody.innerHTML = "<p><em>Rendering...</em></p>";
        previewDiv.style.display = "block";

        fetch("/api/markdown-to-html/", {
            method: "POST",
            body: JSON.stringify({ data: sourceTextarea.value }),
            headers: { 
                "Content-Type": "application/json",
                ...(csrfToken && { "X-CSRFToken": csrfToken })
            }
        })
        .then(response => response.text())
        .then(html => { previewBody.innerHTML = html; })
        .catch(err => { 
            previewBody.innerHTML = "<p style='color:red;'>Preview failed.</p>"; 
        });
    }
}