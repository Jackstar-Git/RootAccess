function createSharePopup() {
    const popup = document.createElement("div");
    popup.className = "share-popup";
    popup.innerHTML = `
        <div class="share-content">
            <h4>Share this article</h4>
            <ul class="share-links">
                <li><a href="#" data-platform="facebook">Facebook</a></li>
                <li><a href="#" data-platform="twitter">Twitter</a></li>
                <li><a href="#" data-platform="linkedin">LinkedIn</a></li>
                <li><a href="#" data-platform="reddit">Reddit</a></li>
            </ul>
            <button id="copyLinkBtn">Copy link</button>
            <button id="closeSharePopup">Close</button>
        </div>
    `;
    document.body.appendChild(popup);

    // attach listeners
    popup.querySelectorAll(".share-links a").forEach(link => {
        link.addEventListener("click", function(e) {
            e.preventDefault();
            const platform = this.dataset.platform;
            const url = encodeURIComponent(window.location.href);
            const text = encodeURIComponent(document.title);
            let shareUrl = "";
            switch (platform) {
                case "facebook":
                    shareUrl = `https://www.facebook.com/sharer/sharer.php?u=${url}`;
                    break;
                case "twitter":
                    shareUrl = `https://twitter.com/intent/tweet?url=${url}&text=${text}`;
                    break;
                case "linkedin":
                    shareUrl = `https://www.linkedin.com/sharing/share-offsite/?url=${url}`;
                    break;
                case "reddit":
                    shareUrl = `https://www.reddit.com/submit?url=${url}&title=${text}`;
                    break;
            }
            window.open(shareUrl, "_blank", "noopener");
        });
    });

    popup.querySelector("#copyLinkBtn").addEventListener("click", () => {
        navigator.clipboard.writeText(window.location.href).then(() => {
            alert("Link copied to clipboard");
        }).catch(() => {
            prompt("Copy the link below:", window.location.href);
        });
    });

    popup.querySelector("#closeSharePopup").addEventListener("click", () => {
        popup.remove();
    });
}

function requestBookmark() {
    if (confirm("Do you want to bookmark this page?")) {
        // try browser-specific API
        try {
            if (window.external && window.external.AddFavorite) {
                window.external.AddFavorite(window.location.href, document.title);
            } else if (window.sidebar && window.sidebar.addPanel) {
                window.sidebar.addPanel(document.title, window.location.href, "");
            } else {
                alert("Press " + (navigator.userAgent.toLowerCase().indexOf("mac") != -1 ? "Cmd" : "Ctrl") + "+D to bookmark this page.");
            }
        } catch (e) {
            alert("Unable to automatically bookmark; please use your browser\"s bookmarking feature.");
        }
    }
}

// attach to icons once DOM loaded
window.addEventListener("DOMContentLoaded", () => {
    const shareIcon = document.querySelector(".fa-share-from-square");
    if (shareIcon) {
        shareIcon.addEventListener("click", createSharePopup);
    }
    const bookmarkIcon = document.querySelector(".fa-bookmark");
    if (bookmarkIcon) {
        bookmarkIcon.addEventListener("click", requestBookmark);
    }
});

window.onscroll = function() {
        let winScroll = document.body.scrollTop || document.documentElement.scrollTop;
        let height = document.documentElement.scrollHeight - document.documentElement.clientHeight;
        let scrolled = (winScroll / height) * 100;
        document.getElementById("progressBar").style.width = scrolled + "%";
    };
