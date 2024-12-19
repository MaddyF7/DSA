# Digital Skills Academy Tracker

The Digital Skills Academy (DSA) Tracker is a Flask web application designed to help manage apprentices' journey throughout their apprenticeship. This includes viewing:
- All apprentices
- All line managers
- Exam progress
- Previous and current projects
- Tracking leave requests

This document acts as a guide through the application's functionality, design and best practices.

---

## Table of Contents
1. Overview  
2. Roles  
3. Installation  
4. Features  
5. Structure & Design  
6. Best Practices  
7. Known Limitations  

---

## 1. Overview
This application enables users to track and manage apprentices' progress and milestones within the Digital Skills Academy. The application consists of four tables:

### User:
- This stores all the applications' users (Apprentices or Admins).
- The user role is assigned on record creation.
- Apprentices use the email, password, first_name, last_name, role, line_manager_id (using the id column of the admin record), cohort, start_date, end_date, created_at and modified_date columns.
- Admins use the email, password, first_name, last_name, role, created_at and modified_date columns.
- The id field auto increments.

### Exam:
- This stores scheduled, completed or unsuccessful exam attempts made by the apprentices.
- The id field auto increments.
- The id, name, exam_date, status, apprentice_id (using the id column of the apprentice record), created_at and modified_date columns are populated.

### Leave_request:
- This stores the requested leave by each apprentice, whether it's pending, approved or rejected.
- The id field auto increments.
- The id, apprentice_id (using the id column of the apprentice record), leave_type, start_date, end_date, status, created_at and modified_date columns are populated.

### Project:
- This stores a record of each apprentice's project, current or past.
- The id field auto increments.
- The id, name, description, start_date, end_date, status, apprentice_id (using the id column of the apprentice record), created_at and modified_date columns are populated.

---

## 2. Roles
The application contains two user roles: Admin and Apprentice.

### Admins:
- These are the line managers that support the apprentices and stay updated on their progress.
- Admins have create, read, update and delete (CRUD) permissions on all tables, but they cannot update apprentices' passwords.

### Apprentices:
- These are the users undertaking the apprenticeship and who will track their own progress.
- Apprentices have create, read and update (CRU) permissions on all tables.
- Apprentices cannot delete records.
- Apprentices can only edit their own records.
- Apprentices can create on the user table to register as an apprentice, but cannot create other apprentices or line managers.

---

## 3. Installation
### Prerequisites:
- Python 3.9 or higher (must be added to your system's PATH)  
- MySQL Server  
- Flask Framework  
- Required Python packages (`requirements.txt`)  

### Steps:
1. Clone the repository.  
2. Set up the MySQL database by executing `schema.sql` in the database folder.  
3. Configure the database connection in `configuration.py` updating the host, user and password.  
4. Install dependencies: `pip install -r requirements.txt`  
5. Run the application: `python app.py`  
6. Access the application in your web browser at `http://localhost:5000` to navigate to the login page.  

### Environment Setup:
1. Ensure `SECRET_KEY` is set as an environment variable for added security (it will use a fallback otherwise).  
   - On Linux/macOS: `export SECRET_KEY="your-secret-key"`  
   - On Windows: `set SECRET_KEY="your-secret-key"`  

---

## 4. Features
### Users:
Add, view, edit, and delete apprentices and line managers. Admins can add, manage and delete line managers and apprentices' details, while apprentices can view and update their own data but only view line managers.

### Exam Tile:
Keep track of scheduled, completed, and unsuccessful exams. Filter exams by apprentice name or exam name. All users can add exams, but apprentices can only edit their own, while admins can edit all exams and delete.

### Leave Requests Tile:
Submit and manage leave requests for apprentices. Admins can approve or reject requests, while apprentices can only add pending status. Apprentices can edit their own leave, but admins can edit and delete all.

### Project Tile:
Manage apprentice projects, including details like start/end date, status and description. Projects can be filtered by apprentice or project name. Apprentices can edit their own projects, but admins can edit and delete all.

### Filtering:
Dynamic filtering on the exam, leave_request, and project tables ensures efficient record management and user experience.

### Login & Register:
Includes a session-based login and logout functionality. New users can register as an apprentice or admin in order to meet project requirements, but for a future iteration I'd have registering limited to the apprentices and exisiting admins would have to add new admins. This would make the application more secure.

---

## 5. Structure & Design
### Files:
- `app.py`: The main entry point for the application. Run (`python app.py` in terminal) to start app.  
- `init.py`: Initialises the Flask app and MySQL database connection.  
- `routes.py`: Contains the `main_bp` route definitions for all pages and functions that are used throughout the application.  
- `schema.sql`: Defines the database schema and includes insert statements for testing purposes.  

### Static:
- `styles.css`: Contains the CSS styling for all HTML pages.  
- `script.js`: Contains the JavaScript functionality (e.g., table filtering and delete confirmation pop-up).  

### Templates:
- `login.html`: The HTML template for the login page.  
- `home.html`: The HTML template for the home page where users can logout or choose a tile to navigate to.  
- `addrecord.html`: The HTML template for the create record page. This is a dynamic template that is used for creating records for all tables.  
- `apprentices.html`: The HTML template for the apprentices tile page. This shows a table of all apprentices along with the logged-in apprentice's details or the admin's apprentices.  
- `editrecord.html`: The HTML template for the edit form page. This dynamically shows the form for editing any table.  
- `exams.html`: The HTML template for the exams tile page. This shows a table of all exams sorted by `modified_date` descending.  
- `leave.html`: The HTML template for the leave request tile page. This shows a table of all leave requests sorted by `created_at` descending.  
- `managers.html`: The HTML template for the line managers tile page. This shows a table of all admin users sorted by `last_name` A-Z.  
- `projects.html`: The HTML template for the projects tile page. This shows a table of all apprentices' projects sorted by `start_date` descending.  

---

## 6. Best Practices
### Modular Design:
- The application is structured with a modular design, separating appropriate files:  
  For example `app.py`, `init.py`, `routes.py` and `configuration.py` are split up for cleaner, more organised code.  
  Templates (HTML), static files (CSS, JavaScript), and database (SQL) scripts are separated for better maintainability.

### Session Management:
- User sessions are used to track the logged-in users and their role.  
- Sessions are cleared during logout to prevent unauthorised access.  
- No passwords are stored in sessions.  

### Dynamic and Reusable Functions:
- Dynamic routes for adding, editing, and deleting records supports DRY by removing repetitive code and reducing the amount of HTML templates required.  
- Functions like `line_managers_session`, `apprentices_session` are also used to remove repetitive code.  

### Consistent Design:
- The application uses a consistent and responsive design for all HTML pages.  
- CSS classes are reused consistently.  

### Error Handling:
- Input validation is implemented to ensure that required fields are completed.  
- Error messages are displayed.  

---

## 7. Known Limitations
### Password Hashing:
- Currently passwords are stored as plain text in the MySQL database.

### Notifications:
- There are no email notifications for system updates (e.g., for registering a new user or if leave is approved).

---