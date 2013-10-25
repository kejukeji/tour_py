# coding: utf-8

数据库配置文件：
..ex_var.py

创建数据库的方法：
打开python，运行 sys.path.extend(['/Users/X/Dropbox/Code/tour'])  # 或者使用pycharm的python console

>>> from tour.models import Base, engine
>>> Base.metadata.create_all(engine)