# coding: utf-8

from sqlalchemy import Column, Integer, String, Boolean, DATETIME

from .database import Base
from ..utils.ex_time import todayfstr
from ..utils.ex_password import generate_password, check_password

USER_TABLE = 'user'


class User(Base):
    """User类，对应于数据库的user表
    id
    login_type 用户登录类型，Integer(4)， 0表示注册用户 1表示微博登录 2表示QQ登录
    login_name 用户登录名，同一类型的登陆用户，登录名不能一样，第三方登陆用户可以为空
    password 用户密码，使用加密
    open_id 第三方登陆的openId
    nick_name 用户昵称，不可重复，第三方注册用户必须填写昵称，评论的时候使用
    sign_up_date 用户注册时间
    admin 是否具有管理员权限 0否 1是
    """

    __tablename__ = USER_TABLE

    id = Column(Integer, primary_key=True)
    login_name = Column(String(32), nullable=True, server_default=None, unique=True)
    password = Column(String(64), nullable=True, server_default=None)
    login_type = Column(Integer, nullable=False, server_default='0')
    open_id = Column(String(64), nullable=True, server_default=None)
    nick_name = Column(String(32), nullable=False, unique=True)
    sign_up_date = Column(DATETIME, nullable=True, server_default=None)
    admin = Column(Boolean, nullable=False, server_default='0')

    def __init__(self, **kwargs):
        self.login_type = kwargs.pop('login_type')
        self.nick_name = kwargs.pop('nick_name')
        self.sign_up_date = todayfstr()
        self.login_name = kwargs.pop('login_name', None)

        password = kwargs.pop('password', None)
        if password is not None:
            self.password = generate_password(password)
        else:
            self.password = password

        self.open_id = kwargs.pop('open_id', None)
        self.admin = kwargs.pop('admin', 0)

    def __repr__(self):
        return '<User(nick_name: %s, login_type: %s, sign_up_date: %s)>' % (self.nick_name, self.login_type,
                                                                            self.sign_up_date)

    def update(self, **kwargs):
        self.login_type = kwargs.pop('login_type')
        self.nick_name = kwargs.pop('nick_name')
        self.login_name = kwargs.pop('login_name', None)

        password = kwargs.pop('password', None)
        if password is not None:
            if self.password != password:
                self.password = generate_password(password)
        else:
            self.password = password

        self.open_id = kwargs.pop('open_id', None)
        self.admin = kwargs.pop('admin', 0)

    def change_password(self, old_password, new_password):
        """设置用户密码"""

        if new_password is None:
            return False

        if old_password is None:
            if self.password is None:
                self.password = generate_password(new_password)
                return True
            else:
                return False
        else:
            if self.check_password(old_password):
                self.password = generate_password(new_password)
                return True
            else:
                return False

    def check_password(self, password):
        """检查密码是否正确"""

        if (password is None) and (self.password is None):
            return True

        if (password is None) or (self.password is None):
            return False

        return check_password(password, self.password)

    def is_authenticated(self):  # todo-lyw 静态method是如何用的，和类方法的不同
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def is_admin(self):
        return bool(self.admin)

    def get_id(self):
        return self.id

