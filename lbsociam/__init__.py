#!/usr/env python
# -*- coding: utf-8 -*-
import os
import nltk
import nlpnet

import ConfigParser
import logging
import logging.config

config = ConfigParser.ConfigParser()
here = os.path.abspath(os.path.dirname(__file__))
config_file = os.path.join(here, '../development.ini')
config.read(config_file)

# Parâmetros globais de configuração
nltk.data.path.append(config.get('nltk', 'data_dir'))
nlpnet.set_data_dir(config.get('nlpnet', 'data_dir'))

# Logging
logging.config.fileConfig(config_file)


class LBSociam(object):
    """
    Classe global com as configurações
    """
    def __init__(self):
        """
        Parâmetro construtor
        """
        self.twitter_sources = config.get('twitter', 'sources')
        self.twitter_hashtags = config.get('twitter', 'hashtags')
        self.twitter_consumer_key = config.get('twitter', 'consumer_key')
        self.twitter_consumer_secret = config.get('twitter', 'consumer_secret')
        self.twitter_access_token = config.get('twitter', 'access_token')
        self.twitter_access_secret = config.get('twitter', 'access_secret')
        self.lbgenerator_rest_url = config.get('lbgenerator', 'rest_url')
        lbsociam_data_dir = config.get('lbsociam', 'data_dir')
        if os.path.isdir(lbsociam_data_dir):
            self.lbsociam_data_dir = lbsociam_data_dir
        else:
            os.mkdir(lbsociam_data_dir)
            self.lbsociam_data_dir = lbsociam_data_dir