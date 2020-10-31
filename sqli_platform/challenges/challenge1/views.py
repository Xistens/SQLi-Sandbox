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

_bp = "challenge1"
challenge1 = Blueprint(_bp , __name__, template_folder='templates', url_prefix=f"/{_bp}")
_templ = "challenges/challenge1"
_query = []

@challenge1.context_processor
def sessions():
    """
    
    """
    global _query
    d = dict(
        csession = session.get(f"{_bp}_user_id", None),
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

@challenge1.route("/")
@challenge1.route("/login", methods=["GET", "POST"])
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
            app_log.debug(data)
            session[f"{_bp}_user_id"] = data[0][0]
            session[f"{_bp}_username"] = data[0][1]
            session[f"{_bp}_userobj"] = data
            app_log.debug(
                f"challenge2 user login: Session: {session[f'{_bp}_user_id']} {session['challenge1_userobj']}")
            return redirect(url_for(f"{_bp}.home"))
        else:
            flash("Invalid username or password.", "danger")
    return render_template(f"{_templ}/login.html")


@challenge1.route("/signup", methods=["GET", "POST"])
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


@challenge1.route("/home")
@login_required
def home():
    sess = session.get(f"{_bp}_user_id", None)
    f = ""
    if sess == 1:
        f = get_flag(_bp)
    return render_template(f"{_bp}/index.html", flag=f)


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
    return redirect(url_for(f"{_bp}.login"))

