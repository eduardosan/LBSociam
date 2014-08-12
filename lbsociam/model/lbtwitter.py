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
        self._base = None

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

    @property
    def base(self):
        #print(self.__dict__)
        return self._base

    @base.setter
    def base(self, status):
        """
        Create a base to hold twitter information on Lightbase
        :param status: One twitter status object to be base model
        :return: LB Base object
        """
        # Remove repeated elements
        del status._user._created_at
        del status._user._location

        lbbase = conv.pyobject2base(status)
        response = self.baserest.create(lbbase)
        #print(response.status_code)
        if response.status_code == 200:
            self._base = lbbase
        else:
            self._base = None

    @base.deleter
    def base(self):
        """
        Remove base from Lightbase
        :param lbbase: LBBase object instance
        :return: True or Error if base was not excluded
        """
        response = self.baserest.delete(self._base)
        if response.status_code == 200:
            del self._base
        else:
            raise IOError('Error excluding base from LB')

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

    def search(self):
        """
        Search public timeline
        """
        status_list = self.api.GetSearch(geocode=None, term=self.term,
          since_id=None, lang='pt')

        return status_list