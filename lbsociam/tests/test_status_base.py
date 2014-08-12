#!/usr/env python
# -*- coding: utf-8 -*-
__author__ = 'eduardo'
import lbsociam
import unittest
import datetime
from liblightbase import lbrest
from lbsociam.model import lbstatus
from liblightbase.lbutils import conv
from liblightbase.lbbase.struct import Base

class StatusBaseTestCase(unittest.TestCase):
    """
    Test Status base creation
    """

    def setUp(self):
        """
        Load test data
        :return:
        """
        self.lbs = lbsociam.LBSociam()
        self.baserest = lbrest.BaseREST(rest_url=self.lbs.lbgenerator_rest_url, response_object=True)
        pass

    def test_communication(self):
        """
        Test communication to LB database
        """
        response = self.baserest.search()
        assert response.status_code == 200

    def test_generate_base(self):
        """
        Test creating LB Base from object
        :return:
        """
        status_base = lbstatus.StatusBase()

        lbbase = status_base.lbbase()
        fd = open('/tmp/status_base.json', 'w+')
        fd.write(lbbase.json)
        fd.close()
        self.assertIsInstance(lbbase, Base)
        j = lbbase.json
        b = conv.json2base(j)
        self.assertIsInstance(b, Base)

    def test_create_base(self):
        """
        Test create base on Lightbase
        :return:
        """
        status_base = lbstatus.StatusBase()
        status_lbbase = status_base.create_base()
        self.assertIsInstance(status_lbbase, Base)
        result = status_base.remove_base()
        self.assertTrue(result)

    def tearDown(self):
        """
        Remove test data
        :return:
        """
        pass