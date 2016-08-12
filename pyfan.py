# -*- coding: utf-8 -*-
"""
    pyfan
    a command line fanfou client
    ~~~~~~~~~~~~~~~~

    :copyright: 2016 by raptor.zh@gmail.com.

    usage:

    python
    >> import pyfan
    >> pyfan.timeline(10)
    >> pyfan.mentions(10)
    >> pyfan.usertimeline(user_id, 10)
    >> pyfan.showstatus("smmM8CbcJ4E")
    >> pyfan.destroy("tp6O2eYs2SI")
    >> pyfan.post(u"status", "photo.jpg")
"""
from os.path import exists
from datetime import datetime

from restclient.fanfou import Fanfou

from config import config

import logging


logger = logging.getLogger(__name__)


def get_api():
    return Fanfou(config['CLIENT_KEY'], client_secret=config['CLIENT_SECRET'],
                  token=config['ACCESS_TOKEN'],
                  token_secret=config['ACCESS_SECRET'],
                  proxies={"http": config['proxy'], "https": config['proxy']} if config['proxy'] else None)


def print_status(status):
    row = {}
    row[u'created'] = datetime.strptime(status['created_at'], "%a %b %d %H:%M:%S +0000 %Y").strftime("%Y-%m-%d %H:%M:%S")
    row[u'id'] = status['id']
    row[u'screen_name'] = status['user']['screen_name']
    row[u'user_id'] = status['user']['id']
    row[u'text'] = status['text']
    row[u'photo'] = status['photo']['largeurl'] if status.get('photo') else ""
    print(u"%(created)s(%(id)s)%(screen_name)s(%(user_id)s): %(text)s %(photo)s" % row)


def timeline(count=10, page=0):
    api = get_api()
    data = api.statuses.GET_home_timeline(count=count, page=page, mode='lite')
    for status in data:
        print_status(status)


def mentions(count=10, page=0):
    api = get_api()
    data = api.statuses.GET_mentions(count=count, page=page, mode="lite")
    for status in data:
        print_status(status)


def usertimeline(user_id, count=10, page=0):
    api = get_api()
    data = api.statuses.GET_user_timeline(id=user_id, count=count, page=page, mode='lite')
    for status in data:
        print_status(status)


def showstatus(status_id):
    api = get_api()
    data = api.statuses.GET_show(id=status_id, mode="lite")
    print_status(data)


def destroy(status_id):
    api = get_api()
    api.statuses.POST_destroy(id=status_id, mode="lite")


def post(status, photo=""):
    api = get_api()
    if photo and exists(photo):
        api.photos.POST_upload(status=status, photo=open(photo, "rb"), mode="lite")
    else:
        api.statuses.POST_update(status=status, mode="lite")
