# coding: utf-8

from tour.models import Base, engine

if __name__ == '__main__':
    Base.metadata.create_all(engine)
