#!/usr/env python
# -*- coding: utf-8 -*-
__author__ = 'eduardo'
import os
import os.path
import nltk
import nlpnet

import ConfigParser
import logging
import logging.config
from beaker.cache import CacheManager
from beaker.util import parse_cache_config_options

environment = 'development'


def load_config():
    """
    Carrega configuração
    :return:
    """
    #print(environment)

    config = ConfigParser.ConfigParser()
    here = os.path.abspath(os.path.dirname(__file__))
    config_file = os.path.join(here, '../' + environment + '.ini')
    config.read(config_file)

    # Parâmetros globais de configuração
    nltk.data.path.append(config.get('nltk', 'data_dir'))
    nlpnet.set_data_dir(config.get('nlpnet', 'data_dir'))

    # Logging
    logging.config.fileConfig(config_file)

    # Cache configurations
    cache_opts = {
        'cache.regions': config.get('lbsociam', 'cache.regions'),
        'cache.type': config.get('lbsociam', 'cache.type'),
        'cache.short_term.expire': config.get('lbsociam', 'cache.short_term.expire'),
        'cache.default_term.expire': config.get('lbsociam', 'cache.default_term.expire'),
        'cache.long_term.expire': config.get('lbsociam', 'cache.long_term.expire')
    }

    cache = CacheManager(**parse_cache_config_options(cache_opts))

    return config