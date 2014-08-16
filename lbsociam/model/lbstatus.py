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
            required=False
        ))

        tokens = Field(**dict(
            name='tokens',
            alias='tokens',
            description='Tokens extracted from Semantic Role Labeling',
            datatype='Text',
            indices=['Textual'],
            multivalued=True,
            required=False
        ))

        arg_content_list = Content()

        arg_metadata = GroupMetadata(**dict(
            name = 'arg_structures',
            alias='arg_structures',
            description ='SRL arg structures',
            multivalued =True
        ))

        predicate = Field(**dict(
            name='predicate',
            alias='predicate',
            description='Predicate for term in SRL',
            datatype='Text',
            indices=['Textual'],
            multivalued=False,
            required=False
        ))

        arg_content_list.append(predicate)

        argument_metadata = GroupMetadata(**dict(
            name = 'argument',
            alias='argument',
            description='Argument for term in SRL',
            multivalued=True
        ))

        argument_list = Content()

        argument_name = Field(**dict(
            name='argument_name',
            alias='argument_name',
            description='Argument identification',
            datatype='Text',
            indices=['Textual'],
            multivalued=False,
            required=False
        ))

        argument_list.append(argument_name)

        argument_value = Field(**dict(
            name='argument_value',
            alias='argument_value',
            description='Argument Value for SRL',
            datatype='Text',
            indices=['Textual'],
            multivalued=True,
            required=False
        ))

        argument_list.append(argument_value)

        argument = Group(
            metadata=argument_metadata,
            content=argument_list
        )

        arg_content_list.append(argument)

        arg_structures = Group(
            metadata=arg_metadata,
            content=arg_content_list
        )


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
        content_list.append(tokens)
        content_list.append(arg_structures)
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

        # These attributes have to be empty
        self.tokens = list()
        self.arg_structures = dict()

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

    @property
    def tokens(self):
        """
        :return: SRL tokenizer object
        """
        return self._tokens

    @tokens.setter
    def tokens(self, value):
        """
        :return:
        """
        self._tokens = value

    @property
    def arg_structures(self):
        """
        :return: SRL arg structures
        """
        return self._arg_structures

    @arg_structures.setter
    def arg_structures(self, value):
        """
        Store arg structures on text
        :return:
        """
        saida = []
        for predicate, argument in value:
            argument_list = list()
            #print(argument)
            for argument_name in argument.keys():
                argument_dict = dict()
                argument_dict['argument_name'] = argument_name
                argument_dict['value'] = argument[argument_name]
                argument_list.append(argument_dict)

            saida.append({
                'predicate': predicate,
                'argument': argument_list
            })

        self._arg_structures = saida


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


    def srl_tokenize(self):
        """
        SRL tokenized attributes initialization
        """
        tagger = nlpnet.SRLTagger()
        sent = tagger.tag(self.text)
        self.tokens = sent[0].tokens
        print(sent[0].__dict__)
        self.arg_structures = sent[0].arg_structures