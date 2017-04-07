# -*- coding: utf-8 -*-
"""
    rest client
    ~~~~~~~~~~~~~~~~
    RESTful api client.

    :copyright: 2012-16 by raptor.zh@gmail.com
"""
import sys
PY3=sys.version>"3"

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
import logging


logger = logging.getLogger(__name__)


class APIObject(object):
    def __init__(self, client, objname):
        self.client = client
        self.objname = objname

    def __getattr__(self, name):
        funcs = name.split("_")
        fn = self.client._get_func(funcs[0], "_".join(
            [f if f != "ID" else "%s" for f in funcs[1:]]), self.objname)
        if fn:
            setattr(self, name, fn)
            return fn
        else:
            raise AttributeError('Invalid function name!')


# auth is requests_oauthlib.OAuth1Session or OAuth2Session
class APIClient(object):
    def __init__(self, auth, url, objlist=None, postcall=None, postfix="", verify=True, proxies=None):
        self.auth = auth
        self.url = url
        self.objlist = objlist
        self.postcall = postcall if postcall else lambda r: r.json()
        self.postfix = postfix
        self.verify = verify
        self.proxies = proxies

    def __getattr__(self, name):
        s = name.replace("_", "/")
        s = s.replace("//", "_")  # "__" will be relaced by "_" and not for split
        funcs = s.split("/")
        fn = self._get_func(funcs[0], "/".join([f if f != "ID" else "%s" for f in funcs[1:]]))
        if fn:
            setattr(self, name, fn)
            return fn
        elif (not self.objlist) or (name in self.objlist):
            obj = APIObject(self, name)
            setattr(self, name, obj)
            return obj
        else:
            raise AttributeError("Invalide object name!")

    def _get_func(self, method, func, objname=None):
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
        return self._process(method, url, **kwargs)

    def _process(self, method, url, **kwargs):
        fn = getattr(self.auth, method.lower())
        if fn:
            if method in ['GET', 'DELETE']:
                r = fn(url, params=kwargs, verify=self.verify, proxies=self.proxies)
            else:
                files = {}
                for k, v in kwargs.items():
                    if isIOBase(v):
                        files[k]=v
                for k in files.keys():
                    del kwargs[k]
                r = fn(url, data=kwargs, files=files if files else None, verify=self.verify, proxies=self.proxies)
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
