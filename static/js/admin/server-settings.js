async function submitServerSettings() {
    const form = document.getElementById("serverSettingsForm");
    const formData = new FormData(form);
    const csrfToken = document.getElementById("csrf_token").value;

    try {
        const response = await fetch("/admin/settings/server", {
            credentials: "same-origin",
            method: "POST",
            headers: {
                "X-CSRF-Token": csrfToken
            },
            body: formData
        });

        const data = await response.json();

        if (data.success) {
            notify(data.message, 'info');
            window.location.reload();
        } else {
            notify("Error: " + data.message, 'error');
        }
    } catch (error) {
        console.error("Failed to update settings:", error);
        notify("A server error occurred while updating settings.", 'error');
    }
}

async function clearGlobalCache() {
    if (!confirm("Are you sure you want to clear the entire application cache? This affects projects, blogs, settings, and events.")) {
        return;
    }

    const csrfToken = document.getElementById("csrf_token").value;

    try {
        const response = await fetch("/api/clear-cache", {
            credentials: "same-origin",
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRF-Token": csrfToken
            }
        });

        const data = await response.json();

        if (data.success) {
            notify(data.message, 'info');
        } else {
            notify("Error clearing cache: " + data.message, 'error');
        }
    } catch (error) {
        console.error("Failed to clear cache:", error);
        notify("A server error occurred while clearing the cache.", 'error');
    }
}