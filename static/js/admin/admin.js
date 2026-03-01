function updateProgressBar(progressElement, value) {
    progressElement.value = value;

    if (value <= 60) {
        progressElement.classList.add("low");
        progressElement.classList.remove("medium", "high", "very-high");
    } else if (value <= 80) {
        progressElement.classList.add("medium");
        progressElement.classList.remove("low", "high", "very-high");
    } else if (value <= 95) {
        progressElement.classList.add("high");
        progressElement.classList.remove("low", "medium", "very-high");
    } else {
        progressElement.classList.add("very-high");
        progressElement.classList.remove("low", "medium", "high");
    }
}

async function fetchSystemUsage() {
    try {
        const response = await fetch("/api/get-system-info/");
        const data = await response.json();

        const cpuBar = document.querySelector("#cpuProgress");
        const cpuPercent = data.cpu_usage.percentage.toFixed(1);
        updateProgressBar(cpuBar, cpuPercent);
        document.getElementById("cpuUsageText").textContent = `${cpuPercent}% der CPU wird genutzt`;

        const ramBar = document.querySelector("#ramProgress");
        const ramPercent = data.ram_usage.percentage.toFixed(1);
        updateProgressBar(ramBar, ramPercent);
        document.getElementById("ramUsageText").textContent = `${ramPercent}% des RAM wird genutzt`;
        document.getElementById("ramAdditionalInfo").textContent = `Verwendet: ${data.ram_usage.used} GB / Gesamt: ${data.ram_usage.total} GB`; // Add additional info for RAM

        const storageBar = document.querySelector("#storageProgress");
        const storagePercent = data.disk_usage.percentage.toFixed(1);
        updateProgressBar(storageBar, storagePercent);
        document.getElementById("storageUsageText").textContent = `${storagePercent}% des Speicherplatzes wird genutzt`;
        document.getElementById("storageAdditionalInfo").textContent = `Verwendet: ${data.disk_usage.used} GB / Gesamt: ${data.disk_usage.total} GB`; // Add additional info for Storage

    } catch (error) {
        console.error("Error fetching system usage:", error);
    }
}

fetchSystemUsage();
