/* global.js - Cleaned and Optimized */

// 1. UI Helpers
function updateFooterYear() {
    const currentDate = new Date();
    const displayElement = document.querySelector("#displayYear");
    if (displayElement) {
        // Displays "Month Year" as per your previous request
        const monthNames = ["January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"];
        displayElement.innerHTML = `${monthNames[currentDate.getMonth()]} ${currentDate.getFullYear()}`;
    }
}

function handlePrivacyBanner() {
    const privacyNotice = document.getElementById("privacy-notice");
    const acceptBtn = document.getElementById("acceptCookies");
    
    const getCookie = (name) => {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) return parts.pop().split(";").shift();
    };

    if (!getCookie("cookiesAccepted") && privacyNotice) {
        privacyNotice.style.display = "flex";
    }

    if (acceptBtn && privacyNotice) {
        acceptBtn.addEventListener("click", () => {
            privacyNotice.style.transform = "translate(-50%, 150%)";
            setTimeout(() => { privacyNotice.style.display = "none"; }, 600);
            document.cookie = "cookiesAccepted=true; path=/; max-age=" + (60 * 60 * 24 * 365);
        });
    }
}

// 2. Component Initializers
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
    const wrapper = document.querySelector(".hero-3d-wrapper");
    if (!wrapper) return;

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

// 3. Theme Logic (Fixed to apply even if no switch is found)
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
        const current = root.getAttribute("data-theme") === "dark" ? "light" : "dark";
        applyMode(current);
    }

    // Initialize Theme
    const saved = localStorage.getItem("theme");
    const initial = saved || (window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
    applyMode(initial);

    // Attach Listeners
    switches.forEach(s => s.addEventListener("click", toggleTheme));
}

// 4. Main Global Loader
function initGlobal() {
    updateFooterYear();
    handlePrivacyBanner();
    initFilterToggle();
    initHeroTilt();
    initThemeSwitch();

    // Safely check if blog search exists (usually in blogs.js)
    if (typeof initBlogSearch === "function") {
        initBlogSearch();
    }
}

// Bootstrapper
if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initGlobal);
} else {
    initGlobal();
}