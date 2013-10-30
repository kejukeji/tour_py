# coding: utf-8

import os
import os.path as op
import platform
import shutil
from operator import itemgetter

from werkzeug import secure_filename
from flask.ext.admin.babel import gettext
from flask import flash, url_for, redirect, request
from flask.ext.admin import helpers
from flask.ext.admin._compat import as_unicode
from flask.ext.admin.base import expose
from flask.ext.admin.contrib.fileadmin import FileAdmin
from flask.ext.admin.contrib.fileadmin import UploadForm

from ..models import TourPicture, db, TourPictureThumbnail
from ..utils import allowed_file_extension, time_file_name
from ..ex_var import TOUR_PICTURE_BASE_PATH, TOUR_PICTURE_UPLOAD_FOLDER, TOUR_PICTURE_ALLOWED_EXTENSION
from .view_tool import picture_resize, save_thumbnail


class TourPictureFile(FileAdmin):  # todo-lyw代码进一步完善中
    """酒吧图片的后台管理"""
    can_upload = True
    can_delete = True
    can_delete_dirs = False
    can_mkdir = False
    can_rename = False

    allowed_extensions = ('jpg', 'gif', 'png', 'jpeg')

    list_template = 'admin_tour/tour_picture_list.html'

    def __init__(self, base_path, base_url,
                 name=None, category=None, endpoint=None, url=None,
                 verify_path=True):
        self.base_path = as_unicode(base_path)
        self.base_url = base_url

        self.init_actions()

        self._on_windows = platform.system() == 'Windows'

        # Convert allowed_extensions to set for quick validation
        if (self.allowed_extensions and 
                not isinstance(self.allowed_extensions, set)):
            self.allowed_extensions = set(self.allowed_extensions)

        # Convert editable_extensions to set for quick validation
        if (self.editable_extensions and
                not isinstance(self.editable_extensions, set)):
            self.editable_extensions = set(self.editable_extensions)

        # Check if path exists
        if not op.exists(base_path):
            raise IOError('FileAdmin path "%s" does not exist or is not accessible' % base_path)

        super(FileAdmin, self).__init__(name, category, endpoint, url)

    def save_file(self, path, file_data):
        """保存图片"""
        file_data.save(path)

    def on_file_upload(self, directory, path, filename):
        """定义图片上传之后的行为"""
        pass

    def on_file_delete(self, full_path, filename):
        """定义图片删除之后的行为"""

        # 在数据库移除记录
        picture = TourPicture.query.filter(TourPicture.pic_name == filename).first()
        thumbnail_picture = TourPictureThumbnail.query.filter(TourPictureThumbnail.picture_id == picture.id).first()
        TourPicture.query.filter(TourPicture.pic_name == filename).delete()
        TourPictureThumbnail.query.filter(TourPictureThumbnail.picture_id == picture.id).delete()
        db.commit()

        # 移除本地略缩图文件
        delete_a_tour_picture(picture, thumbnail_picture)


    @expose('/')
    @expose('/b/<path:path>')
    def index(self, path=None):
        """
            Index view method

            :param path:
                Optional directory path. If not provided, will use the base directory
        """
        # Get path and verify if it is valid
        base_path, directory, path = self._normalize_path(path)

        if not self.is_accessible_path(path):
            flash(gettext(gettext('Permission denied.')))
            return redirect(self._get_dir_url('.index'))

        # Get directory listing
        items = []

        tour_id = request.args.get("tour_id", None)
        if tour_id:
            for picture in TourPicture.query.filter(TourPicture.tour_id == tour_id).all():
                items.append(get_picture(path, directory, picture))

        # Sort by name
        items.sort(key=itemgetter(0))

        # Sort by type
        items.sort(key=itemgetter(2), reverse=True)

        # Generate breadcrumbs
        accumulator = []
        breadcrumbs = []
        for n in path.split(os.sep):
            accumulator.append(n)
            breadcrumbs.append((n, op.join(*accumulator)))

        # Actions
        actions, actions_confirmation = self.get_actions_list()

        return self.render(self.list_template,
                           dir_path=path,
                           breadcrumbs=breadcrumbs,
                           get_dir_url=self._get_dir_url,
                           get_file_url=self._get_file_url,
                           items=items,
                           actions=actions,
                           actions_confirmation=actions_confirmation)

    @expose('/upload/', methods=('GET', 'POST'))
    @expose('/upload/<path:path>', methods=('GET', 'POST'))
    def upload(self, path=None):
        """
            Upload view method

            :param path:
                Optional directory path. If not provided, will use the base directory
        """
        # Get path and verify if it is valid
        base_path, directory, path = self._normalize_path(path)

        if not self.can_upload:
            flash(gettext('File uploading is disabled.'), 'error')
            return redirect(self._get_dir_url('.index', path))

        if not self.is_accessible_path(path):
            flash(gettext(gettext('Permission denied.')))
            return redirect(self._get_dir_url('.index'))

        form = UploadForm(self)
        if helpers.validate_form_on_submit(form):
            tour_id = request.args.get('tour_id')
            if not tour_id:
                flash(gettext('这里无法上传图片，修改折扣即可看到图片管理按钮。'), 'error')
                return redirect("/admin/tourpicturefile")  # todo-lyw ugly
            upload_name = secure_filename(form.upload.data.filename)
            pic_name = time_file_name(upload_name, sign=tour_id)
            save_path_name = op.join(directory, pic_name)

            if not allowed_file_extension(upload_name, TOUR_PICTURE_ALLOWED_EXTENSION):
                flash(gettext('File "%(name)s" must be a picture!', name=pic_name),
                      'error')
            else:
                try:
                    self.save_file(save_path_name, form.upload.data)
                    new_picture = TourPicture(tour_id, TOUR_PICTURE_BASE_PATH, TOUR_PICTURE_UPLOAD_FOLDER, pic_name,
                                              upload_name, cover=0)
                    db.add(new_picture)
                    db.commit()
                    save_thumbnail(new_picture.id)
                    self.on_file_upload(directory, path, pic_name)
                    return redirect('/admin/tourpicturefile/?tour_id=' + str(request.args.get('tour_id')))  # todo-lyw ugly
                except Exception as ex:
                    flash(gettext('Failed to save file: %(error)s', error=ex))

        return self.render(self.upload_template, form=form)

    @expose('/delete/', methods=('POST',))  # todo-lyw 这个是删除一张图片的，集体删除的图片函数需要添加
    def delete(self):
        """
            Delete view method
        """
        path = request.form.get('path')

        if not path:
            return redirect(url_for('.index'))

        # Get path and verify if it is valid
        base_path, full_path, path = self._normalize_path(path)
        tour_id = TourPicture.query.filter(TourPicture.pic_name == path).first().tour_id

        return_url = self._get_dir_url('.index', op.dirname(path)) + "?tour_id=" + str(tour_id)  # todo-lyw ugly

        if not self.can_delete:
            flash(gettext('Deletion is disabled.'))
            return redirect(return_url)

        if not self.is_accessible_path(path):
            flash(gettext(gettext('Permission denied.')))
            return redirect(self._get_dir_url('.index'))

        if op.isdir(full_path):
            if not self.can_delete_dirs:
                flash(gettext('Directory deletion is disabled.'))
                return redirect(return_url)

            try:
                shutil.rmtree(full_path)
                self.on_directory_delete(full_path, path)
                flash(gettext('Directory "%s" was successfully deleted.' % path))
            except Exception as ex:
                flash(gettext('Failed to delete directory: %(error)s', error=ex), 'error')
        else:
            try:
                os.remove(full_path)
                self.on_file_delete(full_path, path)
                flash(gettext('File "%(name)s" was successfully deleted.', name=path))
            except Exception as ex:
                flash(gettext('Failed to delete file: %(name)s', name=ex), 'error')

        return redirect(return_url)


def get_picture(path, directory, picture):
    """获取一个图片相关的tuple用于添加需要显示的图片"""
    fp = op.join(directory, picture.pic_name)
    rel_path = op.join(path, picture.pic_name)

    return picture.pic_name, rel_path, op.isdir(fp), op.getsize(fp)


def delete_a_tour_picture(picture, picture_thumbnail):
    """移除本地的略缩图文件"""
    try:
        base_path = picture.base_path+picture.rel_path+'/'
        os.remove(os.path.join(base_path, picture_thumbnail.picture286_170))
        os.remove(os.path.join(base_path, picture_thumbnail.picture640_288))
        os.remove(os.path.join(base_path, picture_thumbnail.picture300_180))
        os.remove(os.path.join(base_path, picture_thumbnail.picture176_160))
    except:
        pass