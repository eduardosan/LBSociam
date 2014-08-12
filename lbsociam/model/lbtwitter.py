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
        Transform a status list in a JSON list
        """
        return json.dumps([pn for pn in status], cls=encoders.JSONEncoder)

    @staticmethod
    def status_to_dict(status):
        """
        Convert Status object to dict
        :param status: Twitter Status object
        :return: Twitter status Dict
        """
        return [pn.__dict__ for pn in status]

    @property
    def base(self):
        """
        @property base
        :return:
        """
        return self._base

    @base.setter
    def base(self, status):
        """
        Create a base to hold twitter information on Lightbase
        :param status: One twitter status object to be base model
        :return: LB Base object
        """
        lbbase = conv.pyobject2base(status)
        response = self.baserest.create(lbbase)
        if response.status_code == 200:
            self._base = lbbase
        else:
            self._base =  None

    @base.getter
    def base(self):
        return self._base

    @base.deleter
    def base(self):
        """
        Remove base when removing attribute
        """
        response = self.baserest.delete(self._base)
        if response.status_code == 200:
            del self._base

    def search(self):
        """
        Search public timeline
        """
        status_list = self.api.GetSearch(geocode=None, term=self.term,
          since_id=None, lang='pt')

        return status_list