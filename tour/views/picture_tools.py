# coding: utf-8

from ..models import TourPicture, TourPictureThumbnail, db
from ..utils import time_file_name
import Image


def save_thumbnails(picture_id):  # todo-lyw views里面的多个函数式重复的，db参数的问题，这个有时间可以统一一下到单独的文件里面去，而且需要更好的命名
    picture = TourPicture.query.filter(TourPicture.id == picture_id).first()
    base_path = picture.base_path + picture.rel_path + '/'
    picture286 = picture_resize(picture, (286, 170))
    picture286_name = time_file_name(str(picture_id)) + 'nail.jpeg'
    picture286.save(base_path + picture286_name, 'jpeg')
    picture640 = picture_resize(picture, (640, 288))
    picture640_name = time_file_name(str(picture_id)) + 'nail.jpeg'
    picture640.save(base_path + picture640_name, 'jpeg')
    picture300 = picture_resize(picture, (300, 180))
    picture300_name = time_file_name(str(picture_id)) + 'nail.jpeg'
    picture300.save(base_path + picture300_name, 'jpeg')
    picture176 = picture_resize(picture, (176, 160))
    picture176_name = time_file_name(str(picture_id)) + 'nail.jpeg'
    picture176.save(base_path + picture176_name, 'jpeg')
    db.add(TourPictureThumbnail(picture_id, picture286_name, picture640_name, picture300_name, picture176_name))
    db.commit()


class Picture(object):
    """保存图片信息的类"""
    def __init__(self, base_path, normal, picture286_170, picture640_288, picture300_180, picture176_160):
        self.normal = base_path + normal
        self.picture286_170 = base_path + picture286_170
        self.picture640_288 = base_path + picture640_288
        self.picture300_180 = base_path + picture300_180
        self.picture176_160 = base_path + picture176_160


def create_rel_picture(picture, picture_thumbnail):
    """返回一个Picture的类，图片的路径是相对的，用于获取服务器数据"""

    # 如果picture_thumbnail为空，创建一个
    if not picture_thumbnail:
        save_thumbnails(picture.id)
        picture_thumbnail = TourPictureThumbnail.query.filter(TourPictureThumbnail.picture_id == picture.id).first()

    base_path = picture.rel_path + '/'
    return Picture(base_path, picture.pic_name, picture_thumbnail.picture286_170, picture_thumbnail.picture640_288,
                   picture_thumbnail.picture300_180, picture_thumbnail.picture176_160)


def create_base_picture(picture, picture_thumbnail):
    """返回一个Picture的类，图片的路径是绝对的，用于删除本地文件"""

    # 如果picture_thumbnail为空，创建一个
    if not picture_thumbnail:
        save_thumbnails(picture.id)
        picture_thumbnail = TourPictureThumbnail.query.filter(TourPictureThumbnail.picture_id == picture.id).first()

    base_path = picture.base_path + picture.rel_path + '/'
    return Picture(base_path, picture.pic_name, picture_thumbnail.picture286_170, picture_thumbnail.picture640_288,
                   picture_thumbnail.picture300_180, picture_thumbnail.picture176_160)


def picture_resize(picture, resize):
    picture_path = picture.base_path + picture.rel_path + '/' + picture.pic_name
    im = Image.open(picture_path)
    # crop到一定的比例大小，只是裁剪
    normal_size = im.size
    if normal_size[0] <= normal_size[1] * resize[0] / resize[1]:
        start_pos = (normal_size[1] - normal_size[0] * resize[1] / resize[0]) / 2
        image = im.crop((0, start_pos, normal_size[0], normal_size[0] * resize[1] / resize[0]))
    else:
        start_pos = (normal_size[0] - normal_size[1] * resize[0] / resize[1]) / 2
        image = im.crop((start_pos, 0, normal_size[1] * resize[0] / resize[1], normal_size[1]))

    # resize到更小的比例，只是缩小
    resize_image = image.resize(resize)

    return resize_image