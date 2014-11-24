#!/usr/env python
# -*- coding: utf-8 -*-
__author__ = 'eduardo'

import logging
import datetime
from requests.exceptions import HTTPError
from lbsociam import LBSociam
from liblightbase import lbrest
from liblightbase.lbbase.struct import Base, BaseMetadata
from liblightbase.lbbase.lbstruct.group import *
from liblightbase.lbbase.lbstruct.field import *
from liblightbase.lbbase.content import Content
from liblightbase.lbutils import conv

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
        total = Field(**dict(
            name='total',
            description='Total criminal events',
            alias='total',
            datatype='Integer',
            indices=['Ordenado'],
            multivalued=False,
            required=False
        ))

        homicide_list = Content()

        homicide_metadata = GroupMetadata(**dict(
            name='homicide',
            alias='homicide',
            description='Homicide crimes',
            multivalued=False
        ))

        homicide_tokens = Field(**dict(
            name='homicide_tokens',
            alias='homicide_tokens',
            description='Selected search tokens for homicides',
            datatype='Text',
            indices=['Textual'],
            multivalued=True,
            required=False
        ))

        homicide_list.append(homicide_tokens)

        homicide = Group(
            metadata=homicide_metadata,
            content=homicide_list
        )

        theft_list = Content()

        theft_metadata = GroupMetadata(**dict(
            name='theft',
            alias='theft',
            description='Larceny/Theft Offenses',
            multivalued=False
        ))

        theft_tokens = Field(**dict(
            name='theft_tokens',
            alias='theft_tokens',
            description='Selected search tokens for larceny/theft',
            datatype='Text',
            indices=['Textual'],
            multivalued=True,
            required=False
        ))

        theft_list.append(theft_tokens)

        theft = Group(
            metadata=theft_metadata,
            content=theft_list
        )

        robbery_list = Content()

        robbery_metadata = GroupMetadata(**dict(
            name='robbery',
            alias='robbery',
            description='Robbery crimes',
            multivalued=False
        ))

        robbery_tokens = Field(**dict(
            name='robbery_tokens',
            alias='robbery_tokens',
            description='Selected search tokens for robbery',
            datatype='Text',
            indices=['Textual'],
            multivalued=True,
            required=False
        ))

        robbery_list.append(robbery_tokens)

        robbery = Group(
            metadata=robbery_metadata,
            content=robbery_list
        )

        drugs_list = Content()

        drugs_metadata = GroupMetadata(**dict(
            name='drugs',
            alias='drugs',
            description='Drug traffic crimes',
            multivalued=False
        ))

        drugs_tokens = Field(**dict(
            name='drugs_tokens',
            alias='drugs_tokens',
            description='Selected search tokens for drugs',
            datatype='Text',
            indices=['Textual'],
            multivalued=True,
            required=False
        ))

        drugs_list.append(drugs_tokens)

        drugs = Group(
            metadata=drugs_metadata,
            content=drugs_list
        )

        gunfire_list = Content()

        gunfire_metadata = GroupMetadata(**dict(
            name='gunfire',
            alias='gunfire',
            description='Gunfire possession',
            multivalued=False
        ))

        gunfire_tokens = Field(**dict(
            name='gunfire_tokens',
            alias='gunfire_tokens',
            description='Selected search tokens for gunfire possession',
            datatype='Text',
            indices=['Textual'],
            multivalued=True,
            required=False
        ))

        gunfire_list.append(gunfire_tokens)

        gunfire = Group(
            metadata=gunfire_metadata,
            content=gunfire_list
        )

        assault_list = Content()

        assault_metadata = GroupMetadata(**dict(
            name='assault',
            alias='assault',
            description='Sssault crimes',
            multivalued=False
        ))

        assault_tokens = Field(**dict(
            name='assault_tokens',
            alias='assault_tokens',
            description='Selected search tokens for assault',
            datatype='Text',
            indices=['Textual'],
            multivalued=True,
            required=False
        ))

        assault_list.append(assault_tokens)

        assault = Group(
            metadata=assault_metadata,
            content=assault_list
        )

        others_list = Content()

        others_metadata = GroupMetadata(**dict(
            name='others',
            alias='others',
            description='Other crimes',
            multivalued=False
        ))

        others_tokens = Field(**dict(
            name='others_tokens',
            alias='others_tokens',
            description='Selected search tokens for others',
            datatype='Text',
            indices=['Textual'],
            multivalued=True,
            required=False
        ))

        others_list.append(others_tokens)

        others = Group(
            metadata=others_metadata,
            content=others_list
        )

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
        content_list.append(homicide)
        content_list.append(theft)
        content_list.append(robbery)
        content_list.append(drugs)
        content_list.append(gunfire)
        content_list.append(assault)
        content_list.append(others)

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
        if response.crimes_code == 200:
            return True
        else:
            raise IOError('Error updating LB Base structure')

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
            value = value.strftime("%d/%m/%Y")
        elif value is None:
            value = datetime.datetime.now().strftime("%d/%m/%Y")

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
            result = self.documentrest.create(document)
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
        return self.documentrest.update(id=id_doc, document=document)