function filterRequests() {
    const filter = document.getElementById("status-filter").value;
    const requests = document.getElementsByClassName("request-item");

    Array.from(requests).forEach(request => {
        if (filter === "all" || request.getAttribute("data-status") === filter) {
            request.style.display = "flex";
        } else {
            request.style.display = "none";
        }
    });
}

function sortRequests() {
    const sortValue = document.getElementById("sort-options").value;
    const container = document.getElementsByClassName("requests-list")[0];
    const requests = Array.from(container.getElementsByClassName("request-item"));

    const sortedRequests = requests.sort((a, b) => {
        const dateA = new Date(a.getAttribute("data-date"));
        const dateB = new Date(b.getAttribute("data-date"));
        const subjectA = a.querySelector(".request-info h3").innerText.toLowerCase();
        const subjectB = b.querySelector(".request-info h3").innerText.toLowerCase();

        switch (sortValue) {
            case "date-asc":
                return dateA - dateB;
            case "date-desc":
                return dateB - dateA;
            case "name-asc":
                return subjectA.localeCompare(subjectB);
            case "name-desc":
                return subjectB.localeCompare(subjectA);
            default:
                return 0;
        }
    });

    sortedRequests.forEach(request => {
        container.appendChild(request);
    });
}
