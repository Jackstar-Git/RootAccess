async function fetchLogs() {
    try {
        const csrfToken = document.getElementById("csrf_token").value;
        const severity = document.getElementById("severityFilter").value;
        const items = document.getElementById("itemsFilter").value;
        const sorting = document.getElementById("sortingFilter").value;

        const response = await fetch("/api/get-logs", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRF-Token": csrfToken
            },
            body: JSON.stringify({
                severityFilter: severity,
                itemsFilter: items,
                sortingFilter: sorting
            })
        });

        if (!response.ok) {
            throw new Error("Fehler beim Abrufen der Protokolle.");
        }

        const data = await response.json();

        const logsOutput = document.getElementById("logsOutput");
        logsOutput.innerHTML = "";

        data.logs.forEach(log => {
            const lineElement = document.createElement("p");
            lineElement.textContent = log;
            logsOutput.appendChild(lineElement);
        });
    } catch (error) {
        console.error(error);
        const logsOutput = document.getElementById("logsOutput");
        logsOutput.innerHTML = `<p>Fehler: ${error.message}</p>`;
    }
}
