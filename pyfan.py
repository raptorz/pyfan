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
    >> pyfan.showstatus("smmM8CbcJ4E") or index
    >> pyfan.destroy("tp6O2eYs2SI") or index
    >> pyfan.post(u"status", "photo.jpg")
    >> pyfan.repost(u"status", index)
    >> pyfan.reply(u"status", index)
    >> pyfan.replyall(u"status", index)
"""
from os.path import exists
from datetime import datetime
import re

from restclient.fanfou import Fanfou

from config import config

import logging


logger = logging.getLogger(__name__)


tldata = []


pat_reply = re.compile(u"@([^\s]+)\s")


def get_api():
    return Fanfou(config['CLIENT_KEY'], client_secret=config['CLIENT_SECRET'],
                  token=config['ACCESS_TOKEN'],
                  token_secret=config['ACCESS_SECRET'],
                  proxies={"http": config['proxy'], "https": config['proxy']} if config['proxy'] else None)


def print_status(i, status):
    row = {}
    row[u'index'] = i
    row[u'created'] = datetime.strptime(status['created_at'], "%a %b %d %H:%M:%S +0000 %Y").strftime("%Y-%m-%d %H:%M:%S")
    row[u'id'] = status['id']
    row[u'screen_name'] = status['user']['screen_name']
    row[u'user_id'] = status['user']['id']
    row[u'text'] = status['text']
    row[u'photo'] = status['photo']['largeurl'] if status.get('photo') else ""
    print(u"[%(index)s]%(created)s(%(id)s)%(screen_name)s(%(user_id)s): %(text)s %(photo)s" % row)


def timeline(count=10, page=0):
    api = get_api()
    global tldata
    data = api.statuses.GET_home_timeline(count=count, page=page, mode='lite')
    del tldata[:]
    tldata.extend(data)
    for i, status in enumerate(data):
        print_status(i, status)


def mentions(count=10, page=0):
    api = get_api()
    global tldata
    data = api.statuses.GET_mentions(count=count, page=page, mode="lite")
    del tldata[:]
    tldata.extend(data)
    for i, status in enumerate(data):
        print_status(i, status)


def usertimeline(user_id, count=10, page=0):
    api = get_api()
    global tldata
    data = api.statuses.GET_user_timeline(id=user_id, count=count, page=page, mode='lite')
    del tldata[:]
    tldata.extend(data)
    for i, status in enumerate(data):
        print_status(i, status)


def showstatus(status_id):
    if isinstance(status_id, int):
        global tldata
        status_id = tldata[status_id]['id']
    api = get_api()
    data = api.statuses.GET_show(id=status_id, mode="lite")
    del tldata[:]
    tldata.append(data)
    print_status(0, data)


def destroy(status_id):
    if isinstance(status_id, int):
        global tldata
        status_id = tldata[status_id]['id']
    api = get_api()
    api.statuses.POST_destroy(id=status_id, mode="lite")


def post(status, photo="", in_reply_to_status_id=None, repost_status_id=None, in_reply_to_user_id=None):
    api = get_api()
    if photo:
        if not exists(photo):
            print("Photo file {} not found!".format(photo))
        else:
            api.photos.POST_upload(status=status, photo=open(photo, "rb"), mode="lite")
    else:
        api.statuses.POST_update(status=status,
                in_reply_to_status_id=in_reply_to_status_id,
                repost_status_id=repost_status_id,
                in_reply_to_user_id=in_reply_to_user_id,
                mode="lite")


def reply(status, index):
    global tldata
    in_reply_to = tldata[index]
    api = get_api()
    api.statuses.POST_update(status=u"@{} {}".format(in_reply_to['user']['screen_name'], status),
                             in_reply_to_status_id=in_reply_to['id'],
                             in_reply_to_user_id=in_reply_to['user']['id'])


def replyall(status, index):
    global tldata
    in_reply_to = tldata[index]
    users = pat_reply.findall(u"".join([in_reply_to['text'], " ")))
    reply_user = in_reply_to['user']'screen_name']
    users = list(set(users) - set([reply_user]))
    users.insert(0, reply_user)
    api = get_api()
    api.statuses.POST_update(status=u"@{} {}".format(" @".join(users), status),
                             in_reply_to_status_id=in_reply_to['id'],
                             in_reply_to_user_id=in_reply_to['user']['id'])


def repost(status, index):
    global tldata
    in_reply_to = tldata[index]
    api = get_api()
    api.statuses.POST_update(status=u"{} 转:@{} {}".format(status, in_reply_to['user']['screen_name'], in_reply_to['text']),
                             repost_status_id=in_reply_to['id'])

