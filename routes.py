# Import Flask for handelling web application routing
from flask import Blueprint, render_template, request, redirect, session, flash
# Import connection to MySQL database from init.py
from init import mysql
# Define a blueprint for all routes
main_bp = Blueprint('main', __name__)
# Define repeating functions
# Function for setting line_managers session by fetching all users with the role 'Admin' from the User table
def line_managers_session():
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT id, email, first_name, last_name FROM User WHERE role = 'Admin'")
        managers = cur.fetchall()
        session['line_managers'] = {
            manager[0]: {
                'id': manager[0],
                'email': manager[1],
                'first_name': manager[2],
                'last_name': manager[3]
            } for manager in managers
        }
        cur.close()
    except Exception as e:
        print(f"An error occurred while fetching line managers: {str(e)}")
# Function for setting apprentices session by fetching all users with the role 'Apprentice' from the User table
def apprentices_session():
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT id, first_name, last_name FROM User WHERE role = 'Apprentice'")
        apprentices = cur.fetchall()
        session['apprentices'] = {
            apprentice[0]: f"{apprentice[1]} {apprentice[2]}"
            for apprentice in apprentices
        }
        cur.close()
    except Exception as e:
        print(f"An error occurred while fetching apprentices: {str(e)}")
# Function so apprentices can edit their own record if their id matches
def edit_own_record(table_name, record_id, user):
    # For User table use id field not apprentice_id
    if table_name == 'User' and record_id == user['id']:
        return True
    # Dynamically check table_name using apprentice_id to match
    try:
        cur = mysql.connection.cursor()
        cur.execute(f"SELECT apprentice_id FROM {table_name} WHERE id = %s", (record_id,))
        result = cur.fetchone()
        cur.close()
        # Check if the logged-in user matches the apprentice_id
        if result and result[0] == user['id']:
            return True
    except Exception as e:
        print(f"Error checking ownership for {table_name}: {e}")
        return False
    # Set to false to prevent access
    return False
# Define routes
# On app start route to web application login page
@main_bp.route('/', methods=['GET', 'POST'])
def login():
    # Define error variable
    error = None
    if request.method == 'POST':
        # Get login submission details
        email = request.form['email']
        password = request.form['password']
        try:
            # Check MySQL database for matching email and password in user record
            cur = mysql.connection.cursor()
            cur.execute("SELECT * FROM User WHERE email = %s AND password = %s", (email, password))
            user = cur.fetchone()
            cur.close()
            # If user exists, redirect to home page
            if user:
                # Store the matching user's record in a session
                session['user'] = {
                    'id': user[0],
                    'email': user[1],
                    'first_name': user[3],
                    'last_name': user[4],
                    'role': user[5],
                    'line_manager_id': user[6],
                    'cohort': user[7],
                    'start_date': user[8],
                    'end_date': user[9],
                    'created_on': user[10],
                    'modified_on': user[11]
                }
                # Redirect to home page
                return redirect("/home")
            # Else show error message on login.html template
            else:
                error = "Invalid login details."
        except Exception as e:
            error = f"An error occurred: {str(e)}"
    # Loads login.html template and any error messages
    return render_template('login.html', error=error)
# Route to web application home page
@main_bp.route('/home')
def home():
    # Ensure a user is logged in
    if 'user' in session:
        # Get the logged in user's first name from the session
        first_name = session['user']['first_name']
        # Ensure line_managers session is set
        if 'line_managers' not in session:
            try:
                line_managers_session()
            except Exception as e:
                return f"An error occurred while fetching line managers: {str(e)}"
        # Ensure apprentices session is set
        if 'apprentices' not in session:
            try:
                apprentices_session()
            except Exception as e:
                return f"An error occurred while fetching apprentices: {str(e)}"
        # Return the home page
        return render_template('home.html', first_name=first_name)
    # If no one is logged in, redirect to login page
    return redirect('/')
# Route to web application logout page
@main_bp.route('/logout', methods=['POST'])
def logout():
    # Clear session
    session.clear()
    # Show successful log out notification
    flash('You have successfully logged out.','success')
    # Return to login page
    return redirect('/')
# Route to web application apprentice page
@main_bp.route('/apprentices')
def apprentices():
    # Ensure a user is logged in
    if 'user' in session:
        # Set the logged in user's data from session into variable
        user = session['user']
        # Set the line_manager data from session into variable
        line_managers = session.get('line_managers', {})
        # Retrive all apprentices 
        try:
            cur = mysql.connection.cursor()
            # Sort by last_name and store in apprentices
            cur.execute("SELECT * FROM User WHERE role = 'Apprentice' ORDER BY last_name")
            apprentices = cur.fetchall()
            # If the logged in user is an admin retrive their apprentices and sort by last_name
            if user['role'] == 'Admin':
                cur.execute("SELECT * FROM User WHERE role = 'Apprentice' AND line_manager_id = %s ORDER BY last_name", (user['id'],))
                assigned_apprentices = cur.fetchall()
            # If logged in user is an apprentice keep assigned_apprentices null
            else:
                assigned_apprentices = None
            cur.close()
            # Loads apprentices.html template and variables
            return render_template('apprentices.html', user=user,apprentices=apprentices,assigned_apprentices=assigned_apprentices,line_managers=line_managers)
        # An error took place
        except Exception as e:
            return f"An error took place: {str(e)}"
    # If no ones logged in redirect to login page
    else:
        return redirect('/')
# Route to web application exam page
@main_bp.route('/exams')
def exams():
    # Ensure a user is logged in
    if 'user' in session:
        user = session['user']
        try:
            # Connect to MySQL database
            cur = mysql.connection.cursor()
            # Sort by modifed_date newest to oldest
            cur.execute("""
                SELECT e.id, e.apprentice_id, e.name, e.exam_date, e.status, e.modified_date, 
                       u.first_name, u.last_name
                FROM exam e
                JOIN User u ON e.apprentice_id = u.id
                ORDER BY e.modified_date DESC
            """)
            # Fetch all exam records
            exam_records = cur.fetchall()
            exams = [
                {
                    'id': record[0],
                    'apprentice_id': record[1],
                    'name': record[2],
                    'exam_date': record[3].strftime('%d-%m-%Y') if record[3] else '',
                    'status': record[4],
                    'modified_date': record[5],
                    'apprentice_name': f"{record[6]} {record[7]}"
                }
                for record in exam_records
            ]
            cur.close()
            # Return exams.html and pass variables
            return render_template('exams.html', exams=exams, user=user)
        except Exception as e:
            # Return exams.html and show error message
            error_message = f"An error occurred while fetching exams: {str(e)}"
            return render_template('exams.html', error=error_message)
    # If no user is logged in return to login page
    return redirect('/')
# Route to web application leave page
@main_bp.route('/leave')
def leave():
    # Ensure a user is logged in
    if 'user' in session:
        user = session['user']
        try:
            # Connect to MySQL database
            cur = mysql.connection.cursor()
            # Sort by created_at newest to oldest
            cur.execute("""
                SELECT l.id, l.apprentice_id, l.leave_type, l.start_date, l.end_date, l.status, l.created_at,
                       u.first_name, u.last_name
                FROM leave_request l
                JOIN User u ON l.apprentice_id = u.id
                ORDER BY l.created_at DESC
            """)
            # Fetch all leave records
            leave_records = cur.fetchall()
            leaves = [
                {
                    'id': record[0],
                    'apprentice_id': record[1],
                    'leave_type': record[2],
                    'start_date': record[3].strftime('%d-%m-%Y') if record[3] else '',
                    'end_date': record[4].strftime('%d-%m-%Y') if record[4] else '',
                    'status': record[5],
                    'created_at': record[6],
                    'apprentice_name': f"{record[7]} {record[8]}"
                }
                for record in leave_records
            ]
            cur.close()
            # Return leave.html and pass variables
            return render_template('leave.html', leaves=leaves, user=user)
        except Exception as e:
            # Return leave.html and show error message
            error_message = f"An error occurred while fetching leave records: {str(e)}"
            return render_template('leave.html', error=error_message)
    # If no user is logged in return to login page
    return redirect('/')
# Route to web application line managers page
@main_bp.route('/managers')
def managers():
    # Ensure a user is logged in
    if 'user' in session:
        # Get the logged in user
        user = session['user']
        # Get the line_managers from the session
        line_managers = session.get('line_managers', {})
        # Convert the session into a list then sorted alphabetically by last_name
        sorted_line_managers = sorted(line_managers.values(), key=lambda manager: manager['last_name'])
        # If the logged in user has a line manager, retrieve their line manager's details
        if user['role'] != 'Admin' and user.get('line_manager_id'):
            user_line_manager = line_managers.get(str(user['line_manager_id']))
        else:
            user_line_manager = None
        # Render the managers.html template and pass the necessary data
        return render_template(
            'managers.html',user=user,line_managers=sorted_line_managers,user_line_manager=user_line_manager)
    # If no one is logged in, redirect to the login page
    return redirect('/')
# Route to web application projects page
@main_bp.route('/projects')
def project():
    # Ensure a user is logged in
    if 'user' in session:
        user = session['user']
        try:
            # Connect to MySQL database
            cur = mysql.connection.cursor()
            # Sort by start_date newest to oldest
            cur.execute("""
                SELECT p.id, p.apprentice_id, p.name, p.description, p.start_date, p.end_date, p.status, p.created_at,
                       u.first_name, u.last_name
                FROM Project p
                JOIN User u ON p.apprentice_id = u.id
                ORDER BY p.start_date DESC
            """)
            # Fetch all project records
            project_records = cur.fetchall()
            projects = [
                {
                    'id': record[0],
                    'apprentice_id': record[1],
                    'name': record[2],
                    'description': record[3],
                    'start_date': record[4].strftime('%d-%m-%Y') if record[4] else '',
                    'end_date': record[5].strftime('%d-%m-%Y') if record[5] else '',
                    'status': record[6],
                    'created_at': record[7],
                    'apprentice_name': f"{record[8]} {record[9]}"
                }
                for record in project_records
            ]
            cur.close()
            # Return project.html and pass variables
            return render_template('projects.html', projects=projects, user=user)
        except Exception as e:
            # Return project.html and show error message
            error_message = f"An error occurred while fetching project records: {str(e)}"
            return render_template('projects.html', error=error_message)
    # If no user is logged in return to login page
    return redirect('/')
# Route to web application addrecord.html page
# Adds records to tables dynamically
@main_bp.route('/add/<string:table_name>', methods=['GET', 'POST'])
def add_record(table_name):
    try:
        # Store previous route
        if request.method == 'GET':
            route = '/' + request.referrer.split('/')[-1]
            session['form_route'] = route
            # Ensure line_managers session is set 
            if 'line_managers' not in session:
                line_managers_session()
        # When the form is submitted use the previous route from session
        else:
            route = session.get('form_route', '/')
        # Load the logged in user
        user = session.get('user', None)
        # Load line managers and apprentices from the session if set
        line_managers = session.get('line_managers', {})
        apprentices = session.get('apprentices', {})
        # Restrict access if the user is not logged in for specific routes
        if route != '/' and not user:
            return redirect('/')
        # Restrict access to add from /apprentices or /managers for apprentices
        if route in ['/apprentices', '/managers'] and (not user or user.get('role') != 'Admin'):
            return redirect('/')
        # Retrieve table columns, excluding created_at and modified_date
        cur = mysql.connection.cursor()
        cur.execute(f"SHOW COLUMNS FROM {table_name}")
        columns = [column[0] for column in cur.fetchall() if column[0] not in ['created_at', 'modified_date']]
        cur.close()
        # Handle form submission
        if request.method == 'POST':
            # Prepare new record to submit
            new_record = {column: request.form.get(column) for column in columns if column != 'id'}
            # Default role or grab from registration
            if table_name == 'User':
                if route == '/apprentices':
                    new_record['role'] = 'Apprentice' 
                elif route == '/managers':
                    new_record['role'] = 'Admin'
                elif route == '/':
                    new_record['role'] = request.form.get('role')
                # Include apprentice fields only for Apprentice role
                if new_record['role'] == 'Apprentice':
                    new_record['cohort'] = request.form.get('cohort')
                    new_record['start_date'] = request.form.get('start_date')
                    new_record['line_manager_id'] = request.form.get('line_manager_id')
                # Exclude apprentice fields for Admin role
                elif new_record['role'] == 'Admin':
                    # Remove fields specific to apprentices
                    for field in ['cohort', 'start_date', 'line_manager_id']:
                        new_record.pop(field, None)
            # Ensure valid default values for optional fields
            for key, value in new_record.items():
                if value == '' or value is None:
                    new_record[key] = None
            # Default status to pending for adding Leave_request
            if table_name == 'Leave_request':
                new_record['status'] = 'Pending'
            # SQL placeholders and execute the query
            placeholders = ', '.join(['%s'] * len(new_record))
            columns_query = ', '.join(new_record.keys())
            values = list(new_record.values())
            # Insert the new record into the database
            cur = mysql.connection.cursor()
            cur.execute(
                f"INSERT INTO {table_name} ({columns_query}) VALUES ({placeholders})",
                values
            )
            mysql.connection.commit()
            cur.close()
            # Show success notification for adding record
            flash('Record successfully added.', 'success')
            # Reset the sessions for line_managers or apprentices if needed
            if table_name == 'User':
                if new_record.get('role') in ['Admin', 'admin']:
                    if 'line_managers' in session:
                        session.pop('line_managers')
                    line_managers_session()
                elif new_record.get('role') == 'Apprentice':
                    if 'apprentices' in session:
                        session.pop('apprentices')
                    apprentices_session()
            # Redirect based on the previous route
            return redirect(route)
        # Render the addrecord.html template
        return render_template(
            'addrecord.html',table_name=table_name,user=user,line_managers=line_managers,apprentices=apprentices,columns=columns,route=route)
    except Exception as e:
        # Handle any errors during database operations
        return f"An error occurred while adding the record: {str(e)}", 500
# Route to web application editrecord.html page
# Edits table records dynamically
@main_bp.route('/edit/<string:table_name>/<int:record_id>', methods=['GET', 'POST'])
def edit_record(table_name, record_id):
    # Ensure a user is logged in
    if 'user' in session:
        user = session['user']
        try:
            # Store previous route
            if request.method == 'GET':
                route = '/' + request.referrer.split('/')[-1]
                session['form_route'] = route  # Store route in session
                # Ensure line_managers session is set when the route starts
                if 'line_managers' not in session:
                    line_managers_session()
            else:
                route = session.get('form_route', '/')
            # Load line managers and apprentices from the session if set
            line_managers = session.get('line_managers', {})
            apprentices = session.get('apprentices', {})
            # Restrict apprentices to only edit their own records
            if user.get('role') != 'Admin' and not edit_own_record(table_name, record_id, user):
                return redirect(request.referrer)
            # Fetch the record by ID from the selected table
            cur = mysql.connection.cursor()
            cur.execute(f"SELECT * FROM {table_name} WHERE id = %s", (record_id,))
            record = cur.fetchone()
            if not record:
                return f"Record not found in table {table_name}", 404
            # Dynamically map columns
            cur.execute(f"SHOW COLUMNS FROM {table_name}")
            columns = [column[0] for column in cur.fetchall()]
            # Convert the record to a dictionary
            record_dict = {columns[i]: record[i] for i in range(len(columns))}
            cur.close()
            # Handle form submission to update changes
            if request.method == 'POST':
                # Set updates but exclude id, created_at, modified_date, and role
                updates = {}
                for key in columns:
                    if key not in ['id', 'created_at', 'modified_date', 'role']:
                        form_value = request.form.get(key)
                        if key == 'password' and not form_value:
                            # Keep old password if password isn't on form
                            updates[key] = record_dict[key]
                        else:
                            updates[key] = form_value
                # Dynamically set role if editing a User record
                if table_name == 'User' and 'role' not in updates:
                    updates['role'] = 'Apprentice' if route == '/apprentices' else 'Admin'
                # Prepare the update query
                update_query = ", ".join([f"{key} = %s" for key in updates.keys()])
                update_values = list(updates.values()) + [record_id]
                # Update the record dynamically in the database
                cur = mysql.connection.cursor()
                cur.execute(
                    f"UPDATE {table_name} SET {update_query} WHERE id = %s",
                    update_values
                )
                mysql.connection.commit()
                cur.close()
                # Show success notification for record updating
                flash('Record successfully updated.', 'success')
                # Reset sessions if the User table is being edited
                if table_name == 'User':
                    if updates.get('role') == 'Admin':
                        session.pop('line_managers', None)
                        line_managers_session()
                    elif updates.get('role') == 'Apprentice':
                        session.pop('apprentices', None)
                        apprentices_session()
                # Redirect back to the previous page or login
                return redirect(route or '/')
            # Render the editrecord.html template
            return render_template(
                'editrecord.html',
                record=record_dict,
                table_name=table_name,
                user=user,
                line_managers=line_managers,
                apprentices=apprentices,
                route=route
            )
        except Exception as e:
            return f"An error occurred while editing the record: {str(e)}", 500
    # Redirect to login page if no user is logged in
    return redirect('/')
# Route to web application delete popup
# Deletes table records dynamically
@main_bp.route('/delete/<string:table_name>/<int:record_id>', methods=['POST'])
def delete(table_name, record_id):
    # Ensure a user is logged in
    if 'user' in session:
        # Get the logged in user from session
        user = session['user']
        # Ensure the user is admin
        if user.get('role') != 'Admin':
            return redirect(request.referrer)
        try:
            # Fetch the role of the record being deleted if from the User table
            role = None
            if table_name == 'User':
                cur = mysql.connection.cursor()
                cur.execute(f"SELECT role FROM {table_name} WHERE id = %s", (record_id,))
                result = cur.fetchone()
                role = result[0] if result else None
                cur.close()
            # Delete the record from the selected table
            cur = mysql.connection.cursor()
            query = f"DELETE FROM {table_name} WHERE id = %s"
            cur.execute(query, (record_id,))
            mysql.connection.commit()
            cur.close()
            # Show success notification for record deletion
            flash('Record successfully deleted.','success')
            # Reset sessions if the User table is being deleted
            if table_name == 'User':
                if role == 'Admin':
                    session.pop('line_managers', None)
                    line_managers_session()
                elif role == 'Apprentice':
                    session.pop('apprentices', None)
                    apprentices_session()
            # Return to the previous page
            return redirect(request.referrer)
        except Exception as e:
            # Handle errors
            return f"An error occurred while deleting the record: {str(e)}", 500
    # If no one is logged in redirect to the login page
    return redirect('/login')