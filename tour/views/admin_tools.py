# coding: utf-8
from flask.ext import login


def administrator():
    if login.current_user.is_admin() and login.current_user.admin == 1:
        return True

    return False