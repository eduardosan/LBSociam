#!/usr/env python
# -*- coding: utf-8 -*-
__author__ = 'eduardo'

from lbsociam import LBSociam
from googlemaps import client


class GMaps(LBSociam):
    """
    Google Maps
    """
    def __init__(self):
        """
        Start with APi parameters
        """
        LBSociam.__init__(self)
        self.client = client.Client(key=self.gmaps_api_key)