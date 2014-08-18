#!/usr/env python
# -*- coding: utf-8 -*-
import lbsociam
import io
import json
import unittest
import datetime
from liblightbase import lbrest
from lbsociam.model import lbtwitter
from liblightbase.lbutils import conv
from liblightbase.lbbase.struct import Base
from lbsociam.model import lbstatus

from . import test_twitter_import
import nlpnet

class TwitterBaseTestCase(test_twitter_import.TwitterImportTestCase):
    """
    Test LB integration
    """

    def setUp(self):
        """
        Load test data
        """
        test_twitter_import.TwitterImportTestCase.setUp(self)

        self.lbs = lbsociam.LBSociam()
        self.baserest = lbrest.BaseREST(rest_url=self.lbs.lbgenerator_rest_url, response_object=True)
        self.lbt = lbtwitter.Twitter(debug=False, term='crime')
        self.status_base = lbstatus.StatusBase()
        self.tw_status = self.lbt.search()

        # Debug
        fd = open('/tmp/status_base.json', 'w+')
        fd.write(self.status_base.lbbase.json)
        fd.close()
        pass

    def test_status_insert(self):
        """
        Insert twitter status on Base
        """

        tw_status_elm = [self.tw_status[0]]
        tw_status_json = self.lbt.status_to_json(tw_status_elm)

        lbbase = self.status_base.create_base()

        status = lbstatus.Status(
            origin='twitter',
            inclusion_date=datetime.datetime.now(),
            text=tw_status_elm[0].text,
            source=tw_status_json,
            search_term='crime'
        )

        retorno = status.create_status()
        self.assertEqual(retorno, 1)
        retorno = self.status_base.remove_base()
        self.assertTrue(retorno)

    def test_status_to_document(self):
        """
        Test Status conversion to LB Document
        """
        tw_status_elm = [self.tw_status[0]]
        tw_status_json = self.lbt.status_to_json(tw_status_elm)

        lbbase = self.status_base.create_base()

        status = lbstatus.Status(
            origin='twitter',
            inclusion_date=datetime.datetime.now(),
            text=tw_status_elm[0].text,
            search_term='crime',
            source=tw_status_json
        )

        retorno = status.create_status()
        self.assertEqual(retorno, 1)

        TwitterStatus = self.status_base.lbbase.metaclass()
        #print(type(TwitterStatus))
        status_dict = status.status_to_dict()
        #print(status_dict[0])
        status_obj = conv.dict2document(self.status_base.lbbase, status_dict)
        #self.assertIsInstance(status_obj, TwitterStatus)
        self.assertIsNotNone(status_obj)

        retorno = self.status_base.remove_base()
        self.assertTrue(retorno)

    def test_status_tokenizer(self):
        """
        Test Tokenizer tweet
        """
        tagger = nlpnet.SRLTagger()
        tw_status_elm = self.tw_status[0]
        sent = tagger.tag(tw_status_elm.text)
        print(sent[0].tokens)
        print(sent[0].arg_structures)
        self.assertIsInstance(sent[0], nlpnet.taggers.SRLAnnotatedSentence)
        self.assertGreaterEqual(len(sent[0].tokens), 0)
        self.assertGreaterEqual(len(sent[0].arg_structures), 0)

    def test_tokenizer_attributes(self):
        """
        Test tokenized attributes store on Status Object
        """
        tw_status_elm = [self.tw_status[1]]
        tw_status_json = self.lbt.status_to_json(tw_status_elm)

        lbbase = self.status_base.create_base()

        status = lbstatus.Status(
            origin='twitter',
            inclusion_date=datetime.datetime.now(),
            text=tw_status_elm[0].text,
            search_term='crime',
            source=tw_status_json
        )

        retorno = status.create_status()
        self.assertIsInstance(retorno, int)

        # Initialize SRL tokenize
        status.srl_tokenize()

        self.assertGreaterEqual(len(status.tokens), 0)
        self.assertGreaterEqual(len(status.arg_structures), 0)

        # Debug status JSON
        with io.open('/tmp/status_converted.json', 'w+', encoding='utf8') as json_file:
            json_file.write(status.status_to_json())
            json_file.close()

        retorno = self.status_base.remove_base()
        self.assertTrue(retorno)

    def test_repeated_document(self):
        """
        Test repeated document insertion
        """
        tw_status_elm = [self.tw_status[1]]
        tw_status_json = self.lbt.status_to_json(tw_status_elm)

        lbbase = self.status_base.create_base()

        status = lbstatus.Status(
            origin='twitter',
            inclusion_date=datetime.datetime.now(),
            text=tw_status_elm[0].text,
            search_term='crime',
            source=tw_status_json
        )

        retorno = status.create_status()
        self.assertIsInstance(retorno, int)

        # Try to insert again already existent document
        retorno = status.create_status()
        self.assertIsNone(retorno)

        # Try to insert a different document
        tw_status_elm = [self.tw_status[2]]
        tw_status_json = self.lbt.status_to_json(tw_status_elm)

        status = lbstatus.Status(
            origin='twitter',
            inclusion_date=datetime.datetime.now(),
            text=tw_status_elm[0].text,
            search_term='crime',
            source=tw_status_json
        )
        retorno = status.create_status()
        self.assertIsInstance(retorno, int)

        retorno = self.status_base.remove_base()
        self.assertTrue(retorno)

    def tearDown(self):
        """
        Clear test data
        """
        #self.status_base.remove_base()

        test_twitter_import.TwitterImportTestCase.tearDown(self)
        pass
