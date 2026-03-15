const csrfToken = document.getElementById("csrf_token")?.value || '';

const defaultHeaders = {
    "Content-Type": "application/json",
    "X-CSRFToken": csrfToken
};

async function markAsRead(id) {
    try {
        const res = await fetch("/api/admin/contacts/read", {
            method: "POST",
            headers: defaultHeaders,
            body: JSON.stringify({ id: id })
        });
        if(res.ok) window.location.reload();
        else alert("Failed to mark request as read.");
    } catch(e) { console.error(e); }
}

async function deleteContact(id) {
    if(confirm(`Are you sure you want to permanently delete this contact request?`)) {
        try {
            const res = await fetch("/api/admin/contacts/delete", {
                method: "POST",
                headers: defaultHeaders,
                body: JSON.stringify({ id: id })
            });
            if(res.ok) window.location.reload();
            else alert("Failed to delete contact request.");
        } catch(e) { console.error(e); }
    }
}