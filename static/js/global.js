function updateFooterYear() {
    const currentDate = new Date();
    const displayElement = document.querySelector("#displayYear");
    if (displayElement) {
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

    const saved = localStorage.getItem("theme");
    const initial = saved || (window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
    applyMode(initial);

    switches.forEach(s => s.addEventListener("click", toggleTheme));
}

function initGlobal() {
    updateFooterYear();
    handlePrivacyBanner();
    initFilterToggle();
    initThemeSwitch();

    if (typeof initBlogSearch === "function") {
        initBlogSearch();
    }
}
if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initGlobal);
} else {
    initGlobal();
}


(function() {
    const startTime = Date.now();
    const url = window.location.pathname;
    const visitorId = btoa(navigator.userAgent).substring(0, 16);

    const sendData = (isHeartbeat = false) => {
        const endTime = Date.now();
        const timeSpent = isHeartbeat ? (endTime - startTime) / 1000 : 0;

        const payload = JSON.stringify({
            url: url,
            visitor_id: visitorId,
            time_spent: timeSpent,
            is_heartbeat: isHeartbeat
        });

        if (isHeartbeat && navigator.sendBeacon) {
            const blob = new Blob([payload], { type: "application/json" });
            navigator.sendBeacon("/api/analytics/track", blob);
        } else {
            fetch("/api/analytics/track", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: payload
            }).catch(() => {}); 
        }
    };

    sendData(false);

    document.addEventListener("visibilitychange", () => {
        if (document.visibilityState === "hidden") {
            sendData(true);
        }
    });
})();