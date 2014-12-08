#!/usr/env python
# -*- coding: utf-8 -*-
__author__ = 'eduardo'

import os
import sys
import logging
import requests
import nltk
import re
from lbsociam.model.lbstatus import StatusBase
from lbsociam.model.dictionary import DictionaryBase
from liblightbase.lbsearch.search import *
from lbsociam.model import dictionary
from gensim import corpora, models
from multiprocessing import Process, Queue

log = logging.getLogger()


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
    try:
        assert isinstance(lbstatus, StatusBase)
    except AssertionError as e:
        log.error("You have to supply a status instance\n%s", e)
        return

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
            for structure in result['arg_structures']:
                for argument in structure['argument']:
                    argument_name = argument['argument_name']
                    log.debug("Looking for string as argument in argument_name = %s", argument_name)

                    if re.match('A[0-9]', argument_name) is not None:
                        log.debug("String match for argument_name = %s", argument_name)
                        tokens = tokens + argument['argument_value']

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
    try:
        assert isinstance(lbstatus, StatusBase)
    except AssertionError as e:
        log.error("You have to supply a status instance\n%s", e)
        return

    task_queue = Queue()
    done_queue = Queue()
    processes = int(lbstatus.processes)

    # As we are reprocessing tokens, it is necessary to clear frequency
    dic_base = dictionary.DictionaryBase()
    dic_base.remove_base()
    dic_base.create_base()

    id_status_list = lbstatus.get_document_ids()
    if id_status_list is None:
        log.error("No status found. Import some status first")
        return False

    for elm in id_status_list:
        params = dict(
            status_id=elm,
            outfile=outfile
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
        dic2 = done_queue.get()
        dic.merge_with(dic2)
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
    Processa o conjunto de documentos
    :return:
    """
    lbstatus = StatusBase()
    # Now return all the documents collection and parse it
    dic = corpora.Dictionary()
    stemmer = nltk.stem.RSLPStemmer()

    result = lbstatus.get_document(params['status_id'])

    if getattr(result, 'tokens') is not None:
            # Search for the events as argument
            tokens = list()
            for structure in result.arg_structures:
                for argument in structure.argument:
                    argument_name = argument.argument_name
                    log.debug("Looking for string as argument in argument_name = %s", argument_name)

                    if re.match('A[0-9]', argument_name) is not None:
                        log.debug("String match for argument_name = %s", argument_name)
                        for elm in argument.argument_value:
                            # Find element and update frequency
                            stem = stemmer.stem(elm)
                            dic_elm = dictionary.Dictionary(
                                token=elm,
                                stem=stem
                            )
                            id_doc = dic_elm.get_id_doc()
                            if id_doc is None:
                                dic_elm.frequency = 1
                                document = dic_elm.create_dictionary()
                            else:
                                # Try to update frequency
                                try:
                                    dic_elm.frequency += 1
                                except AttributeError:
                                    # No frequency yet
                                    dic_elm.frequency = 1
                                document = dic_elm.update(id_doc)
                                log.debug("Token repetido: %s. Frequencia atualizada para %s", elm, dic_elm.frequency)

                        tokens = tokens + argument.argument_value

            dic.add_documents([tokens])
    else:
        log.error("Tokens não encontrados para o documento %s", result['_metadata']['id_doc'])

    return dic


# Function run by worker processes
def worker(inp, output):
    for func in iter(inp.get, 'STOP'):
        result = process_tokens(func)
        output.put(result)