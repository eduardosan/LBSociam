#!/usr/env python
# -*- coding: utf-8 -*-
__author__ = 'eduardo'

import logging
from paste.script import command
from lbsociam.model import location
from liblightbase.lbbase.struct import Base
from liblightbase.lbsearch.search import *

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

    def __init__(self, name):
        """
        Constructor method
        :param name: Command name
        """
        super(LocationCommands, self).__init__(name)
        self.location_base = location.LocationBase()

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