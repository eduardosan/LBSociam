#!/usr/env python
# -*- coding: utf-8 -*-
__author__ = 'eduardo'

import logging
import datetime
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

    def __init__(self, name):
        """
        Constructor method
        :param name: Command name
        """
        super(AnalyticsCommands, self).__init__(name)
        self.lbs = LBSociam()
        self.analytics_base = analytics.AnalyticsBase()
        self.status_base = lbstatus.StatusBase()
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
        task_queue = Queue()
        done_queue = Queue()
        processes = int(self.lbs.processes)
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
            result = self.process_status(func)
            output.put(result)

    def process_status(self, status_id_doc):
        """
        Process status
        :param id_doc: id_doc for analytics
        :param status_id_doc: Status id_doc
        :return: True or False
        """
        result = self.status_base.get_document(status_id_doc)

        # JSON
        status_dict = conv.document2dict(self.status_base.lbbase, result)
        # Manually add id_doc
        status_dict['_metadata'] = dict()
        status_dict['_metadata']['id_doc'] = status_id_doc

        # Add status to analytics if positives apre bigger than negatives
        update = False
        if status_dict.get('positives') is not None:
            if status_dict.get('negatives') is not None:
                if status_dict['positives'] > status_dict['negatives']:
                    update = True
            else:
                update = True

        # Get actual analytics
        entry_dict = self.analytics_base.get_document(self.id_doc)

        # Manually add id_doc
        entry_dict['_metadata'] = dict()
        entry_dict['_metadata']['id_doc'] = self.id_doc

        if update:
            # Now update total
            if entry_dict.get('total_crimes') is None:
                entry_dict['total_crimes'] = 0

            total_crimes = int(entry_dict['total_crimes']) + 1
            entry_dict['total_crimes'] = total_crimes

            if entry_dict.get('status_crimes') is None:
                entry_dict['status_crimes'] = []

            entry_dict['status_crimes'].append({
                'status_id_doc': status_id_doc,
                'status_positives': status_dict.get('positives'),
                'status_negatives': status_dict.get('negatives')
            })

        # Now update total
        if entry_dict.get('total_status') is None:
            entry_dict['total_status'] = 0
        total_status = int(entry_dict['total_status']) + 1
        entry_dict['total_status'] = total_status

        try:
            result = self.analytics_base.update_document(self.id_doc, entry_dict)
        except HTTPError as e:
            log.error("Error updating status\n%s", e.message)

        if result is None:
            log.error("Error updating total status positives and negatives")

            return False

        return True