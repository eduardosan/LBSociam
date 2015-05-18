#!/usr/env python
# -*- coding: utf-8 -*-
__author__ = 'eduardo'

import logging
import datetime
import requests
import json
from requests.exceptions import HTTPError
from lbsociam import LBSociam
from liblightbase import lbrest
from liblightbase.lbbase.struct import Base, BaseMetadata
from liblightbase.lbbase.lbstruct.group import *
from liblightbase.lbbase.lbstruct.field import *
from liblightbase.lbbase.content import Content
from liblightbase.lbutils import conv
from liblightbase.lbsearch.search import *
from pyramid.response import Response


log = logging.getLogger()


class AnalyticsBase(LBSociam):
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
        analysis_date = Field(**dict(
            name='analysis_date',
            description='Analysis date',
            alias='analysis_date',
            datatype='DateTime',
            indices=['Ordenado'],
            multivalued=False,
            required=True
        ))
        
        total_status = Field(**dict(
            name='total_status',
            description='Total Status Analyzed',
            alias='total_status',
            datatype='Integer',
            indices=['Ordenado'],
            multivalued=False,
            required=True
        ))
        
        total_crimes = Field(**dict(
            name='total_crimes',
            description='Total Crimes Identified',
            alias='total_crimes',
            datatype='Integer',
            indices=['Ordenado'],
            multivalued=False,
            required=True
        ))

        total_positives = Field(**dict(
            name='total_positives',
            description='Total positive status',
            alias='total_positives',
            datatype='Integer',
            indices=['Ordenado'],
            multivalued=False,
            required=False
        ))
        
        status_list = Content()

        status_id_doc = Field(**dict(
            name='status_id_doc',
            description='Identified status id_doc',
            alias='status_id_doc',
            datatype='Integer',
            indices=['Ordenado', 'Unico'],
            multivalued=False,
            required=False
        ))

        status_list.append(status_id_doc)

        status_positives = Field(**dict(
            name='status_positives',
            description='Number of positives for status',
            alias='status_positives',
            datatype='Integer',
            indices=['Ordenado'],
            multivalued=False,
            required=False
        ))

        status_list.append(status_positives)

        status_negatives = Field(**dict(
            name='status_negatives',
            description='Number of negatives for status',
            alias='status_negatives',
            datatype='Integer',
            indices=['Ordenado'],
            multivalued=False,
            required=False
        ))

        status_list.append(status_negatives)

        status_metadata = GroupMetadata(**dict(
            name='status_crimes',
            alias='status_crimes',
            description='Status identified as crimes',
            multivalued=True
        ))

        status_crimes = Group(
            metadata=status_metadata,
            content=status_list
        )

        base_metadata = BaseMetadata(**dict(
            name='analytics',
            description='Criminal data analytics base',
            password='123456',
            idx_exp=False,
            idx_exp_url='index_url',
            idx_exp_time=300,
            file_ext=True,
            file_ext_time=300,
            color='#FFFFFF'
        ))

        content_list = Content()
        content_list.append(analysis_date)
        content_list.append(total_status)
        content_list.append(total_crimes)
        content_list.append(status_crimes)
        content_list.append(total_positives)

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

    def get_document(self, id_doc):
        """
        Get document by ID on base
        """
        url = self.lbgenerator_rest_url + '/' + self.lbbase.metadata.name + '/doc/' + str(id_doc)
        response = requests.get(url)
        if response.status_code > 300:
            return None

        return response.json()

    def update_document(self, id_doc, new_document):
        """
        Update document
        :param id_doc: Document ID
        :return:
        """
        document = json.dumps(new_document)
        return self.documentrest.update(id=id_doc, document=document)

    def update_path(self, id_doc, path, value):
        """
        Update base in proposed path
        """
        response = Response(content_type='application/json')
        url = self.lbgenerator_rest_url + '/' + self.lbbase.metadata.name + '/doc/' + id_doc
        url = url + '/' + path
        params = {
            'value': value
        }

        result = requests.put(
            url=url,
            data=params
        )

        if result.status_code >= 300:
            response.status_code = 500
            response.text = result.text

            return response

        response.status_code = 200
        response.text = result

        return response

    def process_response(self, status_dict, id_doc):
        # Get actual analytics
        entry_dict = self.get_document(id_doc)

        # Manually add id_doc
        entry_dict['_metadata'] = dict()
        entry_dict['_metadata']['id_doc'] = id_doc

        if status_dict is not None:
            # Find out if there are more positives
            positive = False
            if status_dict.get('positives') is not None:
                if status_dict.get('negatives') is not None:
                    if status_dict['positives'] > status_dict['negatives']:
                        positive = True
                else:
                    positive = True

            # Now update total positives
            if positive is True:
                if entry_dict.get('total_positives') is None:
                    entry_dict['total_positives'] = 0
                total_positives = int(entry_dict['total_positives']) + 1
                entry_dict['total_positives'] = total_positives

            # Now update total
            if entry_dict.get('total_crimes') is None:
                entry_dict['total_crimes'] = 0

            total_crimes = int(entry_dict['total_crimes']) + 1
            entry_dict['total_crimes'] = total_crimes

            if entry_dict.get('status_crimes') is None:
                entry_dict['status_crimes'] = []

            # This is eating up all memory. Drop it
            # entry_dict['status_crimes'].append({
            #     'status_id_doc': status_dict['_metadata']['id_doc'],
            #     'status_positives': status_dict.get('positives'),
            #     'status_negatives': status_dict.get('negatives')
            # })

        # Now update total
        if entry_dict.get('total_status') is None:
            entry_dict['total_status'] = 0
        total_status = int(entry_dict['total_status']) + 1
        entry_dict['total_status'] = total_status

        try:
            result = self.update_document(id_doc, entry_dict)
        except HTTPError as e:
            log.error("Error updating status\n%s", e.message)
            result = None

        if result is None:
            log.error("Error updating total status positives and negatives")

        log.info("Processing finished %s", result)

        return True

analytics_base = AnalyticsBase()


class Analytics(analytics_base.metaclass):
    """
    Classe que armazena eventos de crime
    """
    def __init__(self, **args):
        """
        Construct for social networks data
        :return:
        """
        super(Analytics, self).__init__(**args)
        self.analytics_base = analytics_base

    @property
    def analysis_date(self):
        """
        Inclusion date
        :return:
        """
        return analytics_base.metaclass.analysis_date.__get__(self)

    @analysis_date.setter
    def analysis_date(self, value):
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

        analytics_base.metaclass.analysis_date.__set__(self, value)

    def analytics_to_dict(self):
        """
        Convert analytics object to Python dict
        :return: dict for crime
        """
        return conv.document2dict(self.analytics_base.lbbase, self)

    def analytics_to_json(self):
        """
        Convert object to json
        :return: JSON for crime
        """
        return conv.document2json(self.analytics_base.lbbase, self)

    def create_analytics(self):
        """
        Insert document on base
        :return: Document creation analytics
        """
        document = self.analytics_to_json()
        try:
            result = self.analytics_base.documentrest.create(document)
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
        document = self.analytics_to_json()
        #print(document)
        return self.analytics_base.documentrest.update(id=id_doc, document=document)