# coding: utf-8

from flask import render_template
from ..models import Tour, TourPicture, TourPictureThumbnail
from sqlalchemy import desc
from random import choice


def index(page=1):
    """首页视图"""
    banners = wrap_picture(Tour.query.filter(Tour.stopped == 0).order_by(desc(Tour.rank)).limit(4).all())
    tours = wrap_picture(Tour.query.filter(Tour.stopped == 0).order_by(desc(Tour.rank)).all())

    return render_template('mobile_web/index.html',
                           banners=banners,
                           tours=tours)


def detail(tour_id):
    """详情页"""
    tour = wrap_picture(Tour.query.filter(Tour.id == tour_id).first())
    relates = random_select(Tour.query.order_by(desc(Tour.rank)).all(), 3)

    return render_template('mobile_web/detail.html',
                           tour=tour,
                           relates=relates)


def wrap_picture(tours):
    """对旅游类添加图片属性"""

    # 传过来是一个实例，添加所有的图片
    if not hasattr(tours, '__iter__'):
        tours.picture = []
        for picture in TourPicture.query.filter(TourPicture.tour_id == tours.id).all():
            picture_thumbnail = TourPictureThumbnail.query.filter(TourPictureThumbnail.picture_id == picture.id).first()
            tours.picture.append(create_picture(picture, picture_thumbnail))
        return tours

    # 传过来一个列表，每个元素添加一张图片
    for tour in tours:
        picture = TourPicture.query.filter(TourPicture.tour_id == tour.id).first()
        picture_thumbnail = TourPictureThumbnail.query.filter(TourPictureThumbnail.picture_id == picture.id).first()
        tour.picture = create_picture(picture, picture_thumbnail)

    return tours


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


class Picture(object):
    """保存图片信息的类"""
    def __init__(self, base_path, normal, picture286_170, picture640_288, picture300_180, picture176_160):
        self.normal = base_path + normal
        self.picture286_170 = base_path + picture286_170
        self.picture640_288 = base_path + picture640_288
        self.picture300_180 = base_path + picture300_180
        self.picture176_160 = base_path + picture176_160


def create_picture(picture, picture_thumbnail):
    """返回一个Picture的类"""
    base_path = picture.rel_path + '/'
    return Picture(base_path, picture.pic_name, picture_thumbnail.picture286_170, picture_thumbnail.picture640_288,
                   picture_thumbnail.picture300_180, picture_thumbnail.picture176_160)