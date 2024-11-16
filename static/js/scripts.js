document.addEventListener('DOMContentLoaded', () => {
    console.log('JavaScript is connected and running.');

    // Handle flash message animations
    const flashes = document.querySelectorAll('.flash');

    flashes.forEach(function(flash) {
        // Listen for the end of the shrinkLine animation on the progress line
        const progressLine = flash.querySelector('.flash-progress');
        if (progressLine) {
            progressLine.addEventListener('animationend', function() {
                // Add fade-out class for smooth transition
                flash.classList.add('fade-out');

                // Remove the flash message after the fade-out transition completes
                flash.addEventListener('transitionend', function() {
                    flash.remove();
                });
            });
        }
    });

    // Handle flash message close button clicks
    const closeButtons = document.querySelectorAll('.flash .close-btn');
    closeButtons.forEach(button => {
        button.addEventListener('click', () => {
            const flash = button.parentElement;
            flash.classList.add('fade-out');
            flash.addEventListener('transitionend', () => {
                flash.remove();
            });
        });
    });

    // Additional functionalities can be added here
});

// Existing Edit Modal Functions
function openEditModal(button) {
    var modal = document.getElementById("editExpenseModal");

    var expenseId = button.getAttribute("data-expense-id");
    var categoryId = button.getAttribute("data-category-id");
    var amount = button.getAttribute("data-amount");
    var date = button.getAttribute("data-date");

    document.getElementById("edit-category").value = categoryId;
    document.getElementById("edit-amount").value = amount;
    document.getElementById("edit-date").value = date;

    document.getElementById("editExpenseForm").action = "/edit_expense/" + expenseId;

    modal.style.display = "block";
}

function closeEditModal() {
    var modal = document.getElementById("editExpenseModal");
    modal.style.display = "none";
}

// Close the modal when clicking outside of the modal content
window.onclick = function(event) {
    var modal = document.getElementById("editExpenseModal");
    if (event.target == modal) {
        modal.style.display = "none";
    }
}

// Delete Expense Functions (if using the confirm dialog)
function confirmDelete(button) {
    const expenseId = button.getAttribute('data-expense-id');
    const confirmation = confirm('Are you sure you want to delete this expense? This action cannot be undone.');

    if (confirmation) {
        deleteExpense(expenseId);
    }
}

function deleteExpense(expenseId) {
    fetch(`/delete_expense/${expenseId}`, {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrf_token') // Function to get CSRF token from cookies
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Remove the expense row from the table
            const row = document.getElementById(`expense-row-${expenseId}`);
            if (row) {
                row.remove();
            }
            alert('Expense deleted successfully!');
        } else {
            alert(data.message || 'Failed to delete the expense.');
        }
    })
    .catch(error => {
        console.error('Error deleting expense:', error);
        alert('An error occurred while deleting the expense.');
    });
}

// Function to get CSRF token from cookies (if needed)
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Function to Update the Chart After Deletion
function updateChart() {
    // Assuming you have stored chart data globally or have access to it here
    // For simplicity, reload the page to update the chart
    location.reload();
}

// Function to Show Flash Messages Dynamically
function showFlashMessage(message, category) {
    // Create a flash message element
    const flashContainer = document.querySelector('.flash-container') || createFlashContainer();
    const flash = document.createElement('div');
    flash.classList.add('flash', category);
    flash.textContent = message;

    flashContainer.appendChild(flash);

    // Automatically remove the flash message after a few seconds
    setTimeout(() => {
        flash.classList.add('fade-out');
        flash.addEventListener('transitionend', () => {
            flash.remove();
        });
    }, 3000);
}

// Function to Create Flash Container if Not Present
function createFlashContainer() {
    const container = document.createElement('div');
    container.classList.add('flash-container');
    document.body.prepend(container);
    return container;
} 