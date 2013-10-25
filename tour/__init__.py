# coding: utf-8

# 设置python运行环境的编码
import sys
reload(sys)
sys.setdefaultencoding('utf8')

from flask import Flask
from .ex_var import CONFIG_FILE

app = Flask(__name__)
app.config.from_pyfile(CONFIG_FILE)

import urls