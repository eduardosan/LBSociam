#!/usr/env python
# -*- coding: utf-8 -*-
import os
import unittest
import twitter
import json

from lbsociam.model import lbtwitter
from lbsociam import LBSociam

class TwitterImportTestCase(unittest.TestCase):
    """
    Test data import on twitter
    """
    def setUp(self):
        """
        Load test data
        """
        lbsociam = LBSociam()
        self.data_dir = os.path.join(lbsociam.lbsociam_data_dir, 'tests')
        os.mkdir(self.data_dir)
        pass

    def test_dir(self):
        """
        Create data dir for tests
        """
        assert os.path.exists(self.data_dir) == True

    def test_twitter_config(self):
        """
        Test loading twitter configuration
        """
        lbt = lbtwitter.Twitter(debug=True)
        api = lbt.api
        results = api.VerifyCredentials()
        assert isinstance(results, twitter.User)

    def test_twitter_hastag(self):
        """
        Test reading twitter hashtag
        """
        lbt = lbtwitter.Twitter(debug=True, term='#tvbrasilia')
        hashtag = lbt.hashtag
        assert isinstance(hashtag, twitter.Hashtag)

    def test_term_search(self):
        """
        Test twitter term search
        """
        lbt = lbtwitter.Twitter(debug=True, term='crime')
        status = lbt.search()
        assert len(status) > 0

    def test_json_results(self):
        """
        Test convert results to JSON format
        """
        lbt = lbtwitter.Twitter(debug=True, term='crime')
        status = lbt.search()
        json_status = lbt.status_to_json(status)
        fd = open('/tmp/status.json', 'w+')
        fd.write(json_status)
        fd.close()
        assert json.loads(json_status)

    def tearDown(self):
        """
        Remove test data
        """
        assert os.rmdir(self.data_dir) == None
