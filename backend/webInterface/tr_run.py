#!/usr/bin/env python
# encoding: utf-8
# author:alisen
# time: 2020/4/29 10:47
# import json
import time

import tr
import tornado.web
import tornado.gen
import tornado.httpserver

import base64
from PIL import Image, ImageDraw
from io import BytesIO
import datetime
import logging
from logging.handlers import RotatingFileHandler

import json
from backend.tools.np_encoder import NpEncoder
import os

BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if not os.path.exists('./logs'):
    os.mkdir('./logs')

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.INFO)
rHandler = RotatingFileHandler(os.path.join(BASE_PATH, 'logs/log.log'), maxBytes=1 * 1024 * 1024, backupCount=3)
rHandler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
rHandler.setFormatter(formatter)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
console.setFormatter(formatter)

logger.addHandler(rHandler)
logger.addHandler(console)


class TrRun(tornado.web.RequestHandler):
    '''
    使用 tr 的 run 方法
    '''

    # TODO 图片过大会爆内存而退出； 增大 swap 空间

    def get(self):
        self.write("Error Request")

    @tornado.gen.coroutine
    def post(self):
        '''

        :return:
        报错：
        400 没有请求参数

        '''
        start_time = time.time()
        MAX_SIZE = 1600

        img_up = self.request.files.get('file', None)
        img_b64 = self.get_argument('img', None)
        compress_size = self.get_argument('compress', None)

        # 判断是上传的图片还是base64
        self.set_header('content-type', 'application/json')
        up_image_type = None
        if img_up is not None and len(img_up) > 0:
            img_up = img_up[0]
            up_image_type = img_up.content_type
            up_image_name = img_up.filename
            img = Image.open(BytesIO(img_up.body))
        elif img_b64 is not None:
            raw_image = base64.b64decode(img_b64.encode('utf8'))
            img = Image.open(BytesIO(raw_image))
        else:
            self.set_status(400)
            logger.error(json.dumps({'code': 400, 'msg': '没有传入参数'}, cls=NpEncoder))
            self.finish(json.dumps({'code': 400, 'msg': '没有传入参数'}, cls=NpEncoder))
            return

        try:
            if hasattr(img, '_getexif') and img._getexif() is not None:
                orientation = 274
                exif = dict(img._getexif().items())
                if exif[orientation] == 3:
                    img = img.rotate(180, expand=True)
                elif exif[orientation] == 6:
                    img = img.rotate(270, expand=True)
                elif exif[orientation] == 8:
                    img = img.rotate(90, expand=True)
        except Exception as ex:
            error_log = json.dumps({'code': 400, 'msg': '产生了一点错误，请检查日志', 'err': str(ex)}, cls=NpEncoder)
            logger.error(error_log)
            self.finish(error_log)
            return
        img = img.convert("RGB")

        '''
        是否开启图片压缩
        默认为1600px
        值为 0 时表示不开启压缩
        非 0 时则压缩到该值的大小
        '''
        if compress_size is not None:
            try:
                compress_size = int(compress_size)
            except ValueError as ex:
                self.finish(json.dumps({'code': 400, 'msg': 'compress参数类型有误，只能是int类型'}, cls=NpEncoder))
                return

            if compress_size < 1:
                MAX_SIZE = max(img.height, img.width)
            else:
                MAX_SIZE = compress_size

            # elif :
            #     if compress_size < 1:
            #         self.finish(json.dump({'code': 400, 'msg': 'compress值不能小于0哦'}, cls=NpEncoder))
            #         return
            #     else:
            #         MAX_SIZE = compress_size
            # else:
            #     self.finish(json.dumps({'code': 400, 'msg': 'compress参数类型有误，只能是int类型'}, cls=NpEncoder))
            #     return

        if img.height > MAX_SIZE or img.width > MAX_SIZE:
            scale = max(img.height / MAX_SIZE, img.width / MAX_SIZE)

            new_width = int(img.width / scale + 0.5)
            new_height = int(img.height / scale + 0.5)
            img = img.resize((new_width, new_height), Image.BICUBIC)

        res = tr.run(img)

        img_detected = img.copy()
        img_draw = ImageDraw.Draw(img_detected)
        colors = ['red', 'green', 'blue', "purple"]

        for i, r in enumerate(res):
            rect, txt, confidence = r
            x, y, w, h = rect
            for xy in [(x, y, x + w, y), (x + w, y, x + w, y + h), (x + w, y + h, x, y + h), (x, y + h, x, y)]:
                img_draw.line(xy=xy, fill=colors[i % len(colors)], width=2)

        output_buffer = BytesIO()
        img_detected.save(output_buffer, format='JPEG')
        byte_data = output_buffer.getvalue()
        img_detected_b64 = base64.b64encode(byte_data).decode('utf8')

        log_info = {
            'ip': self.request.host,
            'return': res,
            'time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        logger.info(json.dumps(log_info, cls=NpEncoder))

        self.finish(json.dumps(
            {'code': 200, 'msg': '成功',
             'data': {'img_detected': 'data:image/jpeg;base64,' + img_detected_b64, 'raw_out': res,
                      'speed_time': round(time.time() - start_time, 2)}},
            cls=NpEncoder))
        return
