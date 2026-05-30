async function deletePost(blogId) {
    if (!confirm("Are you sure you want to delete this post permanently?")) return;

    try {
        const response = await fetch(`/api/delete-blog`, {
            credentials: "same-origin",
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.getElementById('csrf_token').value
            },
            body: JSON.stringify({ id: blogId })
        });

        const result = await response.json();
        if (result.success) {
            window.location.href = "/admin/blogs/all";
        } else {
            notify(result.error || 'Error', 'error');
        }
    } catch (err) {
        notify('Failed to communicate with the server.', 'error');
    }
}

// --- Toast/notification system for admin ---
(function(){
    function initToasts(){
        window.showToast = function(message = "", type = "info", timeout = 4000) {
            try {
                const container = document.getElementById('global-toast');
                const msg = document.getElementById('global-toast-message');
                const closeBtn = document.getElementById('global-toast-close');
                if (!container || !msg) return;

                msg.textContent = message || (type === 'error' ? 'An error occurred' : 'Notice');
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

