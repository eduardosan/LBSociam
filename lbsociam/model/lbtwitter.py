#!/usr/env python
# -*- coding: utf-8 -*-
__author__ = 'eduardo'
import twitter
import json
import datetime
import logging
from lbsociam import encoders
from lbsociam import LBSociam
from lbsociam.model.lbstatus import Status
from lbsociam.lib import srl, dictionary, location
from liblightbase.lbutils import conv
from liblightbase import lbrest

log = logging.getLogger()


class Twitter(LBSociam):
    """
    Twitter operations
    """
    def __init__(self,
                 status_base=None,
                 dictionary_base=None,
                 debug=False,
                 term=None):
        LBSociam.__init__(self)
        self.debug = debug
        self.term = term
        self.api = None
        self.hashtag = None
        self.baserest = lbrest.BaseREST(rest_url=self.lbgenerator_rest_url, response_object=True)
        if status_base is not None:
            self.status_base = status_base
        if dictionary_base is not None:
            self.dictionary_base = dictionary_base

    @property
    def api(self):
        return self._api

    @api.setter
    def api(self, a):
        """
        Initialize twitter API
        """
        self._api = twitter.Api(
            consumer_key=self.twitter_consumer_key,
            consumer_secret=self.twitter_consumer_secret,
            access_token_key=self.twitter_access_token,
            access_token_secret=self.twitter_access_secret,
            debugHTTP=self.debug,
            use_gzip_compression=True
        )

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
        status_list = self.api.GetSearch(
            geocode=None, term=self.term, since_id=None,
            lang='pt', count=count, result_type='recent'
        )

        saida = []
        if include_rt is True:
            return status_list
        else:
            # Return only status without RT and not replies
            for status in status_list:
                if status.GetRetweeted_status() is None and status.GetInReplyToStatusId() is None:
                    saida.append(status)

        return saida

    def search_user(self,
                    screen_name,
                    include_rts=False,
                    count=15,
                    exclude_replies=True):
        """
        Search specific user timeline

        :param screen_name: user screen_name
        :param include_rts: Whether we include RT's in results or not
        :param count: max 200 results on user timeline
        :param exclude_replies: Whether we should exclude replies or not
        :return: Status list
        """
        status_list = self.api.GetUserTimeline(
            screen_name=screen_name,
            count=count,
            include_rts=include_rts,
            exclude_replies=exclude_replies
            )

        return status_list

    def store_twitter(self, status_list, tokenize=True):
        """
        Store twitter status in LB Database

        :param status_list: List of status to be stored
        :param tokenize: Whether we should tokenize it directly or not
        :return: True or None if it isn't possible to store it
        """
        for elm in status_list:
            status_json = self.status_to_json([elm])

            status = Status(
                origin='twitter',
                inclusion_date=datetime.datetime.now(),
                inclusion_datetime=datetime.datetime.now(),
                search_term=self.term,
                text=elm.text,
                source=status_json,
                base=self.status_base
            )

            retorno = status.create_status()

            if retorno is None:
                log.error("Error inserting status %s on Base" % elm.text)

                return None

            status_dict = conv.document2dict(self.status_base.lbbase, status)

            # Manually add id_doc
            status_dict['_metadata'] = dict()
            status_dict['_metadata']['id_doc'] = retorno

            if tokenize:
                # SRL tokenize
                tokenized = srl.srl_tokenize(status_dict['text'])
                if tokenized.get('arg_structures') is not None:
                    status_dict['arg_structures'] = tokenized.get('arg_structures')
                if tokenized.get('tokens') is not None:
                    status_dict['tokens'] = tokenized.get('tokens')

            # Now try to find location
            status_dict = location.get_location(status_dict)

            # Process tokens if selected
            result = dictionary.process_tokens_dict(status_dict, self.dictionary_base)
            log.debug("Corpus da tokenização calculado. id_doc = %s", retorno)

            # Extract hashtags
            self.status_base.process_hashtags_dict(status_dict)

            # Calculate category
            status_dict = status.get_category(status_dict)

            # Now update document back
            self.status_base.documentrest.update(retorno, json.dumps(status_dict))

        return retorno