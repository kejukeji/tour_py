# coding: utf-8

from .tour import Tour, TourPicture, TourPictureThumbnail
from .user import User
from .order import Order
from .tour_type import TourType

from .database import db, Base, engine


if __name__ == '__main__':
    Base.metadata.create_all(engine)