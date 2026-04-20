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