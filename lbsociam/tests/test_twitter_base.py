#!/usr/env python
# -*- coding: utf-8 -*-
import lbsociam
import unittest
import datetime
from liblightbase import lbrest
from lbsociam.model import lbtwitter
from liblightbase.lbutils import conv
from liblightbase.lbbase.struct import Base
from lbsociam.model import lbstatus

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
        self.lbt = lbtwitter.Twitter(debug=False, term='crime')
        self.status_base = lbstatus.StatusBase()
        pass

    def test_status_insert(self):
        """
        Insert twitter status on Base
        """
        tw_status = self.lbt.search()
        tw_status_elm = [tw_status[0]]
        tw_status_json = self.lbt.status_to_json(tw_status_elm)

        lbbase = self.status_base.create_base()

        status = lbstatus.Status(
            origin='twitter',
            inclusion_date=datetime.datetime.now(),
            source=tw_status_json,
            status_base=self.status_base
        )

        retorno = status.create_status()
        self.assertEqual(retorno, 1)
        retorno = self.status_base.remove_base()
        self.assertTrue(retorno)

    def test_status_to_document(self):
        """
        Test Status conversion to LB Document
        """
        status = self.lbt.search()
        # Remove repeated elements
        status_elm = status[0]

        # Create Base
        #lbbase = conv.pyobject2base(status_elm)
        self.lbt.base = status_elm
        self.assertIsInstance(self.lbt.base, Base)

        TwitterStatus = self.lbt.base.metaclass()
        print(type(TwitterStatus))
        status_dict = self.lbt.status_to_dict(status)
        #print(status_dict[0])
        status_obj = conv.dict2document(self.lbt.base, status_dict[0])
        self.assertIsNotNone(status_obj)
        del self.lbt.base
        self.assertIsNone(self.lbt.base)

    def tearDown(self):
        """
        Clear test data
        """
        #self.status_base.remove_base()

        test_twitter_import.TwitterImportTestCase.tearDown(self)
        pass
