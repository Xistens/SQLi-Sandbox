#!/usr/bin/python3
from functools import wraps
from flask import (
    render_template,
    Blueprint,
    current_app,
    redirect,
    url_for,
    session,
    request,
    flash
)
from sqli_platform import app, app_log, db
from sqli_platform.utils import flag

"""
The login function can be bypassed with ' OR 1=1--
"""

_bp = "challenge1"
challenge1 = Blueprint(_bp , __name__, template_folder='templates', url_prefix='/challenge1')
_templ = "challenges/challenge1"


@challenge1.context_processor
def sessions():
    """
    
    """
    return dict(
        csession = session.get("challenge1_user_id", None),
        csession_name=session.get("challenge1_username", None)
    )

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("challenge1_user_id", None) is None:
            return redirect(url_for(f"challenge1.login", next=request.url))
        return f(*args, **kwargs)
    return decorated_function

@challenge1.route("/")
@challenge1.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].lower()
        password = request.form["password"]

        if not (username and password):
            flash("Username or Password cannot be empty.", "warning")
            return redirect(url_for("challenge1.login"))
        
        user = db.sql_query(_bp,
            f"SELECT id, username FROM users WHERE username = '{username}' AND password = '{password}'")
        
        if user:
            data = []
            for row in user:
                data.append([x for x in row])
            app_log.debug(data)
            session["challenge1_user_id"] = data[0][0]
            session["challenge1_username"] = data[0][1]
            session["challenge1_userobj"] = data
            app_log.debug(
                f"challenge2 user login: Session: {session['challenge1_user_id']} {session['challenge1_userobj']}")
            return redirect(url_for("challenge1.home"))
        else:
            flash("Invalid username or password.", "danger")
    return render_template(f"{_templ}/login.html")


@challenge1.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"].lower()
        password = request.form["password"]

        if not (username and password):
            flash("Username or Password cannot be empty.")
            return redirect(url_for("challenge1.signup"))

        # No error checking etc...
        if db.sql_query(_bp, "SELECT username FROM users WHERE username=?", [username]):
            flash("Username already exists.", "danger")
        else:
            db.sql_insert(_bp, "INSERT INTO users (username, password) VALUES (?, ?)", [
                          username, password])
            return redirect(url_for("challenge1.login"))
    return render_template(f"{_templ}/registration.html")


@challenge1.route("/home")
@login_required
def home():
    sess = session.get("challenge1_user_id", None)
    f = ""
    if sess == 1:
        f = flag.get_flag("challenge1")
    return render_template(f"challenge1/index.html", flag=f)


@challenge1.route("/notes", methods=["GET", "POST"])
@login_required
def notes():
    flash("Not Implemented ", "warning")
    return render_template(f"{_templ}/notes.html")


@challenge1.route("/changepwd", methods=["GET", "POST"])
@login_required
def changepwd():
    flash("Not Implemented ", "warning")
    return render_template(f"{_templ}/updatepwd.html")


@challenge1.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("challenge1.login"))

