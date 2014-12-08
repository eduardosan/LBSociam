#!/usr/env python
# -*- coding: utf-8 -*-
__author__ = 'eduardo'

import logging
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


class DictionaryBase(LBSociam):
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
        token = Field(**dict(
            name='token',
            description='Dictionary token',
            alias='token',
            datatype='Text',
            indices=['Ordenado', 'Unico'],
            multivalued=False,
            required=True
        ))

        stem = Field(**dict(
            name='stem',
            description='Token stem',
            alias='stem',
            datatype='Text',
            indices=['Ordenado'],
            multivalued=False,
            required=False
        ))

        frequency = Field(**dict(
            name='frequency',
            description='Term frequency on last dict update',
            alias='frequency',
            datatype='Integer',
            indices=['Ordenado'],
            multivalued=False,
            required=False
        ))

        base_metadata = BaseMetadata(**dict(
            name='dictionary',
            description='Terms dictionary from social networks'
        ))

        content_list = Content()
        content_list.append(token)
        content_list.append(stem)
        content_list.append(frequency)

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
        :param Dictionary: One twitter Dictionary object to be base model
        :return: LB Base object
        """
        lbbase = self.lbbase
        response = self.baserest.create(lbbase)
        #print(response.Dictionary_code)
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
        if response.Dictionary_code == 200:
            return True
        else:
            raise IOError('Error updating LB Base structure')

    def get_document_ids(self):
        """
        Build a lis with all document ID's
        """
        orderby = OrderBy(asc=['id_doc'])
        select = ['id_doc']
        search = Search(
            select=select,
            limit=None,
            order_by=orderby
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
        for results in collection['results']:
            saida.append(results['_metadata']['id_doc'])

        return saida

    def get_document(self, id_doc):
        """
        Return document data
        """
        return self.documentrest.get(id_doc)

    def get_by_token(self, token):
        """
        Return a crime by name
        """
        orderby = OrderBy(['token'])
        search = Search(
            limit=1,
            order_by=orderby,
            literal="document->>'token' = '" + token + "'",
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
        if len(results['results']) > 0:
            response = results['results'][0]
        else:
            response = None

        return response

    def export(self, outfile, offset=0, limit=100):
        orderby = OrderBy(asc=['id_doc'])
        select = ['id_doc', 'token']
        search = Search(
            select=select,
            limit=limit,
            offset=offset,
            order_by=orderby
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
        for results in collection['results']:
            saida.append(results['_metadata']['id_doc'])

        return saida


dictionary_base = DictionaryBase()


class Dictionary(dictionary_base.metaclass):
    """
    Classe que armazena eventos de crime
    """
    def __init__(self, **args):
        """
        Construct for social networks data
        :return:
        """
        super(Dictionary, self).__init__(**args)
        self.dictionary_base = dictionary_base

    def dictionary_to_dict(self):
        """
        Convert Dictionary object to Python dict
        :return: dict for crime
        """
        return conv.document2dict(self.dictionary_base.lbbase, self)

    def dictionary_to_json(self):
        """
        Convert object to json
        :return: JSON for crime
        """
        return conv.document2json(self.dictionary_base.lbbase, self)

    def create_dictionary(self):
        """
        Insert document on base
        :return: Document creation Dictionary
        """
        document = self.dictionary_to_json()
        try:
            result = self.dictionary_base.documentrest.create(document)
        except HTTPError as err:
            log.error(err.strerror)

            # Provavelmente é repetido. Tenta retornar a última ocorrência e adiciona um contador
            #dic = self.dictionary_base.get_by_token(self.token)
            return None

        return result

    def update(self, id_doc):
        """
        Update document
        :param id_doc: Document ID
        :return:
        """
        document = self.dictionary_to_json()
        #print(document)
        return self.dictionary_base.documentrest.update(id=id_doc, document=document)

    def get_id_doc(self):
        """
        Return a crime by name
        """
        orderby = OrderBy(['token'])
        search = Search(
            limit=1,
            order_by=orderby,
            literal="document->>'token' = '" + self.token + "'",
        )
        params = {
            '$$': search._asjson()
        }

        url = self.dictionary_base.lbgenerator_rest_url + '/' + self.dictionary_base.lbbase.metadata.name + '/doc'
        result = requests.get(
            url=url,
            params=params
        )
        results = result.json()
        if results.get('results') is None:
            return None

        if len(results['results']) > 0:
            response = results['results'][0]['_metadata']['id_doc']
            self.frequency = results['results'][0]['frequency']
        else:
            response = None

        return response