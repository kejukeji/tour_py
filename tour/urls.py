# coding: utf-8

import os

from tour import app
from flask.ext.admin import Admin
from views import TourView, TourPictureFile
from models import db

# 后台管理路径
admin = Admin(name=u'折扣')
admin.init_app(app)
admin.add_view(TourView(db, name=u'折扣管理', category=u'折扣'))
# 折扣图片管理
picture_path = os.path.join(os.path.dirname(__file__), 'static/system/tour_picture')
admin.add_view(TourPictureFile(picture_path, '/static/system/tour_picture/', name=u'折扣图片', category=u'折扣'))
