document.addEventListener("DOMContentLoaded", function () {
    const toggleIcons = document.querySelectorAll(".password-toggle");

    toggleIcons.forEach((toggleIcon) => {
        const passwordField = toggleIcon.previousElementSibling;
        console.log(passwordField);

        toggleIcon.addEventListener("click", function () {
            if (passwordField.type === "password") {
                passwordField.type = "text";
                toggleIcon.classList.replace("fa-eye", "fa-eye-slash");
            } else {
                passwordField.type = "password";
                toggleIcon.classList.replace("fa-eye-slash", "fa-eye");
            }
        });
    });

    const passwordField = document.getElementById("admin_password");
    const requirements = {
        length: document.getElementById("length"),
        lowercase: document.getElementById("lowercase"),
        uppercase: document.getElementById("uppercase"),
        number: document.getElementById("number"),
        symbol: document.getElementById("symbol")
    };

    passwordField.addEventListener("input", function () {
        updateIcons();
        toggleSubmitButton();
    });

    function updateIcons() {
        const value = passwordField.value;
        requirements.length.classList.toggle("valid", value.length >= 10);
        requirements.length.classList.toggle("invalid", value.length < 10);

        requirements.lowercase.classList.toggle("valid", /[a-z]/.test(value));
        requirements.lowercase.classList.toggle("invalid", !/[a-z]/.test(value));

        requirements.uppercase.classList.toggle("valid", /[A-Z]/.test(value));
        requirements.uppercase.classList.toggle("invalid", !/[A-Z]/.test(value));

        requirements.number.classList.toggle("valid", /\d/.test(value));
        requirements.number.classList.toggle("invalid", !/\d/.test(value));

        requirements.symbol.classList.toggle("valid", /[!@#$%^&*(),.?":{}|<>]/.test(value));
        requirements.symbol.classList.toggle("invalid", !/[!@#$%^&*(),.?":{}|<>]/.test(value));

        for (const key in requirements) {
            const requirement = requirements[key];
            const icon = requirement.querySelector("i");
            if (requirement.classList.contains("valid")) {
                icon.classList.remove("fa-times", "text-danger");
                icon.classList.add("fa-check", "text-success");
            } else {
                icon.classList.remove("fa-check", "text-success");
                icon.classList.add("fa-times", "text-danger");
            }
        }
    }

    function toggleSubmitButton() {
        const allValid = Object.values(requirements).every(req => req.classList.contains("valid"));
        document.getElementById("submit-btn").disabled = !allValid;
    }

    updateIcons();
    toggleSubmitButton();
});

async function clearCache() {
    const csrfToken = document.getElementById("csrf_token").value;
    try {
        const response = await fetch("/api/clear-cache", {
            method: "POST",
            headers: {
                "X-CSRF-Token": csrfToken
            }
        });

        if (!response.ok) {
            throw new Error("Failed to clear cache!");
        }

        window.location.reload();
        window.alert("Cache erfolgreich gelöscht!");

    } catch (error) {
        console.error("Error clearing cache:", error);
    }
}

// Update file name when selected
const fileInputs = document.querySelectorAll('.file-input');
fileInputs.forEach(input => {
    input.addEventListener('change', function() {
        const fileName = this.files.length > 0 ? this.files[0].name : '';
        const fileNameDisplay = document.getElementById(`${this.id}-name`);
        fileNameDisplay.textContent = fileName ? `Ausgewählte Datei: ${fileName}` : '';
    });
});
