# coding: utf-8

from sqlalchemy import Column, Integer, String, DATETIME, ForeignKey
from sqlalchemy.orm import relationship

from .database import Base
from .tour import Tour
from ..utils.ex_time import todayfstr
from ..utils.ex_password import generate_password, check_password


class Order(Base):
    """客户预订对应的类
    id
    tour_id
    customer 客户名
    mobile 联系号码
    email 邮件
    time 预订时间
    status 订单状态
    """

    __tablename__ = 'order'
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8'
    }

    id = Column(Integer, primary_key=True)
    tour_id = Column(Integer, ForeignKey(Tour.id, ondelete='set null', onupdate='cascade'))
    tour = relationship(Tour)
    customer = Column(String(16), nullable=True, server_default=None)
    mobile = Column(String(16), nullable=False)
    email = Column(String(32), nullable=True)
    time = Column(DATETIME, nullable=True)
    status = Column(Integer, nullable=False, server_default='0')

    def __init__(self, **kwargs):
        self.tour_id = kwargs.get('tour_id')
        self.customer = kwargs.get('customer', None)
        self.mobile = kwargs.get('mobile')
        self.email = kwargs.get('email')
        self.time = todayfstr()
        self.status = kwargs.get('status', 0)

    def update(self, **kwargs):
        self.tour_id = kwargs.get('tour_id')
        self.customer = kwargs.get('customer', None)
        self.mobile = kwargs.get('mobile')
        self.email = kwargs.get('email')
        self.time = todayfstr()
        self.status = kwargs.get('status', 0)

    def __repr__(self):
        return '<Order(name: %s)>' % self.customer
