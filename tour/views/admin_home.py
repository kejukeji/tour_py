# coding: utf-8

from flask.ext import login
from flask.ext.admin import AdminIndexView, expose


class HomeView(AdminIndexView):

    def __init__(self):
        super(HomeView, self).__init__(template='admin_tour/home.html', name=u'首页')

    @expose("/")
    def index(self):
        try:
            user = login.current_user.nick_name
        except:
            user = None

        return self.render(self._template, user=user)