# -*- coding: utf-8 -*-
"""
    rest client
    ~~~~~~~~~~~~~~~~
    RESTful api client.

    :copyright: 2012-18 by raptor.zh@gmail.com
"""
import sys

PY3 = sys.version>"3"

if PY3:
    from io import IOBase

    def isIOBase(obj):
        return isinstance(obj, IOBase)
else:
    from cStringIO import InputType
    from StringIO import StringIO

    def isIOBase(obj):
        return isinstance(obj, file) or isinstance(obj, StringIO) or isinstance(obj, InputType)

from functools import partial
import json
import logging

from requests_oauthlib import OAuth1Session, OAuth2Session


logger = logging.getLogger(__name__)


class APIObject(object):
    def __init__(self, client, objname):
        self.client = client
        self.objname = objname

    def __getattr__(self, name):
        funcs = name.split("_")
        fn = self.client.get_func(funcs[0], "_".join(
            [f if f != "ID" else "%s" for f in funcs[1:]]), self.objname)
        if fn:
            setattr(self, name, fn)
            return fn
        else:
            raise AttributeError('Invalid function name!')


class APIClient(object):
    def __init__(self, auth, url, objlist=None, postcall=None, postfix="", verify=True, proxies=None):
        """
        API client base class
        :param auth: AuthOAuth1 or AuthOAuth2 object
        :param url: API base url
        :param objlist: available API objects
        :param postcall: method will be called after API calling
        :param postfix: API method postfix, eg. .json or .xml
        :param verify: https verify
        :param proxies: proxies, like: {"http": "http://10.10.1.10:3128", "https": "http://10.10.1.10:1080"}
        """
        self.auth = auth
        self.url = url
        self.objlist = objlist
        self.postcall = postcall if postcall else lambda r: r.json()
        self.postfix = postfix
        self.auth.verify = verify
        self.auth.proxies = proxies

    def __getattr__(self, name):
        s = name.replace("_", "/")
        s = s.replace("//", "_")  # "__" will be replaced by "_" and not for split
        funcs = s.split("/")
        fn = self.get_func(funcs[0], "/".join([f if f != "ID" else "%s" for f in funcs[1:]]))
        if fn:
            setattr(self, name, fn)
            return fn
        elif (not self.objlist) or (name in self.objlist):
            obj = APIObject(self, name)
            setattr(self, name, obj)
            return obj
        else:
            raise AttributeError("Invalid object name!")

    def get_func(self, method, func, objname=None):
        fn = None
        if method in ['GET', 'POST', 'PUT', 'DELETE']:
            if objname:
                func = "/".join([objname, "%s", func] if func else [objname, "%s"])
            if self.postfix:
                func = ".".join([func, self.postfix])
            fn = partial(self._generic_call, method, func)
        return fn

    def _generic_call(self, method, func, *args, **kwargs):
        if func:
            if len(args) == 0:
                index = func.find("/%s")
                if index >= 0:
                    func = "".join([func[:index], func[index+3:]])
            else:
                func = func % args  # It will raise TypeError if args is not match
        url = "/".join([self.url, func])
        try:
            kwargs.update(self.extra_params)
        except AttributeError:
            pass
        return self._process(method, url, **kwargs)

    def _process(self, method, url, **kwargs):
        logger.debug(str(kwargs))
        fn = getattr(self.auth, method.lower())
        if fn:
            if method in ['GET', 'DELETE']:
                r = fn(url, params=kwargs, verify=self.auth.verify, proxies=self.auth.proxies)
            else:
                files = {}
                for k, v in kwargs.items():
                    if isIOBase(v):
                        files[k] = v
                for k in files.keys():
                    del kwargs[k]
                r = fn(url, data=kwargs, files=files if files else None,
                       verify=self.auth.verify, proxies=self.auth.proxies)
        else:
            raise AttributeError("Invalid http method name!")
        r.raise_for_status()
        return self.postcall(r)

    def _request(self, method, url_path, *args, **kwargs):
        url = "/".join([self.url, url_path.format(*args)])
        return self._process(method, url, **kwargs)

    def get(self, url, *args, **kwargs):
        return self._request("GET", url, *args, **kwargs)

    def post(self, url, *args, **kwargs):
        return self._request("POST", url, *args, **kwargs)

    def put(self, url, *args, **kwargs):
        return self._request("PUT", url, *args, **kwargs)

    def delete(self, url, *args, **kwargs):
        return self._request("DELETE", url, *args, **kwargs)


class AuthOAuth1(OAuth1Session):
    def __init__(self, client_id, client_secret, redirect_uri,
                 request_token_uri, authorization_uri, access_token_uri,
                 access_token=None, access_secret=None,
                 https=True, **kwargs):
        super(AuthOAuth1, self).__init__(client_key=client_id, client_secret=client_secret,
                                         resource_owner_key=access_token, resource_owner_secret=access_secret,
                                         callback_uri=redirect_uri, **kwargs)
        self.callback_uri = redirect_uri
        self.request_token_uri = request_token_uri
        self.authorization_uri = authorization_uri
        self.access_token_uri = access_token_uri
        self.https = https
        self.token = {"access_token": access_token, "access_secret": access_secret
                      } if access_token and access_secret else {}

    def get_token_str(self):
        res = {"access_token": self.token['oauth_token'],
               "access_secret": self.token['oauth_token_secret']}
        return json.dumps(res)

    def get_request_url(self, **kwargs):
        if not self.token:
            self.token = self.fetch_request_token(self.request_token_uri)
        else:
            kwargs['request_token'] = self.token
        authorization_url = self.authorization_url(self.authorization_uri, **kwargs)
        return authorization_url

    def get_access_token(self, verifier="", **kwargs):
        self.token = self.fetch_access_token(self.access_token_uri, verifier, **kwargs)
        return self.token


class AuthOAuth2(OAuth2Session):
    def __init__(self, client_id, client_secret, redirect_uri,
                 authorization_uri, access_token_uri,
                 access_token=None, **kwargs):
        super(AuthOAuth2, self).__init__(client_id=client_id, token=access_token,
                                         redirect_uri=redirect_uri, **kwargs)
        self.client_secret = client_secret
        self.authorization_uri = authorization_uri
        self.access_token_uri = access_token_uri
        self.token = access_token

    def get_request_url(self, **kwargs):
        request_url, state = self.authorization_url(self.authorization_uri, **kwargs)
        return request_url

    def get_access_token(self, response_url, **kwargs):
        self.token = self.fetch_token(self.access_token_uri,
                                      client_secret=self.client_secret,
                                      authorization_response=response_url,
                                      **kwargs)
        return self.token
