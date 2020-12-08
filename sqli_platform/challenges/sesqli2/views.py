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
from sqli_platform import (app, clog, db)
from sqli_platform.utils.challenge import (
    get_flag, get_config, format_query, hash_pwd)

"""

"""

_bp = "sesqli2"
sesqli2 = Blueprint(
    _bp, __name__, template_folder='templates', url_prefix=f"/{_bp}")
_templ = "challenges/sesqli"
_query = []


def get_profile():
    query = f"SELECT uid, name, profileID, salary, passportNr, email, nickName, password FROM usertable WHERE UID = ?"
    params = [session.get(f"{_bp}_user_id", None)]
    return db.sql_query(_bp, query, params, one=True)


@sesqli2.context_processor
def sessions():
    """
    
    """
    global _query
    d = dict(
        cname=_bp,
        csession=session.get(f"{_bp}_user_id", None),
        ctitle=get_config(f"{_bp}", "title"),
        query=format_query(_query),
        slides=f"{_bp}/slides/slides.html",
        cdesc=get_config(f"{_bp}", "description")
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


@sesqli2.route("/")
@sesqli2.route("/login", methods=["GET"])
def login():
    global _query

    username = request.args.get("profileID")
    password = request.args.get("password")
    if username and password:
        password = hash_pwd(password)

        query = f"SELECT uid, name, profileID, salary, passportNr, email, nickName, password FROM usertable WHERE profileID = '{username}' AND password = '{password}'"
        _query.append(query)
        user = db.sql_query(_bp, query, one=True)

        if user:
            session[f"{_bp}_user_id"] = user["uid"]
            session[f"{_bp}_data"] = dict(user)

            return redirect(url_for(f"{_bp}.home"))
        else:
            flash("The account information you provided does not exist!", "danger")
            return render_template(f"{_bp}/login.html", slide_num=0)
    else:
        return render_template(f"{_bp}/login.html", slide_num=0)


@sesqli2.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    global _query

    if request.method == "POST":
        email = request.form["email"]
        nick = request.form["nickName"]
        password = request.form["password"]

        query = ""
        if password:
            pwd_hash = hash_pwd(password)
            query = f"UPDATE usertable SET nickName='{nick}',email='{email}',password='{pwd_hash}' WHERE UID='{session[f'{_bp}_user_id']}'"
        else:
            query = f"UPDATE usertable SET nickName='{nick}',email='{email}' WHERE UID='{session[f'{_bp}_user_id']}'"

        _query.append(query)
        db.sql_insert(_bp, query)
        return redirect(url_for(f"{_bp}.home"))
    return render_template(f"{_templ}/profile.html", csess_obj=get_profile())


@sesqli2.route("/home")
@login_required
def home():
    return render_template(f"{_templ}/index.html", csess_obj=get_profile())


@sesqli2.route("/logout")
def logout():
    session.clear()
    return redirect(url_for(f"{_bp}.login"))
