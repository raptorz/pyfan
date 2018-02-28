# -*- coding: utf-8 -*-
"""
    web login
    ~~~~~~~~~~~~~~~~
    web server for user login

    :copyright: 20160811 by raptor.zh@gmail.com.
"""
import json

from bottle import Bottle, run, request, response, redirect
from restclient import Fanfou
from restclient.fanfou import get_authorization, get_access_token

from config import config, get_fullname

import logging


logger = logging.getLogger(__name__)

app = Bottle()


def index_template(content):
    return u"""<!DOCTYPE HTML>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>web login</title>
</head>
<body>
<div>
{0}
</div>
</body>
</html>""".format(content)


@app.get("/")
def get_():
    auth, data = get_authorization(config['CLIENT_KEY'], config['CLIENT_SECRET'],
                                   config.get('ACCESS_TOKEN'), config.get('ACCESS_SECRET'),
                                   "http://{host}:{port}/callback".format(host=config['web_addr'],
                                                                          port=config['web_port']),
                                   config.get('FANFOU_HTTPS', True))
    if auth:
        return index_template(u"Login ok.<br/>User: {}.<br/><a href='/logout'>Logout</a>.".format(data['screen_name']))
    else:
        if not data or isinstance(data, Exception):
            return str(data)
        else:
            response.set_cookie("request_token", json.dumps(data['token']), path="/")
            redirect(data['url'])


@app.get("/callback")
def get_callback():
    request_token = json.loads(request.get_cookie("request_token"))
    response.set_cookie("request_token", "", path="/")
    access_token = get_access_token(config['CLIENT_KEY'], config['CLIENT_SECRET'], request_token,
                                    config.get('FANFOU_HTTPS', True))
    if not access_token or isinstance(access_token, ValueError):
        return index_template(u"Invalid request token")
    with open(get_fullname("config.json"), "r+") as f:
        access_config = json.loads(f.read())
        access_config['ACCESS_TOKEN'] = access_token['oauth_token']
        access_config['ACCESS_SECRET'] = access_token['oauth_token_secret']
        f.seek(0)
        f.truncate()
        f.write(json.dumps(access_config))
        config.update(access_config)
    redirect("/")


@app.get("/logout")
def get_logout():
    with open(get_fullname("config.json"), "r+") as f:
        access_config = json.loads(f.read())
        access_config['ACCESS_TOKEN'] = ""
        access_config['ACCESS_SECRET'] = ""
        f.seek(0)
        f.truncate()
        f.write(json.dumps(access_config))
        config.update(access_config)
    redirect("/")


def error_page(error):
    return index_template(u"Error: {0}".format(error))


handlers = {}
errors = [400, 401, 403, 404, 500]
[handlers.__setitem__(i, error_page) for i in errors]
app.error_handler = handlers


application = app


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG if config['debug'] else logging.WARNING)
    run(application, host=config['web_addr'], port=config['web_port'], debug=config['debug'], reloader=config['debug'])
