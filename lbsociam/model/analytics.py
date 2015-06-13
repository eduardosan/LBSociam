#!/usr/env python
# -*- coding: utf-8 -*-
__author__ = 'eduardo'
import time
import logging
import datetime
import requests
import json
from requests.exceptions import HTTPError
from lbsociam import LBSociam
from lbsociam.model import lbstatus
from liblightbase import lbrest
from liblightbase.lbbase.struct import Base, BaseMetadata
from liblightbase.lbbase.lbstruct.group import *
from liblightbase.lbbase.lbstruct.field import *
from liblightbase.lbbase.content import Content
from liblightbase.lbutils import conv
from liblightbase.lbsearch.search import *
from pyramid.response import Response
from operator import itemgetter
from multiprocessing import Queue, Process
from requests.exceptions import ConnectionError


log = logging.getLogger()


class AnalyticsBase(LBSociam):
    """
    Criminal data base
    """
    def __init__(self, status_base=None):
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

        # Get status base in constructor
        if status_base is None:
            self.status_base = lbstatus.status_base
        else:
            self.status_base = status_base

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

        analysis_end_date = Field(**dict(
            name='analysis_end_date',
            description='Analysis end date',
            alias='analysis_date',
            datatype='DateTime',
            indices=[],
            multivalued=False,
            required=False
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

        # Add states analysis
        state_list = Content()

        state_uf = Field(**dict(
            name='state_uf',
            description='State UF',
            alias='UF',
            datatype='Text',
            indices=[],
            multivalued=False,
            required=False
        ))

        state_list.append(state_uf)

        state_name = Field(**dict(
            name='state_name',
            description='State Name',
            alias='Estado',
            datatype='Text',
            indices=[],
            multivalued=False,
            required=False
        ))

        state_list.append(state_name)

        category_list = Content()

        category_id_doc = Field(**dict(
            name='category_id_doc',
            description='Category ID',
            alias='ID Categoria',
            datatype='Integer',
            indices=[],
            multivalued=False,
            required=False
        ))

        category_list.append(category_id_doc)

        category_name = Field(**dict(
            name='category_name',
            description='Category Name',
            alias='Categoria',
            datatype='Text',
            indices=[],
            multivalued=False,
            required=False
        ))

        category_list.append(category_name)

        category_status = Field(**dict(
            name='category_status',
            description='Category Status Ocurrences',
            alias='Status',
            datatype='Integer',
            indices=[],
            multivalued=False,
            required=False
        ))

        category_list.append(category_status)

        category_metadata = GroupMetadata(**dict(
            name='category',
            alias='Categoria',
            description='Categories data',
            multivalued=True
        ))

        category = Group(
            metadata=category_metadata,
            content=category_list
        )

        # Add to state group
        state_list.append(category)

        state_metadata = GroupMetadata(**dict(
            name='state',
            alias='Estado',
            description='States Data',
            multivalued=True
        ))

        state = Group(
            metadata=state_metadata,
            content=state_list
        )
        
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
        content_list.append(analysis_end_date)
        content_list.append(total_status)
        content_list.append(total_crimes)
        content_list.append(status_crimes)
        content_list.append(total_positives)
        content_list.append(state)

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

    def process_response_categories(self, status_dict, id_doc):
        # Get actual analytics
        entry_dict = self.get_document(id_doc)

        # Manually add id_doc
        entry_dict['_metadata'] = dict()
        entry_dict['_metadata']['id_doc'] = id_doc

        # Check mandatory attributes on status
        if status_dict is None:
            log.debug("Empty status!!!")
            return False

        if status_dict.get('brasil_city') is None:
            log.debug("Brasil City not found for status ID = %s", status_dict['_metadata']['id_doc'])
            return False

        if status_dict.get('category') is None:
            log.debug("Category not found for status ID = %s", status_dict['_metadata']['id_doc'])
            return False

        if status_dict['category'].get('category_id_doc') is None:
            log.debug("Category ID not found for status ID = %s", status_dict['_metadata']['id_doc'])
            return False

        # Now build statistics for the attributes
        if entry_dict.get('state') is None:
            entry_dict['state'] = list()

        # Now try to find specific state
        try:
            uf = (item for item in entry_dict['state'] if item['state_uf'] == status_dict['brasil_city']['state_short_name']).next()
            state_index = entry_dict['state'].index(uf)

            # Now try to find category
            try:
                cat = (item for item in entry_dict['state'][state_index]['category'] if item['category_id_doc'] == status_dict['category']['category_id_doc']).next()
                cat_index = entry_dict['state'][state_index]['category'].index(cat)

                # Finally update category frequency
                log.debug("Increasing count. Status = %s Category = %s", status_dict['_metadata']['id_doc'], status_dict['category']['category_id_doc'])
                entry_dict['state'][state_index]['category'][cat_index]['category_status'] += 1

            except StopIteration as e:
                entry_dict['state'][state_index]['category'].append({
                    'category_id_doc': status_dict['category']['category_id_doc'],
                    'category_status': 1
                })

        except StopIteration as e:
            # In this case there is no available
            entry_dict['state'].append({
                'state_uf': status_dict['brasil_city']['state_short_name'],
                'category': [{
                    'category_id_doc': status_dict['category']['category_id_doc'],
                    'category_status': 1
                }]
            })

        entry_dict['total_status'] += 1

        # Finally update entry back on status
        try:
            result = self.update_document(id_doc, entry_dict)
        except ConnectionError as e:
            log.error("Error updating analytics id = %s\n%s", id_doc, e.message)
            # Wait one second and try again
            time.sleep(1)
            result = self.process_response_categories(status_dict, id_doc)
        except HTTPError as e:
            log.error("Error updating status\n%s", e.message)
            result = None

        if result is None:
            log.error("Error updating total status positives and negatives")

        log.info("Processing finished %s", result)

        return True

    def get_latest_analysis(self, start_date, end_date=None):
        """
        Get latest analysis on dates
        :param start_date: Start date
        :param end_date: End date
        :return: Latest analysis JSON
        """
        orderby = OrderBy(asc=['id_doc'])
        select = ['*']

        # Check if there are date filters
        literal = None
        if start_date is not None:
            if end_date is None:
                # Default to now
                end_date = datetime.datetime.now()

            # Use search by inclusion_datetime
            literal = """analysis_date <= '%s'::date and
                         to_date(document->>'analysis_end_date'::text, 'YYYY-MM-DD HH24:MI:SS') <= '%s'::date """ % (
                start_date.strftime("%Y-%m-%d"),
                end_date.strftime("%Y-%m-%d")
            )
        else:
            log.error("start_date must be supplied")
            return None

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
        response_json = response.json()
        results = response_json['results']
        if len(results) == 0:
            return {}
        else:
            # Get only latest analysis
            escolhido = dict()
            for elm in results:
                if not escolhido:
                    escolhido = elm
                elif int(escolhido['_metadata']['id_doc']) < int(elm['_metadata']['id_doc']):
                    escolhido = elm

            log.debug(results)
            log.debug("Escolhido: %s", escolhido)

            return escolhido

    def get_state_analysis(self, start_date, end_date=None):
        """
        Get state analysis
        """
        analysis = self.get_latest_analysis(
            start_date=start_date,
            end_date=end_date
        )

        output = {
            'total_status': analysis['total_status']
        }

        for state in analysis['state']:
            for cat in state['category']:
                if output.get(cat['category_id_doc']) is None:
                    output[cat['category_id_doc']] = dict()

                output[cat['category_id_doc']][state['state_uf']] = cat['category_status']

        return output

    def create_analysis_categories(self,
                                   start_date,
                                   end_date=None,
                                   offset=0):
        """
        Create analysis for the training bases calculating total positives and negatives
        :param start_date: Analysis start date
        :param end_date: Analysis end date
        :param offset: Starting offset
        :return:
        """
        task_queue = Queue()
        done_queue = Queue()
        processes = int(self.processes)

        # Get end date
        if end_date is None:
            end_date = datetime.datetime.now()

        # First create analysis
        ana = Analytics(
            analysis_date=start_date,
            analysis_end_date=end_date,
            total_status=0,
            total_crimes=0,
            status_crimes=[]
        )

        id_doc = ana.create_analytics()
        if id_doc is None:
            log.error("Error creating analysis")

            return None

        self.status_base.documentrest.response_object = False

        # Now run on every status
        id_document_list = self.status_base.get_document_ids(
            offset=offset,
            start_date=start_date,
            end_date=end_date
        )
        for status_id_doc in id_document_list:
            task_queue.put(status_id_doc)

        for i in range(processes):
            # Permite o processamento paralelo dos status
            Process(target=self.worker_categories, args=(task_queue, done_queue)).start()

        # Process responses
        log.debug("Processing responses")
        for i in range(len(id_document_list)):
            status_dict = done_queue.get()

            # Add retry loop if connection errors
            try:
                self.process_response_categories(
                    status_dict=status_dict,
                    id_doc=id_doc
                )
            except ConnectionError as e:
                log.error("CONNECTION ERROR: connection error on %s\n%s", id_doc, e.message)
                # Wait one second and retry
                time.sleep(1)
                self.process_response_categories(
                    status_dict=status_dict,
                    id_doc=id_doc
                )

        # Tell child processes to stop
        for i in range(processes):
            task_queue.put('STOP')

        return id_doc

    # Function run by worker processes
    def worker_categories(self, inp, output):
        for func in iter(inp.get, 'STOP'):
            result = self.process_status_categories(func)
            output.put(result)

    def process_status_categories(self, status_id_doc):
        """
        Process status
        :param status_id_doc: Status id_doc
        :return: Status dict stored
        """
        try:
            result = self.status_base.get_document(status_id_doc)
        except ConnectionError as e:
            log.error("CONNECTION ERROR: Error processing %s\n%s", status_id_doc, e.message)

            # Try again in one second
            time.sleep(1)
            status_dict = self.process_status_categories(status_id_doc)
            return status_dict

        # JSON
        status_dict = conv.document2dict(self.status_base.lbbase, result)
        # Manually add id_doc
        status_dict['_metadata'] = dict()
        status_dict['_metadata']['id_doc'] = status_id_doc

        return status_dict

    def get_analysis(self, limit=10):
        """
        Get analysis list
        :param limit: Maximum results
        :return: JSON with results
        """
        orderby = OrderBy(desc=['id_doc'])
        select = ['*']

        search = Search(
            select=select,
            limit=limit,
            order_by=orderby
        )
        url = self.documentrest.rest_url
        url += "/" + self.lbbase._metadata.name + "/doc"
        vars = {
            '$$': search._asjson()
        }

        # Envia requisição para o REST
        response = requests.get(url, params=vars)
        response_json = response.json()

        return response_json

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

    @property
    def analysis_end_date(self):
        """
        Inclusion date
        :return:
        """
        return analytics_base.metaclass.analysis_end_date.__get__(self)

    @analysis_end_date.setter
    def analysis_end_date(self, value):
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

        analytics_base.metaclass.analysis_end_date.__set__(self, value)

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