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
    if config['ACCESS_TOKEN'] and config['ACCESS_SECRET']:
        api = Fanfou(config['CLIENT_KEY'], client_secret=config['CLIENT_SECRET'],
                             token=config['ACCESS_TOKEN'],
                             token_secret=config['ACCESS_SECRET'])
        try:
            data = api.account.GET_verify_credentials(mode='lite')
        except:
            data = None
        if data:
            return index_template(u"Login ok.<br/>User: {0}.<br/><a href='/logout'>Logout</a>.".format(data['screen_name']))
    callback_uri = "http://{host}:{port}/callback".format(host=config['web_addr'],
                                                          port=config['web_port'])
    api = Fanfou(config['CLIENT_KEY'], client_secret=config['CLIENT_SECRET'], callback_uri=callback_uri)
    request_token = api.auth.fetch_request_token("http://fanfou.com/oauth/request_token")
    response.set_cookie("request_token", json.dumps(request_token))
    authorization_url = api.auth.authorization_url("http://fanfou.com/oauth/authorize")
    redirect(authorization_url)


@app.get("/callback")
def get_callback():
    request_token = json.loads(request.get_cookie("request_token"))
    response.set_cookie("request_token", "")
    if not request_token:
        return index_template(u"Invalid request token")
    api = Fanfou(config['CLIENT_KEY'], client_secret=config['CLIENT_SECRET'],
                 token=request_token['oauth_token'],
                 token_secret=request_token['oauth_token_secret'],
                 verifier="1234")
    access_token = api.auth.fetch_access_token("http://fanfou.com/oauth/access_token")
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
