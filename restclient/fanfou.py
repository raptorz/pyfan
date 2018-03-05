# -*- coding: utf-8 -*-
"""
    fanfou api
    ~~~~~~~~~~~~~~~~

    :copyright: 2013-18 by raptor.zh@gmail.com.
"""
import json
import logging

from requests.auth import AuthBase

from restclient import APIClient, AuthOAuth1


logger = logging.getLogger(__name__)


class HttpsAuth(AuthBase):
    def __init__(self, auth):
        self.auth = auth
        self.client = auth.client

    def __call__(self, r):
        if r.url.startswith("https://"):
            r.url = r.url.replace("https", "http")
            result = self.auth(r)
            r.url = r.url.replace("http", "https")
        else:
            result = self.auth(r)
        return result


class AuthFanfou(AuthOAuth1):
    def __init__(self,  client_id, client_secret, redirect_uri,
                 access_token=None, access_secret=None,
                 https=False, **kwargs):
        super(AuthFanfou, self).__init__(client_id, client_secret, redirect_uri,
                                         "https://fanfou.com/oauth/request_token",
                                         "https://fanfou.com/oauth/authorize",
                                         "https://fanfou.com/oauth/access_token",
                                         access_token=access_token, access_secret=access_secret,
                                         https=https, **kwargs)

    def get_token_str(self):
        res = {"access_token": self.token['oauth_token'],
               "access_secret": self.token['oauth_token_secret']}
        return json.dumps(res)

    def get_request_url(self):
        return super(AuthFanfou, self).get_request_url(oauth_callback=self.callback_uri)

    def get_access_token(self, verifier="", **kwargs):
        super(AuthFanfou, self).get_access_token(verifier=u"1234")
        return self.get_token_str()


class Fanfou(APIClient):
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
    def __init__(self, client_key, client_secret=None, access_token=None, access_secret=None,
                 redirect_uri=None, proxies=None, https=True, **kwargs):
        super(Fanfou, self).__init__(AuthFanfou(client_key, client_secret=client_secret, redirect_uri=redirect_uri,
                                                access_token=access_token, access_secret=access_secret, **kwargs),
                                     "https://api.fanfou.com" if https else "http://api.fanfou.com",
                                     objlist=['search', 'blocks', 'users', 'account', 'saved_searches',
                                              'photos', 'trends', 'followers', 'favorites', 'friendships',
                                              'friends', 'statuses', 'direct_messages'],
                                     postfix="json", proxies=proxies)
        self.auth._client = HttpsAuth(self.auth.auth)
        self.auth.auth = self.auth._client
