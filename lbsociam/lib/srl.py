#!/usr/env python
# -*- coding: utf-8 -*-
__author__ = 'eduardo'

import nlpnet
import logging
import nltk
import re
from . import dictionary

log = logging.getLogger()


def srl_tokenize(text):
    """
    SRL tokenize text
    :param text: Text to get tokens extracted
    :return: Dict in following format:
        {
            'tokens': tokens,
            'arg_structures': arg_structures
        }
    """
    text = text.lower()
    tagger = nlpnet.SRLTagger()
    sent = tagger.tag(text)

    arg_structures = []
    tokens = []
    for elm in sent:
        # Remove stopwords and punctuations
        for i in range(0, len(elm.tokens)):
            if dictionary.valid_word(elm.tokens[i]):
                tokens.append(elm.tokens[i])

        # Cria elementos de SRL
        for predicate, argument in elm.arg_structures:
            argument_list = list()
            #print(argument)
            for argument_name in argument.keys():
                #print(argument_list)
                argument_dict = dict(
                    argument_name=argument_name,
                    argument_value=argument[argument_name]
                )
                argument_list.append(argument_dict)

            arg_structures_dict = dict(
                predicate=predicate,
                argument=argument_list
            )
            arg_structures.append(arg_structures_dict)

    return {
        'tokens': tokens,
        'arg_structures': arg_structures
    }