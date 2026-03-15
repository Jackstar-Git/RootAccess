function updateProgressBar(progressElement, value) {
    progressElement.value = value;
    
    // Clean up classes
    progressElement.className = '';
    
    // Re-assign based on value thresholds
    if (value <= 60) {
        progressElement.classList.add("low");
    } else if (value <= 80) {
        progressElement.classList.add("medium");
    } else if (value <= 95) {
        progressElement.classList.add("high");
    } else {
        progressElement.classList.add("very-high");
    }
}

async function fetchSystemUsage() {
    try {
        const response = await fetch("/api/get-system-info/");
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();

        if (!data || !data.cpu_usage || !data.ram_usage || !data.disk_usage) {
            throw new Error("Invalid response structure from server");
        }

        const cpuBar = document.querySelector("#cpuProgress");
        const cpuPercent = data.cpu_usage.percentage.toFixed(1);
        if (cpuBar) {
            updateProgressBar(cpuBar, cpuPercent);
        }
        const cpuText = document.getElementById("cpuUsageText");
        if (cpuText) {
            cpuText.textContent = `${cpuPercent}% CPU utilized`;
        }

        const ramBar = document.querySelector("#ramProgress");
        const ramPercent = data.ram_usage.percentage.toFixed(1);
        if (ramBar) {
            updateProgressBar(ramBar, ramPercent);
        }
        const ramText = document.getElementById("ramUsageText");
        if (ramText) {
            ramText.textContent = `${ramPercent}% RAM utilized`;
        }
        const ramInfo = document.getElementById("ramAdditionalInfo");
        if (ramInfo) {
            ramInfo.textContent = `Used: ${data.ram_usage.used} GB / Total: ${data.ram_usage.total} GB`;
        }

        const storageBar = document.querySelector("#storageProgress");
        const storagePercent = data.disk_usage.percentage.toFixed(1);
        if (storageBar) {
            updateProgressBar(storageBar, storagePercent);
        }
        const storageText = document.getElementById("storageUsageText");
        if (storageText) {
            storageText.textContent = `${storagePercent}% Storage utilized`;
        }
        const storageInfo = document.getElementById("storageAdditionalInfo");
        if (storageInfo) {
            storageInfo.textContent = `Used: ${data.disk_usage.used} GB / Total: ${data.disk_usage.total} GB`;
        }

    } catch (error) {
        console.error("Error fetching system usage:", error);
        const errorElements = document.querySelectorAll(".status-card span");
        errorElements.forEach(el => {
            el.textContent = "Error loading data";
        });
    }
}

// ----- Notes Functions -----

function toggleEditNote() {
    const display = document.getElementById("noteDisplay");
    const editArea = document.getElementById("noteEditArea");
    const editBtn = document.getElementById("editNoteBtn");
    
    if (editArea.classList.contains("hidden-form")) {
        editArea.classList.remove("hidden-form");
        display.style.display = "none";
        editBtn.style.display = "none";
    } else {
        editArea.classList.add("hidden-form");
        display.style.display = "block";
        editBtn.style.display = "inline-block";
    }
}

async function saveNote() {
    const noteContent = document.getElementById("noteTextarea").value;
    const csrfToken = document.getElementById("csrf_token") ? document.getElementById("csrf_token").value : "";
    
    try {
        const response = await fetch("/api/save-note", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRF-Token": csrfToken
            },
            body: JSON.stringify({ note: noteContent })
        });
        
        if (!response.ok) throw new Error("Failed to save note");
        
        const data = await response.json();
        document.getElementById("noteDisplay").innerHTML = data.html;
        toggleEditNote();
        
    } catch (error) {
        alert("Error saving note: " + error.message);
    }
}

// ----- Calendar Functions -----

function updateCalendar() {
    const selectedMonth = document.getElementById("monthSelect").value;
    const selectedYear = document.getElementById("yearInput").value;
    window.location.href = `?month=${selectedMonth}&year=${selectedYear}#calendarMonthYear`;
}

async function openModal(day, month, year) {
    const modal = document.getElementById("modal");
    const modalOverlay = document.getElementById("modalOverlay");
    const modalContent = document.getElementById("modalContent");

    // Store data attributes cleanly
    modal.dataset.day = day;
    modal.dataset.month = month;
    modal.dataset.year = year;

    modalContent.innerHTML = `<p class="loading-message">Loading events for ${year}-${month}-${day}...</p>`;
    modal.classList.add("active");
    modalOverlay.classList.add("active");

    try {
        const response = await fetch(`/api/get-events/?year=${year}&month=${month}&day=${day}`);
        if (!response.ok) throw new Error("Error fetching data.");
        
        const events = await response.json();
        
        if (events.length === 0) {
            modalContent.innerHTML = `<p class="no-events-message">No events scheduled for this day.</p>`;
        } else {
            modalContent.innerHTML = '';
            const eventList = document.createElement("ul");
            eventList.classList.add("event-list");
            
            events.forEach(event => {
                const listItem = document.createElement("li");
                listItem.innerHTML = `
                    <div class="event-details">    
                        <strong>${event.name}</strong>
                        <p>${event.description}</p>
                    </div> 
                    <a href="/api/delete-event?id=${event.id}" class="btn delete-btn" 
                       onclick="return confirm('Are you sure you want to delete this event?')">
                       <i class="fas fa-trash-alt"></i>
                    </a>
                `;
                eventList.appendChild(listItem);
            });
            modalContent.appendChild(eventList);
        }
    } catch (error) {
        modalContent.innerHTML = `<p class="error-message">Error: ${error.message}</p>`;
    }
}

function closeModal() {
    document.getElementById("modal").classList.remove("active");
    document.getElementById("modalOverlay").classList.remove("active");
    
    // Reset form state on close
    document.getElementById("addEventForm").classList.add("hidden-form");
    document.getElementById("addEventBtn").style.display = "block";
}

function changeMonth(offset) {
    const currentMonthYear = document.getElementById("calendarMonthYear").innerText;
    const [currentYear, currentMonth] = currentMonthYear.split('-').map(Number);

    let newMonth = currentMonth + offset;
    let newYear = currentYear;

    if (newMonth > 12) {
        newMonth = 1;
        newYear++;
    } else if (newMonth < 1) {
        newMonth = 12;
        newYear--;
    }

    window.location.href = `?month=${newMonth}&year=${newYear}#calendarMonthYear`;
}

function toggleAddEventForm() {
    const form = document.getElementById("addEventForm");
    const addEventBtn = document.getElementById("addEventBtn");
    
    form.classList.toggle("hidden-form");
    addEventBtn.style.display = form.classList.contains("hidden-form") ? "block" : "none";
}

async function submitEvent(event) {
    event.preventDefault();
    const modal = document.getElementById("modal");
    
    const eventData = {
        year: parseInt(modal.dataset.year, 10),
        month: parseInt(modal.dataset.month, 10),
        day: parseInt(modal.dataset.day, 10),
        name: document.getElementById("eventName").value.trim(),
        description: document.getElementById("eventDescription").value.trim()
    };

    if (!eventData.year || !eventData.month || !eventData.day || !eventData.name || !eventData.description) {
        alert("All fields are required.");
        return;
    }

    try {
        const csrfToken = document.getElementById("csrf_token").value;
        const response = await fetch("/api/add-events/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRF-Token": csrfToken
            },
            body: JSON.stringify(eventData)
        });

        if (!response.ok) {
            const errorData = await response.json();
            alert(`Error: ${errorData.error || "Failed to add the event."}`);
            return;
        }

        alert("Event successfully added!");
        window.location.reload();

    } catch (error) {
        console.error("Error submitting event:", error);
        alert("An error occurred while adding the event.");
    }
}

fetchSystemUsage();