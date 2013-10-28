# coding: utf-8

import logging
import os
import Image

from wtforms.fields import TextField
from flask.ext.admin.contrib.sqla import ModelView
from flask.ext.admin.babel import gettext
from werkzeug import secure_filename
from flask import request, flash
from ..models import Tour, TourPicture, TourPictureThumbnail, db
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
        rank=u'排序，值越大，可以约靠前，最前面四个作为广告放在最前面',
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
            pic_to_save = TourPicture(tour_id, base_path, rel_path, pic_name, upload_name, cover=0)
            db.add(pic_to_save)
            picture.save(os.path.join(base_path+rel_path+'/', pic_name))
            db.commit()
            save_thumbnail(pic_to_save.id)


def delete_tour_picture(tour_id):
    pictures = TourPicture.query.filter(TourPicture.tour_id == tour_id).all()
    for picture in pictures:
        try:
            os.remove(os.path.join(picture.base_path+picture.rel_path+'/', picture.pic_name))
        except:
            pass


def save_thumbnail(picture_id):
    picture = TourPicture.query.filter(TourPicture.id == picture_id).first()
    base_path = picture.base_path + picture.rel_path + '/'
    picture286 = picture_resize(picture, (286, 170))
    picture286_name = time_file_name(str(picture_id)) + 'nail.jpeg'
    picture286.save(base_path + picture286_name, 'jpeg')
    picture640 = picture_resize(picture, (640, 288))
    picture640_name = time_file_name(str(picture_id)) + 'nail.jpeg'
    picture640.save(base_path + picture640_name, 'jpeg')
    picture300 = picture_resize(picture, (300, 180))
    picture300_name = time_file_name(str(picture_id)) + 'nail.jpeg'
    picture300.save(base_path + picture300_name, 'jpeg')
    picture176 = picture_resize(picture, (176, 160))
    picture176_name = time_file_name(str(picture_id)) + 'nail.jpeg'
    picture176.save(base_path + picture176_name, 'jpeg')
    db.add(TourPictureThumbnail(picture_id, picture286_name, picture640_name, picture300_name, picture176_name))
    db.commit()


def picture_resize(picture, resize):
    picture_path = picture.base_path + picture.rel_path + '/' + picture.pic_name
    im = Image.open(picture_path)
    # crop到一定的比例大小，只是裁剪
    normal_size = im.size
    if normal_size[0] <= normal_size[1] * resize[0] / resize[1]:
        start_pos = (normal_size[1] - normal_size[0] * resize[1] / resize[0]) / 2
        image = im.crop((0, start_pos, normal_size[0], normal_size[0] * resize[1] / resize[0]))
    else:
        start_pos = (normal_size[0] - normal_size[1] * resize[0] / resize[1]) / 2
        image = im.crop((start_pos, 0, normal_size[1] * resize[0] / resize[1], normal_size[1]))

    # resize到更小的比例，只是缩小
    resize_image = image.resize(resize)

    return resize_image