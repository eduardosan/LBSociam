#!/usr/env python
# -*- coding: utf-8 -*-
__author__ = 'eduardo'

import logging
import datetime
import requests
from requests.exceptions import HTTPError
from lbsociam import LBSociam
from liblightbase import lbrest
from liblightbase.lbbase.struct import Base, BaseMetadata
from liblightbase.lbbase.lbstruct.group import *
from liblightbase.lbbase.lbstruct.field import *
from liblightbase.lbbase.content import Content
from liblightbase.lbutils import conv
from liblightbase.lbsearch.search import *

log = logging.getLogger()


class CrimesBase(LBSociam):
    """
    Criminal data base
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
        category_name = Field(**dict(
            name='category_name',
            description='category name',
            alias='category_name',
            datatype='Text',
            indices=['Ordenado', 'Unico'],
            multivalued=False,
            required=True
        ))
        
        category_pretty_name = Field(**dict(
            name='category_pretty_name',
            description='category pretty name',
            alias='category_pretty_name',
            datatype='Text',
            indices=['Ordenado'],
            multivalued=False,
            required=True
        ))
        
        description = Field(**dict(
            name='description',
            description='category description',
            alias='description',
            datatype='Text',
            indices=[],
            multivalued=False,
            required=False
        ))
        
        tokens = Field(**dict(
            name='tokens',
            description='Identified tokens for this category',
            alias='tokens',
            datatype='Text',
            indices=['Ordenado'],
            multivalued=True,
            required=False
        ))
        
        total = Field(**dict(
            name='total',
            description='Total criminal events',
            alias='total',
            datatype='Integer',
            indices=['Ordenado'],
            multivalued=False,
            required=False
        ))

        date = Field(**dict(
            name='date',
            description='Taxonomy last update',
            alias='date',
            datatype='DateTime',
            indices=['Ordenado'],
            multivalued=False,
            required=True
        ))

        images = Field(**dict(
            name='images',
            description='Taxonomy related images',
            alias='images',
            datatype='File',
            indices=[],
            multivalued=True,
            required=False
        ))

        base_metadata = BaseMetadata(**dict(
            name='crime',
            description='Criminal data from social networks',
            password='123456',
            idx_exp=False,
            idx_exp_url='index_url',
            idx_exp_time=300,
            file_ext=True,
            file_ext_time=300,
            color='#FFFFFF'
        ))

        content_list = Content()
        content_list.append(total)
        content_list.append(category_name)
        content_list.append(category_pretty_name)
        content_list.append(description)
        content_list.append(tokens)
        content_list.append(date)
        content_list.append(images)

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

    def create_base(self):
        """
        Create a base to hold twitter information on Lightbase
        :param crimes: One twitter crimes object to be base model
        :return: LB Base object
        """
        lbbase = self.lbbase
        response = self.baserest.create(lbbase)
        #print(response.crimes_code)
        if response.status_code == 200:
            return lbbase
        else:
            return None

    def remove_base(self):
        """
        Remove base from Lightbase
        :param lbbase: LBBase object instance
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

    def list(self):
        """
        List all documents in base
        """
        orderby = OrderBy(['id_doc'])
        search = Search(
            limit=None,
            order_by=orderby
        )
        results = self.documentrest.get_collection(search)
        return results

    def get_document(self, id_doc):
        """
        Get document by ID on base
        """
        url = self.lbgenerator_rest_url + '/' + self.lbbase._metadata.name + '/doc/' + id_doc
        response = requests.get(
            url=url
        )
        #results = self.documentrest.get(id_doc)
        if response.status_code >= 300:
            return None

        return response.json()

crimes_base = CrimesBase()


class Crimes(crimes_base.metaclass):
    """
    Classe que armazena eventos de crime
    """
    def __init__(self, **args):
        """
        Construct for social networks data
        :return:
        """
        super(Crimes, self).__init__(**args)
        self.crimes_base = crimes_base

    @property
    def date(self):
        """
        Inclusion date
        :return:
        """
        return crimes_base.metaclass.date.__get__(self)

    @date.setter
    def date(self, value):
        """
        Inclusion date setter
        """
        if isinstance(value, datetime.datetime):
            value = value.strftime("%d/%m/%Y %H:%M:%S")
        elif value is None:
            value = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        else:
            # Try to format string
            value = datetime.datetime.strptime(value, "%d/%m/%Y %H:%M:%S").strftime("%d/%m/%Y %H:%M:%S")

        crimes_base.metaclass.date.__set__(self, value)

    def crimes_to_dict(self):
        """
        Convert crimes object to Python dict
        :return: dict for crime
        """
        return conv.document2dict(self.crimes_base.lbbase, self)

    def crimes_to_json(self):
        """
        Convert object to json
        :return: JSON for crime
        """
        return conv.document2json(self.crimes_base.lbbase, self)

    def create_crimes(self):
        """
        Insert document on base
        :return: Document creation crimes
        """
        document = self.crimes_to_json()
        try:
            result = self.crimes_base.documentrest.create(document)
        except HTTPError, err:
            log.error(err.strerror)
            return None

        return result

    def update(self, id_doc):
        """
        Update document
        :param id_doc: Document ID
        :return:
        """
        document = self.crimes_to_json()
        #print(document)
        return self.crimes_base.documentrest.update(id=id_doc, document=document)