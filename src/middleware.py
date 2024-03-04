from functools import wraps
from flask import Response, request, g

from .utils import get_cookie, extract_cookie_data

def login_mw(func):
    @wraps(func)
    def login_mw_dector(*args, **kwargs):
        cookie = get_cookie(request)

        if cookie == None:
            return Response("Authorization failed", status=401)

        g.cookie_data = extract_cookie_data(cookie)
        g.data = {'is_login': True, 'user_type': g.cookie_data['user_type'], "id": g.cookie_data["id"]}
        
        return func(*args, **kwargs)
    return login_mw_dector


def patient_only(func):
    @wraps(func)
    def patient_only_dector(*args, **kwargs):

        if g.cookie_data["user_type"] != "patient":
            return Response("Authorization error, only patient are alowed here", status=401)
        
        return func(*args, **kwargs)
    return patient_only_dector


def doctor_only(func):
    @wraps(func)
    def doctor_only_dector(*args, **kwargs):

        if g.cookie_data["user_type"] != "doctor":
            return Response("Authorization error, only doctor are alowed here", status=401)
        
        return func(*args, **kwargs)
    return doctor_only_dector
