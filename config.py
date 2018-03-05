# -*- coding: utf-8 -*-
"""
    config

    :copyright: 2016 by raptor.zh@gmail.com.
"""
#from __future__ import unicode_literals
import sys
PY3=sys.version>"3"

from os.path import dirname, abspath, expanduser, join as joinpath
import json

import logging

logger = logging.getLogger(__name__)


config_default = {
    "CLIENT_KEY": "",
    "CLIENT_SECRET": "",
    "ACCESS_TOKEN": "",
    "ACCESS_SECRET": "",
    "PROXY": "",
    "FANFOU_HTTPS": True,
    "web_addr": "localhost",
    "web_port": 8880,
    "debug": True,
}


def get_fullname(*args):
    root = dirname(abspath(__file__))
    return joinpath(root, joinpath(*args)) if len(args) > 0 else root


def uniencode(s, coding="utf-8"):
    return s.encode(coding) if s and (PY3 or not isinstance(s, str)) else s


def unidecode(s, coding="utf-8"):
    return unicode(s, coding) if s and (not PY3 or isinstance(s, str)) else s


def reload_config():
    res = config_default.copy()
    try:
        with open(get_fullname("config.json"), "r") as f:
            config = json.loads(f.read())
        res.update(config)
    except IOError:
        pass
    return res
