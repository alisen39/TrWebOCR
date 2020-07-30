#!/usr/bin/env python
# encoding: utf-8
# author:alisen
# time: 2020/4/28 14:54
import os
import sys
from tornado.options import define, options
import tornado.web
import tornado.httpserver
import tornado.ioloop
import logging
from tornado.web import StaticFileHandler

BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_PATH)
from backend.tools.get_host_ip import host_ip
from backend.tools import manage_running_platform
from backend.tools import log


logger = logging.getLogger(log.LOGGER_ROOT_NAME + '.' + __name__)

current_path = os.path.dirname(__file__)
settings = dict(
    # debug=True,
    static_path=os.path.join(current_path, "dist/TrWebOcr_fontend")  # 配置静态文件路径
)


def make_app():
    from backend.webInterface import tr_run
    from backend.webInterface import tr_index

    return tornado.web.Application([
        (r"/api/tr-run/", tr_run.TrRun),
        (r"/", tr_index.Index),
        (r"/(.*)", StaticFileHandler,
         {"path": os.path.join(current_path, "dist/TrWebOcr_fontend"), "default_filename": "index.html"}),

    ], **settings)


if __name__ == "__main__":
    define("port", default=8089, type=int, help='指定运行时端口号')
    define("open_gpu", default=0, type=int, help='是否开启gpu')

    tornado.options.parse_command_line()
    port = options.port
    open_gpu = options.open_gpu

    if open_gpu == 0:
        manage_running_platform.change_version('cpu')
    else:
        manage_running_platform.change_version('gpu')
    app = make_app()

    server = tornado.httpserver.HTTPServer(app)
    # server.listen(port)
    server.bind(port)
    server.start(1)
    print(f'Server is running: http://{host_ip()}:{port}')
    print(f'Now version is: {manage_running_platform.get_run_version()}')

    # tornado.ioloop.IOLoop.instance().start()
    tornado.ioloop.IOLoop.current().start()
