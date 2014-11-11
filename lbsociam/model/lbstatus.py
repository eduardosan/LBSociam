#!/usr/env python
# -*- coding: utf-8 -*-
__author__ = 'eduardo'
import datetime
import nlpnet
import logging
from requests.exceptions import HTTPError
from lbsociam import LBSociam
from liblightbase import lbrest
from liblightbase.lbutils import conv
from liblightbase.lbbase.struct import Base, BaseMetadata
from liblightbase.lbbase.lbstruct.group import *
from liblightbase.lbbase.lbstruct.field import *
from liblightbase.lbbase.content import Content

log = logging.getLogger()


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

        search_term = Field(**dict(
            name='search_term',
            alias='search_term',
            description='Term used on search',
            datatype='Text',
            indices=['Textual'],
            multivalued=False,
            required=True
        ))

        source = Field(**dict(
            name='source',
            alias='source',
            description='Original status source',
            datatype='Json',
            indices=['Textual', 'Unico'],
            multivalued=False,
            required=True
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
            name='arg_structures',
            alias='arg_structures',
            description='SRL arg structures',
            multivalued=True
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
            name='argument',
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
            name='status',
            description='Status from social networks',
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
        content_list.append(search_term)
        content_list.append(tokens)
        content_list.append(arg_structures)
        content_list.append(origin)
        content_list.append(source)

        lbbase = Base(
            metadata=base_metadata,
            content=content_list
        )

        return lbbase

    def metaclass(self, *args, **kwargs):
        """
        Retorna metaclass para essa base
        """
        return self.lbbase.metaclass(*args, **kwargs)

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

    def update_base(self):
        """
        Update base from LB Base
        """
        response = self.baserest.update(self.lbbase)
        if response.status_code == 200:
            return True
        else:
            raise IOError('Error updating LB Base structure')

status_base = StatusBase()
StatusClass = status_base.metaclass()


class Status(StatusClass):
    """
    Class to hold status elements
    """
    def __init__(self, **args):
        """
        Construct for social networks data
        :return:
        """
        super(Status, self).__init__(**args)

        # These have to be null
        self.tokens = list()
        self.arg_structures = list()

    @property
    def inclusion_date(self):
        """
        Inclusion date
        :return:
        """
        return StatusClass.inclusion_date.__get__(self)

    @inclusion_date.setter
    def inclusion_date(self, value):
        """
        Inclusion date setter
        """
        assert isinstance(value, datetime.datetime), "This should be datetime"
        StatusClass.inclusion_date.__set__(self, value.strftime("%d/%m/%Y"))

    @property
    def tokens(self):
        """
        :return: SRL tokenizer object
        """
        return StatusClass.tokens.__get__(self)

    @tokens.setter
    def tokens(self, value):
        """
        :return:
        """
        StatusClass.tokens.__set__(self, value)

    @property
    def arg_structures(self):
        """
        :return: SRL arg structures
        """
        return StatusClass.arg_structures.__get__(self)

    @arg_structures.setter
    def arg_structures(self, value):
        """
        Store arg structures on text
        :return:
        """
        StatusClass.arg_structures.__set__(self, value)

    @property
    def source(self):
        """
        Source property
        """
        return StatusClass.source.__get__(self)

    @source.setter
    def source(self, value):
        StatusClass.source.__set__(self, value)

    @property
    def text(self):
        """
        Text from Status
        """
        return StatusClass.text.__get__(self)

    @text.setter
    def text(self, value):
        """
        Text UTF8 conversion
        """
        StatusClass.text.__set__(self, value)

    def status_to_dict(self):
        """
        Convert status object to Python dict
        :return:
        """
        return conv.document2dict(status_base.lbbase, self)

    def status_to_json(self):
        """
        Convert object to json
        :return:
        """
        return conv.document2json(status_base.lbbase, self)

    def create_status(self):
        """
        Insert document on base
        :param unique: If it is unique, sent this option as true
        :return: Document creation status
        """
        document = self.status_to_json()
        try:
            result = status_base.documentrest.create(document)
        except HTTPError, err:
            log.error(err.strerror)
            return None

        return result

    def update(self, id_doc):
        #print(self.arg_structures)
        document = self.status_to_json()
        #print(document)
        return status_base.documentrest.update(id=id_doc, document=document)

    def srl_tokenize(self):
        """
        SRL tokenized attributes initialization
        """
        tagger = nlpnet.SRLTagger()
        sent = tagger.tag(self.text)

        arg_structures = []
        tokens = []
        ArgStructures = status_base.metaclass('arg_structures')
        for elm in sent:
            tokens = tokens + elm.tokens
            for predicate, argument in elm.arg_structures:
                argument_list = list()
                print(argument)
                for argument_name in argument.keys():
                    print(argument_list)
                    Argument = status_base.metaclass('argument')
                    argument_obj = Argument(
                        argument_name=argument_name,
                        argument_value=argument[argument_name]
                    )
                    argument_list.append(argument_obj)

                print(argument_list)
                arg_stuctures_obj = ArgStructures(
                    predicate=predicate,
                    argument=argument_list
                )
                arg_structures.append(arg_stuctures_obj)

        #print(arg_structures)
        self.tokens = tokens
        self.arg_structures = arg_structures