from flask import Flask, flash, redirect, render_template, request, session, jsonify
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy import create_engine, or_, desc
from sqlalchemy.orm import sessionmaker, aliased
from models import User, Task, Status, Priority, Comment, STATUSES, Notification
from forms import LoginForm, RegisterForm, ChangePasswordForm, TaskForm, EditTaskForm, CommentForm, SearchTaskForm
from flask_wtf.csrf import CSRFProtect
from functools import wraps

# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config["SECRET_KEY"] = "some secret key"
Session(app)

csrf = CSRFProtect()
csrf.init_app(app)

# Establish a database connection
database_url = "sqlite:///tasks.db"
# Create an engine to connect to a SQLite database
engine = create_engine(database_url, connect_args={"check_same_thread": False})

# open a sql session
SQL_Session = sessionmaker(bind=engine)
sql_session = SQL_Session()


def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    
    return response


@app.route("/")
@login_required
def index():
    """
    Task dashboard 
    contains two tables - one of tasks assigned to user and one of tasks assigned by user
    """

    return render_template("index.html", user_tasks_join_lookup=get_user_tasks_join_lookup(), assigned_by_user_tasks_join_lookup=get_user_tasks_join_lookup(is_assigner=True))


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # Flask WTForm
    login_form = LoginForm()

    # User reached route via POST (as by submitting a form via POST) validate the form fields
    if login_form.validate_on_submit():

        # Query database for username
        user = get_user(username=login_form.username.data)

        # Ensure username exists and password is correct
        if user and check_password_hash(user.hash, login_form.password.data):
            # Remember which user has logged in
            session["user_id"] = user.id
            session["username"] = user.username
            # Redirect user to home page
            return redirect("/")
        
        else:
            flash("Incorrrect username or password!") 
    elif request.method == "POST":
        flash("Invalid data!")

    # User reached route via GET (as by clicking a link or via redirect) or form validation failed
    return render_template("user_form.html", title="Log in", action="/login", user_form=login_form)


@app.route("/logout")
def logout():
    """Log user out by clearing session"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/login")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # Forget any user_id
    session.clear()

    register_form = RegisterForm()
    
    # User reached route via POST (as by submitting a form via POST) validate the form fields
    if register_form.validate_on_submit():

        username = register_form.username.data

        # Check if username is already taken
        if not get_user(username=username):
            # Insert a new user into the database
            new_user = User(username=username, hash=generate_password_hash(register_form.password.data))
            sql_session.add(new_user)
            sql_session.commit()

            # Remember which user has logged in
            session["user_id"] = new_user.id
            session["username"] = new_user.username

            flash("Registered!")

            # Redirect user to home page
            return redirect("/")
        
        else:
            flash("Username taken!")
    elif request.method == "POST":
        flash("Password must be at least 8 characters and include an uppercase letter, a lowercase letter, a digit, and a special symbol and must match confirmation!")

    # User reached route via GET (as by clicking a link or via redirect) or form validation failed
    return render_template("user_form.html", title="Register", action="/register", user_form=register_form)


@app.route("/change_password", methods=["GET", "POST"])
@login_required
def change_password():
    """Change password stored in the db as a hash value"""

    change_password_form = ChangePasswordForm()

    # User reached route via POST (as by submitting a form via POST) validate the form fields
    if change_password_form.validate_on_submit():

        user = get_user(session["user_id"])

        # Ensure user entered correct old password
        if check_password_hash(user.hash, change_password_form.old_password.data):
            # change the password
            user.hash = generate_password_hash(change_password_form.password.data)
            sql_session.commit()

            flash("Password changed!")

            # Redirect user to home page
            return redirect("/")
        
        else:
            flash("Incorrect old password!")
    elif request.method == "POST":
        flash("Password must be at least 8 characters and include an uppercase letter, a lowercase letter, a digit, and a special symbol and must match confirmation!")

    # User reached route via GET (as by clicking a link or via redirect) or form validation failed
    return render_template("user_form.html", title="Change Password", action="/change_password", user_form=change_password_form)


@app.route("/new_task", methods=["GET", "POST"])
@login_required
def new_task():
    """Create a new task"""

    task_form = TaskForm()

    # User reached route via POST (as by submitting a form via POST) validate the form fields
    if task_form.validate_on_submit():

        # create a new task with form's data and add it to the db
        new_task = Task()
        if form_to_task(task_form, new_task):
            sql_session.add(new_task)
            sql_session.commit()

            flash("Created task!")

            # send a notification to the assignee
            if session["user_id"] != new_task.assignee_id:
                notify(new_task.assignee_id, new_task.id, f'{session["username"]} assigned you task "{new_task.title}"')

            return redirect(f"show_task?id={new_task.id}")

    # User reached route via GET (as by clicking a link or via redirect) or form validation failed
    return render_template("new_task.html", form=task_form)
    
    
@app.route("/show_task")
@login_required
def show_task():
    """Show more information about a specific task, edit task button and comments on the task."""

    task_id = request.args.get("id")
    
    # get a specific task joined with the look-up tables
    tasks_join_lookup_query = get_tasks_join_lookup_query()
    task_join_lookup = tasks_join_lookup_query.filter(Task.id == task_id).first()

    return render_template(
        "show_task.html", 
        task_join_lookup=task_join_lookup,
        comments=get_comments(task_id),
        comment_form=CommentForm(task_id=task_id)
    )


@app.route("/edit_task", methods=["GET", "POST"])
@login_required
def edit_task():
    """Edit a specific task"""

    edit_task_form = EditTaskForm()

    task_id = request.args.get("id") if request.method == "GET" else edit_task_form.id.data
    task = get_task(task_id)

    # ensure only the assigner and the assignee of the task can edit it
    is_assigner = task.assigner_id == session["user_id"]
    is_assignee = task.assignee_id == session["user_id"]
    if not (is_assigner or is_assignee):
        flash("You can't edit this task")
        return redirect(f"show_task?id={task_id}")

    # User reached via POST. The assigner user can edit everything about a task
    if is_assigner and edit_task_form.validate_on_submit():
        if form_to_task(edit_task_form, task):
            sql_session.commit()
            flash("Edited task!")

            # send a notification to the assignee that the task was editted
            if session["user_id"] != task.assignee_id:
                notify(task.assignee_id, task.id, f'{session["username"]} updated task "{task.title}"')
        
            return redirect(f"show_task?id={task_id}")
    
    # User reached via POST. The assignee can edit only the task's status but not close a task
    elif is_assignee and edit_task_form.status_id.validate(edit_task_form):
        status_id = int(edit_task_form.status_id.data)
        if status_id == STATUSES.index("Closed"):
            flash("You can't close this task!")
        else:
            task.status_id = status_id
            sql_session.commit()
            flash("Edited task status!")

            # send a notification to the assigner that the task status was editted
            notify(task.assigner_id, task.id, f'{session["username"]} updated task "{task.title}" status')

            return redirect(f"show_task?id={task_id}")

    # User reached route via GET (as by clicking a link or via redirect) or form validation failed
    return render_template("edit_task.html", form=EditTaskForm(obj=task, assignee=get_user(task.assignee_id).username), is_assigner=is_assigner)


@app.route("/add_comment", methods=["POST"])
@login_required
def add_comment():
    """ Add a comment to a task"""
    comment_form = CommentForm()

    task_id = comment_form.task_id.data

    # User reached route via POST (as by submitting a form via POST) validate the form fields
    if comment_form.validate_on_submit():
        # add a new comment associated with a specific task
        new_comment = Comment(text=comment_form.text.data, user_id=session["user_id"], task_id=task_id)
        sql_session.add(new_comment)
        sql_session.commit()

        # send a notification to the assigner and the assignee if they didn't write the comment
        task = get_task(task_id)
        if session["user_id"] != task.assignee_id:
            notify(task.assignee_id, task.id, f'{session["username"]} commented on task "{task.title}"')
        if session["user_id"] != task.assigner_id:
            notify(task.assigner_id, task.id, f'{session["username"]} commented on task "{task.title}"')

    return redirect(f"show_task?id={task_id}")


@app.route("/get_users")
@login_required
def get_users():
    """Returns a list of all usernames that contain the provided "name"."""
    name = request.args.get("name")
    
    if not name:
        return jsonify({"error": 'Missing "name" parameter'}), 400
    
    if users := sql_session.query(User).filter(User.username.ilike(f"%{name}%")).all():
        return jsonify([user.username for user in users])
    else:
        return jsonify({"error": "No users found"}), 500


@app.route("/get_notifications")
@login_required
def get_notifications():
    """Returns all notifications for the current user"""
    
    if notifications := sql_session.query(Notification).filter(Notification.user_id == session["user_id"]).order_by(desc(Notification.timestamp)).all():
        return jsonify([{"text": notification.text, "task_id": notification.task_id, "timestamp": notification.timestamp} for notification in notifications])
    else:
        return jsonify({"error": "No notifications found"}), 500
    

@app.route("/search_task", methods=["GET", "POST"])
@login_required
def search_task():
    """Search and filter tasks"""
    search_task_form = SearchTaskForm()
    tasks_join_lookup = []

    # User reached route via POST (as by submitting a form via POST) validate the form fields
    if search_task_form.validate_on_submit():
        # get all tasks that pass the filters provided in the form
        tasks_join_lookup_query = get_tasks_join_lookup_query()
        tasks_join_lookup = filter_tasks_query(tasks_join_lookup_query, search_task_form).all()
        flash(f"{len(tasks_join_lookup)} tasks found!")

    return render_template("search_task.html", form=search_task_form, tasks_join_lookup=tasks_join_lookup)


def get_user(id=None, username=""):
    """Returns a sqlalchemy User table obj by filtering id or username"""
    if username:
        return sql_session.query(User).filter_by(username=username).first()
    return sql_session.query(User).filter_by(id=id).first()


def get_task(id):
    """Returns a sqlalchemy Task table obj by filtering id"""
    return sql_session.query(Task).filter_by(id=id).first()
    

def form_to_task(form, task):
    """ Populate a sqlalchemy Task table obj using a Flask WTForm Task obj"""
    form.populate_obj(task)
    task.assigner_id = session["user_id"]
    if assignee := get_user(username=form.assignee.data):
        task.assignee_id = assignee.id
        return True
    else:
        flash("Invalid assignee!")
        return False


def get_user_tasks_join_lookup(is_assigner=False):
    """ Returns all unclosed tasks joined with look-up tables, where user is assignee (or assigner) """
    query = get_tasks_join_lookup_query()

    query = query.filter(Status.id != STATUSES.index("Closed"))

    if is_assigner:
        query = query.filter(Task.assigner_id == session["user_id"])
    else:
        query = query.filter(Task.assignee_id == session["user_id"])

    return query.all()


def get_tasks_join_lookup_query():
    """ Returns a query of all tasks joined with the look-up tables for users, statuses and priorities"""
    UserAssignee = aliased(User)
    UserAssigner = aliased(User)

    return (sql_session.query(Task, UserAssignee.username, UserAssigner.username, Priority.level, Status.status)
            .join(UserAssignee, Task.assignee_id == UserAssignee.id)
            .join(UserAssigner, Task.assigner_id == UserAssigner.id)
            .join(Priority, Task.priority_id == Priority.id)
            .join(Status, Task.status_id == Status.id)
            )


def filter_tasks_query(tasks_join_lookup_query, form):
    """Filter sqlalchemy Tasks query using form fields as filters"""
    if text := form.text.data:
        tasks_join_lookup_query = tasks_join_lookup_query.filter(
            or_(Task.title.ilike(f"%{text}%"), Task.description.ilike(f"%{text}%")))

    assignee = form.assignee.data
    if user_assignee := get_user(username=assignee):
        tasks_join_lookup_query = tasks_join_lookup_query.filter(Task.assignee_id == user_assignee.id)
    elif assignee:
        tasks_join_lookup_query = tasks_join_lookup_query.filter(False)

    assigner = form.assigner.data
    if user_assigner := get_user(username=assigner):
        tasks_join_lookup_query = tasks_join_lookup_query.filter(Task.assigner_id == user_assigner.id)
    elif assigner:
        tasks_join_lookup_query = tasks_join_lookup_query.filter(False)

    if due_date := form.due_date.data:
        tasks_join_lookup_query = tasks_join_lookup_query.filter(Task.due_date == due_date)

    priority_id = form.priority_id.data
    if priority_id != "Any":
        tasks_join_lookup_query = tasks_join_lookup_query.filter(Task.priority_id == int(priority_id))

    status_id = form.status_id.data
    if status_id != "Any":
        tasks_join_lookup_query = tasks_join_lookup_query.filter(Task.status_id == int(status_id))

    return tasks_join_lookup_query


def get_comments(task_id):
    """ Returns all comments associated with a specific task."""
    return (sql_session.query(Comment, User.username)
            .join(User, Comment.user_id == User.id)
            .filter(Comment.task_id == task_id)
            .order_by(Comment.timestamp)
            .all()
            )


def notify(user_id, task_id, text):
    """Add a new notification to the db associated with a user and a task"""

    new_notification = Notification(user_id=user_id, task_id=task_id, text=text)
    sql_session.add(new_notification)
    sql_session.commit()


# Close the sql session
sql_session.close()