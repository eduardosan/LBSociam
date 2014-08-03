#!/usr/env python
# -*- coding: utf-8 -*-
import lbsociam
import unittest
from liblightbase import lbrest

class LBBaseTestCase(unittest.TestCase):
    """
    Test LB integration
    """

    def setUp(self):
        """
        Load test data
        """
        self.lbs = lbsociam.LBSociam()
        self.baserest = lbrest.BaseREST(rest_url=self.lbs.lbgenerator_rest_url)
        pass

    def test_communication(self):
        """
        Test communication to LB database
        """
        response = self.baserest.search()
        assert response.status_code == 200

    def test_create_base(self):
        """
        Create base in Lightbase to hold twitter status
        """

    def tearDown(self):
        """
        Clear test data
        """
        pass
