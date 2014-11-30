#!/usr/env python
# -*- coding: utf-8 -*-
__author__ = 'eduardo'

import logging
from paste.script import command
from lbsociam.model import dictionary, lbstatus
from lbsociam.lib import dictionary as dictionary_lib
from liblightbase.lbbase.struct import Base
from liblightbase.lbsearch.search import *

log = logging.getLogger()


class DictionaryCommands(command.Command):
    """
    dictionary analytics commands
    Usage:

        paster dictionary create_base
            - Create dictionary base

    The commands should be run from the LBSociam directory.

    """

    max_args = 1
    min_args = 1

    summary = __doc__.split('\n')[0]
    usage = __doc__

    group_name = "LBSociam dictionary Commands"

    parser = command.Command.standard_parser(verbose=True)

    parser.add_option('-t', '--terms',
                      action='store',
                      dest='terms',
                      help='Terms to use in social networks search'
    )

    parser.add_option('-g', '--group',
                      action='store',
                      dest='group',
                      help='Group to store information'
    )

    def __init__(self, name):
        """
        Constructor method
        :param name: Command name
        """
        super(DictionaryCommands, self).__init__(name)
        self.dictionary_base = dictionary.DictionaryBase()
        self.status_base = lbstatus.StatusBase()

    def command(self):
        """
        Parse command line arguments and call appropriate method.
        """
        if not self.args or self.args[0] in ['--help', '-h', 'help']:
            print(DictionaryCommands.__doc__)
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
        if cmd == 'insert_from_status':
            self.insert_from_status()
            return
        else:
            log.error('Command "%s" not recognized' % (cmd,))

    def create_base(self):
        """
        Create the base for twitter status
        """
        dictionary_lbbase = self.dictionary_base.create_base()
        if isinstance(dictionary_lbbase, Base):
            log.info("Dictionary base created")
        else:
            raise StandardError

        return

    def update_base(self):
        """
        Create the base for twitter status
        """
        result = self.dictionary_base.update_base()
        if result:
            log.info("Dictionary base updated")
        else:
            raise StandardError

        return

    def remove_base(self):
        """
        Remove the base for twitter status
        """
        result = self.dictionary_base.remove_base()
        if result:
            log.info("Dictionary base removed")
        else:
            raise StandardError

        return

    def insert_from_status(self):
        """
        Insert tokens on selected group
        """
        result = dictionary_lib.insert_from_status(self.status_base)
        return result