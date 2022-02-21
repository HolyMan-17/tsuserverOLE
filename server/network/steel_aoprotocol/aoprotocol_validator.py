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
# Breaking out the contents of the big network packet handler for message-based client validation into this file.

# The plan is to create handler functions for the main one in aoprotocol.py, then have that one refer to what's in here.
# Organized by packet header, well-documented so we know what's going on.
# Wish me luck... -Steel
# ========================

class AOProtocol_Validate():

    def __init__(self, server):
		super().__init__()
		self.server = server
		self.client = None
		self.buffer = ''
		self.ping_timeout = None

    # Alright, so this will be the entry point for AOProtocol. We take in the self and args here, then go through our tests.
    # We do it in order from the oldest to the newest version. Each handler function will then give us something in return:
    # 0 or False: Validation did not pass, move on to the next function.
    # An args package: Return a version number matching the test that passed.
    def net_validate(self, args):
        if net_validate_130(args) == True:
            return 130
        elif net_validate_135(args) == True:
            return 135
        elif net_validate_140(args) == True:
            return 140
        elif net_validate_260(args) == True:
            return 260
        elif net_validate_270(args) == True:
            return 270
        elif net_validate_290(args) == True:
            return 290
        else:
            return

    def net_validate_130(args):
        if self.validate_net_cmd(args, self.ArgType.STR, self.ArgType.STR_OR_EMPTY, self.ArgType.STR,
								   self.ArgType.STR,
								   self.ArgType.STR, self.ArgType.STR, self.ArgType.STR, self.ArgType.INT,
								   self.ArgType.INT, self.ArgType.INT, self.ArgType.INT_OR_STR, self.ArgType.INT,
								   self.ArgType.INT, self.ArgType.INT, self.ArgType.INT, self.ArgType.STR_OR_EMPTY):
            return True
        else
            return False

    def net_validate_135(args):
        if self.validate_net_cmd(args, self.ArgType.STR, self.ArgType.STR_OR_EMPTY, self.ArgType.STR,
								   self.ArgType.STR,
								   self.ArgType.STR, self.ArgType.STR, self.ArgType.STR, self.ArgType.INT,
								   self.ArgType.INT, self.ArgType.INT, self.ArgType.INT_OR_STR, self.ArgType.INT,
								   self.ArgType.INT, self.ArgType.INT, self.ArgType.INT, self.ArgType.STR_OR_EMPTY,
								   self.ArgType.INT, self.ArgType.INT):
            return True
        else
            return False

    def net_validate_140(args):
        if self.validate_net_cmd(args, self.ArgType.STR, self.ArgType.STR_OR_EMPTY, self.ArgType.STR,
								   self.ArgType.STR,
								   self.ArgType.STR, self.ArgType.STR, self.ArgType.STR, self.ArgType.INT,
								   self.ArgType.INT, self.ArgType.INT, self.ArgType.INT_OR_STR, self.ArgType.INT,
								   self.ArgType.INT, self.ArgType.INT, self.ArgType.INT, self.ArgType.STR_OR_EMPTY,
								   self.ArgType.INT, self.ArgType.INT, self.ArgType.INT):
            return True
        else
            return False

    def net_validate_260(args):
        if self.validate_net_cmd(args, self.ArgType.STR, # msg_type
		    						 self.ArgType.STR_OR_EMPTY, self.ArgType.STR, # pre, folder
			    					 self.ArgType.STR, self.ArgType.STR, # anim, text
				    				 self.ArgType.STR, self.ArgType.STR, # pos, sfx
					    			 self.ArgType.INT, self.ArgType.INT, # anim_type, cid
						    		 self.ArgType.INT, self.ArgType.INT_OR_STR, # sfx_delay, button
							    	 self.ArgType.INT, self.ArgType.INT, # evidence, flip
								     self.ArgType.INT, self.ArgType.INT): # ding, color
			# Pre-2.6 validation monstrosity.
            
            return True
        else
            return False
        
    def net_validate_270(args):
        if self.validate_net_cmd(args, self.ArgType.STR, self.ArgType.STR_OR_EMPTY, self.ArgType.STR,
								   self.ArgType.STR,
								   self.ArgType.STR, self.ArgType.STR, self.ArgType.STR, self.ArgType.INT,
								   self.ArgType.INT, self.ArgType.INT, self.ArgType.INT, self.ArgType.INT,
								   self.ArgType.INT, self.ArgType.INT, self.ArgType.INT, self.ArgType.STR_OR_EMPTY,
								   self.ArgType.INT, self.ArgType.INT, self.ArgType.INT, self.ArgType.STR,
								   self.ArgType.INT, self.ArgType.STR, self.ArgType.STR, self.ArgType.STR):
            return True
        else
            return False

    def net_validate_290(args):
        if self.validate_net_cmd(args, self.ArgType.STR, self.ArgType.STR_OR_EMPTY, self.ArgType.STR, #msg_type, pre, folder
								   self.ArgType.STR, #anim
								   self.ArgType.STR, self.ArgType.STR, self.ArgType.STR, self.ArgType.INT, #text, pos, sfx, anim_type
								   self.ArgType.INT, self.ArgType.INT, self.ArgType.INT_OR_STR, self.ArgType.INT, #cid, sfx_delay, button, evidence
								   self.ArgType.INT, self.ArgType.INT, self.ArgType.INT, self.ArgType.STR_OR_EMPTY, #flip, ding, color, showname
								   self.ArgType.STR, self.ArgType.STR, self.ArgType.INT, self.ArgType.STR, #charid_pair, offset_pair
								   self.ArgType.INT, self.ArgType.STR, self.ArgType.STR, self.ArgType.STR,
								   self.ArgType.INT, self.ArgType.STR):
            return True
        else
            return False