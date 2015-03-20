#!/usr/env python
# -*- coding: utf-8 -*-
__author__ = 'eduardo'

import logging
import requests
from .lbstatus import status_base
from .crimes import crimes_base
from gensim.corpora import dictionary
from liblightbase.lbsearch.search import *

log = logging.getLogger()


class EventsCorpus(object):
    """
    Class to hold Events corpus
    """
    def __init__(self):
        """
        Building method
        """
        self.events_tokens = status_base.get_events_tokens()
        self.dic = self.get_dic()

    def __iter__(self):
        """
        When a dictionary loop is requested make one request at a time
        :return: JSON with dictionary data
        """
        id_list = status_base.get_document_ids()
        for id_doc in id_list:
            document = status_base.get_document(id_doc)
            yield self.dic.doc2bow(getattr(document, 'events_tokens', None))

    def get_dic(self):
        """
        Creates a gensim dictionary and return it
        :return: Gensim dictionary
        """
        return dictionary.Dictionary(self.events_tokens)

    @property
    def documents(self):
        """
        Get documents
        :return: Documents as texts
        """
        return status_base.get_text()

    @property
    def corpus(self):
        """
        Get corpus
        :return: Formatted corpus
        """
        return [self.dic.doc2bow(text) for text in self.events_tokens]


class CategoriesCorpus(object):
    """
    Corpus to categories
    """
    def __init__(self):
        """
        Building method
        """
        self.tokens = crimes_base.get_tokens()
        self.dic = self.get_dic()

    def get_dic(self):
        """
        Creates a gensim dictionary and return it
        :return: Gensim dictionary
        """
        return dictionary.Dictionary(self.tokens)

    @property
    def documents(self):
        """
        Get documents
        :return: Documents as texts
        """
        return status_base.get_text()

    @property
    def corpus(self):
        """
        Get corpus
        :return: Formatted corpus
        """
        return [self.dic.doc2bow(text) for text in self.tokens]