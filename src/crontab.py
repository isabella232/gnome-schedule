# crontab.py - code to interfere with crontab
# Copyright (C) 2004, 2005 Philip Van Hoof <me at freax dot org>
# Copyright (C) 2004, 2005 Gaute Hope <eg at gaute dot eu dot org>
# Copyright (C) 2004, 2005 Kristof Vansant <de_lupus at pandora dot be>

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Library General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02110-1301, USA.

#python modules
import re
import os
import tempfile

#custom modules
import lang
import config


class Crontab:
	def __init__(self,root,user,uid,gid):
		#default preview length
		self.preview_len = 50
		self.root = root
		self.set_rights(user,uid,gid)
		
		self.nooutputtag = ">/dev/null 2>&1"
		self.crontabRecordRegex = re.compile('([^\s]+)\s([^\s]+)\s([^\s]+)\s([^\s]+)\s([^\s]+)\s([^#\n$]*)(\s#\s([^\n$]*)|$)')

		self.timeranges = { 
			"minute"   : range(0,60), 
			"hour"     : range(0,24),
			"day"      : range(1,32),
			"month"    : range(1,13),
			"weekday"  : range(0,8)
			}

		self.timenames = {
			"minute"   : _("Minute"),
			"hour"     : _("Hour"),
			"day"      : _("Day of Month"),
			"month"    : _("Month"),
			"weekday"  : _("Weekday")
			}
	
		self.monthnames = {
			"1"        : "Jan",
			"2"        : "Feb",
			"3"        : "Mar",
			"4"        : "Apr",
			"5"        : "May",
			"6"        : "Jun",
			"7"        : "Jul",
			"8"        : "Aug",
			"9"        : "Sep",
			"10"       : "Oct",
			"11"       : "Nov",
			"12"       : "Dec"
			}

		self.downames = {
			"0"        : "Sun",
			"1"        : "Mon",
			"2"        : "Tue",
			"3"        : "Wed",
			"4"        : "Thu",
			"5"        : "Fri",
			"6"        : "Sat",
			"7"        : "Sun"
			}
		

	def set_rights(self,user,uid,gid):
		self.user = user
		self.uid = uid
		self.gid = gid


	def get_type (self):
		return "crontab"
	
	def checkfield (self, expr, type):
		"""Verifies format of Crontab timefields

		Checks a single Crontab time expression.
		At first possibly contained alias names will be replaced by their
		corresponding numbers. After that every asterisk will be replaced by
		a »first to last« expression. Then the expression will be splitted
		into the komma separated subexpressions.

		Each subexpression will run through: 
		1. Check for stepwidth in range (if it has one)
		2. Check for validness of range-expression (if it is one)
		3. If it is no range: Check for simple numeric
		4. If it is numeric: Check if it's in range

		If one of this checks failed, an exception is raised. Otherwise it will
		do nothing. Therefore this function should be used with 
		a try/except construct.  
		"""

		timerange = self.timeranges[type]

		# Replace alias names only if no leading and following alphanumeric and 
		# no leading slash is present. Otherwise terms like »JanJan« or 
		# »1Feb« would give a valid check. Values after a slash are stepwidths
		# and shouldn't have an alias.
 		if type == "month": alias = self.monthnames.copy()
		elif type == "weekday": alias = self.downames.copy()
		else: alias = None
		if alias != None:
			while True:
				try: key,value = alias.popitem()
				except KeyError: break
				expr = re.sub("(?<!\w|/)" + value + "(?!\w)", key, expr)

		expr = expr.replace("*", str(min(timerange)) + "-" + str(max(timerange)) )
 		
		list = expr.split(",")
		rexp_step = re.compile("^(\d+-\d+)/(\d+)$")
		rexp_range = re.compile("^(\d+)-(\d+)$")

		for field in list:
			result = rexp_step.match(field)
			if  result != None:
				field = result.groups()[0]
				if int(result.groups()[1]) not in timerange:
					raise ValueError("stepwidth", self.timenames[type], _("Must be between %(min)s and %(max)s") % ( min(timerange),max(timerange) ) )

			result = rexp_range.match(field)
			if (result != None): 
				if (int(result.groups()[0]) not in timerange) or (int(result.groups()[1]) not in timerange):
					raise ValueError("range", self.timenames[type], _("Must be between %(min)s and %(max)s") % ( min(timerange),max(timerange) ) )
			elif field.isdigit() != True:
				raise ValueError("fixed", self.timenames[type], _("%s is not a number") % ( field ) )
			elif int(field) not in timerange:
				raise ValueError("fixed", self.timenames[type], _("Must be between %s and %s") % ( min(timerange),max(timerange) ) )


	def update (self,minute, hour, day, month, weekday,command, linenumber, parentiter, nooutput, title, icon = None):
		# update crontab
		record = minute + " " + hour + " " + day + " " + month + " " + weekday + " " + command
		#print "crontab:update:record=" + record
		
		easystring = self.__easy__ (minute, hour, day, month, weekday)

		if nooutput:
			record = record + " " + self.nooutputtag

		if title != None and icon == None:
			record = record + " # " + title
		elif title != None and icon != None:
			record = record + " # " + title + ", " + icon
		elif title == None and icon != None:
			title = _("Untitled")
			record = record + " # " + title + ", " + icon

	
		self.lines[linenumber] = record
		
		# TODO: let write trow an exception if failed
		self.__write__ ()
	
	
	def delete (self, linenumber, iter):
		number = 0
		newlines = list ()
		for line in self.lines:
			if number != linenumber:
				newlines.append (line)
			number = number + 1

		self.lines = newlines
		# TODO: let write trow an exception if failed
		self.__write__ ()
		
		
	def append (self, minute, hour, day, month, weekday, command, nooutput, title, icon = None):
		record = minute + " " + hour + " " + day + " " + month + " " + weekday + " " + command
		if nooutput:
			space = " "
			if record[len(record)-1] == " ":
				space = ""
			record = record + space + self.nooutputtag
		if title != None and icon == None:
			record = record + " # " + title
		elif title != None and icon != None:
			record = record + " # " + title + ", " + icon
		elif title == None and icon != None:
			record = record + " # " + _("Untitled") + ", " + icon

		self.lines.append (record)
		
		# TODO: let write trow an exception if failed
		self.__write__ ()
		

	#read tasks in crontab
	def read (self):
		
		data = []

		if self.root:
			execute = config.getCrontabbin () + " -l -u " + self.user
		else:
			execute = config.getCrontabbin () + " -l"
		
		linecount = 0
		self.lines = os.popen(execute).readlines()
		for line in self.lines:
			#read line and get info
			array_or_false = self.parse (line)
			if array_or_false != False:
				(minute, hour, day, month, weekday, command, title, icon) = array_or_false
				time = minute + " " + hour + " " + day + " " + month + " " + weekday

				#make the command smaller if the lenght is to long
				preview = self.__make_preview__ (command)
				
				#add task to treemodel in mainWindow
				
				data.append([title, self.__easy__ (minute, hour, day, month, weekday), preview, line, linecount, time, self, icon, "", "", "","", _("Recurrent"), "crontab"])
				
				
			linecount = linecount + 1	
		
		#print data
		return data


	def translate_frequency (self, frequency):

		if frequency == "minute":
			return _("minute")
		if frequency == "hour":
			return _("hour")
		if frequency == "day":
			return _("day")
		if frequency == "month":
			return _("month")
		if frequency == "weekday":
			return _("weekday")

		return frequency
	
	
	#get info out of task line
	def parse (self, line):
		if len (line) > 1 and line[0] != '#':
			"""
						   min        hour      day      month      wday     command   comment/title-icon or end
			The regexp:	('([^\s]+)\s([^\s]+)\s([^\s]+)\s([^\s]+)\s([^\s]+)\s([^#\n$]*)(\s#\s([^\n$]*)|$)')
			A record:	* * * * * echo $a >/dev/null 2>&1 # Untitled, /usr/share/icons/gnome/48x48/mimetypes/gnome-mime-application.png
			"""
			m = self.crontabRecordRegex.match(line)	
			if m != None:
					#print m.groups()
					minute = m.groups ()[0]
					hour = m.groups ()[1]
					day = m.groups ()[2]
					month = m.groups ()[3]
					weekday = m.groups ()[4]
					command = m.groups ()[5]

					#icon path is in comment of the task, this is the default
					icon = None
					
					#title is in comment of the task
					title = None
					if m.groups ()[7] != None:
						# TODO: check if works
						lastpiece = m.groups ()[7]
						keep = lastpiece.split (", ")
						title = keep[0]
						if len (keep) > 1:
							icon = keep[1]

					if title == None:
						title = _("Untitled")

					return minute, hour, day, month, weekday, command, title, icon
						
			else:
				print _("ERROR: Failed to parse crontab record")
		return False
		# TODO: throw exception

	
	def __easy__ (self, minute, hour, day, month, weekday):
		return lang.translate_crontab_easy (minute, hour, day, month, weekday)


	#create temp file with old tasks and new ones and then updates crontab
	def __write__ (self):
		tmpfile = tempfile.mkstemp ()
		fd, path = tmpfile
		tmp = os.fdopen(fd, 'w')
		count = 0
		for line in self.lines:

			## Ignore the first three comments:

			## DO NOT EDIT THIS FILE - edit the master and reinstall.
			## (/tmp/crontab.XXXXXX installed on Xxx Xxx  x xx:xx:xx xxxx)
			## (Cron version -- $Id$)

			if not (count < 3 and len(line) > 1 and line[0] == "#"):
				tmp.write (line)
				if line[len(line)-1] != '\n':
					tmp.write ("\n")
			count = count + 1

		tmp.close ()

		#replace crontab config with new one in file
		if self.root:
			# print config.getCrontabbin () + " -u " + self.ParentClass.user + " " + path
			os.system (config.getCrontabbin () + " " + path + " -u " + self.user)
		else:
			# print config.getCrontabbin () + " " + path
			os.system (config.getCrontabbin () + " " + path)

		os.unlink (path)
		
		
	#TODO: check into
	#if a command his lenght is to long the last part is removed 
	def __make_preview__ (self, str, preview_len = 0):
		if preview_len == 0:
			preview_len = self.preview_len
		cnt = 0
		result = ""
		for a in str:
			if cnt <= preview_len:
				result = result + a
			cnt = cnt + 1
		if cnt > preview_len:
			result = result + "..."
		return result

