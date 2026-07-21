const emailForm = document.getElementById("email-form");
const emailInput = document.getElementById("email");
const sendBtn = document.getElementById("send-btn");
const otpSection = document.getElementById("otp-section");
const otpInput = document.getElementById("otp");
const verifyBtn = document.getElementById("verify-btn");
const statusEl = document.getElementById("status");

function setStatus(message, type) {
    statusEl.textContent = message;
    statusEl.className = "show " + type;
}
emailForm.addEventListener("submit", async function (e) {
    e.preventDefault();

    emailInput.disabled = true;
    sendBtn.disabled = true;
    setStatus("Sending OTP...", "info");              // was: statusEl.textContent = "Sending OTP...";

    try {
        const formData = new FormData();
        formData.append("email", emailInput.value);
        const res = await fetch("/login/forgot-password", { method: "POST", body: formData });
        const data = await res.json();

        if (data.success) {
            setStatus(data.message, "success");        // was: statusEl.textContent = data.message;
            otpSection.style.display = "block";
            otpInput.disabled = false;
            verifyBtn.disabled = false;
        } else {
            setStatus(data.error, "error");             // was: statusEl.textContent = data.error;
            emailInput.disabled = false;
            sendBtn.disabled = false;
        }
    } catch (err) {
        setStatus("Network error. Try again.", "error"); // was: statusEl.textContent = "Network error. Try again.";
        emailInput.disabled = false;
        sendBtn.disabled = false;
    }
});

verifyBtn.addEventListener("click", async function () {
    otpInput.disabled = true;
    verifyBtn.disabled = true;
    setStatus("Verifying...", "info");                  // was: statusEl.textContent = "Verifying...";

    try {
        const formData = new FormData();
        formData.append("otp", otpInput.value);
        const res = await fetch("/login/forgot-password/verify-otp", { method: "POST", body: formData });
        const data = await res.json();

        if (data.success) {
            setStatus(data.message, "success");         // was: statusEl.textContent = data.message;
            window.location.href = data.redirect;
        } else {
            setStatus(data.error, "error");              // was: statusEl.textContent = data.error;
            otpInput.disabled = false;
            verifyBtn.disabled = false;
        }
    } catch (err) {
        setStatus("Network error. Try again.", "error"); // was: statusEl.textContent = "Network error. Try again.";
        otpInput.disabled = false;
        verifyBtn.disabled = false;
    }
});