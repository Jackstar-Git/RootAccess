document.addEventListener("DOMContentLoaded", function() {
    const captchaIcons = document.querySelectorAll(".captcha-icon-btn");
    const captchaAnswerInput = document.getElementById("captcha-answer");
    const captchaFeedback = document.getElementById("captcha-feedback");
    const refreshBtn = document.getElementById("refresh-captcha-btn");
    const form = document.querySelector("form");

    let selectedIcon = null;

    captchaIcons.forEach(icon => {
        icon.addEventListener("click", function(e) {
            e.preventDefault();
            
            captchaIcons.forEach(btn => btn.classList.remove("selected"));
            captchaFeedback.textContent = "";
            captchaFeedback.classList.remove("success", "error");

            this.classList.add("selected");
            selectedIcon = this.dataset.icon;
            captchaAnswerInput.value = selectedIcon;
            
            captchaFeedback.textContent = `✓ Selected: ${selectedIcon}`;
            captchaFeedback.classList.add("success");
        });

        icon.addEventListener("keydown", function(e) {
            if (e.key === "Enter" || e.key === " ") {
                e.preventDefault();
                this.click();
            }
        });
    });

    if (refreshBtn) {
        refreshBtn.addEventListener("click", async function(e) {
            e.preventDefault();
            
            try {
                const currentCaptchaId = document.getElementById("captcha-id").value;
                const csrfToken = document.querySelector('input[name="csrf_token"]').value;
                
                const response = await fetch("/api/captcha/refresh", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": csrfToken
                    },
                    body: JSON.stringify({
                        current_captcha_id: currentCaptchaId
                    })
                });

                const data = await response.json();
                
                if (response.ok && data && data.captcha_id && data.choices) {
                    updateCaptchaUI(data);
                } else {
                    captchaFeedback.textContent = "Failed to refresh captcha: " + (data.error || "Unknown error");
                    captchaFeedback.classList.add("error");
                }
            } catch (error) {
                captchaFeedback.textContent = "Error refreshing captcha: " + error.message;
                captchaFeedback.classList.add("error");
            }
        });
    }

    if (form) {
        form.addEventListener("submit", function(e) {
            if (!selectedIcon || !captchaAnswerInput.value) {
                e.preventDefault();
                captchaFeedback.textContent = "Please select an icon to verify.";
                captchaFeedback.classList.add("error");
                captchaFeedback.classList.remove("success");
                return false;
            }
        });
    }

    function updateCaptchaUI(data) {
        if (!data || !data.category) {
            captchaFeedback.textContent = "Error loading captcha.";
            captchaFeedback.classList.add("error");
            return;
        }
        
        document.getElementById("captcha-id").value = data.captcha_id;
        
        document.getElementById("captcha-category").textContent = data.category.charAt(0).toUpperCase() + data.category.slice(1);
        
        captchaFeedback.textContent = "";
        captchaFeedback.classList.remove("success", "error");
        captchaAnswerInput.value = "";
        selectedIcon = null;
        
        // Update choices
        const choicesContainer = document.querySelector(".captcha-choices");
        choicesContainer.innerHTML = "";
        
        data.choices.forEach(icon => {
            const btn = document.createElement("button");
            btn.type = "button";
            btn.className = "captcha-icon-btn";
            btn.dataset.icon = icon;
            btn.title = `Select ${icon}`;
            btn.setAttribute("aria-label", `Select ${icon}`);
            btn.tabIndex = 0;
            btn.innerHTML = `<i class="fas fa-${icon}" aria-hidden="true"></i>`;
            
            btn.addEventListener("click", function(e) {
                e.preventDefault();
                
                document.querySelectorAll(".captcha-icon-btn").forEach(b => b.classList.remove("selected"));
                captchaFeedback.textContent = "";
                captchaFeedback.classList.remove("success", "error");

                this.classList.add("selected");
                selectedIcon = this.dataset.icon;
                captchaAnswerInput.value = selectedIcon;
                
                captchaFeedback.textContent = `✓ Selected: ${selectedIcon}`;
                captchaFeedback.classList.add("success");
            });

            btn.addEventListener("keydown", function(e) {
                if (e.key === "Enter" || e.key === " ") {
                    e.preventDefault();
                    this.click();
                }
            });
            
            choicesContainer.appendChild(btn);
        });
    }
});
