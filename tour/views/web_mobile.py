# coding: utf-8

"""web相关的视图都在这里定义"""

from flask import render_template, url_for
from ..models import Tour, TourPicture, TourPictureThumbnail, db
from sqlalchemy import desc
from random import choice
from .picture_tools import create_rel_picture
import random


def catagory_index(type_id, title=u'淘旅游'):
    """添加参数分类"""
    def catagory():
        """定义一个通用的视图函数"""
        banners = wrap_picture(Tour.query.filter(Tour.stopped == 0).order_by(desc(Tour.rank)).limit(4).all())
        tours = wrap_picture(Tour.query.filter(Tour.stopped == 0).filter(
            Tour.tour_type_id == type_id).order_by(desc(Tour.rank)).all())

        return render_template('web_mobile/catagory.html',
                               banners=banners,
                               tours=tours,
                               title=title)

    return catagory

# 1 国内游 2 出境游 3 上海周边游 4 春秋正品
guonei = catagory_index(1, title=u'淘旅游 - 国内游')
chujing = catagory_index(2, title=u'淘旅游 - 出境游')
shanghai = catagory_index(3, title=u'淘旅游 - 周边游')
zhengpin = catagory_index(4, title=u'淘旅游 - 春秋正品')

def index(page=1):
    """首页视图"""
    banners = wrap_picture(Tour.query.filter(Tour.stopped == 0).order_by(desc(Tour.rank)).limit(4).all())
    tao_url = random_url()

    return render_template('web_mobile/index.html',
                           banners=banners,
                           tao_url=tao_url)


def detail(tour_id):
    """详情页"""
    tour = wrap_picture(Tour.query.filter(Tour.id == tour_id).first())
    relates = random_select(Tour.query.filter(Tour.stopped == 0).filter(
        Tour.tour_type_id == tour.tour_type_id).order_by(desc(Tour.rank)).all(), 3)

    return render_template('web_mobile/detail.html',
                           tour=tour,
                           relates=relates)


def wrap_picture(tours):
    """对旅游类添加图片属性"""

    # 传过来是一个实例，添加所有的图片
    if not hasattr(tours, '__iter__'):
        tours.picture = []
        for picture in TourPicture.query.filter(TourPicture.tour_id == tours.id).all():
            picture_thumbnail = TourPictureThumbnail.query.filter(TourPictureThumbnail.picture_id == picture.id).first()
            if picture_thumbnail:
                tours.picture.append(create_rel_picture(picture, picture_thumbnail))
        return tours

    # 传过来一个列表，每个元素添加一张图片
    new_tours = []  # 过滤没有图片的tour
    for tour in tours:
        picture = TourPicture.query.filter(TourPicture.tour_id == tour.id).first()
        if picture:
            picture_thumbnail = TourPictureThumbnail.query.filter(TourPictureThumbnail.picture_id == picture.id).first()
            if picture_thumbnail:
                tour.picture = create_rel_picture(picture, picture_thumbnail)
                new_tours.append(tour)

    return new_tours


def random_select(tours, number):
    """对一个列表，任意选取number个元素"""

    if len(tours) <= number:
        return tours

    selects = []

    while len(selects) != number:
        select = choice(tours)
        if not (select in selects):
            selects.append(select)

    return selects

def random_url():
    """随机生成一个URL的链接详情页"""
    query = Tour.query.filter(Tour.stopped == 0)
    length = query.count()
    tour_id = query.all()[random.randint(0, length-1)].id
    return url_for('detail', tour_id=tour_id)



