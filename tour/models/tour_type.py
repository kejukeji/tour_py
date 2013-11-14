# coding: utf-8

from sqlalchemy import Column, Integer, String

from .database import Base

TOUR_TYPE_TABLE = 'tour_type'

class TourType(Base):
    """
    id id
    name 类型名字
    code 编号 01 02 03 04 05
    """

    __tablename__ = TOUR_TYPE_TABLE

    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8'
    }

    id = Column(Integer, primary_key=True)
    name = Column(String(16), nullable=False)
    code = Column(String(4), nullable=False)

    def __init__(self, **kwargs):
        self.name = kwargs.pop('name')
        self.code = kwargs.pop('code')

    def update(self, **kwargs):
        self.name = kwargs.pop('name')
        self.code = kwargs.pop('code')

    def __repr__(self):
        return '<Tour(name: %s)>' % self.name