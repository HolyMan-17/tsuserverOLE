# tsuserverCC, an Attorney Online server.
#
# Copyright (C) 2020 Kaiser <kaiserkaisie@gmail.com>
#
# Derivative of tsuserver3, an Attorney Online server. Copyright (C) 2016 argoneus <argoneuscze@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.	See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.	If not, see <https://www.gnu.org/licenses/>.

# ========================
# Alright, ladies n' gents, here's where it starts.
# Breaking out the contents of the big network packet handler for IC messages into this file.

# The plan is to create handler functions for the main one in aoprotocol.py, then have that one refer to what's in here.
# Organized by packet header, well-documented so we know what's going on.
# Wish me luck... -Steel
# ========================


import time
import asyncio
import re
import unicodedata

import logging

logger_debug = logging.getLogger('debug')
logger = logging.getLogger('events')

from enum import Enum

import arrow
from time import localtime, strftime

from server import database
from server.statements import Statement
from server.exceptions import ClientError, AreaError, ArgumentError, ServerError
from server.fantacrypt import fanta_decrypt
from .. import commands

class AOProtocol_IC():

    def __init__(self, server):
		super().__init__()
		self.server = server
		self.client = None
		self.buffer = ''
		self.ping_timeout = None

    