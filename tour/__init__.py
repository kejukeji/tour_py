# coding: utf-8

# 设置python运行环境的编码
import sys
reload(sys)
sys.setdefaultencoding('utf8')

from flask import Flask
from .ex_var import CONFIG_FILE
from models import db

app = Flask(__name__)
app.config.from_pyfile(CONFIG_FILE)

# 自动关闭数据库连接
@app.teardown_appcontext
def close_db(exception=None):
    if exception is not None:
        print('++++' + str(exception) + '++++')
    db.remove()

import urls