#!/usr/env python
# -*- coding: utf-8 -*-
__author__ = 'eduardo'
import twitter
import json
from lbsociam import encoders
from lbsociam import LBSociam
from liblightbase.lbutils import conv
from liblightbase import lbrest


class Twitter(LBSociam):
    """
    Twitter operations
    """
    def __init__(self, debug=False, term=None):
        LBSociam.__init__(self)
        self.debug = debug
        self.term = term
        self.api = None
        self.hashtag = None
        self.baserest = lbrest.BaseREST(rest_url=self.lbgenerator_rest_url, response_object=True)

    @property
    def api(self):
        return self._api

    @api.setter
    def api(self, a):
        """
        Initialize twitter API
        """
        self._api = twitter.Api(consumer_key=self.twitter_consumer_key,
          consumer_secret=self.twitter_consumer_secret,
          access_token_key=self.twitter_access_token,
          access_token_secret=self.twitter_access_secret,
          debugHTTP=self.debug,
          use_gzip_compression=True)

    @property
    def hashtag(self):
        return self._hashtag

    @hashtag.setter
    def hashtag(self, h):
        """
        Initialize twitter Hashtag
        """
        self._hashtag = twitter.Hashtag(self.term)

    @staticmethod
    def status_to_json(status):
        """
        Search public timeline
        """
        return json.dumps([pn for pn in status], cls=encoders.JSONEncoder)

    def status_to_dict(self, status):
        """
        Convert Status object to dict
        :param status: Twitter Status object
        :return: Twitter status Dict
        """
        status_json = self.status_to_json(status)
        return json.loads(status_json)

    def search(self, count=15, include_rt=False):
        """
        Search public timeline
        """
        status_list = self.api.GetSearch(geocode=None, term=self.term,
          since_id=None, lang='pt', count=count)

        saida = []
        if include_rt is True:
            return status_list
        else:
            # Return only status without RT
            for status in status_list:
                if status.GetRetweeted_status() is None:
                    saida.append(status)

        return saida
