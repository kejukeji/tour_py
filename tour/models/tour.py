# coding: utf-8

from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey

from .database import Base

TOUR_TABLE = 'tour'
TOUR_PICTURE_TABLE = 'tour_picture'
PICTURE_THUMBNAIL_TABLE = 'picture_thumbnail'


class Tour(Base):
    """
    id 折扣ID
    title 折扣名字
    intro 折扣介绍
    detail 折扣详情
    price 折扣价格
    order_max 最大订购人数
    ordered 已订购人数
    rank 排序
    stopped 订购是否结束 0 没有 1 结束
    """

    __tablename__ = TOUR_TABLE

    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8'
    }

    id = Column(Integer, primary_key=True)
    title = Column(String(32), nullable=False)
    intro = Column(String(128), nullable=False)
    detail = Column(String(256), nullable=False)
    price = Column(Float, nullable=False)
    order_max = Column(Integer, nullable=False, server_default='0')
    ordered = Column(Integer, nullable=False, server_default='0')
    rank = Column(Integer, nullable=False, server_default='0')
    stopped = Column(Boolean, nullable=False, server_default='0')

    def __init__(self, **kwargs):
        self.title = kwargs.pop('title')
        self.intro = kwargs.pop('intro')
        self.detail = kwargs.pop('detail')
        self.price = kwargs.pop('price')
        self.order_max = kwargs.pop('order_max', 0)
        self.ordered = kwargs.pop('ordered', 0)
        self.rank = kwargs.pop('rank', 0)
        self.stopped = kwargs.pop('stopped', 0)

    def update(self, **kwargs):
        self.title = kwargs.pop('title')
        self.intro = kwargs.pop('intro')
        self.detail = kwargs.pop('detail')
        self.price = kwargs.pop('price')
        self.order_max = kwargs.pop('order_max', 0)
        self.ordered = kwargs.pop('ordered', 0)
        self.rank = kwargs.pop('rank', 0)
        self.stopped = kwargs.pop('stopped', 0)

    def __repr__(self):
        return '<Tour(title: %s)>' % self.title


class TourPicture(Base):
    """
    id
    tour_id 折扣ID
    base_path 基础路径，系统路径
    rel_path 相对路径，服务器路径
    pic_name 保存到系统的名字
    upload_name 上传时候的名字
    cover 是否为图片封面
    """

    __tablename__ = TOUR_PICTURE_TABLE

    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8'
    }

    id = Column(Integer, primary_key=True)
    tour_id = Column(Integer, ForeignKey(Tour.id, ondelete='cascade', onupdate='cascade'), nullable=False)
    base_path = Column(String(128), nullable=False)
    rel_path = Column(String(128), nullable=False)
    pic_name = Column(String(128), nullable=False)
    upload_name = Column(String(128), nullable=False)
    cover = Column(Boolean, nullable=False, server_default='0')

    def __init__(self, tour_id, base_path, rel_path, pic_name, upload_name, cover=0):
        self.tour_id = tour_id
        self.base_path = base_path
        self.rel_path = rel_path
        self.pic_name = pic_name
        self.upload_name = upload_name
        self.cover = cover

    def __repr__(self):
        return '<TourPicture(tour_id: %s, upload_name: %s)>' % (self.tour_id, self.upload_name)


class TourPictureThumbnail(Base):
    """
    id
    picture_id 图片ID
    picture286_170
    picture640_288
    picture300_180
    picture176_160
    """

    __tablename__ = PICTURE_THUMBNAIL_TABLE

    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8'
    }

    id = Column(Integer, primary_key=True)
    picture_id = Column(Integer, ForeignKey(TourPicture.id, ondelete='cascade', onupdate='cascade'), nullable=False)
    picture286_170 = Column(String(128), nullable=False)
    picture640_288 = Column(String(128), nullable=False)
    picture300_180 = Column(String(128), nullable=False)
    picture176_160 = Column(String(128), nullable=False)

    def __init__(self, picture_id, picture286, picture640, picture300, picture176):
        self.picture_id = picture_id
        self.picture176_160 = picture176
        self.picture286_170 = picture286
        self.picture300_180 = picture300
        self.picture640_288 = picture640

    def __repr__(self):
        return '<TourPicture(tour_id: %s)>' % self.picture_id