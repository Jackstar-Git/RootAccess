function updateFooterYear() {
    const currentDate = new Date();
    const currentYear = currentDate.getFullYear();
    const monthNames = ["January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"];
    const currentMonth = currentDate.getMonth();

    const displayElement = document.querySelector("#displayYear");
    if (displayElement) {
        displayElement.innerHTML = `${monthNames[currentMonth]} ${currentYear}`;
    }
}

document.addEventListener("DOMContentLoaded", () => {
    updateFooterYear();
});