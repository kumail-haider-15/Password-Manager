/* ==========================================
   Password Manager - JavaScript Interactivity
   
   Handles dynamic UI features:
   - Password visibility toggles (input & view modes)
   - Copy to clipboard functionality
   - Password generation with cryptographic randomness
   
   All functionality initialized on DOMContentLoaded
========================================== */

document.addEventListener("DOMContentLoaded", function () {

    /* ==========================================
       Password Visibility Toggle (Input Fields)
       
       Used on: Login, Register, Reset Password pages
       Toggles between password (hidden) and text (visible) input types
       Icon changes: eye (show) ↔ see-no-evil (hide)
    ========================================== */

    document.querySelectorAll(".toggle-input-password").forEach(function (button) {

        button.addEventListener("click", function () {

            // Get the password input field from the same wrapper
            const input = this.parentElement.querySelector(".password");

            if (!input) return;

            // Toggle between password and text input type
            if (input.type === "password") {
                input.type = "text";            // Show password as plain text
                this.textContent = "🙈";        // Update icon to hiding emoji
            } else {
                input.type = "password";        // Hide password with dots
                this.textContent = "👁";        // Update icon to eye emoji
            }

        });

    });


    /* ==========================================
       Password Visibility Toggle (View Page)
       
       Used on: Password View page only
       Fetches actual password from backend when clicked
       Auto-hides password after 10 seconds for security
       Icon changes: eye (show) ↔ see-no-evil (hide)
       
       Security Features:
       - Password never loaded unless user clicks toggle
       - Password auto-hides after 10 seconds
       - Requires server-side authorization check
    ========================================== */

    document.querySelectorAll(".toggle-view-password").forEach(function (button) {

        let hideTimer;  // Reference to the auto-hide timeout

        button.addEventListener("click", async function () {

            // Find the password display span in the same row
            const row = this.closest(".view-row");
            const password = row.querySelector(".password-text");

            const current = password.textContent.trim();
            const timer = 10 * 1000;  // 10 seconds in milliseconds

            // If password is hidden (dots), fetch and display it
            if (current === "••••••••") {

                // Get the password ID from data attribute
                const passwordId = password.dataset.passwordId;

                // Fetch the decrypted password from backend
                const response = await fetch(`/get-password/${passwordId}`);

                const data = await response.json();

                // Display the actual password
                password.textContent = data.password;
                this.textContent = "🙈";  // Change icon to hiding emoji

                // Auto-hide password after 10 seconds
                hideTimer = setTimeout(function () {

                    password.textContent = "••••••••";  // Re-hide with dots
                    button.textContent = "👁";         // Change icon back to eye

                }, timer);

            } else {

                // Password is visible, hide it
                password.textContent = "••••••••";
                this.textContent = "👁";

                // Clear the auto-hide timer if user manually hides
                clearTimeout(hideTimer);
            }
        });
    });


    /* ==========================================
       Copy to Clipboard - Username/Email
       
       Used on: Password View page
       Copies username or email to clipboard
       Shows checkmark (✓) for 1 second feedback
       Then reverts to original clipboard icon (📋)
    ========================================== */

    document.querySelectorAll(".copy-btn").forEach(function (button) {

        button.addEventListener("click", function () {

            // Copy the value from data-copy attribute to clipboard
            navigator.clipboard.writeText(this.dataset.copy);

            // Store original emoji
            const original = this.textContent;

            // Show checkmark to indicate success
            this.textContent = "✓";

            // Revert to original emoji after 1 second
            setTimeout(function () {

                button.textContent = original;

            }, 1000);

        });

    });

});


/* ==========================================
   Copy Password to Clipboard
   
   Used on: Password View page only
   Fetches password from backend and copies to clipboard
   Shows checkmark (✓) for 1 second feedback
   Then reverts to original clipboard icon (📋)
   
   Note: Password must be fetched first, ensuring
   only authenticated users can copy passwords
========================================== */

document.querySelectorAll(".copy-password-btn").forEach(function (button) {

    button.addEventListener("click", async function () {

        // Get the password ID from data attribute
        const passwordId = this.dataset.passwordId;

        // Fetch the decrypted password from backend
        const response = await fetch(`/get-password/${passwordId}`);

        const data = await response.json();

        // Copy the password to clipboard
        await navigator.clipboard.writeText(data.password);

        // Store original emoji
        const original = this.textContent;

        // Show checkmark to indicate success
        this.textContent = "✓";

        // Revert to original emoji after 1 second
        setTimeout(function () {
            button.textContent = original;
        }, 1000);
    });
});


/* ==========================================
   Password Generator
   
   Used on: Dashboard page (Generate Password button)
   
   Features:
   - Uses cryptographically secure random number generation (crypto.getRandomValues)
   - Generates random password with:
     * 7-11 random letters (uppercase + lowercase)
     * 5-10 random numbers
     * 5-10 random special characters
   - Shuffles all characters to mix types
   - Fills ALL password input fields in the form
   
   Security:
   - Uses crypto.getRandomValues() instead of Math.random()
   - Guarantees at least one of each character type
   - Sufficient complexity for strong password requirements
========================================== */

function generatePassword() {

    // Character sets for password generation
    const letters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ";
    const numbers = "0123456789";
    const symbols = "!#$%&()*+[@^-_=]{}|;:,.<>?/`~";

    /**
     * Generate a cryptographically secure random integer
     * between min and max (inclusive)
     * Uses crypto.getRandomValues() for security (not predictable like Math.random())
     */
    function randomInt(min, max) {

        const arr = new Uint32Array(1);
        crypto.getRandomValues(arr);  // Get secure random bytes
        return min + (arr[0] % (max - min + 1));

    }

    /**
     * Pick a random character from a string
     * Uses randomInt() to select the index
     */
    function randomChar(chars) {

        return chars[randomInt(0, chars.length - 1)];

    }

    let password = [];

    // Add 7-11 random letters to password
    for (let i = 0; i < randomInt(7, 11); i++)
        password.push(randomChar(letters));

    // Add 5-10 random numbers to password
    for (let i = 0; i < randomInt(5, 10); i++)
        password.push(randomChar(numbers));

    // Add 5-10 random special characters to password
    for (let i = 0; i < randomInt(5, 10); i++)
        password.push(randomChar(symbols));

    // Shuffle array using Fisher-Yates algorithm
    // This mixes character types to avoid patterns
    for (let i = password.length - 1; i > 0; i--) {

        const j = randomInt(0, i);

        // Swap password[i] and password[j]
        [password[i], password[j]] = [password[j], password[i]];

    }

    // Convert array to string
    const generated = password.join("");

    // Fill ALL password input fields with the generated password
    // This allows user to fill both password and confirm_password fields
    document.querySelectorAll(".password").forEach(function (input) {

        input.value = generated;

    });

}
