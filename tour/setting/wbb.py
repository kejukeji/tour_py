# coding: utf-8

# flask模块需要的配置参数
# ===============================================================
DEBUG = True  # 是否启动调试功能
SECRET_KEY = '^&^hA0Zr98j/3yX!jmN]LWX/,?RT^&578756gh/ghj~hj/kh'  # session相关的密匙

# models模块需要的配置参数
# ===============================================================
SQLALCHEMY_DATABASE_URI = 'mysql://root:root@127.0.0.1:3306/tour?charset=utf8'  # 连接的数据库
SQLALCHEMY_ECHO = True  # 是否显示SQL语句

# 折扣图片
TOUR_PICTURE_UPLOAD_FOLDER = '/static/system/tour_picture'  # 运行目录的相对目录，URL获取图片的路径
TOUR_PICTURE_BASE_PATH = 'D:/tour_py/tour'  # pub运行文件的目录，图片的绝对路径使用
TOUR_PICTURE_ALLOWED_EXTENSION = ('png', 'jpg', 'jpeg', 'gif')  # 允许的拓展名