#!/usr/env python
# -*- coding: utf-8 -*-
__author__ = 'eduardo'

import logging
import os
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

    parser.add_option(
        '-o', '--outfile',
        action='store',
        dest='outfile',
        help='File to use in dictionary serialization'
    )

    def __init__(self, name):
        """
        Constructor method
        :param name: Command name
        """
        super(DictionaryCommands, self).__init__(name)
        self.dictionary_base = dictionary.DictionaryBase(
            dic_base='dictionary'
        )
        self.status_base = lbstatus.StatusBase(
            status_name='status',
            dic_name='dictionary'
        )

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
        if cmd == 'dict_file':
            self.dict_file()
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
        if self.options.outfile is None:
            result = dictionary_lib.insert_from_status(self.status_base)
        else:
            dic_dir = self.dictionary_base.lbsociam_data_dir + '/corpus'
            if not os.path.isdir(dic_dir):
                os.mkdir(dic_dir)

            outfile = dic_dir + '/' + self.options.outfile
            log.debug("Saving results on file %s", outfile)
            result = dictionary_lib.insert_from_status(self.status_base, outfile)

        return result

    def dict_file(self):
        """
        Create dict file
        """
        if self.options.outfile is None:
            log.error("You have to supply an outfile")
            return

        dic_dir = self.dictionary_base.lbsociam_data_dir + '/corpus'
        if not os.path.isdir(dic_dir):
            os.mkdir(dic_dir)

        outfile = dic_dir + '/' + self.options.outfile
        log.debug("Saving results on file %s", outfile)
        result = dictionary_lib.create_from_status(self.status_base, outfile)

        return result