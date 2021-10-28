"""
tsuserverOLE, an Attorney Online server.
Copyright (C) 2021 KillerSteel <killermagnum5@gmail.com

Derivative of tsuserverCC, an Attorney Online server.
Copyright (C) 2020 Kaiser <kaiserkaisie@gmail.com>

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
from statements import Statement
from server.network.aoprotocol import AOProtocol

def playback_testimony():
	if AOProtocol.client in AOProtocol.client.area.owners and not AOProtocol.client.area.is_recording and len(AOProtocol.client.area.recorded_messages) != 0:
		for statements in AOProtocol.client.area.recorded_messages:
			if statements.id == 0:
				statement = statements
		AOProtocol.client.area.send_command('MS', *statement.args)
		if AOProtocol.client.can_wtce:
			AOProtocol.client.area.send_command('RT', 'testimony2')
		AOProtocol.client.area.statement = 0
def record_testimony(msg,send_args):
	if AOProtocol.client in AOProtocol.client.area.owners and not AOProtocol.client.area.is_recording:
		AOProtocol.client.area.is_recording = True
		AOProtocol.client.area.recorded_messages.clear()
		AOProtocol.client.area.statement = 0
		statement = Statement(send_args)
		statement.args[4] = msg[2:]
		AOProtocol.client.area.recorded_messages.append(statement)
		AOProtocol.client.send_ooc('Recording testimony!')
		if AOProtocol.client.can_wtce:
			AOProtocol.client.area.send_command('RT', 'testimony1')
def end(send_args):
	if AOProtocol.client in AOProtocol.client.area.owners and AOProtocol.client.area.is_recording:
		AOProtocol.client.area.is_recording = False
		AOProtocol.client.area.statement += 1
		statement = Statement(send_args)
		statement.id = AOProtocol.client.area.statement
		AOProtocol.client.area.statement = 0
		AOProtocol.client.area.recorded_messages.append(statement)
		AOProtocol.client.send_ooc('No longer recording testimony.')
def add(send_args,msg):
	if AOProtocol.client in AOProtocol.client.area.owners and AOProtocol.client.area.is_recording:
		if AOProtocol.client.area.statement >= 30:
			return AOProtocol.client.send_ooc('You\'re trying to add too many statements.')
		AOProtocol.client.area.statement += 1
		statement = Statement(send_args)
		statement.args[4] = msg[1:]
		statement.id = AOProtocol.client.area.statement
		AOProtocol.client.area.recorded_messages.append(statement)
		AOProtocol.client.send_ooc('Statement added!')
	elif AOProtocol.client in AOProtocol.client.area.owners and not AOProtocol.client.area.is_recording and len(AOProtocol.client.area.recorded_messages) != 0:
		if AOProtocol.client.area.statement >= 30:
			return AOProtocol.client.send_ooc('You\'re trying to add too many statements.')
		oldstatement = AOProtocol.client.area.statement
		AOProtocol.client.area.statement += 1
		statement = Statement(send_args)
		statement.args[4] = msg[1:]
		statement.args[14] = 1
		statement.id = AOProtocol.client.area.statement
		for s in AOProtocol.client.area.recorded_messages:
			if s.id >= statement.id:
				s.id += 1
		AOProtocol.client.area.recorded_messages.append(statement)
		AOProtocol.client.send_ooc(f'Substatement added after statement {oldstatement}!')
def ammend(msg,send_args):
	if AOProtocol.client in AOProtocol.client.area.owners and not AOProtocol.client.area.is_recording and len(AOProtocol.client.area.recorded_messages) != 0:
		amend = None
		for s in AOProtocol.client.area.recorded_messages:
			if s.id == AOProtocol.client.area.statement:
				amend = s
		if amend != None:
			newamend = AOProtocol.client.area.recorded_messages[amend.id] = Statement(send_args)
			newamend.id = AOProtocol.client.area.statement
			newamend.args[4] = msg[5:]
			newamend.args[14] = 1
			AOProtocol.client.send_ooc(f'Statement {newamend.id} amended.')
def forward():
	if len(AOProtocol.client.area.recorded_messages) != 0 and not AOProtocol.client.area.is_recording:
		AOProtocol.client.area.statement += 1
		if AOProtocol.client.area.statement >= len(AOProtocol.client.area.recorded_messages):
			AOProtocol.client.area.statement = 1
			AOProtocol.client.area.broadcast_ooc(f'{AOProtocol.client.char_name} reached end, looping back to first statement.')
		else:
			AOProtocol.client.area.broadcast_ooc(f'Testimony advanced by {AOProtocol.client.char_name}.')
		for s in AOProtocol.client.area.recorded_messages:
			if s.id == AOProtocol.client.area.statement:
				statement = s
				break
		playback = True
def jumpto(msg):
	if len(AOProtocol.client.area.recorded_messages) != 0 and not AOProtocol.client.area.is_recording:
		msg = msg[1:]
		try:
			statementno = int(msg)
		except:
			AOProtocol.client.send_ooc('That is not a valid statement number.')
			return
		for s in AOProtocol.client.area.recorded_messages:
			if s.id == statementno:
				statement = s
				AOProtocol.client.area.statement = statementno
				playback = True
				AOProtocol.client.area.broadcast_ooc(f'{AOProtocol.client.char_name} skipped to statement {AOProtocol.client.area.statement}.')
				break
		if not playback:
			AOProtocol.client.send_ooc('No statement with that number found.')
			return
def back():
	if len(AOProtocol.client.area.recorded_messages) != 0 and not AOProtocol.client.area.is_recording:
		AOProtocol.client.area.statement += -1
		if AOProtocol.client.area.statement < 1:
			AOProtocol.client.area.statement = 1
			AOProtocol.client.send_ooc('At first statement, no previous statement available.')
			for s in AOProtocol.client.area.recorded_messages:
				if s.id == AOProtocol.client.area.statement:
					statement = s
					break
			playback = True
		else:
			for s in AOProtocol.client.area.recorded_messages:
				if s.id == AOProtocol.client.area.statement:
					statement = s
					playback = True
					break
			AOProtocol.client.area.broadcast_ooc(f'{AOProtocol.client.char_name} went to the previous statement of the testimony.')
def repeat():
	if len(AOProtocol.client.area.recorded_messages) != 0 and not AOProtocol.client.area.is_recording:
		if AOProtocol.client.area.statement <= 0:
			AOProtocol.client.area.statement = 1
		for s in AOProtocol.client.area.recorded_messages:
			if s.id == AOProtocol.client.area.statement:
				statement = s
				playback = True
				break
		AOProtocol.client.area.broadcast_ooc(f'{AOProtocol.client.char_name} repeated the current statement.')