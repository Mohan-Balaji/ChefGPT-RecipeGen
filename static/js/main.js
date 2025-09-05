// Main JavaScript file for ChefGPT Recipe Generator
// Additional functionality can be added here

// Utility function to show toast notifications
function showToast(message, type = 'info') {
    // Create toast element
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type} border-0`;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'} me-2"></i>
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    // Add to page
    let toastContainer = document.getElementById('toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.id = 'toast-container';
        toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
        toastContainer.style.zIndex = '1055';
        document.body.appendChild(toastContainer);
    }
    
    toastContainer.appendChild(toast);
    
    // Initialize and show toast
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
    
    // Remove from DOM after hiding
    toast.addEventListener('hidden.bs.toast', () => {
        toast.remove();
    });
}

// Add smooth scrolling to all anchor links
document.addEventListener('DOMContentLoaded', function() {
    // Add smooth scrolling
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // Add loading animation to buttons
    document.querySelectorAll('button[type="submit"]').forEach(button => {
        button.addEventListener('click', function() {
            if (this.form.checkValidity()) {
                this.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Processing...';
            }
        });
    });
});

// Function to format recipe text for better display
function formatRecipeText(text) {
    // Add line breaks for better readability
    return text
        .replace(/(\d+\.)/g, '\n$1')  // Add line break before numbered steps
        .replace(/(Ingredients?:)/gi, '\n\n$1')  // Add space before ingredients
        .replace(/(Instructions?:)/gi, '\n\n$1')  // Add space before instructions
        .replace(/(Method?:)/gi, '\n\n$1')  // Add space before method
        .trim();
}

// Function to validate prompt input
function validatePrompt(prompt) {
    if (!prompt || prompt.trim().length < 3) {
        return 'Please enter at least 3 characters for your recipe prompt.';
    }
    if (prompt.length > 500) {
        return 'Prompt is too long. Please keep it under 500 characters.';
    }
    return null;
}

// Export functions for use in other scripts
window.ChefGPT = {
    showToast,
    formatRecipeText,
    validatePrompt
};
