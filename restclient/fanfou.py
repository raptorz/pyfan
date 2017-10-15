# -*- coding: utf-8 -*-
"""
    fanfou api
    ~~~~~~~~~~~~~~~~

    :copyright: 2013-16 by raptor.zh@gmail.com.
"""

from requests.auth import AuthBase
from requests_oauthlib import OAuth1Session
from restclient import APIClient

import logging


logger = logging.getLogger(__name__)


"""
available functions:

search: GET_public_timeline, GET_users, GET_user_timeline
blocks: GET_ids, GET_blocking, POST_create, GET_exists, POST_destroy
users: GET_tagged, GET_show, GET_taglist, GET_followers, GET_recommendation, POST_cancelrecommendation, GET_friends
account: GET_verify_credentials, POST_update_profile_image, GET_rate_limit_status, POST_update_profile,
            GET_notification, POST_update_notify_num, GET_notify_num
saved_searches: POST_create, POST_destroy, GET_show, GET_list
photos: GET_user_timeline, POST_upload
trends: GET_list
followers: GET_ids
favorites: GET_, POST_create, POST_destroy
friendships: POST_create, POST_destroy, GET_requests, POST_deny, GET_exists, POST_accept, GET_show
friends: GET_ids
statuses: GET_home_timeline, GET_public_timeline, GET_friends_timeline, GET_user_timeline, GET_replies,
            POST_update, POST_destroy, GET_followers, GET_friends, GET_context_timeline, GET_mentions, GET_show
direct_messages: GET_inbox, GET_sent, POST_new, POST_destroy, GET_conversation, GET_conversation_list
"""


class HttpsAuth(AuthBase):
    def __init__(self, auth):
        self.auth = auth
        self.client = auth.client

    def __call__(self, r):
        if r.url.startswith("https"):
            r.url = r.url.replace("https", "http")
            result = self.auth(r)
            r.url = r.url.replace("http", "https")
        else:
            result = self.auth(r)
        return result


class Fanfou(APIClient):
    def __init__(self, client_key, client_secret=None, token=None, token_secret=None,
                 callback_uri=None, verifier=None, proxies=None, https=True):
        super(Fanfou, self).__init__(OAuth1Session(client_key, client_secret=client_secret,
                                                   resource_owner_key=token, resource_owner_secret=token_secret,
                                                   callback_uri=callback_uri, verifier=verifier),
                                     "https://api.fanfou.com" if https else "http://api.fanfou.com",
                                     objlist=['search', 'blocks', 'users', 'account', 'saved_searches',
                                              'photos', 'trends', 'followers', 'favorites', 'friendships',
                                              'friends', 'statuses', 'direct_messages'],
                                     postfix="json", proxies=proxies)
        self.auth._client = HttpsAuth(self.auth.auth)
        self.auth.auth = self.auth._client


def get_authorization(client_key, client_secret, access_token, access_secret, callback_uri, https=True):
    if access_token and access_secret:
        api = Fanfou(client_key, client_secret=client_secret, token=access_token, token_secret=access_secret,
                     https=https)
        try:
            data = api.account.GET_verify_credentials(mode='lite')
        except:
            data = None
        if data:
            return True, data
    api = Fanfou(client_key, client_secret=client_secret, callback_uri=callback_uri, https=https)
    try:
        request_token = api.auth.fetch_request_token("http://fanfou.com/oauth/request_token")
    except Exception as e:
        return False, e
    authorization_url = api.auth.authorization_url("https://fanfou.com/oauth/authorize")
    return False, dict(token=request_token, url=authorization_url)


def get_access_token(client_key, client_secret, request_token, https=True):
    if not request_token:
        return ValueError
    api = Fanfou(client_key, client_secret=client_secret,
                 token=request_token['oauth_token'], token_secret=request_token['oauth_token_secret'],
                 verifier="1234", https=https)
    access_token = api.auth.fetch_access_token("http://fanfou.com/oauth/access_token")
    return access_token
