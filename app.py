#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import json

import tornado.escape
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.websocket
# import os.path
import uuid

from tornado.options import define, options

define('port', default=8888, help='run on the given port', type=int)


class Channel(object):
    """暂时将数据放到内存中，但是重启会丢失，后面可以考虑放到mc中"""
    waiters_dict = {}

    @classmethod
    def get_waiters(cls, channel_id):
        return cls.waiters_dict.get(channel_id, set())

    @classmethod
    def add(cls, channel_id, waiter):
        waiters = cls.waiters_dict.setdefault(channel_id, set())
        waiters.add(waiter)

    @classmethod
    def remove(cls, channel_id, waiter):
        waiters = cls.waiters_dict.get(channel_id, set())
        waiters.discard(waiter)
        if not waiters:
            cls.waiters_dict.pop(channel_id, None)


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            ('/', MainHandler),
            ('/push', PushHandler),
            ('/channel', ChannelSocketHandler),
        ]
        super(Application, self).__init__(handlers)


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.finish({'message': 'ok'})


class PushHandler(tornado.web.RequestHandler):
    def post(self):
        logging.info('post body is: %s', self.request.body)
        body = json.loads(self.request.body.decode('utf-8'))
        logging.info('post json is : %s', body)
        channel_id = body.get('channel_id')
        if not channel_id:
            self.finish({'errcode': 1, 'errmsg': 'channel_id is required'})
            return
        data = body.get('data')
        if not data:
            self.finish({'errcode': 1, 'errmsg': 'data is required'})
            return
        waiters = Channel.get_waiters(channel_id)
        logging.info('waiters len - %s', len(waiters))
        for waiter in waiters:
            try:
                waiter.write_message(data)
            except:
                logging.error('Error sending message', exc_info=True)
        self.finish({'errcode': 0, 'errmsg': 'ok'})


class ChannelSocketHandler(tornado.websocket.WebSocketHandler):

    def check_origin(self, origin):
        # 跨域的设置
        logging.info('check origin, origin: %s', origin)
        return True

    def on_message(self, message):
        """管理channel, message格式 {'channel_id': '...'} """
        data = json.loads(message)

        if 'channel_id' not in data:
            self.write({'errcode': 1, 'errmsg': '却少channel_id'})
            return

        channel_id = data['channel_id']
        if not channel_id:
            channel_id = uuid.uuid4().hex

        if not hasattr(self, channel_id):
            self.channel_id = channel_id
            Channel.add(channel_id, self)

        if channel_id != self.channel_id:
            Channel.remove(self.channel_id, self)
            Channel.add(channel_id, self)

        self.write_message({'channel_id': channel_id})

    def on_close(self):
        channel_id = getattr(self, 'channel_id')
        logging.info('websocked closed, channel_id is: %s', channel_id)
        if channel_id:
            Channel.remove(channel_id, self)


def main():
    tornado.options.parse_command_line()
    app = Application()
    app.listen(options.port)
    tornado.ioloop.IOLoop.current().start()


if __name__ == '__main__':
    main()
