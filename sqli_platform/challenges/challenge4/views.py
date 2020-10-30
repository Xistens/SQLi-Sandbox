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
    flash,
    jsonify
)
from sqli_platform import app, app_log, db
from sqli_platform.utils.challenge import get_config

"""
The login function has been patched.
The notes function has been patched.
password update function is patched.

Previous Book Exploit:
challenge4/book?title=test%27)%20UNION%20SELECT%201,2,3,4--
/challenge4/book?title=test')union select 1,2,group_concat(password),group_concat(username) from users--
"""

_bp = "challenge4"
challenge4 = Blueprint(_bp, __name__,
                       template_folder="templates", url_prefix=f"/{_bp}")
_templ = "challenges/challenge1"


@challenge4.context_processor
def sessions():
    """
    
    """
    return dict(
        csession=session.get(f"{_bp}_user_id", None),
        csession_name=session.get(f"{_bp}_username", None),
        ctitle=get_config(_bp, "title")
    )


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get(f"{_bp}_user_id", None) is None:
            return redirect(url_for(f"{_bp}.login", next=request.url))
        return f(*args, **kwargs)
    return decorated_function


@challenge4.route("/")
@challenge4.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].lower()
        password = request.form["password"]

        if not (username and password):
            flash("Username or Password cannot be empty.", "warning")
            return redirect(url_for(f"{_bp}.login"))

        user = db.sql_query(_bp, "SELECT id, username FROM users WHERE username = ? AND password = ?",
                            [username, password], one=True)

        if user:
            session[f"{_bp}_user_id"] = user["id"]
            session[f"{_bp}_username"] = user["username"]
            return redirect(url_for(f"{_bp}.home"))
        else:
            flash("Invalid username or password.", "danger")
    return render_template(f"{_templ}/login.html")


@challenge4.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"].lower()
        password = request.form["password"]

        if not (username and password):
            flash("Username or Password cannot be empty.")
            return redirect(url_for(f"{_bp}.signup"))

        # No error checking etc...
        if db.sql_query(_bp, "SELECT username FROM users WHERE username=?", [username]):
            flash("Username already exists.", "danger")
        else:
            db.sql_insert(_bp, "INSERT INTO users (username, password) VALUES (?, ?)", [
                          username, password])
            return redirect(url_for(f"{_bp}.login"))
    return render_template(f"{_templ}/registration.html")


@challenge4.route("/home")
@login_required
def home():
    return render_template(f"{_bp}/index.html")


@challenge4.route("/notes", methods=["GET", "POST"])
@login_required
def notes():
    user = db.sql_query(_bp, "SELECT username FROM users WHERE id=?",
                        [session[f"{_bp}_user_id"]], one=True)

    if request.method == "POST":
        title = request.form["title"]
        note = request.form["note"]
        db.sql_insert(_bp, "INSERT INTO notes (username, title, note) VALUES (?, ?, ?)",
                      [user["username"], title, note])
        return redirect(url_for(f"{_bp}.notes"))

    notes = db.sql_query(_bp,
                         f"SELECT title, note FROM notes WHERE username = ?", [user['username']])
    return render_template(f"{_templ}/notes.html", notes=notes, user=user["username"])


@challenge4.route("/changepwd", methods=["GET", "POST"])
@login_required
def changepwd():
    if request.method == "POST":
        current_pwd = request.form["current-password"]
        new_pwd = request.form["password"]
        new_pwd2 = request.form["password2"]

        if not (new_pwd == new_pwd2):
            flash("Passwords doesn't match.")
            return redirect(url_for(f"{_bp}.changepwd"))

        user = db.sql_query(_bp, "SELECT username, password FROM users WHERE id = ?",
                            [session[f"{_bp}_user_id"]], one=True)

        if not (current_pwd == user["password"]):
            flash("Wrong password supplied.", "danger")
            return redirect(url_for(f"{_bp}.changepwd"))

        db.sql_insert(
            _bp, 
            f"UPDATE users SET password = ? WHERE username = ?", 
            [user['username'], new_pwd]
        )
        flash("Password changed", "info")
        return redirect(url_for(f"{_bp}.changepwd"))
    return render_template(f"{_templ}/updatepwd.html")


@challenge4.route("/logout")
def logout():
    session.clear()
    return redirect(url_for(f"{_bp}.login"))


@challenge4.route("/book", methods=["GET"])
@login_required
def book():
    if request.method == "GET":
        title = request.args.get("title", "")
        book = None


        book = db.sql_query(
            _bp,
            f"SELECT * from books WHERE id = (SELECT id FROM books WHERE title='{title}')",
            one=True
        )
        if book:
            return jsonify(
                title=book["title"],
                description=book["description"],
                author=book["author"]
            )
        return ""
