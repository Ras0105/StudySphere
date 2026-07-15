const passwordInput = document.getElementById("password");
const passwordToggle = document.getElementById("passwordToggle");

if (passwordInput && passwordToggle) {
    passwordToggle.addEventListener("click", function () {
        const isHidden = passwordInput.type === "password";
        passwordInput.type = isHidden ? "text" : "password";
        passwordToggle.classList.toggle("fa-eye");
        passwordToggle.classList.toggle("fa-eye-slash");
    });
}