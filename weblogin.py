# -*- coding: utf-8 -*-
"""
    web login
    ~~~~~~~~~~~~~~~~
    web server for user login

    :copyright: 20160811 by raptor.zh@gmail.com.
"""
import json

from requests import HTTPError
from flask import Flask, request, redirect, make_response
from restclient.fanfou import Fanfou

from config import reload_config, get_fullname

import logging


logger = logging.getLogger(__name__)

app = Flask(__name__)


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


@app.route("/")
def get_():
    config = reload_config()
    try:
        if config.get("ACCESS_TOKEN") and config.get("ACCESS_SECRET"):
            api = Fanfou(config['CLIENT_KEY'], config['CLIENT_SECRET'],
                         config.get('ACCESS_TOKEN'), config.get('ACCESS_SECRET'),
                         https=config.get('FANFOU_HTTPS', True))
            data = api.account.GET_verify_credentials(mode='lite')
            return index_template(u"Login ok.<br/>User: {}.<br/><a href='/logout'>Logout</a>.".format(data['screen_name']))
        else:
            raise HTTPError
    except HTTPError:
        return index_template(u"<a href='/login'>Login</a>")


@app.route("/login")
def get_login():
    config = reload_config()
    api = Fanfou(config['CLIENT_KEY'], config['CLIENT_SECRET'],
                 redirect_uri="http://{host}:{port}/callback".format(host=config['web_addr'],
                                                                     port=config['web_port']),
                 https=config.get('FANFOU_HTTPS', True))
    url = api.auth.get_request_url()
    response = make_response(redirect(url))
    response.set_cookie("request_token", api.auth.get_token_str(), path="/")
    return response


@app.route("/callback")
def get_callback():
    config = reload_config()
    request_token = json.loads(request.cookies.get("request_token"))
    api = Fanfou(config['CLIENT_KEY'], config['CLIENT_SECRET'],
                 request_token['access_token'], request_token['access_secret'],
                 https=config.get('FANFOU_HTTPS', True))
    api.auth.get_access_token()
    with open(get_fullname("config.json"), "r+") as f:
        access_config = json.loads(f.read())
        access_config['ACCESS_TOKEN'] = api.auth.token['oauth_token']
        access_config['ACCESS_SECRET'] = api.auth.token['oauth_token_secret']
        f.seek(0)
        f.truncate()
        f.write(json.dumps(access_config))
    response = make_response(redirect("/"))
    response.set_cookie("request_token", "", path="/")
    return response


@app.route("/logout")
def get_logout():
    with open(get_fullname("config.json"), "r+") as f:
        access_config = json.loads(f.read())
        access_config['ACCESS_TOKEN'] = ""
        access_config['ACCESS_SECRET'] = ""
        f.seek(0)
        f.truncate()
        f.write(json.dumps(access_config))
    return redirect("/")


def error_page(error):
    return index_template(u"Error: {0}".format(error))


handlers = {}
errors = [400, 401, 403, 404, 500]
[handlers.__setitem__(i, error_page) for i in errors]
app.error_handler = handlers


application = app


if __name__ == "__main__":
    config = reload_config()
    logging.basicConfig(level=logging.DEBUG if config['debug'] else logging.WARNING)
    application.run(host=config['web_addr'], port=config['web_port'], debug=config['debug'], threaded=True)
