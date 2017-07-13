# -*- coding: utf-8 -*-
"""
    fanfou api
    ~~~~~~~~~~~~~~~~

    :copyright: 2013-16 by raptor.zh@gmail.com.
"""

from requests.auth import AuthBase
from requests_oauthlib import OAuth1Session
from restclient import APIClient


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

    def __call__(self, r):
        if r.url[:5] == "https":
            r.url = r.url.replace("https", "http")
        return self.auth(r)


class Fanfou(APIClient):
    def __init__(self, client_key, client_secret=None, token=None, token_secret=None,
                 callback_uri=None, verifier=None, proxies=None):
        super(Fanfou, self).__init__(OAuth1Session(client_key, client_secret=client_secret,
                                                   resource_owner_key=token, resource_owner_secret=token_secret,
                                                   callback_uri=callback_uri, verifier=verifier),
                                     "https://api.fanfou.com",
                                     objlist=['search', 'blocks', 'users', 'account', 'saved_searches',
                                              'photos', 'trends', 'followers', 'favorites', 'friendships',
                                              'friends', 'statuses', 'direct_messages'],
                                     postfix="json", proxies=proxies)
        self.auth.auth = HttpsAuth(self.auth.auth)
