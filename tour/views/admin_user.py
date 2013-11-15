# coding: utf-8

"""
    user相关的后台代码
"""

import logging

from flask.ext.admin.contrib.sqla import ModelView
from flask.ext.admin.babel import gettext
from flask.ext import login
from flask import flash
from wtforms.fields import SelectField

from ..utils import form_to_dict
from ..models import User


class UserView(ModelView):
    """定义了数据库user的视图"""

    page_size = 30
    can_delete = True
    can_create = False
    can_edit = True
    column_exclude_list = ('password', 'open_id')
    column_default_sort = ('sign_up_date', True)
    column_searchable_list = ('login_name', 'nick_name')
    column_display_pk = True
    column_labels = dict(id=u'ID', login_name=u'用户识别', password=u'密码', login_type=u'登陆类型', nick_name=u'昵称',
                         open_id=u'第三方登陆ID', sign_up_date=u'注册时间', admin=u'权限')
    column_descriptions = dict(
        admin=u'权限控制',
        login_type=u'这里默认为注册用户',
        login_name=u'用户邮箱或者手机号，识别用户',
        nick_name=u'用户昵称，用于登陆'
    )
    column_choices = dict(
        admin=[(0, u'普通用户'), (1, u'管理员'), (2, u'编辑员')],
        login_type=[(0, u'注册用户'), (1, u'微博用户'), (2, u'QQ用户')]
    )
    form_choices = dict(
        admin=[('0', u'普通用户'), ('1', u'管理员'), ('2', u'编辑员')],
        login_type=[('0', u'注册用户')]
    )

    def __init__(self, db, **kwargs):
        super(UserView, self).__init__(User, db, **kwargs)

    def scaffold_form(self):
        form_class = super(UserView, self).scaffold_form()
        return form_class

    def is_accessible(self):
        if login.current_user.is_admin() and login.current_user.admin == 1:
            return True

        return False

    def create_model(self, form):
        """改写flask的新建model的函数"""

        try:
            model = self.model(**form_to_dict(form))
            self.session.add(model)
            self.session.commit()
        except Exception, ex:
            flash(gettext('Failed to create model. %(error)s', error=str(ex)), 'error')
            logging.exception('Failed to create model')
            self.session.rollback()
            return False
        else:
            self.after_model_change(form, model, True)

        return True

    def update_model(self, form, model):
        """改写了update函数"""
        try:
            model.update(**form_to_dict(form))
            self.session.commit()
        except Exception, ex:
            flash(gettext('Failed to update model. %(error)s', error=str(ex)), 'error')
            logging.exception('Failed to update model')
            self.session.rollback()
            return False
        else:
            self.after_model_change(form, model, False)

        return True