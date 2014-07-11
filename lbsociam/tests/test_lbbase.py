#!/usr/env python
# -*- coding: utf-8 -*-
import lbsociam
import unittest
import test_import
import liblightbase.lbrest

class LBBaseTestCase(test_import.ImportTestCase):
    """
    Test LB integration
    """

    def setUp(self):
        """
        Load test data
        """
        # Load previous tests data
        test_import.ImportTestCase.setUp(self)

        # Start loading this test data
        self.lbs = lbsociam.LBSociam()
        self.lbrest = liblightbase.lbrest.LBRest(rest_url=self.lbs.lbgenerator_rest_url)
        pass

    def test_communication(self):
        """
        Test communication to LB database
        """
        response = self.lbrest.send_request(method='get')
        assert response.status_code >= 200
        assert response.status_code < 300

    def tearDown(self):
        """
        Clear test data
        """

        # Remove data from previous tests
        test_import.ImportTestCase.tearDown(self)
        pass
