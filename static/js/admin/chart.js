export function initAnalyticsChart(canvasId, data) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    new Chart(ctx, {
        type: "bar",
        data: data,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: { beginAtZero: true, grid: { color: "rgba(255, 255, 255, 0.1)" } },
                x: { grid: { display: false } }
            },
            plugins: {
                legend: { display: false }
            }
        }
    });
}

export async function clearData(url = null) {
    const message = url 
        ? `Are you sure you want to delete data for ${url}?` 
        : "Are you sure you want to wipe ALL analytics data?";
    
    if (!confirm(message)) return;

    const csrfToken = document.getElementById("csrf_token").value;

    try {
        const response = await fetch("/api/analytics/clear", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRF-Token": csrfToken
            },
            body: JSON.stringify({ url: url })
        });

        if (response.ok) {
            window.location.reload();
        } else {
            alert("Failed to clear data. Check console for details.");
        }
    } catch (error) {
        console.error("Analytics Error:", error);
    }
}

export async function loadIgnoredUrls() {
    try {
        const response = await fetch("/api/analytics/ignore");
        const data = await response.json();
        const tbody = document.querySelector("#ignoredUrlsTable tbody");
        if (!tbody) return;

        tbody.innerHTML = "";
        if (data.ignored_urls && data.ignored_urls.length > 0) {
            data.ignored_urls.forEach(url => {
                const tr = document.createElement("tr");
                tr.innerHTML = `
                    <td class="cell-path"><code>${url}</code></td>
                    <td>
                        <button class="btn-delete-row" onclick="removeIgnoredUrl('${url}')" aria-label="Remove ${url} from ignore list">
                            <i class="fa-solid fa-trash-can" aria-hidden="true"></i>
                        </button>
                    </td>
                `;
                tbody.appendChild(tr);
            });
        } else {
            tbody.innerHTML = `<tr><td colspan="2" style="text-align: center; color: var(--third-font-color); padding: var(--spacing-xl);">No endpoints are currently hiding in the shadows.</td></tr>`;
        }
    } catch (error) {
        console.error("Failed to load ignored URLs:", error);
    }
}

export async function addIgnoredUrl() {
    const input = document.getElementById("newIgnoreUrl");
    const url = input.value.trim();
    if (!url) return;

    const csrfToken = document.getElementById("csrf_token").value;
    try {
        const response = await fetch("/api/analytics/ignore", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRF-Token": csrfToken
            },
            body: JSON.stringify({ url: url })
        });
        
        if (response.ok) {
            input.value = "";
            await loadIgnoredUrls();
        } else {
            alert("Failed to banish URL to the void. Check console for details.");
        }
    } catch (error) {
        console.error("Error adding ignored URL:", error);
    }
}

export async function removeIgnoredUrl(url) {
    if (!confirm(`Bring ${url} back into the light? (Stop ignoring)`)) return;

    const csrfToken = document.getElementById("csrf_token").value;
    try {
        const response = await fetch("/api/analytics/ignore", {
            method: "DELETE",
            headers: {
                "Content-Type": "application/json",
                "X-CSRF-Token": csrfToken
            },
            body: JSON.stringify({ url: url })
        });
        
        if (response.ok) {
            await loadIgnoredUrls();
        } else {
            alert("Failed to remove ignored URL. Check console for details.");
        }
    } catch (error) {
        console.error("Error removing ignored URL:", error);
    }
}