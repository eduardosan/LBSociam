#!/usr/env python
# -*- coding: utf-8 -*-
__author__ = 'eduardo'

import unittest
import datetime
import json
import lbsociam
from liblightbase import lbrest
from liblightbase.lbutils import conv
from lbsociam.model import lbstatus, lbtwitter
from lbsociam.lib import srl, dictionary
from gensim import corpora
from gensim.models import ldamodel


class TestDictionary(unittest.TestCase):
    """
    Testa criação dos dicionários
    """

    def setUp(self):
        """
        Ajusta parâmetros iniciais
        """
        self.lbs = lbsociam.LBSociam()
        self.baserest = lbrest.BaseREST(rest_url=self.lbs.lbgenerator_rest_url, response_object=True)
        self.lbt = lbtwitter.Twitter(debug=False, term='crime')
        self.status_base = lbstatus.StatusBase()
        self.tw_status = self.lbt.search()

        # Cria base
        self.lbbase = self.status_base.create_base()

        # Insere dois status
        self.status = list()
        tw_status_elm = [self.tw_status[0]]
        tw_status_json = self.lbt.status_to_json(tw_status_elm)

        status_dict = dict(
            origin='twitter',
            inclusion_date=datetime.datetime.now().strftime("%d/%m/%Y"),
            text=tw_status_elm[0].text,
            source=tw_status_json,
            search_term='crime'
        )

        tokenized = srl.srl_tokenize(tw_status_elm[0].text)
        if tokenized.get('arg_structures'):
            status_dict['arg_structures'] = tokenized.get('arg_structures')
        if tokenized.get('tokens'):
            status_dict['tokens'] = tokenized.get('tokens')

        status = conv.dict2document(self.lbbase, status_dict)
        status_json = conv.document2json(self.lbbase, status)
        result = self.status_base.documentrest.create(status_json)
        self.status.append(status)

        # Segundo status
        tw_status_elm = [self.tw_status[1]]
        tw_status_json = self.lbt.status_to_json(tw_status_elm)

        status_dict = dict(
            origin='twitter',
            inclusion_date=datetime.datetime.now().strftime("%d/%m/%Y"),
            text=tw_status_elm[0].text,
            source=tw_status_json,
            search_term='crime'
        )

        tokenized = srl.srl_tokenize(tw_status_elm[0].text)
        if tokenized.get('arg_structures'):
            status_dict['arg_structures'] = tokenized.get('arg_structures')
        if tokenized.get('tokens'):
            status_dict['tokens'] = tokenized.get('tokens')

        status = conv.dict2document(self.lbbase, status_dict)
        status_json = conv.document2json(self.lbbase, status)
        result = self.status_base.documentrest.create(status_json)
        self.status.append(status)

    def test_dictionary_mapping(self):
        """
        Mapeia tokens extraídos em um dicionário do gensim
        """
        # Verifica se lista de documentos foi gerada com sucesso
        documents = dictionary.status_to_document(self.status)
        self.assertGreater(len(documents), 0)

        dic = dictionary.create_from_documents(documents)
        self.assertIsInstance(dic, corpora.Dictionary)

        # Cria corpus e modelo LDA
        corpus = [dic.doc2bow(text) for text in documents]
        #corpora.BleiCorpus.serialize('/tmp/corpus.lda-c', corpus)
        model = ldamodel.LdaModel(corpus, id2word=dic, num_topics=2)
        print(model.print_topics(num_topics=2))

    def tearDown(self):
        """
        Remove dados de teste
        """
        self.status_base.remove_base()