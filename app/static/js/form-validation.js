document.addEventListener('DOMContentLoaded', function() {
    // Get all input fields with error messages
    const inputsWithErrors = document.querySelectorAll('.form-control');

    inputsWithErrors.forEach(input => {
        // Check if there is an error message
        const errorSpan = input.parentElement.querySelector('.error-message');
        if (errorSpan) {
            // Add error styling
            input.classList.add('error');
            // Clear the input value
            input.value = '';

            // Add an input event listener
            input.addEventListener('input', function() {
                // Remove error styling when the user starts typing
                this.classList.remove('error');
                // Hide error messages
                const errorMessages = this.parentElement.querySelectorAll('.error-message');
                errorMessages.forEach(msg => msg.style.display = 'none');
            });
        }
    });

    // Check the current page
    const isRegisterPage = window.location.pathname.includes('register');

    // Add password validation only on the registration page
    if (isRegisterPage) {
        const passwordInputs = document.querySelectorAll('input[type="password"]');
        passwordInputs.forEach(input => {
            input.addEventListener('input', function() {
                validatePassword(this);
            });

            input.addEventListener('blur', function() {
                validatePassword(this, true);
            });
        });
    }
});

function validatePassword(input, showError = false) {
    const password = input.value;
    let isValid = true;
    let errorMessage = '';

    // Simplified password validation rules
    if (password.length < 6) {
        isValid = false;
        errorMessage = 'Password must be at least 6 characters long';
    } else if (password.length > 20) {
        isValid = false;
        errorMessage = 'Password must not exceed 20 characters';
    } else if (!/[a-zA-Z]/.test(password)) {
        isValid = false;
        errorMessage = 'Password must contain at least one letter';
    } else if (!/[0-9]/.test(password)) {
        isValid = false;
        errorMessage = 'Password must contain at least one number';
    }

    // Get or create the error message element
    let errorSpan = input.parentElement.querySelector('.error-message');
    if (!errorSpan && !isValid) {
        errorSpan = document.createElement('span');
        errorSpan.className = 'error-message';
        input.parentElement.appendChild(errorSpan);
    }

    // Update input field styling and error message
    if (!isValid && showError) {
        input.classList.add('error');
        if (errorSpan) {
            errorSpan.textContent = errorMessage;
            errorSpan.style.display = 'block';
        }
    } else {
        input.classList.remove('error');
        if (errorSpan) {
            errorSpan.style.display = 'none';
        }
    }

    return isValid;
}

// Form submission validation
document.querySelectorAll('form').forEach(form => {
    form.addEventListener('submit', function(event) {
        // Perform password validation only on the registration page
        if (window.location.pathname.includes('register')) {
            const passwordInput = this.querySelector('input[type="password"]');
            if (passwordInput && !validatePassword(passwordInput, true)) {
                event.preventDefault();
            }
        }
    });
});