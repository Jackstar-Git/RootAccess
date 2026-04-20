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

