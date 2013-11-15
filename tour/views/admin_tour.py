# coding: utf-8

"""旅游折扣管理界面"""

import logging
import os

from wtforms.fields import TextField, TextAreaField, HiddenField
from flask.ext.admin.base import expose
from flask.ext.admin.contrib.sqla import ModelView
from flask.ext.admin.babel import gettext
from werkzeug import secure_filename
from flask import request, flash
from flask.ext import login
from ..models import Tour, TourPicture, TourPictureThumbnail, db
from ..utils import form_to_dict, allowed_file_extension, time_file_name
from ..ex_var import TOUR_PICTURE_BASE_PATH, TOUR_PICTURE_UPLOAD_FOLDER, TOUR_PICTURE_ALLOWED_EXTENSION
from .picture_tools import create_base_picture, save_thumbnails
from sqlalchemy import or_
from flask.ext.admin.contrib.sqla import tools
from sqlalchemy.orm import joinedload

log = logging.getLogger("flask-admin.sqla")


class TourView(ModelView):
    """折扣类型的类"""

    page_size = 30
    can_create = True
    can_delete = False
    can_edit = True
    column_display_pk = True
    column_searchable_list = ('title', 'intro', 'detail')
    column_default_sort = ('id', False)
    column_labels = dict(
        id=u'ID',
        title=u'标题',
        intro=u'简介',
        detail=u'详情',
        price=u'市场价',
        discount=u'折扣价',
        order_max=u'最大订购人数',
        ordered=u'已订购人数',
        rank=u'排序',
        stopped=u'是否停止本订购',
        tel=u'联系电话',
        tour_type_id=u'所属分类'
    )
    column_descriptions = dict(
        order_max=u'最大订购人数，如果没有限制，默认为0',
        ordered=u'已订购人数，首先默认为0，打电话之后手动添加',
        rank=u'排序，值越大，可以约靠前，最前面四个作为广告放在最前面，默认为0',
        stopped=u'如果这个订购取消，可以勾选'
    )
    column_list = ('title', 'price', 'order_max', 'ordered', 'stopped', 'rank', 'tel', 'discount', 'tour_type_id')
    edit_template = 'admin_tour/edit.html'
    create_template = 'admin_tour/create.html'
    list_template = 'admin_tour/list.html'

    form_overrides = dict(
        intro=TextAreaField,
        detail=TextAreaField,
        user_id=HiddenField
    )

    def __init__(self, db_session, **kwargs):
        super(TourView, self).__init__(Tour, db_session, **kwargs)

    def is_accessible(self):
        return login.current_user.is_admin()

    def scaffold_form(self):
        form_class = super(TourView, self).scaffold_form()
        form_class.picture = TextField(label=u'折扣图片', description=u'折扣图片，按control键可以选择多张图片')
        return form_class

    def create_model(self, form):
        """改写flask的新建model的函数"""

        try:
            form_dict = form_to_dict(form)
            form_dict['user_id'] = login.current_user.id
            model = self.model(**form_dict)
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
            if administrator() or login.current_user.id == model.user_id:
                model.update(**form_to_dict(form))
                self.session.commit()
            else:
                flash('权限不够呢，所以无法修改', 'info')
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
            if administrator() or login.current_user.id == model.user_id:
                picture_list = get_picture_list(model.id)
                self.on_model_delete(model)
                self.session.flush()
                self.session.delete(model)
                self.session.commit()  # 级联删除数据库记录
                delete_pictures(picture_list)  # 删除所有的本地文件
                return True
            else:
                flash('权限不够呢，所以无法删除', 'info')

        except Exception as ex:
            if self._debug:
                raise

            flash(gettext('Failed to delete model. %(error)s', error=str(ex)), 'error')
            log.exception('Failed to delete model')
            self.session.rollback()
            return False

    def get_list(self, page, sort_column, sort_desc, search, filters, execute=True, user_id=None):
        """
            Return models from the database.

            :param page:
                Page number
            :param sort_column:
                Sort column name
            :param sort_desc:
                Descending or ascending sort
            :param search:
                Search query
            :param execute:
                Execute query immediately? Default is `True`
            :param filters:
                List of filter tuples
        """

        # Will contain names of joined tables to avoid duplicate joins
        joins = set()

        query = self.get_query()
        count_query = self.get_count_query()

        if user_id:
            query = query.filter(Tour.user_id == user_id)

        # Apply search criteria
        if self._search_supported and search:
            # Apply search-related joins
            if self._search_joins:
                for jn in self._search_joins.values():
                    query = query.join(jn)
                    count_query = count_query.join(jn)

                joins = set(self._search_joins.keys())

            # Apply terms
            terms = search.split(' ')

            for term in terms:
                if not term:
                    continue

                stmt = tools.parse_like_term(term)
                filter_stmt = [c.ilike(stmt) for c in self._search_fields]
                query = query.filter(or_(*filter_stmt))
                count_query = count_query.filter(or_(*filter_stmt))

        # Apply filters
        if filters and self._filters:
            for idx, value in filters:
                flt = self._filters[idx]

                # Figure out joins
                tbl = flt.column.table.name

                join_tables = self._filter_joins.get(tbl, [])

                for table in join_tables:
                    if table.name not in joins:
                        query = query.join(table)
                        count_query = count_query.join(table)
                        joins.add(table.name)

                # Apply filter
                query = flt.apply(query, value)
                count_query = flt.apply(count_query, value)

        # Calculate number of rows
        count = count_query.scalar()

        # Auto join
        for j in self._auto_joins:
            query = query.options(joinedload(j))

        # Sorting
        if sort_column is not None:
            if sort_column in self._sortable_columns:
                sort_field = self._sortable_columns[sort_column]

                query, joins = self._order_by(query, joins, sort_field, sort_desc)
        else:
            order = self._get_default_order()

            if order:
                query, joins = self._order_by(query, joins, order[0], order[1])

        # Pagination
        if page is not None:
            query = query.offset(page * self.page_size)

        query = query.limit(self.page_size)

        # Execute if needed
        if execute:
            query = query.all()

        return count, query

    # Views
    @expose('/')
    def index_view(self):
        """
            List view
        """
        if administrator():
            self.can_delete = True
        else:
            self.can_delete = False

        # Grab parameters from URL
        page, sort_idx, sort_desc, search, filters = self._get_extra_args()

        # Map column index to column name
        sort_column = self._get_column_by_idx(sort_idx)
        if sort_column is not None:
            sort_column = sort_column[0]

        # Get count and data
        if administrator():
            user_id = None
        else:
            user_id = login.current_user.id
        count, data = self.get_list(page, sort_column, sort_desc,
                                    search, filters, user_id=user_id)

        # Calculate number of pages
        num_pages = count // self.page_size
        if count % self.page_size != 0:
            num_pages += 1

        # Pregenerate filters
        if self._filters:
            filters_data = dict()

            for idx, f in enumerate(self._filters):
                flt_data = f.get_options(self)

                if flt_data:
                    filters_data[idx] = flt_data
        else:
            filters_data = None

        # Various URL generation helpers
        def pager_url(p):
            # Do not add page number if it is first page
            if p == 0:
                p = None

            return self._get_url('.index_view', p, sort_idx, sort_desc,
                                 search, filters)

        def sort_url(column, invert=False):
            desc = None

            if invert and not sort_desc:
                desc = 1

            return self._get_url('.index_view', page, column, desc,
                                 search, filters)

        # Actions
        actions, actions_confirmation = self.get_actions_list()

        return self.render(self.list_template,
                               data=data,
                               # List
                               list_columns=self._list_columns,
                               sortable_columns=self._sortable_columns,
                               # Stuff
                               enumerate=enumerate,
                               get_pk_value=self.get_pk_value,
                               get_value=self.get_list_value,
                               return_url=self._get_url('.index_view',
                                                        page,
                                                        sort_idx,
                                                        sort_desc,
                                                        search,
                                                        filters),
                               # Pagination
                               count=count,
                               pager_url=pager_url,
                               num_pages=num_pages,
                               page=page,
                               # Sorting
                               sort_column=sort_idx,
                               sort_desc=sort_desc,
                               sort_url=sort_url,
                               # Search
                               search_supported=self._search_supported,
                               clear_search_url=self._get_url('.index_view',
                                                              None,
                                                              sort_idx,
                                                              sort_desc),
                               search=search,
                               # Filters
                               filters=self._filters,
                               filter_groups=self._filter_groups,
                               filter_types=self._filter_types,
                               filter_data=filters_data,
                               active_filters=filters,

                               # Actions
                               actions=actions,
                               actions_confirmation=actions_confirmation)


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
            picture.save(os.path.join(base_path+rel_path+'/', pic_name))
            db.add(pic_to_save)
            db.commit()
            save_thumbnails(pic_to_save.id)


def get_picture_list(tour_id):
    """通过tour的id，返回所有需要删除的文件列表"""
    picture_list = []
    pictures = TourPicture.query.filter(TourPicture.tour_id == tour_id).all()
    for picture in pictures:
        thumbnail_picture = TourPictureThumbnail.query.filter(TourPictureThumbnail.picture_id == picture.id).first()
        picture_list.append(create_base_picture(picture, thumbnail_picture))

    return picture_list


def delete_pictures(picture_list):
    for picture in picture_list:
            os.remove(picture.normal)
            os.remove(picture.picture640_288)
            os.remove(picture.picture176_160)
            os.remove(picture.picture286_170)
            os.remove(picture.picture300_180)

def administrator():
    if login.current_user.is_admin() and login.current_user.admin == 1:
        return True

    return False