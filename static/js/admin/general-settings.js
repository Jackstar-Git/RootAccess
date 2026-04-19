function togglePasswordVisibility(fieldId) {
    const field = document.getElementById(fieldId);
    const btn = event.currentTarget;
    const icon = btn.querySelector("i");

    if (field.type === "password") {
        field.type = "text";
        icon.classList.remove("fa-eye");
        icon.classList.add("fa-eye-slash");
    } else {
        field.type = "password";
        icon.classList.remove("fa-eye-slash");
        icon.classList.add("fa-eye");
    }
}

function handleTimezoneChange() {
    const timezone = document.getElementById("timezone");
    const customField = document.getElementById("timezone_custom");
    
    if (timezone.value === "custom") {
        customField.style.display = "block";
    } else {
        customField.style.display = "none";
    }
}

async function submitGeneralSettings() {
    const adminPasswordForm = document.getElementById("adminPasswordForm");
    const generalSettingsForm = document.getElementById("generalSettingsForm");
    const adminPassword = document.getElementById("admin_password").value;
    const adminPasswordConfirm = document.getElementById("admin_password_confirm").value;

    if (adminPassword || adminPasswordConfirm) {
        if (adminPassword !== adminPasswordConfirm) {
            alert("Passwords do not match!");
            return;
        }
        if (adminPassword.length < 6) {
            alert("Password must be at least 6 characters long!");
            return;
        }
    }

    const formData = new FormData();
    
    let timezone = document.getElementById("timezone").value;
    if (timezone === "custom") {
        timezone = document.getElementById("timezone_custom").value;
        if (!timezone) {
            alert("Please enter a custom timezone value!");
            return;
        }
    }
    
    formData.append("timezone", timezone);
    formData.append("site_name", document.getElementById("site_name").value);
    formData.append("site_description", document.getElementById("site_description").value);
    
    if (adminPassword) {
        formData.append("admin_password", adminPassword);
    }

    const csrfToken = document.getElementById("csrf_token").value;

    try {
        const response = await fetch("/admin/settings/general", {
            method: "POST",
            headers: {
                "X-CSRF-Token": csrfToken
            },
            body: formData
        });

        const data = await response.json();

        if (data.success) {
            alert(data.message);
            if (adminPassword) {
                document.getElementById("admin_password").value = "";
                document.getElementById("admin_password_confirm").value = "";
            }
            window.location.reload();
        } else {
            alert("Error: " + data.message);
        }
    } catch (error) {
        console.error("Failed to update settings:", error);
        alert("A server error occurred while updating settings.");
    }
}

function toggleFileEditor(fileName) {
    const editor = document.getElementById(`editor-${fileName}`);
    if (editor.style.display === "none" || editor.style.display === "") {
        loadFileContent(fileName);
        editor.style.display = "block";
    } else {
        editor.style.display = "none";
    }
}

async function loadFileContent(fileName) {
    const textarea = document.getElementById(`textarea-${fileName}`);
    const csrfToken = document.getElementById("csrf_token").value;

    try {
        textarea.value = "Loading...";
        const response = await fetch(`/admin/settings/general/file/read/${fileName}`, {
            method: "GET",
            headers: {
                "X-CSRF-Token": csrfToken
            }
        });

        const data = await response.json();

        if (data.success) {
            textarea.value = data.content;
        } else {
            textarea.value = "Error loading file: " + data.message;
        }
    } catch (error) {
        console.error("Failed to load file:", error);
        textarea.value = "Error loading file: " + error.message;
    }
}

async function saveFileContent(fileName) {
    const textarea = document.getElementById(`textarea-${fileName}`);
    const content = textarea.value;
    const csrfToken = document.getElementById("csrf_token").value;

    try {
        const response = await fetch(`/admin/settings/general/file/save/${fileName}`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRF-Token": csrfToken
            },
            body: JSON.stringify({ content: content })
        });

        const data = await response.json();

        if (data.success) {
            alert(data.message);
            toggleFileEditor(fileName);
        } else {
            alert("Error: " + data.message);
        }
    } catch (error) {
        console.error("Failed to save file:", error);
        alert("A server error occurred while saving the file.");
    }
}

async function downloadDataFile(fileName) {
    try {
        const response = await fetch(`/download/data/${fileName}.json`, {
            method: "GET"
        });

        if (!response.ok) {
            alert("Error downloading file");
            return;
        }

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = url;
        link.download = `${fileName}.json`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
    } catch (error) {
        console.error("Failed to download file:", error);
        alert("A server error occurred while downloading the file.");
    }
}

function openUploadDialog(fileName) {
    const fileInput = document.getElementById("fileUploadInput");
    fileInput.dataset.fileName = fileName;
    fileInput.click();
}

async function handleFileUpload(event) {
    const file = event.target.files[0];
    const fileName = event.target.dataset.fileName;
    const csrfToken = document.getElementById("csrf_token").value;

    if (!file) return;

    if (file.type !== "application/json") {
        alert("Please upload a valid JSON file");
        event.target.value = "";
        return;
    }

    const formData = new FormData();
    formData.append("file", file);

    try {
        const response = await fetch(`/admin/settings/general/file/upload/${fileName}`, {
            method: "POST",
            headers: {
                "X-CSRF-Token": csrfToken
            },
            body: formData
        });

        const data = await response.json();

        if (data.success) {
            alert(data.message);
            event.target.value = "";
        } else {
            alert("Error: " + data.message);
        }
    } catch (error) {
        console.error("Failed to upload file:", error);
        alert("A server error occurred while uploading the file.");
    }
}
