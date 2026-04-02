let adjustmentData = { url: "", currentVisits: 0, currentUnique: 0 };

export function openAdjustModal(url, visits, unique) {
    adjustmentData = { url, currentVisits: visits, currentUnique: unique };
    
    document.getElementById("adjustModalUrl").textContent = url;
    document.getElementById("visitsInput").value = "0";
    document.getElementById("uniqueInput").value = "0";
    document.getElementById("currentVisits").textContent = visits;
    document.getElementById("currentUnique").textContent = unique;
    
    updateProjection();
    
    const modal = document.getElementById("adjustAnalyticsModal");
    modal.setAttribute("aria-hidden", "false");
    modal.style.display = "flex";
}

export function closeAdjustModal() {
    const modal = document.getElementById("adjustAnalyticsModal");
    modal.setAttribute("aria-hidden", "true");
    modal.style.display = "none";
}

function updateProjection() {
    const visitsChange = parseInt(document.getElementById("visitsInput").value) || 0;
    const uniqueChange = parseInt(document.getElementById("uniqueInput").value) || 0;
    
    const projectedVisits = Math.max(0, adjustmentData.currentVisits + visitsChange);
    const projectedUnique = Math.max(0, Math.min(adjustmentData.currentUnique + uniqueChange, projectedVisits));
    
    document.getElementById("projectedVisits").textContent = projectedVisits;
    document.getElementById("projectedUnique").textContent = projectedUnique;
}

export function increaseVisits() {
    const input = document.getElementById("visitsInput");
    input.value = (parseInt(input.value) || 0) + 1;
    updateProjection();
}

export function decreaseVisits() {
    const input = document.getElementById("visitsInput");
    input.value = (parseInt(input.value) || 0) - 1;
    updateProjection();
}

export function increaseUnique() {
    const input = document.getElementById("uniqueInput");
    input.value = (parseInt(input.value) || 0) + 1;
    updateProjection();
}

export function decreaseUnique() {
    const input = document.getElementById("uniqueInput");
    input.value = (parseInt(input.value) || 0) - 1;
    updateProjection();
}

export async function applyAnalyticsAdjustment() {
    const visitsChange = parseInt(document.getElementById("visitsInput").value) || 0;
    const uniqueChange = parseInt(document.getElementById("uniqueInput").value) || 0;
    const csrfToken = document.getElementById("csrf_token").value;

    try {
        const response = await fetch("/api/analytics/adjust", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrfToken
            },
            body: JSON.stringify({
                url: adjustmentData.url,
                visits_change: visitsChange,
                unique_visits_change: uniqueChange
            })
        });

        if (response.ok) {
            const data = await response.json();
            alert(`Analytics updated successfully!\nVisits: ${data.data.visits}\nUnique: ${data.data.unique_visits}`);
            closeAdjustModal();
            location.reload();
        } else {
            const error = await response.json();
            alert("Failed to adjust analytics: " + (error.error || "Unknown error"));
        }
    } catch (error) {
        console.error("Error:", error);
        alert("An error occurred while adjusting analytics.");
    }
}

export function initAdjustmentModal() {
    const modal = document.getElementById("adjustAnalyticsModal");
    
    modal.addEventListener("click", function(e) {
        if (e.target === this) {
            closeAdjustModal();
        }
    });

    document.getElementById("visitsInput").addEventListener("change", updateProjection);
    document.getElementById("uniqueInput").addEventListener("change", updateProjection);
    
    window.openAdjustModal = openAdjustModal;
    window.closeAdjustModal = closeAdjustModal;
    window.increaseVisits = increaseVisits;
    window.decreaseVisits = decreaseVisits;
    window.increaseUnique = increaseUnique;
    window.decreaseUnique = decreaseUnique;
    window.applyAnalyticsAdjustment = applyAnalyticsAdjustment;
}
