#!/usr/env python
# -*- coding: utf-8 -*-
__author__ = 'eduardo'

import logging
from paste.script import command
from lbsociam.model import crimes
from liblightbase.lbbase.struct import Base
from liblightbase.lbsearch.search import *

log = logging.getLogger()


class CrimeCommands(command.Command):
    """
    Crime analytics commands
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

    parser.add_option('-t', '--terms',
                      action='store',
                      dest='terms',
                      help='Terms to use in social networks search'
    )

    parser.add_option('-c', '--categories',
                      action='store',
                      dest='categories',
                      help='Category to store information'
    )

    parser.add_option('-f', '--field',
                      action='store',
                      dest='field',
                      help='Field to be updated'
    )

    parser.add_option('-a', '--value',
                      action='store',
                      dest='value',
                      help='Value to be used in update'
    )



    def __init__(self, name):
        """
        Constructor method
        :param name: Command name
        """
        super(CrimeCommands, self).__init__(name)
        self.crimes_base = crimes.CrimesBase()

    def command(self):
        """
        Parse command line arguments and call appropriate method.
        """
        if not self.args or self.args[0] in ['--help', '-h', 'help']:
            print(CrimeCommands.__doc__)
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
        if cmd == 'update_field':
            self.update_field()
            return
        else:
            log.error('Command "%s" not recognized' % (cmd,))

    def create_base(self):
        """
        Create the base for twitter status
        """
        crimes_lbbase = self.crimes_base.create_base()
        if isinstance(crimes_lbbase, Base):
            log.info("Crimes base created")
        else:
            raise StandardError

        return

    def update_base(self):
        """
        Create the base for twitter status
        """
        result = self.crimes_base.update_base()
        if result:
            log.info("Crimes base updated")
        else:
            raise StandardError

        return

    def remove_base(self):
        """
        Remove the base for twitter status
        """
        result = self.crimes_base.remove_base()
        if result:
            log.info("Crimes base removed")
        else:
            raise StandardError

        return

    def insert_tokens(self):
        """
        Insert tokens on selected taxonomy
        """
        if self.options.categories is None:
            raise StandardError("You have to supply crime type")

        orderby = OrderBy(asc=['id_doc'])
        search = Search(
            limit=10,
            offset=0,
            order_by=orderby
        )
        self.crimes_base.documentrest.response_object = False
        result = self.crimes_base.documentrest.get_collection(search)

    def update_field(self):
        """
        Update field with supplied value
        """
        if self.options.categories is None:
            raise StandardError("You have to supply crime type")

        if self.options.value is None:
            raise StandardError("You have to supply crime value")

        if self.options.field is None:
            raise StandardError("You have to supply crime field")

        crime = self.crimes_base.get_crime_by_name(self.options.categories)
        crime[self.options.field] = self.options.value

        self.crimes_base.update_document(crime['_metadata']['id_doc'], crime)
        return