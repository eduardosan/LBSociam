#!/usr/env python
# -*- coding: utf-8 -*-
__author__ = 'eduardo'
import logging
import tempfile
import datetime
import sys
import lbsociam
import json
from paste.script import command
from liblightbase import lbrest
from lbsociam.model import lbtwitter
from lbsociam.model import lbstatus
from lbsociam.model import dictionary as dicbase
from liblightbase.lbbase.struct import Base
from liblightbase.lbsearch.search import *
from liblightbase.lbutils import conv
from ..lib import srl, dictionary, location
from multiprocessing import Queue, Process
from requests.exceptions import ConnectionError

log = logging.getLogger()


class TwitterCommands(command.Command):
    """
    Twitter integration commands
    Usage::

        paster lbtwitter create_base -c <path to config file>

        paster lbtwitter clean -c <path to config file>
            - Remove all data from twitter

    The commands should be run from the LBSociam directory.

    """
    max_args = 1
    min_args = 1

    summary = __doc__.split('\n')[0]
    usage = __doc__

    group_name = "LBSociam Commands"

    parser = command.Command.standard_parser(verbose=True)

    parser.add_option(
        '-t', '--terms',
        action='store',
        dest='terms',
        help='Terms to use in social networks search'
    )

    parser.add_option(
        '-o', '--output',
        action='store',
        dest='output',
        help='Output JSON status file',
        default=tempfile.gettempdir() + '/status.json'
    )

    parser.add_option(
        '-n', '--number',
        action='store',
        dest='number',
        help='Number of results to be returned',
        default=15
    )

    parser.add_option(
        '-u', '--unique',
        action='store',
        dest='unique',
        help='Should we check for unique hashes',
        default=False
    )

    parser.add_option(
        '-i', '--init',
        action='store',
        dest='init',
        help='Starting ID on processing',
        default=None
    )

    parser.add_option(
        '-k', '--tokenize',
        action='store',
        dest='tokenize',
        help='Force tokenizer to work on information retrieval',
        default=None
    )

    def __init__(self, name):
        """
        Constructor method
        """
        super(TwitterCommands, self).__init__(name)

        # Set base to production
        self.status_base = lbstatus.StatusBase(
            status_name='status',
            dic_name='dictionary'
        )

        self.dictionary_base = dicbase.DictionaryBase(
            dic_base='dictionary'
        )

        self.lbt = lbtwitter.Twitter(
            debug=False,
            term='crime',
            status_base=self.status_base,
            dictionary_base=self.dictionary_base
        )

    def command(self):
        """
        Parse command line arguments and call appropriate method.
        """
        if not self.args or self.args[0] in ['--help', '-h', 'help']:
            print(TwitterCommands.__doc__)
            return

        cmd = self.args[0]
        if cmd == 'create_base':
            self.create_base()
            return
        if cmd == 'remove_base':
            self.remove_base()
            return
        if cmd == 'update_base':
            self.update_base()
            return
        if cmd == 'search_twitter':
            if self.options.terms:
                self.search_twitter()
            else:
                log.error("Search terms (-t) are mandatory on twitter search")
            return
        if cmd == 'store_twitter':
            if self.options.terms:
                self.store_twitter()
            else:
                log.error("Search terms (-t) are mandatory on twitter search")
            return
        if cmd == 'srl_twitter':
            self.srl_twitter()

            return
        if cmd == 'hashtags_twitter':
            self.hashtags_twitter()

            return
        else:
            log.error('Command "%s" not recognized' % (cmd,))

    def create_base(self):
        """
        Create the base for twitter status
        """
        status_lbbase = self.status_base.create_base()
        if isinstance(status_lbbase, Base):
            log.info("Status base created")
        else:
            raise StandardError

        return

    def update_base(self):
        """
        Create the base for twitter status
        """
        result = self.status_base.update_base()
        if result:
            log.info("Status base updated")
        else:
            raise StandardError

        return

    def remove_base(self):
        """
        Remove the base for twitter status
        """
        result = self.status_base.remove_base()
        if result:
            log.info("Status base removed")
        else:
            raise StandardError

        return

    def search_twitter(self):
        """
        Import tweets for supplied list of terms
        """
        saida = list()
        if type(self.options.terms) != list:
            self.lbt.term = self.options.terms
            status = self.lbt.search(count=self.options.number)
            saida = status
        else:
            for elm in self.options.terms:
                self.lbt.term = elm
                status = self.lbt.search(count=self.options.number)
                saida = saida + status

        fd = open(self.options.output, 'w+')
        fd.write(self.lbt.status_to_json(saida))
        fd.close()

        log.info("Results writen to %s" % self.options.output)
        return

    def store_twitter(self):
        """
        Store tweets on LB database
        """
        # saida = list()
        if type(self.options.terms) != list:
            self.lbt.term = self.options.terms
            status = self.lbt.search(count=self.options.number)
            result = self.lbt.store_twitter(status_list=status, tokenize=self.options.tokenize)
            # saida = status
        else:
            for elm in self.options.terms:
                self.lbt.term = elm
                status = self.lbt.search(count=self.options.number)
                # Store every twitter on LB database
                result = self.lbt.store_twitter(status_list=status, tokenize=self.options.tokenize)
                # saida = saida + status

        return result

    def srl_twitter(self, offset=0):
        """
        Apply SRL to tweets already stored on database
        """
        task_queue = Queue()
        done_queue = Queue()
        processes = int(self.lbt.processes)
        if self.options.init is not None:
            # Set starting point from command line
            offset = int(self.options.init)

        orderby = OrderBy(asc=['id_doc'])
        search = Search(
            limit=processes,
            offset=offset,
            order_by=orderby
        )
        self.status_base.documentrest.response_object = False

        # Make sure we don't have to validate returned structures from base
        self.status_base.metaclass.__valreq__ = False
        # collection = self.status_base.documentrest.get_collection(search)

        id_document_list = self.status_base.get_document_ids(offset=offset)

        for id_doc in id_document_list:
            task_queue.put(id_doc)

        # if collection.result_count > (offset+processes):
            # Call the same function again increasing offset
        #    self.srl_twitter(offset=(offset+processes))

        for i in range(processes):
            # Permite o processamento paralelo dos tokens
            Process(target=self.worker, args=(task_queue, done_queue)).start()

        # Process responses
        log.debug("Processing responses")
        for i in range(processes):
            result = done_queue.get()
            log.info("Processing finished %s", result)

        # Tell child processes to stop
        for i in range(processes):
            task_queue.put('STOP')

        return

    # Function run by worker processes
    def worker(self, inp, output):
        for func in iter(inp.get, 'STOP'):
            result = self.process_tokens(func)
            output.put(result)

    def process_tokens(self, id_doc):
        """
        Process tokens
        :param id_doc: Document id_doc to be processed
        :return: True or False
        """
        try:
            result = self.status_base.process_tokens(id_doc)
        except ConnectionError as e:
            log.error("CONNECTION ERROR: Error processing id_doc = %s\n%s", id_doc, e.message)
            # Try again
            result = self.process_tokens(id_doc)

        return result

    def hashtags_twitter(self, offset=0):
        """
        Get hashtags from all status
        """
        task_queue = Queue()
        done_queue = Queue()
        processes = int(self.lbt.processes)
        if self.options.init is not None:
            # Set starting point from command line
            offset = int(self.options.init)

        orderby = OrderBy(asc=['id_doc'])
        search = Search(
            limit=processes,
            offset=offset,
            order_by=orderby
        )
        self.status_base.documentrest.response_object = False

        # Make sure we don't have to validate returned structures from base
        self.status_base.metaclass.__valreq__ = False
        # collection = self.status_base.documentrest.get_collection(search)

        id_document_list = self.status_base.get_document_ids(offset=offset)

        for id_doc in id_document_list:
            task_queue.put(id_doc)

        # if collection.result_count > (offset+processes):
            # Call the same function again increasing offset
        #    self.srl_twitter(offset=(offset+processes))

        for i in range(processes):
            # Permite o processamento paralelo dos tokens
            Process(target=self.hashtags_worker, args=(task_queue, done_queue)).start()

        # Process responses
        log.debug("Processing responses")
        for i in range(processes):
            result = done_queue.get()
            log.info("Processing finished %s", result)

        # Tell child processes to stop
        for i in range(processes):
            task_queue.put('STOP')

        return

    def hashtags_worker(self, inp, output):
        for func in iter(inp.get, 'STOP'):
            result = self.process_hashtags(func)
            output.put(result)

    def process_hashtags(self, id_doc):
        """
        Process tokens
        :param id_doc: Document id_doc to be processed
        :return: True or False
        """
        try:
            result = self.status_base.process_hashtags(id_doc)
        except ConnectionError as e:
            log.error("CONNECTION ERROR: Error processing id_doc = %s\n%s", id_doc, e.message)
            # Try again
            result = self.process_hashtags(id_doc)

        return result