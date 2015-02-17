#!/usr/env python
# -*- coding: utf-8 -*-
__author__ = 'eduardo'
import datetime
import json
import logging
from liblightbase import lbrest
from lbsociam.model import location, lbstatus
from liblightbase.lbutils import conv
from liblightbase.lbbase.struct import Base
from .test_twitter_base import TwitterBaseTestCase
from lbsociam.commands import twitter_commands
from lbsociam.lib import location as liblocation

log = logging.getLogger()


class StatusBaseTestCase(TwitterBaseTestCase):
    """
    Test Status base creation
    """

    def setUp(self):
        """
        Load test data
        :return:
        """
        # Load setup from previous
        TwitterBaseTestCase.setUp(self)

        # Load data to perform searches
        self.command = command
        pass

    def test_create_base(self):
        """
        Test create base on Lightbase
        :return:
        """
        location_base = location.LocationBase()
        location_lbbase = location_base.create_base()
        self.assertIsInstance(location_lbbase, Base)
        result = location_base.remove_base()
        self.assertTrue(result)

    def test_store_location(self):
        """
        Test location base storage
        """
        # Load data
        self.lbt.search(count=10)

        status_id_list = self.status_base.get_document_ids()
        log.debug("Number of status found: %s", len(status_id_list))
        status = self.status_base.get_document(status_id_list[0])

        status_dict = conv.document2dict(self.status_base.lbbase, status)
        # Manually add id_doc
        status_dict['_metadata'] = dict()
        status_dict['_metadata']['id_doc'] = status._metadata.id_doc
        # Now try to find location
        status_dict = liblocation.get_location(status_dict)

        # Update base
        self.assertIsNotNone(
            self.status_base.documentrest.update(
                status_dict['_metadata']['id_doc'],
                json.dumps(status_dict)
            )
        )

    def tearDown(self):
        """
        Remove test data
        :return:
        """
        TwitterBaseTestCase.tearDown(self)
        pass