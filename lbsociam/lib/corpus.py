#!/usr/env python
# -*- coding: utf-8 -*-
__author__ = 'eduardo'
from beaker.cache import cache_region
from lbsociam.model.corpus import EventsCorpus


@cache_region('long_term')
def get_events_corpus(status_base):
    """
    Get cached events corpus
    :return: EventsCorpus object instance
    """
    c = EventsCorpus(status_base=status_base)
    return c
