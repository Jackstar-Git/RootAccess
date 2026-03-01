/* global.js - shared behavior across all pages */

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

function handlePrivacyBanner() {
    const privacyNotice = document.getElementById("privacy-notice");
    const acceptBtn = document.getElementById("acceptCookies");

    function getCookie(name) {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) return parts.pop().split(";").shift();
    }

    // show banner if not accepted
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
}

function initFilterToggle() {
    const filterBtn = document.getElementById("filter-btn");
    const drawer = document.getElementById("filter-drawer");

    if (filterBtn && drawer) {
        filterBtn.addEventListener("click", () => {
            drawer.classList.toggle("active");
            filterBtn.classList.toggle("active");
        });
    }
}

function initHeroTilt() {
    const card = document.getElementById("tilt-card");
    const wrapper = document.querySelector(".hero-3d-wrapper");

    if (card && wrapper) {
        document.addEventListener("mousemove", (e) => {
            let xAxis = (window.innerWidth / 2 - e.pageX) / 25;
            let yAxis = (window.innerHeight / 2 - e.pageY) / 25;

            wrapper.style.transform = `rotateY(${xAxis}deg) rotateX(${yAxis}deg)`;
        });

        document.addEventListener("mouseleave", () => {
            wrapper.style.transform = `rotateY(0deg) rotateX(0deg)`;
            wrapper.style.transition = "all 0.5s ease";
        });

        document.addEventListener("mouseenter", () => {
            wrapper.style.transition = "none";
        });
    }
}

function initThemeSwitch() {
    const switches = document.querySelectorAll(".theme-switch");
    const root = document.documentElement;

    function applyMode(mode) {
        if (mode === "dark") {
            root.setAttribute("data-theme", "dark");
        } else {
            root.removeAttribute("data-theme");
        }
        switches.forEach(s => {
            const thumb = s.querySelector(".switch-thumb");
            if (mode === "dark") {
                s.classList.add("dark");
                if (thumb) thumb.style.transform = "translateX(26px)";
            } else {
                s.classList.remove("dark");
                if (thumb) thumb.style.transform = "translateX(0)";
            }
        });
        try { localStorage.setItem("theme", mode); } catch(e) {}
    }

    function toggleTheme() {
        const current = localStorage.getItem("theme") ||
            (window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
        applyMode(current === "dark" ? "light" : "dark");
    }

    if (switches.length) {
        switches.forEach(s => s.addEventListener("click", toggleTheme));
        const saved = localStorage.getItem("theme");
        const initial = saved ||
            (window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
        applyMode(initial);
    }
}

function initGlobal() {
    updateFooterYear();
    handlePrivacyBanner();
    initFilterToggle();
    initHeroTilt();
    initThemeSwitch();
}

// execute when DOM content loaded
if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initGlobal);
} else {
    initGlobal();
}
