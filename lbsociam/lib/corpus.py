#!/usr/env python
# -*- coding: utf-8 -*-
__author__ = 'eduardo'
import logging
from beaker.cache import cache_region
from lbsociam.model.corpus import EventsCorpus

log = logging.getLogger()

@cache_region('long_term')
def get_events_corpus(status_base):
    """
    Get cached events corpus
    :return: EventsCorpus object instance
    """
    log.debug("EVENTS CORPUS: fetch events corpus from base %s", status_base.lbbase.metadata.name)
    c = EventsCorpus(status_base=status_base)
    return c
