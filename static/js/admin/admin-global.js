

// --- Toast/notification system for admin ---
(function(){
    function initToasts(){
        window.showToast = function(message = "", type = "info", timeout = 4000) {
            try {
                const container = document.getElementById("global-toast");
                const msg = document.getElementById("global-toast-message");
                const closeBtn = document.getElementById("global-toast-close");
                if (!container || !msg) return;

                // Extract and improve error messages
                let displayMessage = message;
                if (type === "error" && message) {
                    displayMessage = window.improveErrorMessage(message);
                }
                
                msg.textContent = displayMessage || (type === "error" ? "An error occurred" : "Notice");
                container.classList.remove('error');
                if (type === 'error') container.classList.add('error');
                container.removeAttribute('hidden');
                container.classList.add('toast-show');

                let timer = setTimeout(()=>{
                    container.classList.remove('toast-show');
                    container.setAttribute('hidden', '');
                }, timeout);

                closeBtn.onclick = function(){
                    clearTimeout(timer);
                    container.classList.remove('toast-show');
                    container.setAttribute('hidden', '');
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
                'Network error': 'Failed to connect to server. Please check your internet connection.',
                'Failed to communicate with the server': 'Unable to reach the server. Please try again.',
                'Unauthorized': 'You are not authorized to perform this action.',
                'Forbidden': 'Access denied. You lack the required permissions.',
                'Not found': 'The requested item was not found. It may have been deleted.',
                'Internal server error': 'Server error. Please try again later.',
                'Too many requests': 'Too many requests. Please wait before trying again.',
                'Bad request': 'Invalid request format. Please check your input.',
                'CSRF': 'Security validation failed. Please refresh and try again.',
                'timeout': 'Request timed out. Please check your connection.',
                'duplicate': 'This item already exists.',
                'required': 'Required fields are missing.',
                'invalid': 'Invalid input provided.',
                'file too large': 'File exceeds maximum size limit.',
                'permission denied': 'You do not have permission for this action.',
                'blog.*not found': 'Blog post not found.',
                'project.*not found': 'Project not found.'
            };
            
            // Check if error matches any known pattern (case-insensitive)
            for (const [key, value] of Object.entries(errorMap)) {
                const regex = new RegExp(key, 'i');
                if (regex.test(error)) {
                    return value;
                }
            }
            
            // Default: return original error if no match
            return error || 'An unexpected error occurred. Please try again.';
        };

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
})()

