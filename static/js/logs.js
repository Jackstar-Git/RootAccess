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
            throw new Error("Error fetching logs.");
        }

        const data = await response.json();
        const logsOutput = document.getElementById("logsOutput");
        logsOutput.innerHTML = "";

        if (!data.logs || data.logs.length === 0) {
            logsOutput.innerHTML = '<div class="log-empty">No logs available.</div>';
            return;
        }

        data.logs.forEach(log => {
            const lineElement = document.createElement("div");
            lineElement.className = "log-line";
            
            if (log.includes("CRITICAL") || log.includes("ERROR")) {
                lineElement.classList.add("log-error");
            } else if (log.includes("WARNING")) {
                lineElement.classList.add("log-warning");
            } else if (log.includes("INFO")) {
                lineElement.classList.add("log-info");
            } else if (log.includes("DEBUG")) {
                lineElement.classList.add("log-debug");
            }
            
            lineElement.textContent = log;
            logsOutput.appendChild(lineElement);
        });
    } catch (error) {
        console.error(error);
        const logsOutput = document.getElementById("logsOutput");
        logsOutput.innerHTML = `<div class="log-error">Fehler: ${error.message}</div>`;
    }
}

async function clearLogs() {
    if (!confirm("Are you sure you want to permanently delete all logs?")) {
        return;
    }

    try {
        const csrfToken = document.getElementById("csrf_token").value;
        const response = await fetch("/api/clear-logs", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRF-Token": csrfToken
            }
        });

        if (!response.ok) {
            throw new Error("Error loading the logs.");
        }

        fetchLogs();
    } catch (error) {
        console.error(error);
        alert(`Fehler: ${error.message}`);
    }
}

async function sendCommand() {
    const commandInput = document.getElementById("consoleInput");
    const passwordInput = document.getElementById("consolePassword");
    const command = commandInput.value.trim();
    const password = passwordInput.value;
    const csrfToken = document.getElementById("csrf_token").value;

    if (!command) return;

    const logsOutput = document.getElementById("logsOutput");
    
    const cmdEcho = document.createElement("div");
    cmdEcho.className = "log-line log-debug";
    cmdEcho.textContent = `admin@server:~$ ${command}`;
    logsOutput.appendChild(cmdEcho);
    
    logsOutput.scrollTop = logsOutput.scrollHeight;
    
    commandInput.value = "";

    try {
        const response = await fetch("/api/execute-command", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRF-Token": csrfToken
            },
            body: JSON.stringify({
                command: command,
                consolePassword: password
            })
        });

        const data = await response.json();
        
        const resultLine = document.createElement("div");
        resultLine.className = `log-line ${data.status === 'error' ? 'log-error' : 'log-info'}`;
        
        resultLine.style.whiteSpace = "pre-wrap"; 
        resultLine.textContent = data.output;
        
        logsOutput.appendChild(resultLine);
        logsOutput.scrollTop = logsOutput.scrollHeight;

    } catch (error) {
        console.error(error);
        const errorLine = document.createElement("div");
        errorLine.className = "log-line log-error";
        errorLine.textContent = `Systemfehler: ${error.message}`;
        logsOutput.appendChild(errorLine);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    fetchLogs(); 

    const consoleInput = document.getElementById("consoleInput");
    if(consoleInput) {
        consoleInput.addEventListener("keypress", function(event) {
            if (event.key === "Enter") {
                event.preventDefault();
                sendCommand();
            }
        });
    }
});