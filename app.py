import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import login_required, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///project.db")

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
    """Landing page"""

    return render_template("/index.html")

@app.route("/contact")
@login_required
def contact():
    '''Shows table of contacts'''
    contacts = db.execute("SELECT * FROM contact ORDER BY name ASC")
    return render_template("/contact.html", contacts = contacts)

@app.route("/contact/create", methods=["GET", "POST"])
@login_required
def contact_create():
    '''Creates new contact'''
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        type = request.form.get("type")
        agency = request.form.get("agency")
        
        if not name:
            return "Name is required.", 400
        else:
            if not email:
                email = ''
            if not phone:
                phone = ''
            if not agency:
                agency = ''
            db.execute("INSERT INTO contact (name, email, phone, type, agency) VALUES (?, ?, ?, ?, ?)", name, email, phone, type, agency)
            return redirect("/contact")
    else:
        return render_template("/contact_create.html")
    
@app.route("/contact/edit/<int:id>", methods=["GET", "POST"])
@login_required
def contact_edit(id):
    '''Edits existing contact'''
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        type = request.form.get("type")
        agency = request.form.get("agency") 
        db.execute("UPDATE contact SET name = ?, email = ?, phone = ?, type = ?, agency = ? WHERE id = ?", name, email, phone, type, agency, id)
        
        return redirect("/contact")           
    else:
        contact = db.execute("SELECT * FROM contact WHERE id = ?", id)
        return render_template("/contact_edit.html", contact = contact)

@app.route("/contact/delete/<id>")
@login_required
def contact_delete(id):
    '''Deletes existing contact'''
    try:
        db.execute("DELETE FROM contact WHERE id= ?", id)
        return redirect("/contact")
    except:
        return "Contact could not be deleted.", 400


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Clear session
    session.clear()

    if request.method == "POST":
        if not request.form.get("username"):
            return "A username is required.", 400
        elif not request.form.get("password"):
            return "A password is required.", 400
        
        # Query users for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Check username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return "Your login attempt has failed.", 400
        
        # Create new session for success login
        session["user_id"] = rows[0]["id"]

        # Redirect user to homepage
        return redirect("/")

    else:
        return render_template("/login.html")

@app.route("/logout")
def logout():
    """Logout user"""

    session.clear()
    return redirect("/")


@app.route("/project")
@login_required
def project():
    '''Shows table of projects'''
    projects = db.execute("SELECT * FROM project ORDER BY title ASC")
    return render_template("/project.html", projects = projects)


@app.route("/project/create", methods=["GET", "POST"])
@login_required
def project_create():
    '''Creates new project'''
    if request.method == "POST":
        title = request.form.get("title")
        main_contact = request.form.get("main_contact")
        date = request.form.get("date")
        progress = request.form.get("progress")
        amount = request.form.get("amount")
        type = request.form.get("type")
        location = request.form.get("location")
        description = request.form.get("description")
        
        if not title:
            return "Title is required.", 400
        # if not main_contact:
        #     return "Main contact is required.", 400
        else:
            if not description:
                description = ""
            db.execute("INSERT INTO project (title, main_contact, date, progress, amount, type, location, description) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                       title, main_contact, date, progress, amount, type, location, description)
            return redirect("/project")
    else:
        return render_template("/project_create.html")


@app.route("/project/edit/<int:id>", methods=["GET", "POST"])
@login_required
def project_edit(id):
    '''Edits project'''
    if request.method == "POST":
        return redirect("/project/detail/"+id+".html")
    else:
        project = db.execute("SELECT * FROM project WHERE id = ?", id)
        return render_template("project_edit.html", project = project)
    
    
@app.route("/project/detail/<int:id>")
@login_required
def project_detail(id):
    '''Displays project detail'''
    project = db.execute("SELECT * FROM project WHERE id = ?", id)
    return render_template("/project_detail.html", project = project)


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register User"""
    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        if not username:
            return "You must enter a username.", 400
        # Check if username is not entered exists
        if not username:
            return 400
        rows = db.execute("SELECT username FROM users WHERE username = ?", username)
        if len(rows) == 1:
            return "Username already exists.", 400
        # Check if password is blank
        if (not password) or (not confirmation):
            return "You must enter a password.", 400
        # Check if passwords do not match
        if password != confirmation:
            return "Please enter matching passwords.", 400
        else:
            # Register the user and login
            db.execute ("INSERT INTO users (username, hash) VALUES (? , ?)", username, generate_password_hash(password))
            session["user_id"] = db.execute("SELECT id FROM users WHERE username = ?", username)
            return redirect("/")
    
    else:
        return render_template("register.html")