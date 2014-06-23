#!/usr/env python
# -*- coding: utf-8 -*-
import lbsociam
import unittest

class LBBaseTestCase(unittest.TestCase):
    """
    Test LB integration
    """

    def setUp(self):
        """
        Load test data
        """
        pass

    def test_communication(self):
        """
        Test communication to LB database
        """
        lbs = lbsociam.LBSociam()

    def tearDown(self):
        """
        Clear test data
        """
        pass
