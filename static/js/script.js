document.addEventListener("click", function (event) {
    const toggleBtn = event.target.closest("[data-toggle]");

    if (toggleBtn) {
        const target = document.getElementById(toggleBtn.getAttribute("data-toggle"));
        if (target) {
            target.classList.toggle("show");
        }
        return;
    }
    
    document.querySelectorAll("[data-toggle]").forEach(function (btn) {
        const target = document.getElementById(btn.getAttribute("data-toggle"));
        if (!target || !target.classList.contains("show")) return;

        const clickedLink = event.target.closest("a");
        const clickedInside = target.contains(event.target);

        if (!clickedInside || clickedLink) {
            target.classList.remove("show");
        }
    });
});

document.addEventListener("keydown", function (event) {
    if (event.key === "Escape") {
        document.querySelectorAll(".show").forEach(function (el) {
            el.classList.remove("show");
        });
    }
});

/* OTP-modal ko dropdown/sidebar ke andar se open karne par,
   parent overlay (dropdown/sidebar) ko pehle hi band kar do - same
   reason as profile-modal: warna modal close hone ke baad woh
   overlay achanak khula dikhega. */
document.querySelectorAll('[data-toggle="otp-modal"]').forEach(function (trigger) {
    trigger.addEventListener("click", function () {
        const dropdown = document.getElementById("profile-dropdown");
        const sidebar = document.getElementById("sidebar");
        if (dropdown) dropdown.classList.remove("show");
        if (sidebar) sidebar.classList.remove("show");
    });
});

/* Password-toast: reset-password-modal-form submit hone ke baad backend
   se page reload hota hai (form action="/change-password", normal POST -
   no AJAX), isliye toast ko show karne ka trigger yahan sessionStorage se
   milta hai. Form submit hote hi ek flag set karo, aur naye page load pe
   agar flag mila to toast dikhado aur flag clear kardo. */
const resetPasswordForm = document.getElementById("reset-password-modal-form");
if (resetPasswordForm) {
    resetPasswordForm.addEventListener("submit", function () {
        sessionStorage.setItem("showPasswordToast", "1");
    });
}

const passwordToast = document.getElementById("password-toast");
if (passwordToast && sessionStorage.getItem("showPasswordToast") === "1") {
    sessionStorage.removeItem("showPasswordToast");

    passwordToast.classList.add("show");
    setTimeout(function () {
        passwordToast.classList.remove("show");
    }, 3000);
}


/* ============================================
   TWO-STEP CHANGE PASSWORD FLOW
   Step 1 - #otp-modal: Send OTP -> Verify OTP (AJAX, no page reload)
   Step 2 - #reset-password-modal: opens automatically once OTP is
            verified, real form submit to /change-password
============================================ */
const otpSendBtn = document.getElementById("otp-send-btn");
const otpVerifyBtn = document.getElementById("otp-verify-btn");
const otpStatus = document.getElementById("otp-status");
const otpInput = document.getElementById("otp-input");
const otpModal = document.getElementById("otp-modal");
const resetPasswordModal = document.getElementById("reset-password-modal");

if (otpSendBtn) {
    otpSendBtn.addEventListener("click", async function () {
        otpSendBtn.disabled = true;
        otpSendBtn.textContent = "Sending...";
        if (otpVerifyBtn) otpVerifyBtn.disabled = true;

        try {
            const res = await fetch("/send-password-otp", { method: "POST" });
            const data = await res.json();
            otpStatus.textContent = data.message || data.error;

            // Only unlock Verify once an OTP has actually been sent
            if (data.success && otpVerifyBtn) {
                otpVerifyBtn.disabled = false;
            }
        } catch (err) {
            otpStatus.textContent = "Network error. Try again.";
        }

        otpSendBtn.disabled = false;
        otpSendBtn.textContent = "Resend OTP";
    });
}

if (otpVerifyBtn) {
    otpVerifyBtn.addEventListener("click", async function () {
        const formData = new FormData();
        formData.append("otp", otpInput.value);

        try {
            const res = await fetch("/verify-password-otp", { method: "POST", body: formData });
            const data = await res.json();
            otpStatus.textContent = data.message || data.error;

            if (data.success) {
                // OTP verified - close step 1, open step 2
                if (otpModal) otpModal.classList.remove("show");
                if (resetPasswordModal) resetPasswordModal.classList.add("show");
                otpInput.value = "";
            }
        } catch (err) {
            otpStatus.textContent = "Network error. Try again.";
        }
    });
}

/* Agar user OTP verify karne ke baad field ko dobara edit kare,
   to purani verification stale ho jaati hai - status clear karo
   taaki confusion na ho ki kaunsa OTP verify hua tha. */
if (otpInput) {
    otpInput.addEventListener("input", function () {
        otpStatus.textContent = "";
    });
}

/* /change-password ek real form POST hai (page reload), isliye agar
   backend error/success ke saath redirect karta hai, JS state (modal
   open/closed) reset ho jaata hai - reset-password-modal band mil jaata
   hai chahe uske andar error/success message render ho chuka ho.
   Isliye: page load pe agar modal ke andar koi message hai, to use
   khud-ba-khud khol do taaki user ko dikhe. */
if (resetPasswordModal) {
    const hasMessage = resetPasswordModal.querySelector(".error-message, .success-message");
    if (hasMessage) {
        resetPasswordModal.classList.add("show");
        const backdrop = document.getElementById("reset-password-modal-backdrop");
        if (backdrop) backdrop.classList.add("show");
    }
}