#!/usr/env python
# -*- coding: utf-8 -*-
__author__ = 'eduardo'

import logging
from paste.script import command
from lbsociam.model import location
from liblightbase.lbbase.struct import Base
from liblightbase.lbsearch.search import *
from lbsociam.model import lbstatus
from lbsociam.model import dictionary as dicbase
from multiprocessing import Queue, Process
from requests.exceptions import ConnectionError

log = logging.getLogger()


class LocationCommands(command.Command):
    """
    Location analytics commands
    Usage:

        paster crime create_base
            - Create crime base

    The commands should be run from the LBSociam directory.

    """

    max_args = 1
    min_args = 1

    summary = __doc__.split('\n')[0]
    usage = __doc__

    group_name = "LBSociam crime Commands"

    parser = command.Command.standard_parser(verbose=True)

    parser.add_option(
        '-f', '--field',
        action='store',
        dest='field',
        help='Field to be updated'
    )

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
        super(LocationCommands, self).__init__(name)
        self.location_base = location.LocationBase()

        # Set base to production
        self.status_base = lbstatus.StatusBase(
            status_name='status',
            dic_name='dictionary'
        )

        self.dictionary_base = dicbase.DictionaryBase(
            dic_base='dictionary'
        )

    def command(self):
        """
        Parse command line arguments and call appropriate method.
        """
        if not self.args or self.args[0] in ['--help', '-h', 'help']:
            print(LocationCommands.__doc__)
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
        if cmd == 'geo_status':
            self.geo_status()
            return
        else:
            log.error('Command "%s" not recognized' % (cmd,))

    def create_base(self):
        """
        Create the base for twitter status
        """
        location_lbbase = self.location_base.create_base()
        if isinstance(location_lbbase, Base):
            log.info("Locations base created")
        else:
            raise StandardError

        return

    def update_base(self):
        """
        Create the base for twitter status
        """
        result = self.location_base.update_base()
        if result:
            log.info("Locations base updated")
        else:
            raise StandardError

        return

    def remove_base(self):
        """
        Remove the base for twitter status
        """
        result = self.location_base.remove_base()
        if result:
            log.info("Locations base removed")
        else:
            raise StandardError

        return

    def geo_status(self, offset=0):
        """
        Get geo from all status
        """
        task_queue = Queue()
        done_queue = Queue()
        processes = int(self.location_base.processes)
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

        id_document_list = self.status_base.get_document_ids(offset=offset)

        for id_doc in id_document_list:
            task_queue.put(id_doc)

        for i in range(processes):
            # Permite o processamento paralelo dos tokens
            Process(target=self.geo_worker, args=(task_queue, done_queue)).start()

        # Process responses
        log.debug("Processing responses")
        for i in range(processes):
            result = done_queue.get()
            log.info("Processing finished %s", result)

        # Tell child processes to stop
        for i in range(processes):
            task_queue.put('STOP')

        return

    def geo_worker(self, inp, output):
        for func in iter(inp.get, 'STOP'):
            result = self.process_geo(func)
            output.put(result)

    def process_geo(self, id_doc):
        """
        Process tokens
        :param id_doc: Document id_doc to be processed
        :return: True or False
        """
        try:
            result = self.status_base.process_geo(id_doc)
        except ConnectionError as e:
            log.error("CONNECTION ERROR: Error processing id_doc = %s\n%s", id_doc, e.message)
            # Try again
            result = self.process_geo(id_doc)

        return result