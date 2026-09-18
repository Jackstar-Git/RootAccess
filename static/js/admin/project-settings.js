const csrfToken = document.querySelector('input[name="csrf_token"]')?.value || '';

const defaultHeaders = {
    "Content-Type": "application/json",
    "X-CSRFToken": csrfToken
};

async function editTopic(oldName) {
    const newName = prompt("Enter new name for topic:", oldName);
    if (newName && newName.trim() !== "" && newName !== oldName) {
        try {
            const res = await fetch("/api/settings/project-topics", {
                credentials: "same-origin",
                method: "PUT",
                headers: defaultHeaders,
                body: JSON.stringify({ old_name: oldName, new_name: newName.trim() })
            });
            if (res.ok) window.location.reload();
            else notify("Failed to update topic.", 'error');
        } catch (e) {
            console.error(e);
        }
    }
}

async function deleteTopic(topicName) {
    if (confirm(`Are you sure you want to delete the topic '${topicName}'?`)) {
        try {
            const res = await fetch("/api/settings/project-topics", {
                credentials: "same-origin",
                method: "DELETE",
                headers: defaultHeaders,
                body: JSON.stringify({ topic_name: topicName })
            });
            if (res.ok) window.location.reload();
            else notify("Failed to delete topic.", 'error');
        } catch (e) {
            console.error(e);
        }
    }
}
