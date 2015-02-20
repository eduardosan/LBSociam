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

        default_token = Field(**dict(
            name='default_token',
            description='Default token for this category',
            alias='default_token',
            datatype='Text',
            indices=['Ordenado'],
            multivalued=False,
            required=False
        ))

        color = Field(**dict(
            name='color',
            description='Color to be shown on interface',
            alias='Color',
            datatype='Text',
            indices=[],
            multivalued=False,
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
        content_list.append(default_token)
        content_list.append(color)

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
        params = {
            '$$': search._asjson()
        }

        url = self.lbgenerator_rest_url + '/' + self.lbbase.metadata.name + '/doc'
        result = requests.get(
            url=url,
            params=params
        )
        results = result.json()

        return results

    def get_document(self, id_doc):
        """
        Get document by ID on base
        """
        url = self.lbgenerator_rest_url + '/' + self.lbbase.metadata.name + '/doc/' + id_doc
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
        #print(document)
        return self.documentrest.update(id=id_doc, document=document)

    def upload_file(self, fileobj):
        """
        Upload file on LB
        """
        url = self.lbgenerator_rest_url + "/" + self.lbbase._metadata.name + "/file"
        result = requests.post(
            url=url,
            files={
                'file': fileobj.file.read()
            }
        )

        return result

    def update_file_document(self, id_doc, file_dict):
        """
        Insert file in document
        """
        url = self.lbgenerator_rest_url + "/" + self.lbbase._metadata.name + \
              "/doc/" + id_doc + '/images'

        log.debug("URL para insercao dos atributos da imagem %s", url)
        log.debug(file_dict)

        result = requests.post(
            url=url,
            data={
                'value': json.dumps(file_dict)
            }
        )

        return result

    def remove_file(self, id_doc, id_file):
        """
        Remove image from base
        """
        # First gets document
        document = self.get_document(id_doc)

        # Now create a new image dict removing selected files
        new_image = list()
        for image in document.get('images'):
            if image['id_file'] != id_file:
                new_image.append(image)

        # Finally update document and submit it back to base
        document['images'] = new_image

        response = Response(content_type='application/json')
        try:
            log.debug(document)
            result = self.update_document(id_doc, document)
        except HTTPError as e:

            response.status_code = 500
            response.text = e.message

            return response

        # TODO: Not yet implemented. Need fix
        # Now remove file from database
        #url = self.lbgenerator_rest_url + '/' + self.lbbase._metadata.name + '/' + id_file
        #result = requests.delete(
        #    url=url
        #)
        #if result.status_code >= 300:
        #    response.status_code = result.status_code
        #    response.text = result.text

        #    return response

        response.status_code = 200
        response.text = result

        return response

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

    def get_crime_by_name(self, name):
        """
        Return a crime by name
        """
        orderby = OrderBy(['category_name'])
        search = Search(
            limit=1,
            order_by=orderby,
            literal="document->>'category_name' = '" + name + "'",
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
        response = results['results'][0]

        return response

    def get_all(self):
        """
        Get category for the supplied token
        """
        orderby = OrderBy(['category_name'])
        search = Search(
            select=['*'],
            limit=None,
            order_by=orderby,
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

        # Now find token for this category
        return results['results']

    def get_token_by_name(self, name, full_search=False):
        """
        Return a crime by name
        """
        orderby = OrderBy(['default_token'])
        search = Search(
            limit=1,
            order_by=orderby,
            literal="document->>'default_token' = '" + name + "'",
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

        if full_search is True and len(results['results']) == 0:
            log.debug("Token %s not found. Trying on other tokens", name)
            # Try to find in other tokens
            orderby = OrderBy(['default_token'])
            search = Search(
                limit=None,
                order_by=orderby,
                literal="document->>'default_token' <> '" + name + "'",
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
            for elm in results['results']:
                if elm.get('tokens') is not None:
                    log.debug("Trying to find token %s in tokens list %s", name, elm['tokens'])
                    if any(name in s for s in elm['tokens']):
                        # Return the element as we found the token
                        log.debug("Token %s found on string comparison\n%s", name, elm)
                        return elm

            # If we got here the token was not found
            response = None
        elif len(results['results']) == 0:
            response = None
        else:
            response = results['results'][0]

        return response


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