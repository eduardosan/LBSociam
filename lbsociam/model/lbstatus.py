#!/usr/env python
# -*- coding: utf-8 -*-
__author__ = 'eduardo'
import datetime
import logging
import requests
from requests.exceptions import HTTPError
from lbsociam import LBSociam
from liblightbase import lbrest
from liblightbase.lbutils import conv
from liblightbase.lbbase.struct import Base, BaseMetadata
from liblightbase.lbbase.lbstruct.group import *
from liblightbase.lbbase.lbstruct.field import *
from liblightbase.lbbase.content import Content
from liblightbase.lbsearch.search import *

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

    def __iter__(self):
        """
        When a dictionary loop is requested make one request at a time
        :return: JSON with dictionary data
        """
        id_list = self.get_document_ids()
        for id_doc in id_list:
            yield self.get_document(id_doc)

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
            required=False
        ))

        inclusion_datetime = Field(**dict(
            name='inclusion_datetime',
            description='Attribute inclusion date',
            alias='inclusion_datetime',
            datatype='DateTime',
            indices=['Ordenado'],
            multivalued=False,
            required=False
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

        events_tokens = Field(**dict(
            name='events_tokens',
            alias='events_tokens',
            description='Identified Events tokens',
            datatype='Text',
            indices=['Textual'],
            multivalued=True,
            required=False
        ))

        selected_category = Field(**dict(
            name='selected_category',
            alias='selected_category',
            description='Manually selected category',
            datatype='Text',
            indices=['Textual'],
            multivalued=False,
            required=False
        ))

        positives = Field(**dict(
            name='positives',
            alias='positives',
            description='Positive crime identification',
            datatype='Integer',
            indices=['Ordenado'],
            multivalued=False,
            required=False
        ))

        negatives = Field(**dict(
            name='negatives',
            alias='negatives',
            description='False positive on crime identification',
            datatype='Integer',
            indices=['Ordenado'],
            multivalued=False,
            required=False
        ))

        location_list = Content()

        id_location = Field(**dict(
            name='id_location',
            alias='ID Location',
            description='Location Identification',
            datatype='Text',
            indices=[],
            multivalued=False,
            required=False
        ))

        location_list.append(id_location)

        latitude = Field(**dict(
            name='latitude',
            alias='Latitude',
            description='Latitude',
            datatype='Decimal',
            indices=[],
            multivalued=False,
            required=False
        ))

        location_list.append(latitude)

        longitude = Field(**dict(
            name='longitude',
            alias='Longitude',
            description='Longitude',
            datatype='Decimal',
            indices=[],
            multivalued=False,
            required=False
        ))

        location_list.append(longitude)

        city = Field(**dict(
            name='city',
            alias='City',
            description='City identified',
            datatype='Text',
            indices=[],
            multivalued=False,
            required=False
        ))

        location_list.append(city)

        loc_origin = Field(**dict(
            name='loc_origin',
            alias='Location Origin',
            description='Origin from location identificaton',
            datatype='Text',
            indices=[],
            multivalued=False,
            required=False
        ))

        location_list.append(loc_origin)

        location_metadata = GroupMetadata(**dict(
            name='location',
            alias='location',
            description='Status origin',
            multivalued=False
        ))

        location = Group(
            metadata=location_metadata,
            content=location_list
        )

        base_metadata = BaseMetadata(**dict(
            name=self.status_base,
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
        content_list.append(inclusion_datetime)
        content_list.append(text)
        content_list.append(search_term)
        content_list.append(tokens)
        content_list.append(arg_structures)
        content_list.append(origin)
        content_list.append(source)
        content_list.append(events_tokens)
        content_list.append(selected_category)
        content_list.append(positives)
        content_list.append(negatives)
        content_list.append(location)

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
        vars = {
            '$$': search._asjson()
        }

        # Envia requisição para o REST
        response = requests.get(url, params=vars)
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

    def search_by_token(self, token, limit=10):
        """
        Search status by content
        """
        orderby = OrderBy(['tokens'])
        search = Search(
            limit=limit,
            order_by=orderby,
            literal="document->>'tokens' = '" + token + "'",
        )
        params = {
            '$$': search._asjson()
        }

        url = self.lbgenerator_rest_url + '/' + self.lbbase.metadata.name + '/doc'
        result = requests.get(
            url=url,
            params=params
        )
        results = result.json()
        response = results

        return response

    def get_events_tokens(self):
        """
        Get events corpus
        :return: Events corpus
        """
        orderby = OrderBy(asc=['id_doc'])
        select = ['events_tokens']
        search = Search(
            select=select,
            limit=None,
            order_by=orderby,
            offset=0
        )
        url = self.documentrest.rest_url
        url += "/" + self.lbbase._metadata.name + "/doc"
        vars = {
            '$$': search._asjson()
        }

        # Envia requisição para o REST
        response = requests.get(url, params=vars)
        collection = response.json()
        saida = list()

        # Cria uma lista de resultados como ID
        if collection.get('results') is None:
            return None

        for results in collection['results']:
            if results is not None:
                saida.append(results['events_tokens'])

        return saida

    def get_text(self):
        """
        Get events corpus
        :return: Events corpus
        """
        orderby = OrderBy(asc=['id_doc'])
        select = ['text']
        search = Search(
            select=select,
            limit=None,
            order_by=orderby,
            offset=0
        )
        url = self.documentrest.rest_url
        url += "/" + self.lbbase._metadata.name + "/doc"
        vars = {
            '$$': search._asjson()
        }

        # Envia requisição para o REST
        response = requests.get(url, params=vars)
        collection = response.json()
        saida = list()

        # Cria uma lista de resultados como ID
        if collection.get('results') is None:
            return None

        for results in collection['results']:
            if results is not None:
                saida.append(results['text'])

        return saida

    def get_status(self, offset=0, limit=100, literal=''):
        """
        Build a lis with all document ID's
        """
        orderby = OrderBy(asc=['id_doc'])
        search = Search(
            limit=limit,
            order_by=orderby,
            offset=offset,
            literal=literal
        )
        url = self.documentrest.rest_url
        url += "/" + self.lbbase._metadata.name + "/doc"
        vars = {
            '$$': search._asjson()
        }

        # Envia requisição para o REST
        response = requests.get(url, params=vars)
        collection = response.json()

        return collection

    def get_locations(self):
        """
        Get all status with locations
        """
        orderby = OrderBy(asc=['positives'])
        select = [
            "id_doc",
            "location",
            "positives",
            "negatives",
            "source",
            "inclusion_datetime",
            "text",
            "origin"
        ]

        search = Search(
            select=select,
            limit=None,
            order_by=orderby,
            offset=0
        )
        url = self.documentrest.rest_url
        url += "/" + self.lbbase._metadata.name + "/doc"
        vars = {
            '$$': search._asjson()
        }

        # Envia requisição para o REST
        response = requests.get(url, params=vars)
        collection = response.json()

        return collection

status_base = StatusBase()
StatusClass = status_base.metaclass
ArgStructures = status_base.arg_structures
Argument = status_base.argument


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
        #self.tokens = list()
        #self.arg_structures = list()
        self.status_base = status_base

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
        if isinstance(value, datetime.datetime):
            value = value.strftime("%d/%m/%Y")
        elif value is None:
            value = datetime.datetime.now().strftime("%d/%m/%Y")
        else:
            # Try to format string
            value = datetime.datetime.strptime(value, "%d/%m/%Y").strftime("%d/%m/%Y")

        StatusClass.inclusion_date.__set__(self, value)
    @property
    def inclusion_datetime(self):
        """
        Inclusion date
        :return:
        """
        return StatusClass.inclusion_datetime.__get__(self)

    @inclusion_datetime.setter
    def inclusion_datetime(self, value):
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

        StatusClass.inclusion_datetime.__set__(self, value)

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
        return conv.document2dict(self.status_base.lbbase, self)

    def status_to_json(self):
        """
        Convert object to json
        :return:
        """
        return conv.document2json(self.status_base.lbbase, self)

    def create_status(self):
        """
        Insert document on base
        :param unique: If it is unique, sent this option as true
        :return: Document creation status
        """
        document = self.status_to_json()
        try:
            result = self.status_base.documentrest.create(document)
        except HTTPError, err:
            log.error(err.strerror)
            return None

        return result

    def update(self, id_doc):
        #print(self.arg_structures)
        document = self.status_to_json()
        #print(document)
        return self.status_base.documentrest.update(id=id_doc, document=document)