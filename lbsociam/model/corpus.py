#!/usr/env python
# -*- coding: utf-8 -*-
__author__ = 'eduardo'
import logging
from gensim.corpora import dictionary

log = logging.getLogger()


class EventsCorpus(object):
    """
    Class to hold Events corpus
    """
    def __init__(self,
                 status_base):
        """
        Building method
        """
        self.status_base = status_base
        self.events_tokens = status_base.get_events_tokens()
        self.dic = self.get_dic()

    def __iter__(self):
        """
        When a dictionary loop is requested make one request at a time
        :return: JSON with dictionary data
        """
        id_list = self.status_base.get_document_ids()
        for id_doc in id_list:
            document = self.status_base.get_document(id_doc)
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
        return self.status_base.get_text()

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
    def __init__(self, crimes_base):
        """
        Building method
        """
        self.crimes_base = crimes_base
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
        return self.crimes_base.get_text()

    @property
    def corpus(self):
        """
        Get corpus
        :return: Formatted corpus
        """
        return [self.dic.doc2bow(text) for text in self.tokens]