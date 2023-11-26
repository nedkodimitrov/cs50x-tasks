# CS50xTasks

#### Video Demo: <https://www.youtube.com/watch?v=PeDQRbp62ys>


## Overview

*CS50xTasks* is a web application, built using Flask, that is designed as a straightforward task management tool for teams. It covers essential features such as user authentication, task organization, progress tracking, notifications, search, and collaborative commenting.
## Getting Started

To set up *CS50xTasks*, follow these steps:

1. Install required packages using  
`pip3 install -r requirements.txt`.

2. Initialize the database with  
`python models.py`.

## Key Libraries

- **Flask**: The primary web framework.
- **Flask-Session**: Manages user sessions.
- **SQLAlchemy**: Handles database interactions.
- **Werkzeug**: A utility library used for security functions like password hashing.
- **Flask-WTF**: Integrates Flask with WTForms for form handling.
- **WTForms**: A library for creating and validating web forms.
- **wtforms-alchemy**: Extends WTForms for use with SQLAlchemy models.

## Usage

To run the application, execute  
`flask run`.

## File Contents

Here's an overview of the files in *CS50xTasks*:

### app.py
Serves as the backend of the Flask web application, managing endpoints for user authentication, task management, notifications, and user interactions. It connects to a database using SQLAlchemy and utilizes Flask-WTF for form handling and CSRF protection.

### models.py
Defines SQLAlchemy models for the task management system, including tables for users, tasks, priorities, statuses, comments, and notifications. The `create_db` function initializes the SQLite database.

### forms.py
Manages Flask-WTF forms for all POST interactions and offers comprehensive form validation.

### templates/layout.html
Provides the HTML layout for the web app. It includes styling and libraries like Bootstrap, jQuery, and Font Awesome. The main content is customizable using block tags and handles notifications.

### templates/user_form.html
A template for user login, registration, and password change forms.

### templates/macro_render_tasks_table.html
A macro for creating HTML tables to display task information.

### templates/index.html
A template for the tasks dashboard, showing tasks assigned to and assigned by the user.

### templates/macro_render_task_form.html
A macro template form for creating, editing, and searching tasks.

### templates/new_task.html
A template for creating a new task with a form and JavaScript for date retrieval and assignee autocomplete.

### templates/edit_task.html
A template for editing tasks with form fields and assignee autocomplete.

### templates/show_task.html
Displays detailed task information, related comments, and allows task editing and adding comments.

### templates/search_task.html
A template for searching tasks with form fields and assignee/assigner autocompletion.

### static/styles.css
CSS styles for the web app.

### static/js/get_curr_date.js
JavaScript for setting due date to the current date.

### static/js/autocomplete_assignee.js
JavaScript for assignee autocomplete.

### static/js/autocomplete_assigner.js
JavaScript for assigner autocomplete.

### static/js/get_notifications.js
JavaScript for populating the notifications dropdown menu.
