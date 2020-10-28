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

"""
The login function has been patched.
The developers have added the note function, it is not directly vulnerable.

Signup:
' union select 1,2'
' union select 1,group_concat(tbl_name) from sqlite_master where type='table' and tbl_name not like 'sqlite_%''
"""

_bp = "challenge2"
challenge2 = Blueprint(_bp, __name__, template_folder="templates", url_prefix="/challenge2")
_templ = "challenges/challenge1"


@challenge2.context_processor
def sessions():
    """
    
    """
    return dict(
        csession=session.get("challenge2_user_id", None),
        csession_name=session.get("challenge2_username", None)
    )


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("challenge2_user_id", None) is None:
            return redirect(url_for(f"challenge2.login", next=request.url))
        return f(*args, **kwargs)
    return decorated_function


@challenge2.route("/")
@challenge2.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].lower()
        password = request.form["password"]

        if not (username and password):
            flash("Username or Password cannot be empty.", "warning")
            return redirect(url_for("challenge2.login"))

        user = db.sql_query(_bp, "SELECT id, username FROM users WHERE username = ? AND password = ?",
                            [username, password], one=True)

        if user:
            session["challenge2_user_id"] = user["id"]
            session["challenge2_username"] = user["username"]
            return redirect(url_for("challenge2.home"))
        else:
            flash("Invalid username or password.", "danger")
    return render_template(f"{_templ}/login.html")


@challenge2.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"].lower()
        password = request.form["password"]

        if not (username and password):
            flash("Username or Password cannot be empty.")
            return redirect(url_for("challenge2.signup"))

        # No error checking etc...
        if db.sql_query(_bp, "SELECT username FROM users WHERE username=?", [username]):
            flash("Username already exists.", "danger")
        else:
            db.sql_insert(_bp, "INSERT INTO users (username, password) VALUES (?, ?)", [
                          username, password])
            return redirect(url_for("challenge2.login"))
    return render_template(f"{_templ}/registration.html")


@challenge2.route("/home")
@login_required
def home():
    return render_template(f"{_templ}/index.html")


@challenge2.route("/notes", methods=["GET", "POST"])
@login_required
def notes():
    user = db.sql_query(_bp, "SELECT username FROM users WHERE id=?",
                        [session["challenge2_user_id"]], one=True)

    if request.method == "POST":
        title = request.form["title"]
        note = request.form["note"]
        db.sql_insert(_bp, "INSERT INTO notes (username, title, note) VALUES (?, ?, ?)",
                      [user["username"], title, note])
        return redirect(url_for("challenge2.notes"))

    notes = db.sql_query(_bp,
                         f"SELECT title, note FROM notes WHERE username = '{user['username']}'")
    return render_template(f"{_templ}/notes.html", notes=notes, user=user["username"])


@challenge2.route("/changepwd", methods=["GET", "POST"])
@login_required
def changepwd():
    flash("Not Implemented ", "warning")
    return render_template(f"{_templ}/updatepwd.html")


@challenge2.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("challenge2.login"))

