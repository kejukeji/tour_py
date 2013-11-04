# coding: utf-8

import os

from tour import app
from flask.ext.admin import Admin
from views import TourView, TourPictureFile
from views import index, detail
from views.admin_user import UserView
from models import db
from views.admin_login import login_view, register_view, logout_view
from views.admin_home import HomeView

# 后台管理路径
admin = Admin(name=u'旅游折扣会', index_view=HomeView())
admin.init_app(app)
admin.add_view(TourView(db, name=u'折扣管理', category=u'折扣'))
admin.add_view(UserView(db, name=u'用户管理'))
# 用户登陆
app.add_url_rule('/login', 'login_view', login_view, methods=('GET', 'POST'))
app.add_url_rule('/register', 'register_view', register_view, methods=('GET', 'POST'))
app.add_url_rule('/logout', 'logout_view', logout_view, methods=('GET', 'POST'))
# 折扣图片管理
picture_path = os.path.join(os.path.dirname(__file__), 'static/system/tour_picture')
admin.add_view(TourPictureFile(picture_path, '/static/system/tour_picture/', name=u'折扣图片', category=u'折扣'))

# 手机页面
app.add_url_rule('/', 'index', index)
app.add_url_rule('/<int:page>', 'index', index)  # todo-lyw 如何更好的传递参数
app.add_url_rule('/detail/<int:tour_id>', 'detail', detail)