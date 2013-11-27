# coding: utf-8

from flask.ext.admin.contrib.sqla import ModelView
from flask.ext import login

from ..models import Order


class OrderView(ModelView):
    """管理用户预订的节目"""

    page_size = 30
    can_create = False
    can_delete = True
    column_labels = {
        'id':u'ID',
        'tour.title':u'产品',
        'tour.id':u'产品ID',
        'mobile':u'联系方式',
        'email':u'邮箱',
        'customer':u'客户',
        'time':u'时间',
        'status':u'订单状态'
    }
    column_choices = dict(
        status=[(0, u'新的订单'), (1, u'等待付款'), (2, u'订单成交'), (3, u'订单取消')]
    )
    form_choices = dict(
        status=[('0', u'新的订单'), ('1', u'等待付款'), ('2', u'订单成交'), ('3', u'订单取消')]
    )
    column_list = ('id', 'tour.title', 'tour.id', 'mobile', 'email', 'customer', 'time', 'status')
    column_default_sort = ('status', False)

    def __init__(self, db_session, **kwargs):
        super(OrderView, self).__init__(Order, db_session, **kwargs)

    def is_accessible(self):
        if login.current_user.is_admin() and login.current_user.admin == 1:
            return True

        return False