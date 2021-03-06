# coding: utf-8

from wtforms import BooleanField
import jsonpickle

pickler = jsonpickle.pickler.Pickler(unpicklable=False, max_depth=2)


def form_to_dict(form):
    form_dict = {}

    for key in form._fields:  # todo-lyw可以编写一个更好的函数，可惜我不会。。。
        if isinstance(form._fields[key].data, BooleanField) or isinstance(form._fields[key].data, int):
            form_dict[key] = form._fields[key].data
            continue

        if form._fields[key].data:
            form_dict[key] = form._fields[key].data

    return form_dict