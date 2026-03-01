function updateCalendar() {
    const selectedMonth = document.getElementById("monthSelect").value;
    const selectedYear = document.getElementById("yearInput").value;

    window.location.href = `?month=${selectedMonth}&year=${selectedYear}#calendarMonthYear`;
}

function openModal(day, month, year) {
    const modal = document.getElementById("modal");
    const modalOverlay = document.getElementById("modalOverlay");
    const modalContent = document.getElementById("modalContent");

    modal.setAttribute("data-day", day);
    modal.setAttribute("data-month", month);
    modal.setAttribute("data-year", year);

    modalContent.innerHTML = `<p>Lade Ereignisse für den ${day}.${month}.${year}...</p>`;
    modal.classList.add("active");
    modalOverlay.classList.add("active");

    fetch(`/api/get-events/?year=${year}&month=${month}&day=${day}`)
        .then(response => {
            if (!response.ok) {
                throw new Error("Fehler beim Abrufen der Daten.");
            }
            return response.json();
        })
        .then(events => {
            modalContent.innerHTML = `<h3>Details für den ${day}.${month}.${year}</h3>`;

            if (events.length === 0) {
                modalContent.innerHTML += `<p>Keine Ereignisse für diesen Tag.</p>`;
            } else {
                const eventList = document.createElement("ul");
                eventList.classList.add("event-list");
                events.forEach(event => {
                    const listItem = document.createElement("li");
                    listItem.innerHTML = `
                        <div>    
                            <strong>${event.name}</strong>
                            <p>${event.description}</p>
                        </div> 
                        <a href="/api/delete-event?id=${event.id}" class="btn delete-btn" onclick="return confirm('Bist du sicher, dass du dieses Event löschen möchtest?')"><i class="fas fa-trash-alt"></i></a>
                    `;
                    eventList.appendChild(listItem);
                });
                modalContent.appendChild(eventList);
            }
        })
        .catch(error => {
            modalContent.innerHTML = `<p>Fehler: ${error.message}</p>`;
        });
}

function closeModal() {
    document.getElementById("modal").classList.remove("active");
    document.getElementById("modalOverlay").classList.remove("active");
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
    form.style.display = form.style.display === "none" ? "block" : "none";
    addEventBtn.style.display = form.style.display === "none" ? "block" : "none";
}


async function submitEvent(event) {
    event.preventDefault();
    const modal = document.getElementById("modal");
    const day = modal.getAttribute("data-day");
    const month = modal.getAttribute("data-month");
    const year = modal.getAttribute("data-year");
    const name = document.getElementById("eventName").value;
    const description = document.getElementById("eventDescription").value;

    if (!year || !month || !day || !name || !description) {
        alert("All fields are required.");
        return;
    }

    const eventData = {
        year: parseInt(year, 10),
        month: parseInt(month, 10),
        day: parseInt(day, 10),
        name,
        description
    };

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

        // Optionally clear the form fields
        document.getElementById("eventName").value = "";
        document.getElementById("eventDescription").value = "";
        window.location.reload()
        alert("Event erfolgreich hinzugefügt!")

    } catch (error) {
        console.error("Error submitting event:", error);
        alert("An error occurred while adding the event.");
    }
}
