# coding: utf-8

from flask.ext import restful
from tour.models.tour_type import TourType
from tour.models.tour import Tour


class GetTourType(restful.Resource):
    """获取tour的全部类型"""

    @staticmethod
    def get():
        tour_type = TourType.query.filter().all()

        json = []
        for i in tour_type:
            json.append([i.id, i.name])

        return json


class GetTourTypeById(restful.Resource):
    """通过ID获取tour类型的分类"""

    @staticmethod
    def get(tour_id):
        tour_type = Tour.query.filter(Tour.id == tour_id).first()

        if tour_type.tour_type_id:
            return [tour_type.tour_type_id]

        return [""]