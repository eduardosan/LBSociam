#!/usr/env python
# -*- coding: utf-8 -*-
import os
from config import load_config


class LBSociam(object):
    """
    Classe global com as configurações
    """
    def __init__(self):
        """
        Parâmetro construtor
        """
        config = load_config()
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
        self.processes = config.get('lbsociam', 'processes')
        self.max_size = config.get('lbsociam', 'max_size')
        self.status_base = config.get('lbsociam', 'status_base')
        self.dictionary_base = config.get('lbsociam', 'dictionary_base')