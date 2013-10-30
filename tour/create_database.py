# coding: utf-8
# 添加git的测试代码

from tour.models import Base, engine

if __name__ == '__main__':
    Base.metadata.create_all(engine)
