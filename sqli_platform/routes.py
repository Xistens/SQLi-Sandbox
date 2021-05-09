import json
import sqli_platform.utils as utils
from flask import (
    render_template,
    redirect,
    url_for,
    Blueprint, 
    abort, 
    request, 
    session,
    send_from_directory
)
from jinja2 import TemplateNotFound
from werkzeug.utils import secure_filename
from sqli_platform import *
from sqli_platform.utils.challenge import get_config, download_enabled

@app.context_processor
def context():
    """
    Inject variables automatically into the context of the templates.
    https://flask.palletsprojects.com/en/1.1.x/templating/#context-processors
    """
    bp = request.blueprint
    return dict(
        cname=bp,
        csession=session.get(f"{bp}_user_id", None),
        csession_name=session.get(f"{bp}_username", None),
        ctitle=get_config(bp, "title"),
        slides=f"{bp}/slides/slides.html",
        cdesc=get_config(bp, "description"),
        cconf=get_config(bp)
    )

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

@app.route('/')
def index():
    # Get track information from database
    tracks = db.get_tracks()

    # Build menu object...
    # Should probably refactor this
    obj = {}
    for t in tracks:
        name = t["track_name"]
        if not name in obj:
            obj[name] = []
        data = {
            "name": t["name"],
            "title": t["title"],
            "tags": t["tags"],
            "difficulty": t["difficulty"],
            "description": t["description"],
            "position": t["track_position"]
        }
        obj[name].append(data)
    
    # Sort challenges
    for i in obj:
        tmp = obj[i]
        newlist = sorted(tmp, key=lambda k: k["position"])
        obj[i] = newlist
            
    return render_template("index.html", tracks=obj, isIndex=True)


@app.route('/settings', methods=["POST"])
def settings():
    """
    This view receives the JSON data from the settings via the ajax call
    on the main page/landing page and will update the settings for
    the current session.
    """
    if request.method == "POST":
        data = json.loads(request.data)
        whitelist = ["query", "guidance"]
        
        conf = data.get("id", None)
        value = data.get("value", False)
        if conf in whitelist:
            status = True if value else False
            session[f"mainapp_{conf}"] = status
        return {"Status": "Success"}


@app.route("/download/<path:filename>", defaults={"dir": ""})
@app.route("/download/<dir>/<path:filename>")
@download_enabled
def download(dir, filename):
    directory = f"{DOWNLOAD_PATH}"
    if dir and dir in DOWNLOAD_WHITELIST:
        directory = f"{DOWNLOAD_PATH}/{dir}"
    return send_from_directory(directory=directory, filename=filename, cache_timeout=-1)



@app.route("/view/<path:filename>", defaults={"dir": ""})
@app.route("/view/<dir>/<path:filename>")
@download_enabled
def view(dir, filename):
    if not filename == "__init__.py":
        filename = secure_filename(filename)
        
    dir_path = ""
    content = ""
    if dir:
        if dir in DOWNLOAD_WHITELIST:
            dir_path = f"{DOWNLOAD_PATH}{dir}/{filename}"
        else:
            content = "File does not exists."
    else:
        dir_path = f"{DOWNLOAD_PATH}{filename}"

    try:
        with open(dir_path, "r") as fd:
            content = fd.read()
    except IOError:
        content = "File does not exist."
    return render_template("view.html", dir=dir, text=content, name=filename)

@app.route("/downloads/", defaults={"dir": None})
@app.route("/downloads/<path:dir>")
@download_enabled
def downloads(dir):
    dir_path = DOWNLOAD_PATH
    if dir:
        if dir in DOWNLOAD_WHITELIST:
            dir_path = f"{DOWNLOAD_PATH}{dir}"
        else:
            return redirect(url_for("downloads"))
    else:
        dir = ""
    return render_template("downloads.html", dir=dir, files=utils.get_files(dir_path))
