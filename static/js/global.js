function updateFooterYear() {
    const displayElement = document.querySelector("#displayYear");
    if (displayElement) {
        displayElement.innerHTML = new Date().getFullYear();
    }
}

function handlePrivacyBanner() {
    const privacyNotice = document.getElementById("privacy-notice");
    const acceptBtn = document.getElementById("acceptCookies");
    const getCookie = (name) => {
        const parts = (`; ${document.cookie}`).split(`; ${name}=`);
        if (parts.length === 2) return parts.pop().split(";").shift();
    };

    if (!getCookie("cookiesAccepted") && privacyNotice) privacyNotice.style.display = "flex";
    if (acceptBtn && privacyNotice) {
        acceptBtn.addEventListener("click", () => {
            privacyNotice.style.display = "none";
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
        root.setAttribute("data-theme", mode);
        localStorage.setItem("active-theme", mode);
        switches.forEach(s => {
            const thumb = s.querySelector(".switch-thumb");
            const isDark = (mode === "dark");
            s.classList.toggle("dark", isDark);
            if (thumb) thumb.style.transform = isDark ? "translateX(26px)" : "translateX(0)";
        });
    }

    switches.forEach(s => s.addEventListener("click", () => {
        const current = root.getAttribute("data-theme") === "dark" ? "light" : "dark";
        applyMode(current);
    }));
}

function initGlobal() {
    updateFooterYear();
    handlePrivacyBanner();
    initFilterToggle();
    initThemeSwitch();
    if (typeof initBlogSearch === "function") initBlogSearch();
}

if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initGlobal);
} else {
    initGlobal();
}

// Analytics tracking
(function() {
    const startTime = Date.now();
    const url = window.location.pathname;
    const visitorId = btoa(navigator.userAgent).substring(0, 16);
    const sendData = (isHeartbeat = false) => {
        const payload = JSON.stringify({ url, visitor_id: visitorId, time_spent: isHeartbeat ? (Date.now() - startTime) / 1000 : 0, is_heartbeat: isHeartbeat });
        if (isHeartbeat && navigator.sendBeacon) navigator.sendBeacon("/api/analytics/track", new Blob([payload], { type: "application/json" }));
        else fetch("/api/analytics/track", { credentials: "same-origin", method: "POST", headers: { "Content-Type": "application/json" }, body: payload }).catch(() => {});
    };

    window.addEventListener("load", () => {
        sendData(false);
    });

    document.addEventListener("visibilitychange", () => {
        if (document.visibilityState === "hidden") {
            sendData(true);
        }
    });
})();

// Toast Utility
(function(){
    function initToasts(){
        window.showToast = function(message = "", type = "info", timeout = 4000) {
            const container = document.getElementById('global-toast');
            const msg = document.getElementById('global-toast-message');
            if (!container || !msg) return;
            msg.textContent = type === 'error' ? window.improveErrorMessage(message) : message;
            container.classList.toggle('error', type === 'error');
            container.hidden = false;
            container.classList.add('toast-show');
            setTimeout(()=>{ container.classList.remove('toast-show'); container.hidden = true; }, timeout);
        };
        window.improveErrorMessage = (err) => {
            const errorMap = { 'Network error': 'Server connection failed.', 'Unauthorized': 'Access denied.', 'Not found': 'Resource missing.' };
            return errorMap[Object.keys(errorMap).find(k => String(err).includes(k))] || 'An error occurred.';
        };
        document.querySelectorAll('[data-toast]').forEach(el => el.addEventListener('click', () => window.showToast(el.getAttribute('data-toast'), el.getAttribute('data-toast-type'))));
    }
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', initToasts); else initToasts();
})();