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
                credentials: "same-origin",
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: payload
            }).catch(() => {}); 
        }
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

// --- Global toast/snackbar utility (site-wide) ---
(function(){
    function initToasts(){
        window.showToast = function(message = "", type = "info", timeout = 4000) {
            try {
                const container = document.getElementById('global-toast');
                const msg = document.getElementById('global-toast-message');
                const closeBtn = document.getElementById('global-toast-close');
                if (!container || !msg) return;

                // Extract and improve error messages
                let displayMessage = message;
                if (type === 'error' && message) {
                    displayMessage = window.improveErrorMessage(message);
                }
                
                msg.textContent = displayMessage || (type === 'error' ? 'An error occurred' : 'Notice');
                container.classList.remove('error');
                if (type === 'error') container.classList.add('error');
                container.hidden = false;
                container.classList.add('toast-show');

                let timer = setTimeout(()=>{
                    container.classList.remove('toast-show');
                    container.hidden = true;
                }, timeout);

                closeBtn.onclick = function(){
                    clearTimeout(timer);
                    container.classList.remove('toast-show');
                    container.hidden = true;
                };
            } catch (e) {
                console.error(e);
            }
        };
        
        // Helper function to improve error messages
        window.improveErrorMessage = function(error) {
            if (typeof error !== 'string') {
                error = String(error);
            }
            
            // Map of common errors to user-friendly messages
            const errorMap = {
                'Network error': 'Failed to connect to server. Please check your internet connection and try again.',
                'Failed to communicate with the server': 'Unable to reach the server. Please try again later.',
                'Unauthorized': 'You do not have permission to perform this action. Please contact an administrator if you believe this is an error.',
                'Forbidden': 'Access denied. You do not have the required permissions for this action.',
                'Not found': 'The requested resource was not found. It may have been deleted.',
                'Internal server error': 'An unexpected error occurred on the server. Please try again later.',
                'Too many requests': 'Too many requests. Please wait a moment before trying again.',
                'Bad request': 'Invalid request. Please check your input and try again.',
                'CSRF': 'Security validation failed. Please refresh the page and try again.',
                'timeout': 'Request took too long. Please check your connection and try again.',
                'duplicate': 'This item already exists. Please use a different name.',
                'required': 'Required fields are missing. Please fill in all fields.',
                'invalid': 'Invalid input. Please check your data and try again.',
                'file too large': 'The file is too large. Please upload a smaller file.'
            };
            
            // Check if error matches any known pattern (case-insensitive)
            for (const [key, value] of Object.entries(errorMap)) {
                if (error.toLowerCase().includes(key.toLowerCase())) {
                    return value;
                }
            }
            
            // Default: return original error if no match
            return error || 'An unexpected error occurred. Please try again.';
        };

        document.querySelectorAll('[data-toast]').forEach(function(el){
            el.addEventListener('click', function(){
                const msg = el.getAttribute('data-toast') || '';
                const type = el.getAttribute('data-toast-type') || 'info';
                window.showToast(msg, type);
            });
        });

        window.notify = function(message, type='info'){
            if (window.showToast) return window.showToast(message, type);
            try { alert(message); } catch(e){}
        };
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initToasts);
    } else {
        initToasts();
    }
})();