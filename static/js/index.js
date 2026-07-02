function initHeroTilt() {
    const wrapper = document.querySelector(".hero-3d-wrapper");
    if (!wrapper) return;

    document.addEventListener("mousemove", (e) => {
        let xAxis = (window.innerWidth / 2 - e.pageX) / 25;
        let yAxis = (window.innerHeight / 2 - e.pageY) / 25;
        wrapper.style.transform = `rotateY(${-xAxis}deg) rotateX(${yAxis}deg)`;
    });

    document.addEventListener("mouseleave", () => {
        wrapper.style.transform = `rotateY(0deg) rotateX(0deg)`;
        wrapper.style.transition = "all 0.5s ease";
    });

    document.addEventListener("mouseenter", () => {
        wrapper.style.transition = "none";
    });
}

function calculateDaysSinceStart() {
    const startDate = new Date("2021-07-25");
    const currentDate = new Date();
    const timeDiff = currentDate - startDate;
    const daysDiff = Math.floor(timeDiff / (1000 * 60 * 60 * 24));
    return daysDiff;
}

function roundDownToHalfYear(days) {
    const daysInHalfYear = 182.5;
    return Math.floor(days / daysInHalfYear) * 0.5;
}

function initTerminalLogs() {
    const terminalBody = document.getElementById("terminal-logs");
    const promptLine = document.getElementById("terminal-prompt");
    const terminalInput = document.getElementById("terminal-input");
    const heroCard = document.querySelector(".hero-3d-card");
    if (!terminalBody) return;

    const availableThemes = ["light", "dark", "barrel-roll", "matrix", "high-contrast", "midnight-neo", "wild-west", "brutalism", "abstract", "pride"];

    const logs = [
        "[INFO] Booting sequence initiated...",
        "[OK] Python backend established.",
        "[WARN] Frontend styling is experimental.",
        "[INFO] Fetching Austrian coffee reserves...",
        "[OK] Caffeine levels at 100%.",
        "[ERROR] Off-by-one error encountered.",
        "[INFO] Ignoring error and continuing...",
        "[SUCCESS] Root.Access granted."
    ];

    let logIndex = 0;

    function typeLog() {
        if (logIndex < logs.length) {
            const line = document.createElement("div");
            line.className = "log-line";
            const text = logs[logIndex];
            
            if (text.includes("[ERROR]")) line.style.color = "#ff5555";
            else if (text.includes("[WARN]")) line.style.color = "#ffb86c";
            else if (text.includes("[OK]") || text.includes("[SUCCESS]")) line.style.color = "#50fa7b";
            else line.style.color = "#f8f8f2";

            line.textContent = text;
            terminalBody.insertBefore(line, promptLine);
            terminalBody.scrollTop = terminalBody.scrollHeight;
            logIndex++;
            setTimeout(typeLog, Math.random() * 500 + 150);
        } else if (promptLine) {
            promptLine.style.display = "flex";
            terminalBody.scrollTop = terminalBody.scrollHeight;
        }
    }

    setTimeout(typeLog, 500);

    if (terminalInput) {
        terminalInput.addEventListener("keydown", function(e) {
            if (e.key === "Enter") {
                const val = this.value.trim();
                const cmd = val.toLowerCase();
                if (val === "") return;

                const inputRecord = document.createElement("div");
                inputRecord.className = "log-line";
                inputRecord.style.color = "#f8f8f2";
                inputRecord.textContent = "➜ ~ " + val;
                terminalBody.insertBefore(inputRecord, promptLine);

                const responseLine = document.createElement("div");
                responseLine.className = "log-line";
                responseLine.style.color = "#8be9fd";

                if (cmd.startsWith("sudo theme")) {
                    const themeName = cmd.split(" ")[2];
                    if (themeName === "--list") {
                        responseLine.textContent = `Themes: ${availableThemes.join(", ")}`;
                    } else if (themeName === "reset") {
                        document.documentElement.setAttribute("data-theme", "light");
                        localStorage.removeItem("active-theme");
                        responseLine.textContent = "Theme reset to default.";
                    } else if (availableThemes.includes(themeName)) {
                        document.documentElement.setAttribute("data-theme", themeName);
                        localStorage.setItem("active-theme", themeName);
                        responseLine.textContent = `Theme switched to: ${themeName}`;
                    } else {
                        responseLine.textContent = "Usage: sudo theme [name] | --list | reset";
                    }
                } else if (cmd === "sudo barrelroll") {
                    document.body.classList.add("barrel-roll");
                    setTimeout(() => document.body.classList.remove("barrel-roll"), 2000);
                    responseLine.textContent = "Executing barrel roll...";
                } else if (cmd === "sudo matrix") {
                    document.body.classList.toggle("matrix-mode");
                    const isMatrix = document.body.classList.contains("matrix-mode");
                    responseLine.style.color = "#00ff00";
                    responseLine.textContent = isMatrix ? "[CRITICAL] Matrix active." : "[INFO] Reality restored.";
                } else {
                    responseLine.textContent = `bash: ${val}: command not found`;
                }

                terminalBody.insertBefore(responseLine, promptLine);
                this.value = "";
                terminalBody.scrollTop = terminalBody.scrollHeight;
            }
        });

        if (heroCard) heroCard.addEventListener("click", () => terminalInput.focus());
    }
}

document.addEventListener("DOMContentLoaded", () => {
    initHeroTilt();
    initTerminalLogs();
    const daysPassed = calculateDaysSinceStart();
    const yearsExpElement = document.getElementById("years-of-experience");
    if (yearsExpElement) yearsExpElement.textContent = `${roundDownToHalfYear(daysPassed)}+`;
});