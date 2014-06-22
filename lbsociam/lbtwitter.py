#!/usr/env python
# -*- coding: utf-8 -*-
import twitter
import json
from lbsociam import encoders
from lbsociam import LBSociam

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

    def search(self):
        """
        Search public timeline
        """
        status_list = self.api.GetSearch(geocode=None, term=self.term,
          since_id=None, lang='pt')

        return status_list

    def statusToJSON(self, status):
        """
        Transform a status list in a JSON list
        """
        return json.dumps([dict(mpn=pn) for pn in status], cls=encoders.JSONEncoder)
