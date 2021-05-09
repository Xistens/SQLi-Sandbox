#!/usr/bin/python3
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
from sqli_platform.utils.challenge import get_config, format_query, login_required, clear_session

"""
The login function has been patched.
The developers have added the note function, it is not directly vulnerable.

Signup:
' union select 1,2'
' union select 1,group_concat(tbl_name) from sqlite_master where type='table' and tbl_name not like 'sqlite_%''
"""

_bp = "challenge4"
challenge4 = Blueprint(_bp, __name__, template_folder="templates", url_prefix=f"/{_bp}")
_templ = "challenges/challenge1"
_query = []


@challenge4.context_processor
def context():
    global _query
    d = dict(
        query=format_query(_query)
    )
    _query = []
    return d


@challenge4.route("/")
@challenge4.route("/login", methods=["GET", "POST"])
def login():
    global _query

    if request.method == "POST":
        username = request.form["username"].lower()
        password = request.form["password"]

        if not (username and password):
            flash("Username or Password cannot be empty.", "warning")
            return redirect(url_for("challenge4.login"))

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


@challenge4.route("/signup", methods=["GET", "POST"])
def signup():
    global _query

    if request.method == "POST":
        username = request.form["username"].lower()
        password = request.form["password"]

        if not (username and password):
            flash("Username or Password cannot be empty.")
            return redirect(url_for("challenge4.signup"))

        # No error checking etc...
        query = "SELECT username FROM users WHERE username=?"
        _query.append((query, [username]))
        if db.sql_query(_bp, query, [username]):
            flash("Username already exists.", "danger")
        else:
            query = "INSERT INTO users (username, password) VALUES (?, ?)"
            params = [username, password]
            _query.append((query, params))
            db.sql_insert(_bp, query, params)
            return redirect(url_for(f"{_bp}.login"))
    return render_template(f"{_templ}/registration.html")


@challenge4.route("/home")
@login_required(_bp)
def home():
    return render_template(f"{_templ}/index.html")


@challenge4.route("/notes", methods=["GET", "POST"])
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

    query = f"SELECT title, note FROM notes WHERE username = '{user['username']}'"
    _query.append(query)
    notes = db.sql_query(_bp, query)
    return render_template(f"{_templ}/notes.html", notes=notes, user=user["username"])


@challenge4.route("/changepwd", methods=["GET", "POST"])
@login_required(_bp)
def changepwd():
    flash("Not Implemented ", "warning")
    return render_template(f"{_templ}/updatepwd.html")


@challenge4.route("/logout")
def logout():
    clear_session(_bp)
    return redirect(url_for(f"{_bp}.login"))

