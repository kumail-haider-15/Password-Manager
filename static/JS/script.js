document.addEventListener("DOMContentLoaded", function () {
    // Select all toggle buttons
    const toggleButtons = document.querySelectorAll(".toggle-password");

    // Loop through each button
    toggleButtons.forEach(function (button) {
        button.addEventListener("click", function () {
            // Find the password input inside the same wrapper
            const passwordInput = this.parentElement.querySelector(".password");

            // Toggle password visibility
            const type = passwordInput.type === "password" ? "text" : "password";
            passwordInput.type = type;

            // Change icon
            this.textContent = type === "password" ? "👁" : "🙈";
        });
    });
});

function generatePassword() {
    const letters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ';
    const numbers = '0123456789';
    const symbols = '!#$%&()*+[@^-_=]{}|;:,.<>?/`~';

    function randomInt(min, max) {
        const range = max - min + 1;
        const arr = new Uint32Array(1);
        crypto.getRandomValues(arr);
        return min + (arr[0] % range);
    }

    // Explicitly using simple text formatting to keep math clear inline
    function randomChar(str) {
        return str[randomInt(0, str.length - 1)];
    }

    let password = [];

    for (let i = 0; i < randomInt(7, 11); i++) {
        password.push(randomChar(letters));
    }

    for (let i = 0; i < randomInt(5, 10); i++) {
        password.push(randomChar(symbols));
    }

    for (let i = 0; i < randomInt(5, 10); i++) {
        password.push(randomChar(numbers));
    }

    for (let i = password.length - 1; i > 0; i--) {
        const j = randomInt(0, i);
        [password[i], password[j]] = [password[j], password[i]];
    }

    const finalPassword = password.join("");

    const passwordInputs = document.querySelectorAll(".password");
    passwordInputs.forEach(function (input) {
        input.value = finalPassword;
    });
}

document.addEventListener("DOMContentLoaded", function () {
    const toggles = document.querySelectorAll(".toggle-password");

    toggles.forEach(function (icon) {
        icon.addEventListener("click", function () {
            const td = this.parentElement;
            const span = td.querySelector(".password-text");
            const realPassword = span.getAttribute("data-password");
            const isHidden = span.textContent === "••••••";

            if (isHidden) {
                span.textContent = realPassword;
                this.textContent = "🙈";
            } else {
                span.textContent = "••••••";
                this.textContent = "👁";
            }
        });
    });
});

document.querySelectorAll('.toggle-password').forEach(toggle => {
    toggle.addEventListener('click', function () {
        const span = this.previousElementSibling;
        if (span.textContent === '••••••') {
            span.textContent = span.dataset.password;
            this.textContent = '🙈';
        } else {
            span.textContent = '••••••';
            this.textContent = '👁';
        }
    });
});