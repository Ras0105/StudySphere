/* ---------- Security code field: only for teacher/admin ---------- */
const roleInputs = document.querySelectorAll('input[name="role"]');
const securityCodeGroup = document.getElementById("securityCodeGroup");
const securityCodeInput = document.getElementById("security_code");

function toggleSecurityCode() {
    const selected = document.querySelector('input[name="role"]:checked');
    const needsCode = selected && selected.value !== "student";

    if (securityCodeGroup && securityCodeInput) {
        securityCodeGroup.hidden = !needsCode;
        securityCodeInput.required = needsCode;
        if (!needsCode) securityCodeInput.value = "";
    }
}

roleInputs.forEach(function (input) {
    input.addEventListener("change", toggleSecurityCode);
});

toggleSecurityCode(); // initial state on page load

/* ---------- Profile photo preview ---------- */
const photoInput = document.getElementById("photoInput");
const photoPreview = document.getElementById("photo-preview");

if (photoInput && photoPreview) {
    photoInput.addEventListener("change", function () {
        const file = photoInput.files[0];
        if (!file) return;

        const reader = new FileReader();
        reader.onload = function (event) {
            photoPreview.src = event.target.result;
        };
        reader.readAsDataURL(file);
    });
}

/* ---------- Password show/hide toggles ---------- */
function setupToggle(inputId, toggleId) {
    const input = document.getElementById(inputId);
    const toggle = document.getElementById(toggleId);

    if (!input || !toggle) return;

    toggle.addEventListener("click", function () {
        const isHidden = input.type === "password";
        input.type = isHidden ? "text" : "password";
        toggle.classList.toggle("fa-eye");
        toggle.classList.toggle("fa-eye-slash");
    });
}

setupToggle("password", "passwordToggle");
setupToggle("confirm_password", "confirmPasswordToggle");

/* ---------- Password strength meter ---------- */
const passwordInput = document.getElementById("password");
const strengthBar = document.getElementById("strength-bar");
const strengthText = document.getElementById("strength-text");

function getStrength(value) {
    let score = 0;
    if (value.length >= 8) score++;
    if (/[A-Z]/.test(value)) score++;
    if (/[0-9]/.test(value)) score++;
    if (/[^A-Za-z0-9]/.test(value)) score++;
    return score;
}

if (passwordInput && strengthBar && strengthText) {
    passwordInput.addEventListener("input", function () {
        const score = getStrength(passwordInput.value);

        const levels = [
            { width: "0%",   color: "#eeeeee", label: "Password Strength" },
            { width: "25%",  color: "#d32f2f", label: "Weak" },
            { width: "50%",  color: "#f57c00", label: "Fair" },
            { width: "75%",  color: "#fbc02d", label: "Good" },
            { width: "100%", color: "#2e7d32", label: "Strong" }
        ];

        const level = levels[score];
        strengthBar.style.width = level.width;
        strengthBar.style.backgroundColor = level.color;
        strengthText.textContent = level.label;
    });
}

/* ---------- Confirm password check on submit ---------- */
const registerForm = document.getElementById("registerForm");
const confirmPasswordInput = document.getElementById("confirm_password");
const registerSuccessMessage = document.getElementById("registerSuccessMessage");

if (registerForm && passwordInput && confirmPasswordInput) {
    registerForm.addEventListener("submit", function (event) {
        if (passwordInput.value !== confirmPasswordInput.value) {
            event.preventDefault();

            if (registerSuccessMessage) {
                registerSuccessMessage.textContent = "Passwords do not match.";
                registerSuccessMessage.style.backgroundColor = "#fdecea";
                registerSuccessMessage.style.color = "#d32f2f";
                registerSuccessMessage.style.borderColor = "#f5c6cb";
                registerSuccessMessage.classList.add("show");
            }
        }
    });
}