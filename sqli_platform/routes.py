import json
from flask import (
    render_template, Blueprint, abort, request
)
from jinja2 import TemplateNotFound
from sqli_platform import *

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
            print(f"{conf}: {value}")
        return {"Status": "Success"}
