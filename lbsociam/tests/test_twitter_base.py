#!/usr/env python
# -*- coding: utf-8 -*-
import lbsociam
import unittest
from liblightbase import lbrest
from lbsociam.model import lbtwitter
from liblightbase.lbutils import conv
from liblightbase.lbbase.struct import Base

from . import test_twitter_import

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
        self.lbt = lbtwitter.Twitter(debug=True, term='crime')
        pass

    def test_communication(self):
        """
        Test communication to LB database
        """
        response = self.baserest.search()
        assert response.status_code == 200

    def test_generate_base(self):
        """
        Auto generate LBBase from status object
        """
        status = self.lbt.search()
        lbbase = conv.pyobject2base(status[0])
        fd = open('/tmp/status_base.json', 'w+')
        fd.write(lbbase.json)
        fd.close()
        self.assertIsInstance(lbbase, Base)

    def test_base_to_json(self):
        """
        Test auto generated base json conversion back to base
        """
        status = self.lbt.search()
        lbbase = conv.pyobject2base(status[0])
        j = lbbase.json
        b = conv.json2base(j)
        self.assertIsInstance(b, Base)

    def test_status_to_document(self):
        """
        Test Status conversion to LB Document
        """
        status = self.lbt.search()
        lbbase = conv.pyobject2base(status[0])
        TwitterStatus = lbbase.metaclass()
        status_json = self.lbt.statusToJSON(status)
        status_obj = conv.json2document(lbbase, status_json[0])
        self.assertIsInstance(status_obj, TwitterStatus)

    def tearDown(self):
        """
        Clear test data
        """
        test_twitter_import.TwitterImportTestCase.tearDown(self)
        pass
