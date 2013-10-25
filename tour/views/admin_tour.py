# coding: utf-8

import logging
import os

from wtforms.fields import TextField
from flask.ext.admin.contrib.sqla import ModelView
from flask.ext.admin.babel import gettext
from werkzeug import secure_filename
from flask import request, flash
from ..models import Tour, TourPicture, db
from ..utils import form_to_dict, allowed_file_extension, time_file_name
from ..ex_var import TOUR_PICTURE_BASE_PATH, TOUR_PICTURE_UPLOAD_FOLDER, TOUR_PICTURE_ALLOWED_EXTENSION

log = logging.getLogger("flask-admin.sqla")


class TourView(ModelView):
    """折扣类型的类"""

    page_size = 30
    can_create = True
    can_delete = True
    can_edit = True
    column_display_pk = True
    column_searchable_list = ('title', 'intro', 'detail')
    column_default_sort = ('id', False)
    column_labels = dict(
        id=u'ID',
        title=u'标题',
        intro=u'简介',
        detail=u'详情',
        price=u'价格',
        order_max=u'最大订购人数',
        ordered=u'已订购人数',
        rank=u'排序',
        stopped=u'是否停止本订购'
    )
    column_descriptions = dict(
        order_max=u'最大订购人数，如果没有限制，可以不写',
        ordered=u'已订购人数，系统自动添加',
        rank=u'排序，值越大，可以约靠前',
        stopped=u'如果这个订购取消，可以勾选'
    )
    column_list = ('title', 'price', 'order_max', 'ordered', 'stopped', 'rank')
    edit_template = 'admin_tour/edit.html'
    create_template = 'admin_tour/create.html'

    def __init__(self, db_session, **kwargs):
        super(TourView, self).__init__(Tour, db_session, **kwargs)

    def scaffold_form(self):
        form_class = super(TourView, self).scaffold_form()
        form_class.picture = TextField(label=u'折扣图片', description=u'折扣图片，按control键可以选择多张图片')
        return form_class

    def create_model(self, form):
        """改写flask的新建model的函数"""

        try:
            model = self.model(**form_to_dict(form))
            self.session.add(model)  # 保存折扣基本资料
            self.session.commit()
            tour_id = model.id  # 获取和保存折扣id
            tour_pictures = request.files.getlist("picture")  # 获取折扣图片
            save_tour_pictures(tour_id, tour_pictures)

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
            tour_id = model.id
            tour_pictures = request.files.getlist("picture")  # 获取酒吧图片
            save_tour_pictures(tour_id, tour_pictures)
        except Exception, ex:
            flash(gettext('Failed to update model. %(error)s', error=str(ex)), 'error')
            logging.exception('Failed to update model')
            self.session.rollback()
            return False
        else:
            self.after_model_change(form, model, False)

        return True

    def delete_model(self, model):
        """
            Delete model.

            :param model:
                Model to delete
        """
        try:
            self.on_model_delete(model)
            delete_tour_picture(model.id)
            self.session.flush()
            self.session.delete(model)
            self.session.commit()
            return True
        except Exception as ex:
            if self._debug:
                raise

            flash(gettext('Failed to delete model. %(error)s', error=str(ex)), 'error')
            log.exception('Failed to delete model')
            self.session.rollback()
            return False

    #def is_accessible(self):  # 登陆管理功能先关闭，后期添加
    #    return current_user.is_admin()


def save_tour_pictures(tour_id, pictures):
    """保存酒吧图片"""
    for picture in pictures:
        if not allowed_file_extension(picture.filename, TOUR_PICTURE_ALLOWED_EXTENSION):
            continue
        else:
            upload_name = picture.filename
            base_path = TOUR_PICTURE_BASE_PATH
            rel_path = TOUR_PICTURE_UPLOAD_FOLDER
            pic_name = time_file_name(secure_filename(upload_name), sign=tour_id)
            db.add(TourPicture(tour_id, base_path, rel_path, pic_name, upload_name, cover=0))
            picture.save(os.path.join(base_path+rel_path+'/', pic_name))
            db.commit()


def delete_tour_picture(tour_id):
    pictures = TourPicture.query.filter(TourPicture.tour_id == tour_id).all()
    for picture in pictures:
        try:
            os.remove(os.path.join(picture.base_path+picture.rel_path+'/', picture.pic_name))
        except:
            pass