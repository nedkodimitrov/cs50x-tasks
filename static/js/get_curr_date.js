// populate due_date date field with current date
// Run script once DOM is loaded
document.addEventListener("DOMContentLoaded", function(event) {
    let today = new Date().toLocaleDateString('en-CA')
    due_date_picker = document.getElementById('due_date')
    due_date_picker.value = today
    due_date_picker.min = today
});