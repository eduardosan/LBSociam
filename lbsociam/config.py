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

    return config