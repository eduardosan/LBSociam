#!/usr/env python
# -*- coding: utf-8 -*-
__author__ = 'eduardo'
from beaker.cache import cache_region
from lbsociam.model.corpus import EventsCorpus


@cache_region('long_term')
def get_events_corpus():
    """
    Get cached events corpus
    :return: EventsCorpus object instance
    """
    c = EventsCorpus()
    return c
