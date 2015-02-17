#!/usr/env python
# -*- coding: utf-8 -*-
__author__ = 'eduardo'

import logging
import requests
from lbsociam import LBSociam
from liblightbase import lbrest
from liblightbase.lbbase.struct import Base, BaseMetadata
# from liblightbase.lbbase.lbstruct.group import *
from liblightbase.lbbase.lbstruct.field import *
from liblightbase.lbbase.content import Content
from liblightbase.lbsearch.search import *

log = logging.getLogger()


class LocationBase(LBSociam):
    """
    Location cache search base
    """
    def __init__(self):
        """
        Construct for social networks data
        :return:
        """
        LBSociam.__init__(self)
        self.baserest = lbrest.BaseREST(
            rest_url=self.lbgenerator_rest_url,
            response_object=True
        )
        self.documentrest = lbrest.DocumentREST(
            rest_url=self.lbgenerator_rest_url,
            base=self.lbbase,
            response_object=False
        )

    @property
    def lbbase(self):
        """
        Generate LB Base object
        :return:
        """
        location_name = Field(**dict(
            name='location_name',
            description='Location name',
            alias='Location name',
            datatype='Text',
            indices=['Textual'],
            multivalued=False,
            required=True
        ))

        latitude = Field(**dict(
            name='latitude',
            description='Latitude',
            alias='Latitude',
            datatype='Decimal',
            indices=[],
            multivalued=False,
            required=True
        ))

        longitude = Field(**dict(
            name='longitude',
            description='Longitude',
            alias='longitude',
            datatype='Decimal',
            indices=[],
            multivalued=False,
            required=True
        ))

        location_type = Field(**dict(
            name='location_type',
            description='Location type',
            alias='Location type',
            datatype='Text',
            indices=['Textual'],
            multivalued=False,
            required=True
        ))

        base_metadata = BaseMetadata(**dict(
            name='location',
            description='Status location'
        ))

        content_list = Content()
        content_list.append(location_name)
        content_list.append(latitude)
        content_list.append(longitude)
        content_list.append(location_type)

        lbbase = Base(
            metadata=base_metadata,
            content=content_list
        )

        return lbbase

    @property
    def metaclass(self):
        """
        Retorna metaclass para essa base
        """
        return self.lbbase.metaclass()

    @property
    def arg_structures(self):
        """
        Metaclass para o grupo
        """
        return self.lbbase.metaclass('arg_structures')

    @property
    def argument(self):
        """
        Metaclass para o grupo
        """
        return self.lbbase.metaclass('argument')

    def create_base(self):
        """
        Create a base to hold twitter information on Lightbase
        :return: LB Base object
        """
        lbbase = self.lbbase
        response = self.baserest.create(lbbase)
        # print(response.status_code)
        if response.status_code == 200:
            return lbbase
        else:
            return None

    def remove_base(self):
        """
        Remove base from Lightbase
        :return: True or Error if base was not excluded
        """
        response = self.baserest.delete(self.lbbase)
        if response.status_code == 200:
            return True
        else:
            raise IOError('Error excluding base from LB')

    def update_base(self):
        """
        Update base from LB Base
        """
        response = self.baserest.update(self.lbbase)
        if response.status_code == 200:
            return True
        else:
            raise IOError('Error updating LB Base structure')

    def get_base(self):
        """
        Get base
        :return: Base JSON object
        """
        url = self.lbgenerator_rest_url + '/' + self.lbbase.metadata.name + '/doc'
        response = requests.get(
            url=url
        )

        if response.status_code == 200:
            return response.json()
        else:
            raise IOError('Error getting LB Base structure')

    def get_document_ids(self, offset=0):
        """
        Build a lis with all document ID's
        """
        orderby = OrderBy(asc=['id_doc'])
        select = ['id_doc']
        search = Search(
            select=select,
            limit=None,
            order_by=orderby,
            offset=offset
        )
        url = self.documentrest.rest_url
        url += "/" + self.lbbase._metadata.name + "/doc"
        params = {
            '$$': search._asjson()
        }

        # Envia requisição para o REST
        response = requests.get(url, params=params)
        collection = response.json()
        saida = list()

        # Cria uma lista de resultados como ID
        if collection.get('results') is None:
            return None

        for results in collection['results']:
            saida.append(results['_metadata']['id_doc'])

        return saida

    def get_document(self, id_doc):
        """
        Return document data
        """
        return self.documentrest.get(id_doc)

    def get_location(self, name):
        """
        Find location in base
        :param name: Location to search
        :return: Search result as dict
        """
        orderby = OrderBy(asc=['id_doc'])
        select = ['*']
        search = Search(
            select=select,
            limit=1,
            order_by=orderby,
            offset=0,
            literal="document->'location'->>'city' = '" + name + "'",
        )
        url = self.documentrest.rest_url
        url += "/" + self.lbbase._metadata.name + "/doc"
        vars = {
            '$$': search._asjson()
        }

        # Envia requisição para o REST
        response = requests.get(url, params=vars)
        collection = response.json()

        # Retorna resultado
        if collection.get('results') is None:
            saida = None
        else:
            saida = collection['results'][0]

        return saida