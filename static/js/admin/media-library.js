const urlParams = new URLSearchParams(window.location.search);
const path = urlParams.get("path") ? urlParams.get("path") : "/";
const root = "uploads";
const inputPath = document.getElementById("address-bar");
inputPath.value = path;

var selectedItems = [];

async function fetchFiles() {
    try {
        let response = await fetch(`/api/files/get_all?path=${path}`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                root: root
            })
        });
        
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        
        let files = await response.json();

        if (files.error === "Directory not found") {
            window.location.href = `?path=/`;
            alert("Directory not found!");
        }
        else{
            return files;
        }

    } catch (error) {
        console.error('Error fetching files:', error);
        return null;
    }
}

async function deleteFiles() {
    if (confirm("Are you sure you want to delete the selected paths?\nTHIS ACTION CAN'T BE UNDONE!\n\nPress either 'OK' to continue or 'Cancel'")){
        try {
            const response = await fetch("/api/files/delete", {
                method: "DELETE",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    path: path,
                    files: selectedItems,
                    root: root
                })
            });
    
            if (!response.ok) {
                throw new Error("Network response was not ok");
            }
            location.reload();

        } catch (error) {
            console.error('There was a problem with the delete operation:', error);
        }
    } 
}

async function renamePath() {
    const newName = prompt("Please enter a new name for the file/folder!\n\nPress either 'OK' to continue or 'Cancel'");

    if (newName) {
        try {
            const response = await fetch("/api/files/rename", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    path: path,
                    name: selectedItems[0],
                    new_name: newName,
                    root: root
                })
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Unknown error occurred');
            }
            location.reload();
        } catch (error) {
            alert(`There was a problem with the rename operation: ${error.message}`);
        }
    }
}

function copyPath() {
    if (selectedItems.length === 0) {
        alert('Please select a file or folder to copy.');
        return;
    }

    const fileToCopy = selectedItems[0];
    copiedFile = {
        path: path,          
        file_name: fileToCopy,
        root: root
    };

    sessionStorage.setItem('copiedFile', JSON.stringify(copiedFile));

    alert(`File ${fileToCopy} copied. You can now navigate to a new folder and paste it.`);
}

async function pastePath() {
    copiedFile = JSON.parse(sessionStorage.getItem('copiedFile'));

    if (!copiedFile) {
        alert('No file copied. Please copy a file before pasting.');
        return;
    }

    const newLocation = path; 
    
    if (newLocation) {
        try {
            const response = await fetch("/api/files/copy", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    path: copiedFile.path,
                    file_name: copiedFile.file_name, 
                    new_name:  newLocation + "/" + copiedFile.file_name,
                    root: copiedFile.root
                })
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Unknown error occurred');
            }

            alert('File pasted successfully!');
            sessionStorage.removeItem('copiedFile');
            location.reload();

        } catch (error) {
            alert(`There was a problem with the paste operation: ${error.message}`);
        }
    }
}

function folderUp() {
    const pathComponents = path.split("/");
    const newPath = pathComponents.slice(0, -1);

    if (newPath.length <= 1) {
        var newPathStr = "/";
    }
    else {
        var newPathStr = newPath.join("/");
    }
    window.location.href = `?path=${newPathStr}`;
}

function renderFiles(files) {
    const fileListContainer = document.getElementById('file-list');
    fileListContainer.innerHTML = '';

    const filePath = root !== "/" ? `/${root}${path}` : `${root}${path}`;

    files.forEach(file => {
        const fileItem = `
            <div class="file-explorer-item">
                <!-- Added checkbox for selection, moved to the left -->
                <div class="checkbox-column">
                    <input type="checkbox" class="file-checkbox" name="selected_items" value="${file.name}" onclick="handleItemSelection(this)">
                </div>

                <div class="file-details">
                    <i class="file-icon">
                        ${getFileIcon(file.type)}
                    </i>
                    ${file.type === 'folder'
                        ? `<a href="?path=${path}${path === '/' ? "" : "/"}${file.name}" class="location-path">${file.name}</a>`
                        : `<a href="${filePath}${file.name}" class="location-path"">${file.name}</a>`
                    }
                </div>
                <span class="file-date">${file.last_modified}</span>
                <span class="file-type">${file.type}</span>
                <span class="file-size">${file.type === 'folder' ? '' : (file.size ? file.size + ' KB' : '0 KB')}</span>
            </div>
        `;
        fileListContainer.insertAdjacentHTML('beforeend', fileItem);
    });
}

function getFileIcon(type) {
    switch(type) {
        case 'image': return '<i class="fa-solid fa-file-image"></i>';
        case 'video': return '<i class="fa-solid fa-file-video"></i>';
        case 'audio': return '<i class="fa-solid fa-file-audio"></i>';
        case 'archive': return '<i class="fa-solid fa-file-zipper"></i>';
        case 'document': return '<i class="fa-solid fa-file-lines"></i>';
        case 'folder': return '<i class="fa-solid fa-folder"></i>';
        default: return '<i class="fa-solid fa-file"></i>';
    }
}

async function displayFiles() {
    let files = await fetchFiles();
    files = sortFiles(files);
    renderFiles(files);
}

const sortOptions = document.getElementById('sort-options');
sortOptions.addEventListener('change', async (e) => {
    const files = await fetchFiles();  // Re-fetch files
    const [criteria, order] = e.target.value.split('-');
    const x = sortFiles(files, criteria, order);

    renderFiles(x);
});

function sortFiles(files, criteria = 'name', order = 'asc') {
    const folders = files.filter(file => file.type === 'folder');
    const otherFiles = files.filter(file => file.type !== 'folder');

    const sortFunc = (a, b) => {
        if (criteria === 'name') {
            return order === 'asc' ? a.name.localeCompare(b.name) : b.name.localeCompare(a.name);
        } else if (criteria === 'size') {
            return order === 'asc' ? a.size - b.size : b.size - a.size;
        } else if (criteria === 'date') {
            return order === 'asc' ? new Date(a.last_modified) - new Date(b.last_modified) : new Date(b.last_modified) - new Date(a.last_modified);
        }
    };

    const sortedFolders = folders.sort(sortFunc);
    const sortedFiles = otherFiles.sort(sortFunc);

    return [...sortedFolders, ...sortedFiles];

}

// Checkbox selection logic
function handleItemSelection(checkbox) {
    const itemName = checkbox.value;
    if (checkbox.checked) {
        selectedItems.push(itemName);
    } else {
        selectedItems = selectedItems.filter(item => item !== itemName);
    }
    console.log(selectedItems)
}

function selectAllItems() {
    const checkboxes = document.querySelectorAll('.file-checkbox');
    checkboxes.forEach(checkbox => checkbox.checked = true);
    selectedItems = [...checkboxes].map(checkbox => checkbox.value);
    console.log('All items selected:', selectedItems);
}

function navigateToPath() {
    const newPath = inputPath.value;
    window.location.href = `?path=${newPath}`;
}

function uploadFile() {
    let input = document.createElement('input');
    input.type = 'file';
    input.multiple = true; // Allow multiple file uploads

    input.onchange = e => {
        var files = e.target.files;
        var formData = new FormData();

        for (let file of files) {
            formData.append("files[]", file);
        }

        fetch(`/api/files/upload?dir=${path}`, {
            method: "POST",
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            location.reload();
        })
        .catch(error => {
            console.error('Error:', error);
        });
    }
    input.click();
};

async function createLocation() {
    const folderName = prompt("Bitte den Namen des neuen Ordners eingeben!\n\nDrücke 'OK' um fortzufahren oder 'Abbrechen'");

    if (folderName) {
        try {
            const response = await fetch("/api/files/create_folder", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    path: path,
                    folder_name: folderName,
                    root: root
                })
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Unknown error occurred');
            }
            location.reload();
        } catch (error) {
            alert(`There was a problem with the folder creation: ${error.message}`);
        }
    }
}

displayFiles();