#!/usr/env python
# -*- coding: utf-8 -*-
__author__ = 'eduardo'

import logging
import datetime
import time
from paste.script import command
from lbsociam.model import analytics
from liblightbase.lbbase.struct import Base
from liblightbase.lbsearch.search import *
from liblightbase.lbutils import conv
from lbsociam.model import lbstatus
from lbsociam import LBSociam
from multiprocessing import Queue, Process
from lbsociam.model import analytics
from requests.exceptions import HTTPError
from requests.exceptions import ConnectionError

log = logging.getLogger()


class AnalyticsCommands(command.Command):
    """
        Crime analytics commands
    Usage:

        paster analytics create_base
            - Create analytics base

    The commands should be run from the LBSociam directory.
    """

    max_args = 1
    min_args = 1

    summary = __doc__.split('\n')[0]
    usage = __doc__

    group_name = "LBSociam analytics Commands"

    parser = command.Command.standard_parser(verbose=True)

    parser.add_option(
        '-i', '--init',
        action='store',
        dest='init',
        help='Starting ID on processing',
        default=None
    )

    parser.add_option(
        '-s', '--start',
        action='store',
        dest='start',
        help='Start date',
        default=None
    )

    parser.add_option(
        '-e', '--end',
        action='store',
        dest='end',
        help='End date',
        default=None
    )

    def __init__(self, name):
        """
        Constructor method
        :param name: Command name
        """
        super(AnalyticsCommands, self).__init__(name)
        self.analytics_base = analytics.AnalyticsBase()
        self.status_base = lbstatus.StatusBase(
            status_name='status',
            dic_name='dictionary'
        )
        self.id_doc = None

    def command(self):
        """
        Parse command line arguments and call appropriate method.
        """
        if not self.args or self.args[0] in ['--help', '-h', 'help']:
            print(AnalyticsCommands.__doc__)
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
        if cmd == 'create_analysis':
            self.create_analysis()
            return
        if cmd == 'create_analysis_categories':
            self.create_analysis_categories()
            return
        else:
            log.error('Command "%s" not recognized' % (cmd,))

    def create_base(self):
        """
        Create the base for twitter status
        """
        analytics_lbbase = self.analytics_base.create_base()
        if isinstance(analytics_lbbase, Base):
            log.info("Analytics base created")
        else:
            raise StandardError

        return

    def update_base(self):
        """
        Create the base for twitter status
        """
        result = self.analytics_base.update_base()
        if result:
            log.info("Analytics base updated")
        else:
            raise StandardError

        return

    def remove_base(self):
        """
        Remove the base for twitter status
        """
        result = self.analytics_base.remove_base()
        if result:
            log.info("Analytics base removed")
        else:
            raise StandardError

        return

    def create_analysis(self, offset=0):
        """
        Create analysis for the training bases calculating total positives and negatives

        :param offset:
        :return:
        """
        task_queue = Queue()
        done_queue = Queue()
        processes = int(self.analytics_base.processes)
        if self.options.init is not None:
            # Set starting point from command line
            offset = int(self.options.init)

        # First create analysis
        ana = analytics.Analytics(
            analysis_date=datetime.datetime.now(),
            total_status=0,
            total_crimes=0,
            status_crimes=[]
        )

        self.id_doc = ana.create_analytics()
        if self.id_doc is None:
            log.error("Error creating analysis")

        self.status_base.documentrest.response_object = False

        # Now run on every status
        id_document_list = self.status_base.get_document_ids(offset=offset)
        for status_id_doc in id_document_list:
            task_queue.put(status_id_doc)

        for i in range(processes):
            # Permite o processamento paralelo dos status
            Process(target=self.worker, args=(task_queue, done_queue)).start()

        # Process responses
        log.debug("Processing responses")
        for i in range(len(id_document_list)):
            status_dict = done_queue.get()

            # Add retry loop if connection errors
            try:
                self.analytics_base.process_response(status_dict=status_dict, id_doc=self.id_doc)
                retry = False
            except ConnectionError as e:
                log.error("CONNECTION ERROR: connection error on %s\n%s", self.id_doc, e.message)
                # Wait one second and retry
                time.sleep(1)
                self.analytics_base.process_response(status_dict=status_dict, id_doc=self.id_doc)

        # Tell child processes to stop
        for i in range(processes):
            task_queue.put('STOP')

        return

    # Function run by worker processes
    def worker(self, inp, output):
        for func in iter(inp.get, 'STOP'):
            result = self.process_status(func)
            output.put(result)

    def process_status(self, status_id_doc):
        """
        Process status
        :param id_doc: id_doc for analytics
        :param status_id_doc: Status id_doc
        :return: True or False
        """
        try:
            result = self.status_base.get_document(status_id_doc)
        except ConnectionError as e:
            log.error("CONNECTION ERROR: Error processing %s\n%s", status_id_doc, e.message)
            time.sleep(1)
            result = self.status_base.get_document(status_id_doc)

        # JSON
        status_dict = conv.document2dict(self.status_base.lbbase, result)
        # Manually add id_doc
        status_dict['_metadata'] = dict()
        status_dict['_metadata']['id_doc'] = status_id_doc

        # Add status to analytics if positives are bigger than negatives
        update = False
        if status_dict.get('positives') is not None or status_dict.get('negatives') is not None:
            update = True

        if update:
            return status_dict
        else:
            return None

    def create_analysis_categories(self, offset=0):
        """
        Create analysis for the training bases calculating total positives and negatives

        :param offset:
        :return:
        """
        task_queue = Queue()
        done_queue = Queue()
        processes = int(self.analytics_base.processes)
        if self.options.init is not None:
            # Set starting point from command line
            offset = int(self.options.init)

        # Get starting date
        if self.options.start is None:
            raise StandardError("Start date is mandatory (-s)")
        else:
            start_date = datetime.datetime.strptime(self.options.start, "%Y-%m-%d")

        # Get end date
        if self.options.end is None:
            end_date = datetime.datetime.now()
        else:
            end_date = datetime.datetime.strptime(self.options.end, "%Y-%m-%d")

        # First create analysis
        ana = analytics.Analytics(
            analysis_date=start_date,
            analysis_end_date=end_date,
            total_status=0,
            total_crimes=0,
            status_crimes=[]
        )

        self.id_doc = ana.create_analytics()
        if self.id_doc is None:
            log.error("Error creating analysis")

            return

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
                self.analytics_base.process_response_categories(status_dict=status_dict, id_doc=self.id_doc)
            except ConnectionError as e:
                log.error("CONNECTION ERROR: connection error on %s\n%s", self.id_doc, e.message)
                # Wait one second and retry
                time.sleep(1)
                self.analytics_base.process_response_categories(status_dict=status_dict, id_doc=self.id_doc)

        # Tell child processes to stop
        for i in range(processes):
            task_queue.put('STOP')

        return

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
            time.sleep(1)
            result = self.status_base.get_document(status_id_doc)

        # JSON
        status_dict = conv.document2dict(self.status_base.lbbase, result)
        # Manually add id_doc
        status_dict['_metadata'] = dict()
        status_dict['_metadata']['id_doc'] = status_id_doc

        return status_dict
