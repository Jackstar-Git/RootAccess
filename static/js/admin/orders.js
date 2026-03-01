function filterOrders() {
    const filter = document.getElementById("status-filter").value;
    const orders = document.getElementsByClassName("order-item");

    Array.from(orders).forEach(order => {
        if (filter === "all" || order.getAttribute("data-status") === filter) {
            order.style.display = "flex";
        } else {
            order.style.display = "none";
        }
    });
}

function sortOrders() {
    const sortValue = document.getElementById("sort-options").value;
    const container = document.getElementsByClassName("orders-list")[0];
    const orders = Array.from(container.getElementsByClassName("order-item"));

    const sortedOrders = orders.sort((a, b) => {
        const dateA = new Date(a.getAttribute("data-date"));
        const dateB = new Date(b.getAttribute("data-date"));
        const nameA = a.getAttribute("data-name").toLowerCase();
        const nameB = b.getAttribute("data-name").toLowerCase();
        const priceA = parseFloat(a.getAttribute("data-price"));
        const priceB = parseFloat(b.getAttribute("data-price"));

        switch (sortValue) {
            case "date-asc":
                return dateA - dateB;
            case "date-desc":
                return dateB - dateA;
            case "name-asc":
                return nameA.localeCompare(nameB);
            case "name-desc":
                return nameB.localeCompare(nameA);
            case "price-asc":
                return priceA - priceB;
            case "price-desc":
                return priceB - priceA;
            default:
                return 0;
        }
    });

    sortedOrders.forEach(order => {
        container.appendChild(order);
    });
}
