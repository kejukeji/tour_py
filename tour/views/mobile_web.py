# coding: utf-8

from flask import render_template


def index():
    return render_template('mobile_web/index.html')


def detail():
    return render_template('mobile_web/detail.html')