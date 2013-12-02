# coding: utf-8

from flask import render_template, request

from ..models.order import Order
from ..models.tour import Tour
from ..models import db
from .web_mobile import wrap_picture
from sqlalchemy import desc
from web_mobile import *




def order_tour(tour_id):
    """订单"""
    if request.method == 'GET':
        tour = wrap_picture(Tour.query.filter(Tour.id == tour_id).first())
        return render_template('web_mobile/order_tour.html',
                           tour=tour)

    if request.method == 'POST':
        tour = wrap_picture(Tour.query.filter(Tour.id == tour_id).first())
        relates = random_select(Tour.query.filter(Tour.stopped == 0).filter(
        Tour.tour_type_id == tour.tour_type_id).order_by(desc(Tour.rank)).all(), 3)
        if not request.form.get('mobile', None):
            message = u'订单提交失败了，手机号必填哦。'
            return render_template('web_mobile/detail.html',
                           message=message,
                           tour=tour,
                           relates=relates)

        order = get_order(request.form, tour_id)
        if repeat_order(order, tour_id):
            message = u'重复订单，您之前的订单已经记录'
        else:
            db.add(order)
            db.commit()
            message = u'您的订单提交成功，我们的工作人员将会在三个工作日内联系您！'
        return render_template('web_mobile/detail.html',
                           message=message,
                           tour=tour,
                           relates=relates)

def get_order(form, tour_id):
    """通过form，生产order类"""
    return Order(tour_id=tour_id,
                 customer=form.get('customer', None),
                 mobile= form.get('mobile'),
                 email=form.get('email', None))

def repeat_order(order, tour_id):
    """订单重复返回True"""
    return bool(Order.query.filter(Order.mobile == order.mobile).filter(Order.tour_id == tour_id).count())