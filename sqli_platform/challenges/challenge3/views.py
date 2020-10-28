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
from sqli_platform.utils.flag import get_flag

"""
The login function has been patched.
The notes function has been patched.

Create user:
username: admin' -- -
password: whatever

Change password, enter old password <whatever> and set something new. 
Login with:
username: admin
password: <password set in previous step>
"""

_bp = "challenge3"
challenge3 = Blueprint(_bp, __name__,
                       template_folder="templates", url_prefix="/challenge3")
_templ = "challenges/challenge1"


@challenge3.context_processor
def sessions():
    """
    
    """
    return dict(
        csession=session.get("challenge3_user_id", None),
        csession_name=session.get("challenge3_username", None)
    )


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("challenge3_user_id", None) is None:
            return redirect(url_for(f"challenge3.login", next=request.url))
        return f(*args, **kwargs)
    return decorated_function


@challenge3.route("/")
@challenge3.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].lower()
        password = request.form["password"]

        if not (username and password):
            flash("Username or Password cannot be empty.", "warning")
            return redirect(url_for("challenge3.login"))

        user = db.sql_query(_bp, "SELECT id, username FROM users WHERE username = ? AND password = ?",
                            [username, password], one=True)

        if user:
            session["challenge3_user_id"] = user["id"]
            session["challenge3_username"] = user["username"]
            return redirect(url_for("challenge3.home"))
        else:
            flash("Invalid username or password.", "danger")
    return render_template(f"{_templ}/login.html")


@challenge3.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"].lower()
        password = request.form["password"]

        if not (username and password):
            flash("Username or Password cannot be empty.")
            return redirect(url_for("challenge3.signup"))

        # No error checking etc...
        if db.sql_query(_bp, "SELECT username FROM users WHERE username=?", [username]):
            flash("Username already exists.", "danger")
        else:
            db.sql_insert(_bp, "INSERT INTO users (username, password) VALUES (?, ?)", [
                          username, password])
            return redirect(url_for("challenge3.login"))
    return render_template(f"{_templ}/registration.html")


@challenge3.route("/home")
@login_required
def home():
    sess = session.get("challenge3_user_id", None)
    f = ""
    if sess == 1:
        f = get_flag("challenge3")
    return render_template(f"challenge3/index.html", flag=f)


@challenge3.route("/notes", methods=["GET", "POST"])
@login_required
def notes():
    user = db.sql_query(_bp, "SELECT username FROM users WHERE id=?",
                        [session["challenge3_user_id"]], one=True)

    if request.method == "POST":
        title = request.form["title"]
        note = request.form["note"]
        db.sql_insert(_bp, "INSERT INTO notes (username, title, note) VALUES (?, ?, ?)",
                      [user["username"], title, note])
        return redirect(url_for("challenge3.notes"))

    notes = db.sql_query(_bp,
                         f"SELECT title, note FROM notes WHERE username = ?", [user['username']])
    return render_template(f"{_templ}/notes.html", notes=notes, user=user["username"])


@challenge3.route("/changepwd", methods=["GET", "POST"])
@login_required
def changepwd():
    if request.method == "POST":
        current_pwd = request.form["current-password"]
        new_pwd = request.form["password"]
        new_pwd2 = request.form["password2"]

        if not (new_pwd == new_pwd2):
            flash("Passwords doesn't match.")
            return redirect(url_for("challenge3.changepwd"))

        user = db.sql_query(_bp, "SELECT username, password FROM users WHERE id = ?",
                            [session["challenge3_user_id"]], one=True)

        if not (current_pwd == user["password"]):
            flash("Wrong password supplied.", "danger")
            return redirect(url_for("challenge3.changepwd"))

        db.sql_insert(
            _bp, f"UPDATE users SET password = ? WHERE username = '{user['username']}'", [new_pwd])
        flash("Password changed", "info")
        return redirect(url_for("challenge3.changepwd"))
    return render_template(f"{_templ}/updatepwd.html")


@challenge3.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("challenge3.login"))
# @challenge3.route('/test')
# def test():
#     result = db.get_engine(current_app, bind="challenge3").execute("SELECT * FROM user")
#     for i in result:
#         print(i)
#     return render_template('index.html')
