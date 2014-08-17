#!/usr/env python
# -*- coding: utf-8 -*-
__author__ = 'eduardo'
import logging
import tempfile
import datetime
import sys
import lbsociam
from paste.script import command
from liblightbase import lbrest
from lbsociam.model import lbtwitter
from lbsociam.model import lbstatus
from liblightbase.lbbase.struct import Base
from liblightbase.lbsearch.search import *
from liblightbase.lbutils import conv

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
    #parser.add_option('--goodbye',
    #                  action='store_true',
    #                  dest='goodbye',
    #                  help="Say 'Goodbye' instead")


    parser.add_option('-t', '--terms',
                      action='store',
                      dest='terms',
                      help='Terms to use in social networks search'
        )

    parser.add_option('-o', '--output',
                      action='store',
                      dest='output',
                      help='Output JSON status file',
                      default=tempfile.gettempdir() + '/status.json'
        )

    parser.add_option('-c', '--count',
                      action='store',
                      dest='count',
                      help='Number of results to be returned',
                      default='15'
        )

    def __init__(self, name):
        """
        Constructor method
        """
        super(TwitterCommands,self).__init__(name)

        #self.lbs = lbsociam.LBSociam()
        #self.baserest = lbrest.BaseREST(rest_url=self.lbs.lbgenerator_rest_url, response_object=True)
        self.lbt = lbtwitter.Twitter(debug=False, term='crime')
        self.status_base = lbstatus.StatusBase()
        #self.tw_status = self.lbt.search()

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
            status = self.lbt.search(count=self.options.count)
            saida = status
        else:
            for elm in self.options.terms:
                self.lbt.term = elm
                status = self.lbt.search(count=self.options.count)
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
        saida = list()
        if type(self.options.terms) != list:
            self.lbt.term = self.options.terms
            status = self.lbt.search(count=self.options.count)
            saida = status
        else:
            for elm in self.options.terms:
                self.lbt.term = elm
                status = self.lbt.search(count=self.options.count)
                saida = saida + status


        # Store every twitter on LB database
        for elm in saida:
            status_json = self.lbt.status_to_json([elm])
            status = lbstatus.Status(
                origin='twitter',
                inclusion_date=datetime.datetime.now(),
                text=elm.text,
                source=status_json,
                status_base=self.status_base
            )
            retorno = status.create_status()
            if retorno is None:
                log.error("Error inserting status %s on Base" % elm.text)

        return

    def srl_twitter(self, offset=0):
        """
        Apply SRL to tweets already stored on database
        """
        orderby = OrderBy(asc=['id_doc'])
        search = Search(
            limit=10,
            offset=offset,
            order_by=orderby
        )
        self.status_base.documentrest.response_object = False
        collection = self.status_base.documentrest.get_collection(search)
        for i in range(0, 10):
            try:
                result = collection.results[i]
            except IndexError:
                break
            # Put status from base in LB Status Object
            status = lbstatus.Status(
                origin=result.origin,
                inclusion_date=datetime.datetime.strptime(result.inclusion_date, "%d/%m/%Y"),
                text=result.text,
                source=result.source,
                status_base=self.status_base
            )
            status.srl_tokenize()
            #print(status.tokens)
            #print(status.arg_structures)
            try:
                status.update(id=result._metadata.id_doc)
            except:
                exctype, value = sys.exc_info()[:2]
                log.error("Error updating document id = %d\n%s" % (result._metadata.id_doc, value))

        if collection.result_count > (offset+10):
            # Call the same function again increasing offset
            self.srl_twitter(offset=(offset+10))

        return