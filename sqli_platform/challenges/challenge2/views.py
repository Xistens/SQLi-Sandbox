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
from sqli_platform import (app, clog, db)
from sqli_platform.utils.challenge import (get_flag, get_config, format_query, login_required, clear_session)

"""
Dump passwords to get flag:
' UNION SELECT 1,group_concat(password) FROM users--

This was also possible from challenge 1: Flask Session Cookie decode:
https://www.kirsle.net/wizards/flask-session.cgi
"""

_bp = "challenge2"
challenge2 = Blueprint(_bp , __name__, template_folder='templates', url_prefix=f"/{_bp}")
_templ = "challenges/challenge1"
_query = []

@challenge2.context_processor
def context():
    global _query
    d = dict(
        query=format_query(_query)
    )
    _query = []
    return d


@challenge2.route("/")
@challenge2.route("/login", methods=["GET", "POST"])
def login():
    global _query

    if request.method == "POST":
        username = request.form["username"].lower()
        password = request.form["password"]

        if not (username and password):
            flash("Username or Password cannot be empty.", "warning")
            return redirect(url_for(f"{_bp}.login"))
        
        query = f"SELECT id, username FROM users WHERE username = '{username}' AND password = '{password}'"
        _query.append(query)
        user = db.sql_query(_bp, query)
        
        if user:
            data = []
            for row in user:
                data.append([x for x in row])
            
            # User can decode the cookie to get the flag
            session[f"{_bp}_user_id"] = data[0][0]
            session[f"{_bp}_username"] = data[0][1]

            clog.debug(f"{_bp} login: Session: {session[f'{_bp}_user_id']}")
            return redirect(url_for(f"{_bp}.home"))
        else:
            flash("Invalid username or password.", "danger")
    return render_template(f"{_templ}/login.html", slide_num=0)


@challenge2.route("/signup", methods=["GET", "POST"])
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
        _query.append((query, [username]))
        if db.sql_query(_bp, query, [username]):
            flash("Username already exists.", "danger")
        else:
            query = "INSERT INTO users (username, password) VALUES (?, ?)"
            params = [username, password]
            _query.append((query, params))
            db.sql_insert(_bp, query, params)
            clog.info(f"{_bp} - signup: {username} {password}")
            return redirect(url_for(f"{_bp}.login"))
    return render_template(f"{_templ}/registration.html")


@challenge2.route("/home")
@login_required(_bp)
def home():
    return render_template(f"{_bp}/index.html")


@challenge2.route("/notes", methods=["GET", "POST"])
@login_required(_bp)
def notes():
    flash("Not Implemented ", "warning")
    return render_template(f"{_templ}/notes.html")


@challenge2.route("/changepwd", methods=["GET", "POST"])
@login_required(_bp)
def changepwd():
    flash("Not Implemented ", "warning")
    return render_template(f"{_templ}/updatepwd.html")


@challenge2.route("/logout")
def logout():
    clear_session(_bp)
    return redirect(url_for(f"{_bp}.login"))

