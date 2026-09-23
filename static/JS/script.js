document.addEventListener("DOMContentLoaded", function () {

    /* ==========================================
       Login / Register Password Toggle
    ========================================== */

    document.querySelectorAll(".toggle-input-password").forEach(function (button) {

        button.addEventListener("click", function () {

            const input = this.parentElement.querySelector(".password");

            if (!input) return;

            if (input.type === "password") {

                input.type = "text";
                this.textContent = "🙈";

            } else {

                input.type = "password";
                this.textContent = "👁";

            }

        });

    });


    /* ==========================================
       View Password Toggle
    ========================================== */

document.querySelectorAll(".toggle-view-password").forEach(function (button) {

    let hideTimer;

    button.addEventListener("click", async function () {

        const row = this.closest(".view-row");
        const password = row.querySelector(".password-text");

        const current = password.textContent.trim();
//        10 seconds
        const timer = 10 * 1000;

        if (current === "••••••••") {

            const passwordId = password.dataset.passwordId;

            const response = await fetch(`/get-password/${passwordId}`);

            const data = await response.json();

            password.textContent = data.password;
            this.textContent = "🙈";

            hideTimer = setTimeout(function () {

                password.textContent = "••••••••";
                button.textContent = "👁";

            }, timer);

        } else {

            password.textContent = "••••••••";
            this.textContent = "👁";

            clearTimeout(hideTimer);
        }
    });
});


    /* ==========================================
       Copy Buttons
    ========================================== */

    document.querySelectorAll(".copy-btn").forEach(function (button) {

        button.addEventListener("click", function () {

            navigator.clipboard.writeText(this.dataset.copy);

            const original = this.textContent;

            this.textContent = "✓";

            setTimeout(function () {

                button.textContent = original;

            }, 1000);

        });

    });

});


document.querySelectorAll(".copy-password-btn").forEach(function (button) {

    button.addEventListener("click", async function () {

        const passwordId = this.dataset.passwordId;

        const response = await fetch(`/get-password/${passwordId}`);

        const data = await response.json();

        await navigator.clipboard.writeText(data.password);

        const original = this.textContent;

        this.textContent = "✓";

        setTimeout(function () {
            button.textContent = original;
        }, 1000);
    });
});


/* ==========================================
   Password Generator
========================================== */

function generatePassword() {

    const letters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ";
    const numbers = "0123456789";
    const symbols = "!#$%&()*+[@^-_=]{}|;:,.<>?/`~";

    function randomInt(min, max) {

        const arr = new Uint32Array(1);
        crypto.getRandomValues(arr);

        return min + (arr[0] % (max - min + 1));

    }

    function randomChar(chars) {

        return chars[randomInt(0, chars.length - 1)];

    }

    let password = [];

    for (let i = 0; i < randomInt(7, 11); i++)
        password.push(randomChar(letters));

    for (let i = 0; i < randomInt(5, 10); i++)
        password.push(randomChar(numbers));

    for (let i = 0; i < randomInt(5, 10); i++)
        password.push(randomChar(symbols));

    for (let i = password.length - 1; i > 0; i--) {

        const j = randomInt(0, i);

        [password[i], password[j]] = [password[j], password[i]];

    }

    const generated = password.join("");

    document.querySelectorAll(".password").forEach(function (input) {

        input.value = generated;

    });

}