const urlParams = new URLSearchParams(window.location.search);
const path = urlParams.get("path") || "/";
const root = "uploads";
const inputPath = document.getElementById("address-bar");
let selectedItems = [];

if (inputPath) {
    inputPath.value = path;
}

const getCsrfToken = () => document.getElementById("csrf_token")?.value || "";

async function apiCall(endpoint, method, body = null, isRawBody = false) {
    const options = {
        method,
        headers: {
            "X-CSRFToken": getCsrfToken()
        }
    };

    if (body) {
        if (isRawBody) {
            options.body = body;
        } else {
            options.headers["Content-Type"] = "application/json";
            options.body = JSON.stringify(body);
        }
    }

    const response = await fetch(endpoint, options);
    if (!response.ok) throw new Error(`${method} request to ${endpoint} failed`);
    return response;
}

async function deleteFiles() {
    if (selectedItems.length === 0) return alert("Please select items to delete.");

    if (confirm("Are you sure you want to delete the selected paths?\nTHIS ACTION CAN'T BE UNDONE!")) {
        try {
            await apiCall("/api/files/delete", "DELETE", { path, files: selectedItems, root });
            location.reload();
        } catch (error) {
            console.error("Delete operation failed:", error);
        }
    }
}

async function renamePath() {
    if (selectedItems.length === 0) return alert("Select an item to rename.");

    const newName = prompt("Please enter a new name:");
    if (newName) {
        try {
            await apiCall("/api/files/rename", "POST", {
                path,
                name: selectedItems[0],
                new_name: newName,
                root
            });
            location.reload();
        } catch (error) {
            alert(`Rename operation failed: ${error.message}`);
        }
    }
}

function copyPath() {
    if (selectedItems.length === 0) return alert("Please select a file to copy.");

    const copiedData = { path, file_name: selectedItems[0], root };
    sessionStorage.setItem("copiedFile", JSON.stringify(copiedData));
    alert(`Copied ${selectedItems[0]}.`);
}

async function pastePath() {
    const copiedFile = JSON.parse(sessionStorage.getItem("copiedFile"));
    if (!copiedFile) return alert("No file in clipboard.");

    try {
        await apiCall("/api/files/copy", "POST", {
            path: copiedFile.path,
            file_name: copiedFile.file_name,
            new_path: path,
            root: copiedFile.root
        });
        sessionStorage.removeItem("copiedFile");
        location.reload();
    } catch (error) {
        alert(`Paste operation failed: ${error.message}`);
    }
}

function handleItemSelection(checkbox) {
    if (checkbox.checked) {
        selectedItems.push(checkbox.value);
    } else {
        selectedItems = selectedItems.filter(item => item !== checkbox.value);
    }
}

function getFileIcon(type) {
    const icons = {
        image: 'fa-file-image',
        video: 'fa-file-video',
        audio: 'fa-file-audio',
        archive: 'fa-file-zipper',
        document: 'fa-file-lines',
        folder: 'fa-folder'
    };
    return `<i class="fa-solid ${icons[type] || 'fa-file'}"></i>`;
}

function sortFiles(files, criteria = "name", order = "asc") {
    if (!Array.isArray(files)) return [];

    const folders = files.filter(f => f.type === "folder");
    const items = files.filter(f => f.type !== "folder");

    const compare = (a, b) => {
        let valA = a[criteria];
        let valB = b[criteria];

        if (criteria === "date") {
            valA = new Date(a.last_modified);
            valB = new Date(b.last_modified);
        }

        if (order === "asc") return valA > valB ? 1 : -1;
        return valA < valB ? 1 : -1;
    };

    return [...folders.sort(compare), ...items.sort(compare)];
}

function renderFiles(files) {
    const container = document.getElementById("file-list");
    if (!container) return;

    container.innerHTML = "";
    const displayPath = root !== "/" ? `/${root}${path}` : `${root}${path}`;

    files.forEach(file => {
        const isFolder = file.type === "folder";
        const folderLink = `?path=${path}${path === "/" ? "" : "/"}${file.name}`;
        const fileLink = `${displayPath}${file.name}`;

        const itemHtml = `
            <div class="file-explorer-item">
                <div class="checkbox-column">
                    <input type="checkbox" class="file-checkbox" value="${file.name}" onclick="handleItemSelection(this)">
                </div>
                <div class="file-details">
                    <i class="file-icon">${getFileIcon(file.type)}</i>
                    <a href="${isFolder ? folderLink : fileLink}" class="location-path">${file.name}</a>
                </div>
                <span class="file-date">${file.last_modified}</span>
                <span class="file-type">${file.type}</span>
                <span class="file-size">${isFolder ? "" : (Math.round(file.size / 1024) + " KB")}</span>
            </div>`;
        container.insertAdjacentHTML("beforeend", itemHtml);
    });
}

function uploadFile() {
    const input = document.createElement("input");
    input.type = "file";
    input.multiple = true;

    input.onchange = async e => {
        const formData = new FormData();
        for (let file of e.target.files) {
            formData.append("files[]", file);
        }

        try {
            await apiCall(`/api/files/upload?dir=${path}&root=${root}`, "POST", formData, true);
            location.reload();
        } catch (error) {
            console.error("Upload error:", error);
        }
    };
    input.click();
}

async function createLocation() {
    const folderName = prompt("New folder name:");
    if (folderName) {
        try {
            await apiCall("/api/files/create_folder", "POST", { path, folder_name: folderName, root });
            location.reload();
        } catch (error) {
            alert(error.message);
        }
    }
}

async function displayFiles() {
    try {
        const response = await fetch(`/api/files/list?path=${path}&root=${root}`);
        const files = await response.json();
        if (Array.isArray(files)) {
            renderFiles(sortFiles(files));
        }
    } catch (error) {
        console.error("Failed to load files:", error);
    }
}

function folderUp() {
    const parts = path.split("/").filter(p => p);
    parts.pop();
    window.location.href = `?path=/${parts.join("/")}`;
}

displayFiles();