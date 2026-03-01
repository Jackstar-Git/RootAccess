function applyStyle(style) {
    const textarea = document.getElementById("content");
    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    const selectedText = textarea.value.substring(start, end);

    if (selectedText.length > 0) {
        let markdownSyntax = "";
        switch (style) {
            case "bold":
                markdownSyntax = "**";
                break;
            case "underline":
                markdownSyntax = "__";
                break;
            case "italic":
                markdownSyntax = "*";
                break;
            case "strikethrough":
                markdownSyntax = "~~";
                break;
            case "inlinecode":
                markdownSyntax = "`";
                break;
            default:
                console.error("Unknown style:", style);
                return;
        }

        const newText = `${markdownSyntax}${selectedText}${markdownSyntax}`;
        textarea.value = textarea.value.substring(0, start) + newText + textarea.value.substring(end);
        textarea.setSelectionRange(start + markdownSyntax.length, start + newText.length - markdownSyntax.length);
    }
}

function applyLineStyle(style) {
    const textarea = document.getElementById("content");
    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    const selectedText = textarea.value.substring(start, end);

    const lines = selectedText.split(/\r?\n/);

    if (selectedText.length > 0) {
        let markdownSyntax = "";
        switch (style) {
            case "unordered":
                markdownSyntax = "- ";
                break;
            case "blockquote":
                markdownSyntax = "> ";
                break;
            case "codeblock":
                markdownSyntax = "```\n";
                break;
            case "html":
                break;
            case "h1":
                markdownSyntax = "# ";
                break;
            case "h2":
                markdownSyntax = "## ";
                break;
            case "h3":
                markdownSyntax = "### ";
                break;
            default:
                console.error("Unknown style:", style);
                return;
        }

        if (style === 'html') {
            const newText = `{html}\n${selectedText}\n{/html}\n`;
            textarea.value = textarea.value.substring(0, start) + newText + textarea.value.substring(end);
            textarea.setSelectionRange(start + markdownSyntax.length, start + newText.length - markdownSyntax.length);
        } else if (style === 'codeblock') {
            const newText = `${markdownSyntax}${selectedText}\n${markdownSyntax}`;
            textarea.value = textarea.value.substring(0, start) + newText + textarea.value.substring(end);
            textarea.setSelectionRange(start + markdownSyntax.length, start + newText.length - markdownSyntax.length);
        } else {
            lines.forEach(function (item, index) {
                lines[index] = `${markdownSyntax}${item}\n`;
            });

            const newText = lines.join("");
            textarea.value = textarea.value.substring(0, start) + newText + textarea.value.substring(end);
            textarea.setSelectionRange(start + markdownSyntax.length, start + newText.length - markdownSyntax.length);
        }
    }
};

function textAlign(style) {
    const textarea = document.getElementById("content");
    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    const selectedText = textarea.value.substring(start, end);

    const newText = `{align:${style}}${selectedText}{/align}`;
    textarea.value = textarea.value.substring(0, start) + newText + textarea.value.substring(end);
    textarea.setSelectionRange(start + newText.length - selectedText.length, start + newText.length);
};

function changeColor() {
    const color = document.getElementById("color-picker-input").value;

    const textarea = document.getElementById("content");
    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    const selectedText = textarea.value.substring(start, end);

    const newText = `{color:${color}}${selectedText}{/color}`;
    textarea.value = textarea.value.substring(0, start) + newText + textarea.value.substring(end);
    textarea.setSelectionRange(start + newText.length - selectedText.length, start + newText.length);

    document.querySelector('#color-picker::after').style.color = selectedColor;
};

function addLink() {
    const url = prompt("Enter the URL");
    if (url) {
        const textarea = document.getElementById("content");
        const start = textarea.selectionStart;
        const end = textarea.selectionEnd;
        const selectedText = textarea.value.substring(start, end);
        const linkText = `[${selectedText || url}](${url})`;

        textarea.value = textarea.value.substring(0, start) + linkText + textarea.value.substring(end);
        textarea.setSelectionRange(start + linkText.length, start + linkText.length);
    }
};

function toggleView() {
    const sourceTextarea = document.getElementById("content");
    const outputDiv = document.getElementById("output");
    const toggleViewButton = document.getElementById("toggle-view-button");

    if (sourceTextarea.style.display === "none") {
        toggleViewButton.innerHTML = "<i class='fas fa-eye'></i> Toggle View";
        sourceTextarea.style.display = "block";
        outputDiv.style.display = "none";
    } else {
        toggleViewButton.innerHTML = "<i class='fa-solid fa-pen'></i> Toggle View";
        sourceTextarea.style.display = "none";
        fetch("/api/markdown-to-html/", {
                                method: "POST",
                                body: JSON.stringify({
                                    data: sourceTextarea.value
                                }),
                                headers: {
                                    "Content-type": "application/json; charset=UTF-8"
                                }
                                })
                                .then(response => {
                                    if (!response.ok) {
                                        throw new Error('Network response was not ok');
                                    }
                                    return response.text();
                                })
                                .then(html => {
                                    outputDiv.innerHTML = html;
                                }
        )
        outputDiv.style.display = "block";
    }
}

const productID = document.getElementById("id").value;

document.getElementById("add-image").addEventListener("click", function () {
    const inputList = document.querySelector(".image-input-list");
    const wrapper = document.createElement("div");
    wrapper.classList.add("image-path-wrapper");

    wrapper.innerHTML = `
        <input name="images[]" type="text" class="image-path-input" placeholder="Bildpfad eingeben">
        <a class="delete-image"><i class="fas fa-trash-alt"></i></a>
    `;

    inputList.appendChild(wrapper);
});

document.querySelector(".image-input-list").addEventListener("click", function (event) {
    const deleteButton = event.target.closest(".delete-image");

    if (deleteButton) {
        const wrapper = deleteButton.closest(".image-path-wrapper");
        if (wrapper) {
            wrapper.remove();
        }
    }
});


// Thumbnail upload handler
document.getElementById("thumbnail-upload").addEventListener("change", function (event) {
    const file = event.target.files[0];

    if (file) {
        const reader = new FileReader();

        reader.onload = function (e) {
            const preview = document.getElementById("thumbnail-preview");
            preview.innerHTML = `<img src="${e.target.result}" alt="Thumbnail" class="image-thumb" style="max-height: 200px;">`;
        };

        reader.readAsDataURL(file);
    }
});






