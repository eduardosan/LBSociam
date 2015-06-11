#!/usr/env python
# -*- coding: utf-8 -*-
__author__ = 'eduardo'
import datetime
import logging
import requests
import sys
import json
from requests.exceptions import HTTPError
from lbsociam import LBSociam
from lbsociam.lib import srl, dictionary, location, lda
from liblightbase import lbrest
from liblightbase.lbutils import conv
from liblightbase.lbbase.struct import Base, BaseMetadata
from liblightbase.lbbase.lbstruct.group import *
from liblightbase.lbbase.lbstruct.field import *
from liblightbase.lbbase.content import Content
from liblightbase.lbsearch.search import *
from ..model import crimes
from ..model import dictionary as dic

log = logging.getLogger()


class StatusBase(LBSociam):
    """
    Base class to social networks status
    """
    def __init__(self,
                 status_name=None,
                 dic_name=None):
        """
        Bulding method for Status Base
        :param status_name: Name of status base
        :param dic_name: Name of dict status
        :return:
        """
        LBSociam.__init__(self)
        if status_name is not None:
            self.status_base = status_name
        if dic_name is not None:
            self.dictionary_base = dic_name
        self.baserest = lbrest.BaseREST(
            rest_url=self.lbgenerator_rest_url,
            response_object=True
        )
        self.documentrest = lbrest.DocumentREST(
            rest_url=self.lbgenerator_rest_url,
            base=self.lbbase,
            response_object=False
        )
        self.crimes_base = crimes.crimes_base

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

        hashtags = Field(**dict(
            name='hashtags',
            alias='hashtags',
            description='Hashtags identified',
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
            datatype='Integer',
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

        # Category
        category_list = Content()

        category_id_doc = Field(**dict(
            name='category_id_doc',
            alias='Category ID',
            description='id_doc for category in category base',
            datatype='Integer',
            indices=['Ordenado'],
            multivalued=False,
            required=False
        ))

        category_list.append(category_id_doc)

        category_probability = Field(**dict(
            name='category_probability',
            alias='Category Probability',
            description='Classification probability',
            datatype='Decimal',
            indices=[],
            multivalued=False,
            required=False
        ))

        category_list.append(category_probability)

        category_metadata = GroupMetadata(**dict(
            name='category',
            alias='Category',
            description='Category classification information',
            multivalued=False
        ))

        category = Group(
            metadata=category_metadata,
            content=category_list
        )

        # Brasil City
        city_list = Content()

        city_id = Field(**dict(
            name='city_id',
            alias='City ID',
            description='Id for city in LBGeo database',
            datatype='Integer',
            indices=[],
            multivalued=False,
            required=False
        ))

        city_list.append(city_id)

        city_name = Field(**dict(
            name='city_name',
            alias='City Name',
            description='City name in LBGeo database',
            datatype='Text',
            indices=[],
            multivalued=False,
            required=False
        ))

        city_list.append(city_name)

        city_state_id = Field(**dict(
            name='city_state_id',
            alias='City State ID',
            description='Id for state in LBGeo database',
            datatype='Integer',
            indices=[],
            multivalued=False,
            required=False
        ))

        city_list.append(city_state_id)

        state_name = Field(**dict(
            name='state_name',
            alias='State Name',
            description='State Name in LBGeo database',
            datatype='Text',
            indices=[],
            multivalued=False,
            required=False
        ))

        city_list.append(state_name)

        state_short_name = Field(**dict(
            name='state_short_name',
            alias='UF',
            description='UF in LBGeo database',
            datatype='Text',
            indices=[],
            multivalued=False,
            required=False
        ))

        city_list.append(state_short_name)

        state_slug = Field(**dict(
            name='state_slug',
            alias='Stte Slug',
            description='State Slug in LBGeo database',
            datatype='Text',
            indices=[],
            multivalued=False,
            required=False
        ))

        city_list.append(state_slug)

        city_slug = Field(**dict(
            name='city_slug',
            alias='City Slug',
            description='City Slug in LBGeo database',
            datatype='Text',
            indices=[],
            multivalued=False,
            required=False
        ))

        city_list.append(city_slug)

        city_lat = Field(**dict(
            name='city_lat',
            alias='City Latitude',
            description='City Latitude in LBGeo database',
            datatype='Decimal',
            indices=[],
            multivalued=False,
            required=False
        ))

        city_list.append(city_lat)

        city_lng = Field(**dict(
            name='city_lng',
            alias='City Longitude',
            description='City Longitude in LBGeo database',
            datatype='Decimal',
            indices=[],
            multivalued=False,
            required=False
        ))

        city_list.append(city_lng)

        city_distance = Field(**dict(
            name='city_distance',
            alias='City Distance',
            description='Distance from city in LBGeo database',
            datatype='Decimal',
            indices=[],
            multivalued=False,
            required=False
        ))

        city_list.append(city_distance)

        city_metadata = GroupMetadata(**dict(
            name='brasil_city',
            alias='City in Brasil',
            description='City in Brasil identified by LBGeo',
            multivalued=False
        ))

        brasil_city = Group(
            metadata=city_metadata,
            content=city_list
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
        content_list.append(hashtags)
        content_list.append(category)
        content_list.append(brasil_city)

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

    def get_document_ids(self, offset=0, start_date=None, end_date=None):
        """
        Build a lis with all document ID's
        """
        orderby = OrderBy(asc=['id_doc'])
        select = ['id_doc']
        literal = ""

        # Check if there are date filters
        if start_date is not None:
            if end_date is None:
                # Default to now
                end_date = datetime.datetime.now()

            # Use search by inclusion_datetime
            literal = """inclusion_datetime between '%s'::date and '%s'::date""" % (
                start_date.strftime("%Y-%m-%d"),
                end_date.strftime("%Y-%m-%d")
            )

        search = Search(
            select=select,
            limit=None,
            literal=literal,
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
            "origin",
            "search_term",
            "hashtags"
        ]

        search = Search(
            select=select,
            limit=None,
            order_by=orderby,
            literal="document->>'location' <> '{}'",
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

    def process_tokens(self, id_doc):
        """
        Process tokens for this id_doc

        :param id_doc: Document to be processed
        :return: True or False
        """
        result = self.get_document(id_doc)

        # JSON
        status_dict = conv.document2dict(self.lbbase, result)

        # Manually add id_doc
        status_dict['_metadata'] = dict()
        status_dict['_metadata']['id_doc'] = id_doc

        # SRL tokenize
        tokenized = srl.srl_tokenize(status_dict['text'])
        if tokenized.get('arg_structures') is not None:
            status_dict['arg_structures'] = tokenized.get('arg_structures')

        if tokenized.get('tokens') is not None:
            status_dict['tokens'] = tokenized.get('tokens')

        # Now try to find location
        status_dict = location.get_location(status_dict)

        # Process tokens if selected
        dictionary_base = dic.DictionaryBase(
            dic_base=self.dictionary_base
        )
        result = dictionary.process_tokens_dict(status_dict, dictionary_base)
        log.debug("Corpus da tokenização calculado. id_doc = %s", id_doc)
        status_dict = result['status']

        # Extract hashtags
        status_dict = self.get_hashtags_dict(status_dict)

        # Calculate category
        status_dict = self.get_category(status_dict)

        # Get brasil city information
        status_dict = self.status_base.process_geo_dict(
            id_doc=id_doc,
            status_dict=status_dict
        )

        # Now update document back
        self.documentrest.update(id_doc, json.dumps(status_dict))

        return True

    def process_hashtags(self, id_doc):
        result = self.get_document(id_doc)

        # JSON
        status_dict = conv.document2dict(self.lbbase, result)

        # Manually add id_doc
        status_dict['_metadata'] = dict()
        status_dict['_metadata']['id_doc'] = id_doc

        return self.process_hashtags_dict(status_dict)

    def get_hashtags(self):
        """
        Get a list of identified hashtags
        """
        orderby = OrderBy(asc=['id_doc'])
        select = [
            "hashtags"
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

    def get_hashtags_dict(self, status_dict):
        """
        Get hashtags dict
        """
        # Get hashtags
        source = json.loads(status_dict['source'])
        status_dict['hashtags'] = list()
        hashtags = source[0].get('hashtags')
        for elm in hashtags:
            if elm.get('text') is not None:
                status_dict['hashtags'].append(elm['text'])

        return status_dict

    def process_hashtags_dict(self, status_dict_orig):
        """
        Process hashtags
        """
        status_dict = self.get_hashtags_dict(status_dict_orig)

        if len(status_dict['hashtags']) > 0:
            # Don't update if there's no hashtags
            return True

        try:
            self.documentrest.update(
                status_dict['_metadata']['id_doc'],
                json.dumps(status_dict)
            )
            # FIXME: Esse método só vai funcionar quando a liblightbase estiver ok
            # status.update(id_doc=result._metadata.id_doc)
        except:
            exctype, value = sys.exc_info()[:2]
            log.error("Error updating document id = %d\n%s" % (status_dict['_metadata']['id_doc'], value))
            return False

    def search_equal(self, source, limit=1):
        """
        Search status by content
        """
        orderby = OrderBy(['id_doc'])
        search = Search(
            limit=limit,
            order_by=orderby,
            literal="document->>'source' = '" + source + "'",
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
        if results.get('result_count') is None:
            return None

        if results['result_count'] == 0:
            return None

        response = results['results'][0]['_metadata']['id_doc']

        return response

    def get_category(self, status_dict):
        """
        Find category for this status

        :param status_dict: Status dict to be inserted back on the base
        :return dict: Identified category
        """
        # Consider always training base for the model
        status_base = StatusBase()

        # Use default status base to calculate LDA Model
        category = lda.get_category(
            status_dict,
            status_base,
            self.crimes_base
        )

        return category

    def process_geo_dict(self, id_doc, max_distance=50000, status_dict=None):
        """
        Get Brasil city distance from document
        :param max_distance: Max distance (Meters) to consider
        :return: Dict with Geo information from LBGeo
        """
        if status_dict is None:
            document = self.get_document(id_doc)
            status_dict = conv.document2dict(self.lbbase, document)

        if status_dict.get('location') is None:
            if status_dict.get('arg_structures') is not None:
                # Now try to find location again
                status_dict['_metadata'] = dict()
                status_dict['_metadata']['id_doc'] = id_doc
                status_dict = location.get_location(status_dict)

                if status_dict.get('location') is None:
                    log.error("Location not available for document id = %s", id_doc)
                    return status_dict
            else:
                log.error("Location not available for document id = %s", id_doc)
                return status_dict

        params = {
            'lat': status_dict['location']['latitude'],
            'lng': status_dict['location']['longitude']
        }

        url = self.geo_url + '/city'
        result = requests.post(
            url=url,
            data=json.dumps(params)
        )

        # Check for Exception
        try:
            result.raise_for_status()
        except HTTPError as e:
            log.error("Connection error in id_doc = %s\n%s", id_doc, e.message)
            return status_dict

        try:
            city = result.json()
        except ValueError as e:
            log.error("Error parsing response for id_doc = %s\n%s", id_doc, e.message)
            return status_dict

        # Check for max distance
        if float(city['city_distance']) > float(max_distance):
            # Do not take this distance
            log.debug("Distance = %s bigger than maximum = %s", city['city_distance'], max_distance)
            return status_dict

        # Now update document with city
        status_dict['brasil_city'] = city

        return status_dict

    def process_geo(self, id_doc, max_distance=50000):
        """
        Get Brasil city distance from document
        :param max_distance: Max distance (Meters) to consider
        :return: JSON with Geo information from LBGeo
        """
        status_dict = self.process_geo_dict(id_doc, max_distance)
        try:
            self.documentrest.update(
                id_doc,
                json.dumps(status_dict)
            )
            # FIXME: Esse método só vai funcionar quando a liblightbase estiver ok
            # status.update(id_doc=result._metadata.id_doc)
        except:
            exctype, value = sys.exc_info()[:2]
            log.error("Error updating document id = %d\n%s" % (id_doc, value))
            return None

        return True

    def get_status_probability(self, category_id_doc, start_date, end_date=None):
        """
        Build a lis with all document ID's
        """
        orderby = OrderBy(asc=['id_doc'])
        select = ['category_id_doc', 'category_probability']

        # Check if there are date filters
        literal = None
        if start_date is not None:
            if end_date is None:
                # Default to now
                end_date = datetime.datetime.now()

            # Use search by inclusion_datetime
            literal = """inclusion_datetime between '%s'::date and '%s'::date """ % (
                start_date.strftime("%Y-%m-%d"),
                end_date.strftime("%Y-%m-%d")
            )
        else:
            log.error("start_date must be supplied")
            return None

        # look for category
        literal += """ and category_id_doc = %s""" % category_id_doc

        search = Search(
            select=select,
            limit=None,
            order_by=orderby,
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


status_base = StatusBase()
StatusClass = status_base.metaclass
ArgStructures = status_base.arg_structures
Argument = status_base.argument


class Status(StatusClass):
    """
    Class to hold status elements
    """
    def __init__(self, base=None, **args):
        """
        Construct for social networks data
        :return:
        """
        super(Status, self).__init__(**args)

        # These have to be null
        #self.tokens = list()
        #self.arg_structures = list()
        if base is None:
            self.status_base = status_base
        else:
            self.status_base = base
        self.crimes_base = crimes.crimes_base

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
        :return: Document creation status
        """
        document = self.status_to_json()
        try:
            result = self.status_base.documentrest.create(document)
        except HTTPError as err:
            log.error("STATUS: Error inserting status!!!")

            # Try to search document with same source
            try:
                result = self.status_base.search_equal(self.source)
            except:
                exctype, value = sys.exc_info()[:2]
                log.error("STATUS: Status not found!!!\n%s" % (value))
                return None

        return result

    def update(self, id_doc):
        """
        Update document on base
        :param id_doc: document to be updated
        :return: Ok or HTTPException if error
        """
        # print(self.arg_structures)
        document = self.status_to_json()
        # print(document)
        return self.status_base.documentrest.update(id=id_doc, document=document)

    def get_category(self, status_dict=None):
        """
        Find category for this status
        """
        if status_dict is None:
            self.status_to_dict()

        # Use default status base to calculate LDA Model
        category = lda.get_category(
            status_dict,
            status_base,
            self.crimes_base
        )

        return category