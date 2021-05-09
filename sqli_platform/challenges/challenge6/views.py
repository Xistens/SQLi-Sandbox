#!/usr/bin/python3
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
from sqli_platform.utils.challenge import get_config, format_query, login_required, clear_session

"""
The login function has been patched.
The notes function has been patched.
password update function is patched.

Previous Book Exploit:
challenge6/book?title=test%27)%20UNION%20SELECT%201,2,3,4--
/challenge6/book?title=test')union select 1,2,group_concat(password),group_concat(username) from users--
"""

_bp = "challenge6"
challenge6 = Blueprint(_bp, __name__,
                       template_folder="templates", url_prefix=f"/{_bp}")
_templ = "challenges/challenge1"
_query = []

@challenge6.context_processor
def context():
    global _query
    d = dict(
        query=format_query(_query)
    )
    _query = []
    return d


@challenge6.route("/")
@challenge6.route("/login", methods=["GET", "POST"])
def login():
    global _query

    if request.method == "POST":
        username = request.form["username"].lower()
        password = request.form["password"]

        if not (username and password):
            flash("Username or Password cannot be empty.", "warning")
            return redirect(url_for(f"{_bp}.login"))

        query = "SELECT id, username FROM users WHERE username = ? AND password = ?"
        params = [username, password]
        _query.append((query, params))
        user = db.sql_query(_bp, query, params, one=True)

        if user:
            session[f"{_bp}_user_id"] = user["id"]
            session[f"{_bp}_username"] = user["username"][:30]
            return redirect(url_for(f"{_bp}.home"))
        else:
            flash("Invalid username or password.", "danger")
    return render_template(f"{_templ}/login.html")


@challenge6.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"].lower()
        password = request.form["password"]

        # No error checking etc...
        query = "SELECT username FROM users WHERE username=?"
        params = [username]
        _query.append((query, params))
        if db.sql_query(_bp, query, params):
            flash("Username already exists.", "danger")
        else:
            query = "INSERT INTO users (username, password) VALUES (?, ?)"
            params = [username, password]
            _query.append((query, params))
            db.sql_insert(_bp, query, params)
            return redirect(url_for(f"{_bp}.login"))
    return render_template(f"{_templ}/registration.html")


@challenge6.route("/home")
@login_required(_bp)
def home():
    return render_template(f"{_bp}/index.html")


@challenge6.route("/notes", methods=["GET", "POST"])
@login_required(_bp)
def notes():
    global _query

    query = "SELECT username FROM users WHERE id=?"
    params = [session[f"{_bp}_user_id"]]
    #_query.append((query, params))
    user = db.sql_query(_bp, query, params, one=True)

    if request.method == "POST":
        title = request.form["title"]
        note = request.form["note"]

        query = "INSERT INTO notes (username, title, note) VALUES (?, ?, ?)"
        params = [user["username"], title, note]
        _query.append((query, params))
        db.sql_insert(_bp, query, params)
        return redirect(url_for(f"{_bp}.notes"))

    query = f"SELECT title, note FROM notes WHERE username = ?"
    params = [user['username']]
    _query.append((query, params))
    notes = db.sql_query(_bp, query, params)
    return render_template(f"{_templ}/notes.html", notes=notes, user=user["username"])


@challenge6.route("/changepwd", methods=["GET", "POST"])
@login_required(_bp)
def changepwd():
    global _query

    if request.method == "POST":
        current_pwd = request.form["current-password"]
        new_pwd = request.form["password"]
        new_pwd2 = request.form["password2"]

        if not (new_pwd == new_pwd2):
            flash("Passwords doesn't match.")
            return redirect(url_for(f"{_bp}.changepwd"))

        query = "SELECT username, password FROM users WHERE id = ?"
        params = [session[f"{_bp}_user_id"]]
        _query.append((query, params))
        user = db.sql_query(_bp, query, params, one=True)

        if not (current_pwd == user["password"]):
            flash("Wrong password supplied.", "danger")
            return redirect(url_for(f"{_bp}.changepwd"))

        query = f"UPDATE users SET password = ? WHERE username = ?"
        params = [user['username'], new_pwd]
        _query.append((query, params))
        db.sql_insert(_bp, query, params)

        flash("Password changed", "info")
        return redirect(url_for(f"{_bp}.changepwd"))
    return render_template(f"{_templ}/updatepwd.html")


@challenge6.route("/logout")
def logout():
    clear_session(_bp)
    return redirect(url_for(f"{_bp}.login"))


@challenge6.route("/book", methods=["GET"])
@login_required(_bp)
def book():
    global _query

    if request.method == "GET":
        title = request.args.get("title", "")
        book = {}

        query = f"SELECT * from books WHERE id = (SELECT id FROM books WHERE title like '{title}%')"
        _query.append(query)
        book = db.sql_query(_bp, query)
        return render_template(f"{_templ}/book.html", data=book)
