# crontab.py - code to interfere with crontab
# Copyright (C) 2004, 2005 Philip Van Hoof <me at pvanhoof dot be>
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
import string

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
		self.__setup_timespec__()
		self.env_vars = [ ]
		
		self.crontabdata = os.path.expanduser ("~/.gnome/gnome-schedule/crontab")
		if os.path.exists(self.crontabdata) != True:
			if os.makedirs(self.crontabdata, 0700):
				pass
			else:
				pass
				# FAILED TO CREATE DATADIR
			
		
		
	def __setup_timespec__ (self):
		self.special = {
			"@reboot"  : '',
			"@hourly"  : '0 * * * *',
			"@daily"   : '0 0 * * *',
			"@weekly"  : '0 0 * * 0',
			"@monthly" : '0 0 1 * *',
			"@yearly"  : '0 0 1 1 *'
			}
				
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
		a "first to last" expression. Then the expression will be splitted
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
					raise ValueError("stepwidth", self.timenames[type], _("Must be between %(min)s and %(max)s") % { "min": min(timerange), "max": max(timerange) } )

			result = rexp_range.match(field)
			if (result != None): 
				if (int(result.groups()[0]) not in timerange) or (int(result.groups()[1]) not in timerange):
					raise ValueError("range", self.timenames[type], _("Must be between %(min)s and %(max)s") % { "min": min(timerange), "max": max(timerange) } )
			elif field.isdigit() != True:
				raise ValueError("fixed", self.timenames[type], _("%s is not a number") % ( field ) )
			elif int(field) not in timerange:
				raise ValueError("fixed", self.timenames[type], _("Must be between %(min)s and %(max)s") % { "min": min(timerange), "max": max(timerange) } )


	def update (self, minute, hour, day, month, weekday, command, linenumber, parentiter, nooutput, job_id, comment, title, icon, desc):
		# update crontab
		record = minute + " " + hour + " " + day + " " + month + " " + weekday + " " + command
		#print "crontab:update:record=" + record
		
		easystring = self.__easy__ (minute, hour, day, month, weekday)

		if nooutput:
			record = record + " " + self.nooutputtag
		
		if comment:
			record = record + " #" + comment
		
		if job_id == False:
			## Create a job_id for an existing task
			f = os.path.join (self.crontabdata, "last_id")
			if os.access (f, os.R_OK):
				fh = open (f, 'r+')
				r = fh.read ()
				if r == "":
					last_id = 1
				else:
					last_id = int (r)
					
				print "last_id" + str (last_id)
				job_id = last_id + 1
				print "job_id" + str (job_id)
				fh.seek (0)
				fh.truncate (1)
				fh.write ( str(job_id))
				fh.close ()
				
				
			else:
				job_id = 1
				fh = open (f, 'w')
				fh.write ('1')
				fh.close ()
				
			record = record + " # JOB_ID_" + str (job_id)
			
			
		if title == None:
			title = _("Untitled")
	
		f = os.path.join (self.crontabdata, str(job_id))
		print f
		fh = open (f, 'w')
		fh.truncate (1)
		fh.seek (0)
		fh.write ("title=" + title + "\n")
		fh.write ("icon=" + icon +  "\n")
		fh.write ("desc=" + desc + "\n")
		fh.close ()	

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
		
		
	def append (self, minute, hour, day, month, weekday, command, nooutput, title, icon = None, desc = None):
		record = minute + " " + hour + " " + day + " " + month + " " + weekday + " " + command
		if nooutput:
			space = " "
			if record[len(record)-1] == " ":
				space = ""
			record = record + space + self.nooutputtag
			
			if title == None:
				title = _("Untitled")
				
			if desc == None:
				desc = ""
			
			if icon == None:
				icon = ""
				
			# Create and write data file
			f = os.path.join (self.crontabdata, "last_id")
			if os.access (f, os.R_OK):
				fh = open (f, 'r+')
				r = fh.read ()
				print r
				if r == "":
					last_id = 1
				else:
					last_id = int (r)
					
				print "last_id" + str (last_id)
				job_id = last_id + 1
				print "job_id" + str (job_id)
				fh.seek (0)
				fh.truncate (1)
				fh.write ( str(job_id))
				fh.close ()
				
				
			else:
				job_id = 1
				fh = open (f, 'w')
				fh.write ('1')
				fh.close ()
			
			f = os.path.join (self.crontabdata, str(job_id))
			print f
			fh = open (f, 'w')
			fh.truncate (1)
			fh.seek (0)
			fh.write ("title=" + title + "\n")
			fh.write ("icon=" + icon +  "\n")
			fh.write ("desc=" + desc + "\n")
			fh.close ()
				
			record = record + " # JOB_ID_" + str (job_id)
			
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
				if array_or_false[0] == 2:
					(minute, hour, day, month, weekday, command, comment, job_id, title, icon, desc) = array_or_false[1]
					
					time = minute + " " + hour + " " + day + " " + month + " " + weekday

					#make the command smaller if the lenght is to long
					preview = self.__make_preview__ (command)
				
					#add task to treemodel in mainWindow
					data.append([title, self.__easy__ (minute, hour, day, month, weekday), preview, line, linecount, time, self, icon, job_id, "", "","", _("Recurrent"), "crontab"])
				
				
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
		# Format of gnome-schedule job line
		# * * * * * ls -l >/dev/null >2&1 # JOB_ID_1
		
		# Return types
		# 0: Special expression
		# 1: Enivornment variable
		# 2: Standard expression
		# 3: Comment
		
		line = line.lstrip()
		comment = ""
		
		if line	!= "":
			#print "Parsing line: " + line
			if line[0] == "#":
				comment = line[1:]
				line = ""
				return [3, comment]
			else:
				if (line.find ('#') != -1):
					line, comment = line.rsplit('#', 1)
				
			comment = comment.strip ()
			line = line.strip ()
		
		
		#special expressions
		if line == "":
			#Empty
			if comment != "":
				return [3, comment]
			else:
				return False
				
		elif line[0] == "@":
			if (line.find('\s')):
				i = line.find('\s')
			elif (line.find('\t')):
				i = line.find('\t')
				
			else:
				return False
			special_expression = line[0:i]
			line = line[i + 1:]
			
			## TODO: continue and return
			return [0, line]
	
		elif (line[0].isalpha()):
			if line[0] != '*':
				#ENVIRONMENT VARIABLE
				return [1, line]
		else:
			# Minute
			minute, line = self.get_exp_sec (line)
			
			# Hour
			hour, line = self.get_exp_sec (line)
		
			# Day of Month
			dom, line = self.get_exp_sec (line)
			
			# Month of Year
			moy, line = self.get_exp_sec (line)
			
			# Day of Week
			dow, line = self.get_exp_sec (line)
			
		
		command = line.strip ()
		
		# Retrive jobid
		if (comment.find ('JOB_ID_') != -1):
			i = comment.find ('JOB_ID_')
			job_id = int (comment[i + 7:].rstrip ())
		else:
			job_id = False
		
		# Retrive title and icon data
		if job_id:
			title, icon, desc = self.get_job_data (job_id)
		else:
			title = ""
			icon = ""
			desc = ""
			
		return [2, [minute, hour, dom, moy, dow, command, comment, job_id, title, icon, desc]]
		
	def get_job_data (self, job_id):
		f = os.path.join (self.crontabdata, str (job_id))
		if os.access (f, os.R_OK):
			fh = open (f, 'r')
			d = fh.read ()
				
			d = d.strip ()
			
			title = d[6:d.find ("\n")]
			d = d[d.find ("\n") + 1:]
			
			icon = d[5:d.find ("\n")]
			d = d[d.find ("\n") + 1:]
			
			desc = d[5:]
			fh.close ()
			
			return title, icon, desc
			
		else: 
			return "", "", ""
			
			
		
				
	def get_exp_sec (self, line):
		line = line.lstrip ()
		#print "line: \"" + line + "\""
		
		## find next whitespace
		i = 0
		found = False
		while (i <= len(line)) and (found == False):
			if line[i] in string.whitespace:
				found = True
				#print "found: " + str (i)
			else:
				i = i + 1
		sec = line[0:i]
		#print "sec: \"" + sec + "\""
		line = line[i + 1:]
		return sec, line
		
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

