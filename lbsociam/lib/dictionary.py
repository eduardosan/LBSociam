#!/usr/env python
# -*- coding: utf-8 -*-
__author__ = 'eduardo'

import os
import sys
import logging
import requests
import nltk
import re
import json
# from lbsociam.model.lbstatus import StatusBase
from lbsociam.model.dictionary import DictionaryBase
from liblightbase.lbsearch.search import *
from lbsociam.model import dictionary
from gensim import corpora, models
from multiprocessing import Process, Queue
from liblightbase.lbutils import conv
from requests.exceptions import HTTPError, ConnectionError

log = logging.getLogger()


def valid_word(word):
    """
    Apply processing to word and return valid word
    :return: True if it is valid or False if it is not
        Ĩf a list is supplied, return a list of valid tokens or empty list
    """
    # Processing modules
    stopwords = set(nltk.corpus.stopwords.words('portuguese'))
    stopwords.update(['http', 'pro', 'https', 't.', 'co'])
    re.LOCALE = 'pt_BR.UTF-8'

    # Validate list or single word
    if type(word) == list:
        saida = list()

        for text in word:
            if text not in stopwords and \
                    re.match(r'\w+', text) and \
                    len(text) > 2:
                saida.append(text)

        return saida

    if word not in stopwords and \
            re.match(r'\w+', word) and \
            len(word) > 2:
        return True
    else:
        return False


def status_to_document(status_list):
    """
    Receive a status object and convert tokens to document
    :param status_list: List of status
    :return: Document ready to create a list
    """
    document = list()
    for status in status_list:
        if type(status.tokens) == list and \
                len(status.tokens) > 0:
            document.append(status.tokens)

    return document


def create_from_documents(documents):
    """
    Create dictionary object from documents list
    :param documents: List of documents
    :return: Corpora object
    """
    return corpora.Dictionary(documents)


def create_from_status(lbstatus, outfile=None, offset=0):
    """
    Create dicitonary object from LBStatus Base

    :param lbstatus: LBStatus instance
    :param outfile: File to write out results
    :param offset: Start number
    :return: Gensim Dictionary object instance
    """
    # try:
    #     assert isinstance(lbstatus, StatusBase)
    # except AssertionError as e:
    #     log.error("You have to supply a status instance\n%s", e)
    #     return

    # Stopwords and punctuations removal
    stopwords = nltk.corpus.stopwords.words('portuguese')
    re.LOCALE = 'pt_BR.UTF-8'

    # Now return all the documents collection and parse it
    orderby = OrderBy(asc=['id_doc'])
    select = ['id_doc', 'arg_structures']
    search = Search(
        select=select,
        limit=10,
        offset=offset,
        order_by=orderby
    )
    url = lbstatus.documentrest.rest_url
    url += "/" + lbstatus.lbbase._metadata.name + "/doc"
    vars = {
        '$$': search._asjson()
    }

    # Envia requisição para o REST
    response = requests.get(url, params=vars)
    collection = response.json()
    dic = corpora.Dictionary()
    #print(collection)
    for i in range(0, 10):
        try:
            result = collection['results'][i]
        except IndexError:
            break
        # Adiciona documentos ao dicionário
        if result.get('arg_structures') is not None:
            # Search for the events as argument
            tokens = list()
            tokens.append(result.get('search_term'))
            for structure in result['arg_structures']:
                for argument in structure['argument']:
                    argument_name = argument['argument_name']
                    log.debug("Looking for string as argument in argument_name = %s", argument_name)

                    if re.match('A[0-9]', argument_name) is not None:
                        log.debug("String match for argument_name = %s", argument_name)
                        saida = valid_word(argument['argument_value'])

                        # Add only valid tokens
                        tokens += saida

            dic.add_documents([tokens])
        else:
            log.error("Tokens não encontrados para o documento %s", result['_metadata']['id_doc'])
            continue

    if collection['result_count'] > (offset+10):
        # Call the same function again increasing offset
        create_from_status(
            lbstatus=lbstatus,
            outfile=outfile,
            offset=(offset+10)
        )
    else:
        if outfile is not None:
            dic.save(outfile)
        else:
            return dic


def insert_from_status(lbstatus, outfile=None):
    # try:
    #     assert isinstance(lbstatus, StatusBase)
    # except AssertionError as e:
    #     log.error("You have to supply a status instance\n%s", e)
    #     return

    task_queue = Queue()
    done_queue = Queue()
    processes = int(lbstatus.processes)

    # As we are reprocessing tokens, it is necessary to clear frequency
    dic_base = dictionary.DictionaryBase()
    dic_base.remove_base()
    dic_base.create_base()

    # Lust send the GET request
    rest_url = lbstatus.documentrest.rest_url
    rest_url += "/" + lbstatus.lbbase._metadata.name + "/doc/"

    id_status_list = lbstatus.get_document_ids()
    if id_status_list is None:
        log.error("No status found. Import some status first")
        return False

    for elm in id_status_list:
        params = dict(
            status_id=elm,
            outfile=outfile,
            rest_url=rest_url + elm
        )
        task_queue.put(params)

    for i in range(processes):
        # Permite o processamento paralelo dos tokens
        Process(target=worker, args=(task_queue, done_queue)).start()

    # Load dictionary
    dic = corpora.Dictionary()
    if outfile is not None:
        if os.path.exists(outfile):
            dic.load(outfile)

    max_size = lbstatus.max_size
    # Merge results with this dictionary
    log.debug("Processing results from dictionary creation")
    for i in range(len(id_status_list)):
        # Update status after processing
        processed = done_queue.get()
        dic2 = processed['dic']
        result = processed['status']

        status_dict = conv.document2dict(lbstatus.lbbase, result)
        try:
            retorno = lbstatus.documentrest.update(params['status_id'], json.dumps(status_dict))
        except HTTPError as e:
            log.error("Error updating document id = %d\n%s" % (params['status_id'], e.message))

        dic.merge_with(dic2)
        log.debug("111111111111111111111: Novo dicionário %s", dic)
        if outfile is not None:
            # Serialize if it grows bigger than the amount of size
            if sys.getsizeof(dic, 0) >= max_size:
                log.info("Serializing dict as it reached max size %s", max_size)
                dic.save(outfile)

    if outfile is not None:
        dic.save(outfile)

    # Tell child processes to stop
    for i in range(processes):
        task_queue.put('STOP')

    return True


def process_tokens(params):
    """
    Process the documents
    :return: Dictionary object
    """
    # lbstatus = StatusBase()
    # Now return all the documents collection and parse it
    dic = corpora.Dictionary()
    stemmer = nltk.stem.RSLPStemmer()

    # result = lbstatus.get_document(params['status_id'])

    # Try to find doc
    try:
        response = requests.get(
            url=params['rest_url']
        )
    except ConnectionError as e:
        log.error("Connection error trying to get document id = %s\n%s", params['status_id'], e.message)
        return None

    if response.status_code != 200:
        log.error("Error trying to get document id = %s", params['status_id'])
        return None

    result = response.json()

    if result.get('tokens') is not None:
            # Search for the events as argument
            tokens = list()
            for structure in result.get('arg_structures'):
                for argument in structure.get('argument'):
                    argument_name = argument['argument_name']
                    log.debug("Looking for string as argument in argument_name = %s", argument_name)

                    if re.match('A[0-9]', argument_name) is not None:
                        log.debug("String match for argument_name = %s", argument_name)
                        for elm in argument['argument_value']:

                            # Check valid tokens
                            if valid_word(elm):
                                # Find element and update frequency
                                stem = stemmer.stem(elm)
                                dic_elm = dictionary.Dictionary(
                                    token=elm,
                                    stem=stem
                                )
                                id_doc = dic_elm.get_id_doc()
                                if id_doc is None:
                                    dic_elm.frequency = 1
                                    dic_elm.status_list = [params['status_id']]
                                    document = dic_elm.create_dictionary()
                                else:
                                    # Try to update frequency
                                    try:
                                        if params['status_id'] not in dic_elm.status_list:
                                            dic_elm.frequency += 1
                                            #dic_elm.status_list = [id_doc]
                                            dic_elm.status_list.append(params['status_id'])
                                    except AttributeError:
                                        # No frequency yet
                                        dic_elm.frequency = 1
                                        dic_elm.status_list = [params['status_id']]
                                    document = dic_elm.update(id_doc)
                                    log.debug("Token repetido: %s. Frequencia atualizada para %s", elm, dic_elm.frequency)

                                tokens.append(elm)
                            else:
                                log.debug("Invalid tokens in %s", elm)

            # Add tokens back to status object
            result['events_tokens'] = tokens

            dic.add_documents([tokens])
    else:
        log.error("Tokens não encontrados para o documento %s", params['status_id'])

    # Add search term on dictionary
    elm = result['search_term']
    stem = stemmer.stem(elm)
    dic_elm = dictionary.Dictionary(
        token=elm,
        stem=stem
    )
    id_doc = dic_elm.get_id_doc()
    if id_doc is None:
        dic_elm.frequency = 1
        dic_elm.status_list = [params['status_id']]
        document = dic_elm.create_dictionary()
    else:
        # Try to update frequency
        try:
            if params['status_id'] not in dic_elm.status_list:
                dic_elm.frequency += 1
                #dic_elm.status_list = [id_doc]
                dic_elm.status_list.append(params['status_id'])
        except AttributeError:
            # No frequency yet
            dic_elm.frequency = 1
            dic_elm.status_list = [params['status_id']]
        document = dic_elm.update(id_doc)
        log.debug("Token repetido: %s. Frequencia atualizada para %s", elm, dic_elm.frequency)

    return {
        'dic': dic,
        'status': result
    }


# Function run by worker processes
def worker(inp, output):
    for func in iter(inp.get, 'STOP'):
        result = process_tokens(func)
        output.put(result)


def create_file(lbstatus, outfile, offset=0):
    """
    Create status file

    :param lbstatus: StatusBase instance
    :param outfile: File to record results
    :param offset: Starting point
    :return: True or false
    """
    # try:
    #     assert isinstance(lbstatus, StatusBase)
    # except AssertionError as e:
    #     log.error("You have to supply a status instance\n%s", e)
    #     return

    processes = int(lbstatus.processes)
    # 100 times the maximum number of processes, for some reason
    limit = processes * 1000

    # Now return all the documents collection and parse it
    orderby = OrderBy(asc=['id_doc'])
    select = ['id_doc', 'arg_structures']
    search = Search(
        select=select,
        limit=10,
        offset=offset,
        order_by=orderby
    )
    url = lbstatus.documentrest.rest_url
    url += "/" + lbstatus.lbbase._metadata.name + "/doc"
    vars = {
        '$$': search._asjson()
    }

    # Envia requisição para o REST
    response = requests.get(url, params=vars)
    collection = response.json()
    dic = corpora.Dictionary()

    if outfile is not None:
        if os.path.exists(outfile):
            dic.load(outfile)

    #print(collection)
    for i in range(0, limit):
        try:
            result = collection['results'][i]
        except IndexError:
            break
        # Adiciona documentos ao dicion


    # Save dict for now
    dic.save(outfile)

    if collection['result_count'] > (offset+10):
        # Call the same function again increasing offset
        create_from_status(
            lbstatus=lbstatus,
            outfile=outfile,
            offset=(offset+10)
        )
    else:
        if outfile is not None:
            dic.save(outfile)