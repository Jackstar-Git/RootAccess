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
    initFilterToggle();
    initThemeSwitch();
    if (typeof window.initCustomMultiselects === "function") {
        window.initCustomMultiselects();
    }
    if (typeof initBlogSearch === "function") initBlogSearch();
    if (typeof initProjectSearch === "function") initProjectSearch();
}

if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initGlobal);
} else {
    initGlobal();
}

function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return decodeURIComponent(parts.pop().split(';').shift());
    return null;
}

function setCookie(name, value, days = 365) {
    const expires = new Date();
    expires.setTime(expires.getTime() + (days * 24 * 60 * 60 * 1000));
    const secure = window.location.protocol === "https:" ? "; Secure" : "";
    document.cookie = `${name}=${encodeURIComponent(value)}; expires=${expires.toUTCString()}; path=/; SameSite=Lax${secure}`;
}

function hasTrackingConsent() {
    const value = getCookie("hasAcceptedCookies");
    return value === "true" || value === "1" || value === "accepted";
}

function updateCookieBanner() {
    const banner = document.getElementById("privacy-notice");
    if (!banner) return;

    const choice = getCookie("hasAcceptedCookies");
    const hasChoice = choice === "true" || choice === "false" || choice === "accepted" || choice === "rejected" || choice === "1" || choice === "0";
    banner.style.display = hasChoice ? "none" : "flex";
}

window.getCookie = getCookie;
window.setCookie = setCookie;
window.hasTrackingConsent = hasTrackingConsent;
window.updateCookieBanner = updateCookieBanner;

if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", () => {
        updateCookieBanner();

        const acceptButton = document.getElementById("acceptCookies");
        const rejectButton = document.getElementById("rejectCookies");

        if (acceptButton) acceptButton.addEventListener("click", () => {
            setCookie("hasAcceptedCookies", "true");
            updateCookieBanner();
        });

        if (rejectButton) rejectButton.addEventListener("click", () => {
            setCookie("hasAcceptedCookies", "false");
            updateCookieBanner();
        });
    });
}

// Analytics tracking
(function() {
    const startTime = Date.now();
    const url = window.location.pathname;
    const visitorId = btoa(navigator.userAgent).substring(0, 16);
    const sendData = (isHeartbeat = false) => {
        if (!hasTrackingConsent()) return;
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