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
from sqli_platform.utils.challenge import (get_flag, get_config, format_query, hash_pwd, login_required, clear_session)

"""

"""

_bp = "sesqli6"
sesqli6 = Blueprint(_bp , __name__, template_folder='templates', url_prefix=f"/{_bp}")
_templ = "challenges/sesqli"
_query = []

def get_profile():
    query = f"SELECT uid, name, profileID, salary, passportNr, email, nickName, password FROM usertable WHERE UID = ?"
    params = [session.get(f"{_bp}_user_id", None)]
    return db.sql_query(_bp, query, params, one=True)

@sesqli6.context_processor
def context():
    global _query
    d = dict(
        query=format_query(_query)
    )
    _query = []
    return d


@sesqli6.route("/")
@sesqli6.route("/login", methods=["GET", "POST"])
def login():
    global _query

    if request.method == "POST":
        username = request.form["profileID"]
        password = request.form["password"]
        password = hash_pwd(password)
        # Hash password

        if not (username and password):
            flash("Username or Password cannot be empty.", "warning")
            return redirect(url_for(f"{_bp}.login"))
        
        query = f"SELECT uid, name, profileID, salary, passportNr, email, nickName, password FROM usertable WHERE profileID=? AND password=?"
        params = [username, password]
        _query.append((query, params))
        user = db.sql_query(_bp, query, params, one=True)
        
        if user:
            session[f"{_bp}_user_id"] = user["uid"]
            session[f"{_bp}_data"] = dict(user)

            return redirect(url_for(f"{_bp}.home"))
        else:
            flash("The account information you provided does not exist!", "danger")
    return render_template(f"{_bp}/login.html", slide_num=0)


@sesqli6.route("/profile", methods=["GET", "POST"])
@login_required(_bp)
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


@sesqli6.route("/home")
@login_required(_bp)
def home():
    return render_template(f"{_templ}/index.html", csess_obj=get_profile())


@sesqli6.route("/logout")
def logout():
    clear_session(_bp)
    return redirect(url_for(f"{_bp}.login"))

