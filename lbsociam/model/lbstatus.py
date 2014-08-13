#!/usr/env python
# -*- coding: utf-8 -*-
__author__ = 'eduardo'
import datetime
import json
import nlpnet
from lbsociam import LBSociam
from liblightbase import lbrest
from liblightbase.lbutils import conv
from liblightbase.lbbase.struct import Base, BaseMetadata
from liblightbase.lbbase.lbstruct.group import *
from liblightbase.lbbase.lbstruct.field import *
from liblightbase.lbbase.content import Content
from liblightbase.lbutils.const import PYSTR

class StatusBase(LBSociam):
    """
    Base class to social networks status
    """
    def __init__(self):
        """
        Construct for social networks data
        :return:
        """
        LBSociam.__init__(self)
        self.baserest = lbrest.BaseREST(rest_url=self.lbgenerator_rest_url, response_object=True)

    def create_base(self):
        """
        Create a base to hold twitter information on Lightbase
        :param status: One twitter status object to be base model
        :return: LB Base object
        """
        lbbase = self.lbbase
        response = self.baserest.create(lbbase)
        #print(response.status_code)
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

    @property
    def lbbase(self):
        """
        Generate LB Base object
        :return:
        """
        inclusion_date = Field(**dict(
            name='inclusion_date',
            description='Attribute inclusion date',
            alias='inclusion_date',
            datatype='Date',
            indices=['Ordenado'],
            multivalued=False,
            required=True
        ))

        origin = Field(**dict(
            name='origin',
            alias='origin',
            description='Where this status came from',
            datatype='Text',
            indices=['Textual'],
            multivalued=False,
            required=True
        ))

        source = Field(**dict(
            name='source',
            alias='source',
            description = 'Original status source',
            datatype = 'Json',
            indices = ['Textual'],
            multivalued = False,
            required = True
        ))

        text = Field(**dict(
            name='text',
            alias='text',
            description='Status original text',
            datatype='Text',
            indices=['Textual'],
            multivalued=False,
            required=True
        ))


        base_metadata = BaseMetadata(**dict(
            name = 'status',
            description = 'Status from social networks',
            password='123456',
            idx_exp=False,
            idx_exp_url='index_url',
            idx_exp_time=300,
            file_ext=True,
            file_ext_time=300,
            color='#FFFFFF'
        ))

        content_list = Content()
        content_list.append(inclusion_date)
        content_list.append(text)
        content_list.append(origin)
        content_list.append(source)

        lbbase = Base(
            metadata=base_metadata,
            content=content_list
        )

        return lbbase

class Status(LBSociam):
    """
    Class to hold status elements
    """
    def __init__(self, inclusion_date, source, origin, status_base, text):
        """
        Construct for social networks data
        :return:
        """
        LBSociam.__init__(self)
        self.inclusion_date = inclusion_date
        self.source = source
        self.origin = origin
        self.text = text
        self.status_base = status_base
        self.documentrest = lbrest.DocumentREST(
            rest_url=self.lbgenerator_rest_url,
            base=self.status_base.lbbase,
            response_object=False
        )

    @property
    def inclusion_date(self):
        """
        Inclusion date
        :return:
        """
        return self._inclusion_date

    @inclusion_date.setter
    def inclusion_date(self, value):
        """
        Inclusion date setter
        """
        assert isinstance(value, datetime.datetime), "This should be datetime"
        self._inclusion_date = value

    @property
    def inclusion_date_str(self):
        """
        :return: Property in standard format
        """

    @inclusion_date_str.getter
    def inclusion_date_str(self):
        """
        :return:
        """
        return self.inclusion_date.strftime("%d/%m/%Y")

    @property
    def status_base(self):
        """
        Status base
        """
        return self._status_base

    @status_base.setter
    def status_base(self, value):
        """
        It has to be an instance of StatusBase object
        """
        assert isinstance(value, StatusBase), "It has be an instance of StatusBase"
        self._status_base = value

    @property
    def lbstatus(self):
        """
        Get LB Status object
        :return: LB Metaclass for status
        """
        lbstatus = conv.dict2document(self.status_base.lbbase, self.status_to_dict())
        return lbstatus

    def status_to_dict(self):
        """
        Convert status object to Python dict
        :return:
        """
        saida = {
            'inclusion_date': self.inclusion_date_str,
            'text': self.text,
            'source': self.source,
            'origin': self.origin,
            'tokens': self.tokens,
            'arg_structures': self.arg_structures
        }

        return saida

    def status_to_json(self):
        """
        Convert object to json
        :return:
        """
        saida = self.status_to_dict()
        saida['inclusion_date'] = self.inclusion_date_str
        return json.dumps(saida)

    def create_status(self):
        """
        Insert document on base
        :param document:
        :return:
        """
        document = self.status_to_json()
        return self.documentrest.create(document)

    @property
    def tokens(self):
        """
        :return: SRL tokenizer object
        """
        return self._tokens

    @property
    def arg_structures(self):
        """
        :return: SRL arg structures
        """
        return self._arg_structures

    def srl_tokenize(self):
        """
        SRL tokenized attributes initialization
        """
        tagger = nlpnet.SRLTagger()
        sent = tagger.tag(self.text)
        self._tokens = sent[0].tokens
        self._arg_structures = sent[0].arg_structures