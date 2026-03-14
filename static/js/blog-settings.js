const csrfToken = document.querySelector('input[name="csrf_token"]')?.value || '';

const defaultHeaders = {
    "Content-Type": "application/json",
    "X-CSRFToken": csrfToken
};
async function editTopic(oldName) {
    const newName = prompt("Enter new name for topic:", oldName);
    if(newName && newName.trim() !== "" && newName !== oldName) {
        try {
            const res = await fetch("/api/settings/topics", {
                method: "PUT",
                headers: defaultHeaders,
                body: JSON.stringify({ old_name: oldName, new_name: newName.trim() })
            });
            if(res.ok) window.location.reload();
            else alert("Failed to update topic.");
        } catch(e) { console.error(e); }
    }
}

async function deleteTopic(topicName) {
    if(confirm(`Are you sure you want to delete the topic '${topicName}'?`)) {
        try {
            const res = await fetch("/api/settings/topics", {
                method: "DELETE",
                headers: defaultHeaders,
                body: JSON.stringify({ topic_name: topicName })
            });
            if(res.ok) window.location.reload();
            else alert("Failed to delete topic.");
        } catch(e) { console.error(e); }
    }
}
async function editType(oldName, oldIcon) {
    const newName = prompt("Enter new name for type:", oldName);
    if(!newName || newName.trim() === "") return;
    
    const newIcon = prompt("Enter new icon class for type:", oldIcon);
    if(!newIcon || newIcon.trim() === "") return;

    if(newName !== oldName || newIcon !== oldIcon) {
        try {
            const res = await fetch("/api/settings/types", {
                method: "PUT",
                headers: defaultHeaders,
                body: JSON.stringify({ old_name: oldName, new_name: newName.trim(), new_icon: newIcon.trim() })
            });
            if(res.ok) window.location.reload();
            else alert("Failed to update type.");
        } catch(e) { console.error(e); }
    }
}

async function deleteType(typeName) {
    if(confirm(`Are you sure you want to delete the type '${typeName}'?`)) {
        try {
            const res = await fetch("/api/settings/types", {
                method: "DELETE",
                headers: defaultHeaders,
                body: JSON.stringify({ type_name: typeName })
            });
            if(res.ok) window.location.reload();
            else alert("Failed to delete type.");
        } catch(e) { console.error(e); }
    }
}