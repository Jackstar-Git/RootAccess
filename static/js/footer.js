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

function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(";").shift();
}

document.addEventListener("DOMContentLoaded", () => {
    updateFooterYear();

    const privacyNotice = document.getElementById("privacy-notice");
    const acceptBtn = document.getElementById("acceptCookies");

    if (!getCookie("cookiesAccepted") && privacyNotice) {
        privacyNotice.style.display = "flex";
    }

    if (acceptBtn && privacyNotice) {
        acceptBtn.addEventListener("click", () => {
            privacyNotice.style.transform = "translate(-50%, 150%)";
            setTimeout(() => { privacyNotice.style.display = "none"; }, 600);

            document.cookie = "cookiesAccepted=true; path=/; max-age=" + 60 * 60 * 24 * 365;
        });
    }
});