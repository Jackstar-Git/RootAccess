async function submitServerSettings() {
    const form = document.getElementById("serverSettingsForm");
    const formData = new FormData(form);
    const csrfToken = document.getElementById("csrf_token").value;

    try {
        const response = await fetch("/admin/settings/server", {
            method: "POST",
            headers: {
                "X-CSRF-Token": csrfToken
            },
            body: formData
        });

        const data = await response.json();

        if (data.success) {
            alert(data.message);
            window.location.reload();
        } else {
            alert("Error: " + data.message);
        }
    } catch (error) {
        console.error("Failed to update settings:", error);
        alert("A server error occurred while updating settings.");
    }
}

async function clearGlobalCache() {
    if (!confirm("Are you sure you want to clear the entire application cache? This affects projects, blogs, settings, and events.")) {
        return;
    }

    const csrfToken = document.getElementById("csrf_token").value;

    try {
        const response = await fetch("/api/clear-cache", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRF-Token": csrfToken
            }
        });

        const data = await response.json();

        if (data.success) {
            alert(data.message);
        } else {
            alert("Error clearing cache: " + data.message);
        }
    } catch (error) {
        console.error("Failed to clear cache:", error);
        alert("A server error occurred while clearing the cache.");
    }
}