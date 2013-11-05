# coding: utf-8

"""web相关的视图都在这里定义"""

from flask import render_template
from ..models import Tour, TourPicture, TourPictureThumbnail, db
from sqlalchemy import desc
from random import choice
from .picture_tools import create_rel_picture


def index(page=1):
    """首页视图"""
    banners = wrap_picture(Tour.query.filter(Tour.stopped == 0).order_by(desc(Tour.rank)).limit(4).all())
    tours = wrap_picture(Tour.query.filter(Tour.stopped == 0).order_by(desc(Tour.rank)).all())

    return render_template('web_mobile/index.html',
                           banners=banners,
                           tours=tours)


def detail(tour_id):
    """详情页"""
    tour = wrap_picture(Tour.query.filter(Tour.id == tour_id).first())
    relates = random_select(Tour.query.filter(Tour.stopped == 0).order_by(desc(Tour.rank)).all(), 3)

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