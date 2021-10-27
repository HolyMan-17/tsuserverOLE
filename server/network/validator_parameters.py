"""
tsuserverCC, an Attorney Online server.
Copyright (C) 2020 Kaiser <kaiserkaisie@gmail.com>

Derivative of tsuserver3, an Attorney Online server. 
Copyright (C) 2016 argoneus <argoneuscze@gmail.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.
 
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.
 
You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

from enum import Enum

class ArgType(Enum):
		"""Represents the data type of an argument for a network command."""
		STR = 1,
		STR_OR_EMPTY = 2,
		INT = 3,
		INT_OR_STR = 3

def validator_pre260():
    parameters =   [ArgType.STR, 
                    ArgType.STR_OR_EMPTY, ArgType.STR, 
			        ArgType.STR, ArgType.STR, 
		            ArgType.STR, ArgType.STR, 
			        ArgType.INT, ArgType.INT,
			        ArgType.INT, ArgType.INT_OR_STR, 
			        ArgType.INT, ArgType.INT, 
			        ArgType.INT, ArgType.INT]
    return parameters

def validator_130():
    
    parameters =   [ArgType.STR, 
                    ArgType.STR_OR_EMPTY, ArgType.STR,
				    ArgType.STR, ArgType.STR, 
                    ArgType.STR, ArgType.STR, 
                    ArgType.INT,ArgType.INT,
                    ArgType.INT, ArgType.INT_OR_STR, 
                    ArgType.INT,ArgType.INT, 
                    ArgType.INT, ArgType.INT,
                    ArgType.STR_OR_EMPTY]
    return parameters

def validator_135():
    
    parameters =   [ArgType.STR,
                    ArgType.STR_OR_EMPTY,ArgType.STR,
					ArgType.STR, ArgType.STR,
                    ArgType.STR,ArgType.STR,
                    ArgType.INT,ArgType.INT,
                    ArgType.INT,ArgType.INT_OR_STR,ArgType.INT,
					ArgType.INT,ArgType.INT,
                    ArgType.INT,ArgType.STR_OR_EMPTY,
					ArgType.INT,ArgType.INT]
    return parameters

def validator_140():
    parameters =   [ArgType.STR,
                    ArgType.STR_OR_EMPTY,ArgType.STR,
				    ArgType.STR,
					ArgType.STR,ArgType.STR,
                    ArgType.STR,ArgType.INT,
					ArgType.INT,ArgType.INT,
                    ArgType.INT_OR_STR,ArgType.INT,
					ArgType.INT,ArgType.INT,
                    ArgType.INT,ArgType.STR_OR_EMPTY,
					ArgType.INT,ArgType.INT,ArgType.INT]
    return parameters 

def validator_270():
    parameters =   [ArgType.STR, ArgType.STR_OR_EMPTY, 
                    ArgType.STR,ArgType.STR,
					ArgType.STR, ArgType.STR, 
                    ArgType.STR, ArgType.INT,
					ArgType.INT, ArgType.INT, 
                    ArgType.INT, ArgType.INT,
					ArgType.INT, ArgType.INT, 
                    ArgType.INT, ArgType.STR_OR_EMPTY,
					ArgType.INT, ArgType.INT, 
                    ArgType.INT, ArgType.STR,
					ArgType.INT, ArgType.STR, 
                    ArgType.STR, ArgType.STR]
    return parameters

def validator_290():
    parameters =       [ArgType.STR, ArgType.STR_OR_EMPTY, 
                        ArgType.STR, ArgType.STR, 
						ArgType.STR, ArgType.STR, 
                        ArgType.STR, ArgType.INT, 
						ArgType.INT, ArgType.INT, 
                        ArgType.INT_OR_STR, ArgType.INT, 
						ArgType.INT, ArgType.INT, 
                        ArgType.INT, ArgType.STR_OR_EMPTY, 
						ArgType.STR, ArgType.STR, 
                        ArgType.INT, ArgType.STR, 
						ArgType.INT, ArgType.STR, 
                        ArgType.STR, ArgType.STR,
						ArgType.INT, ArgType.STR]
    return parameters

