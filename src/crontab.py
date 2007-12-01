# crontab.py - code to interfere with crontab
# Copyright (C) 2004, 2005  Philip Van Hoof <me at pvanhoof dot be>
# Copyright (C) 2004 - 2008 Gaute Hope <eg at gaute dot vetsj dot com>
# Copyright (C) 2004, 2005  Kristof Vansant <de_lupus at pandora dot be>

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
		self.crontabdatafileversion = 2
		
		if os.path.exists(self.crontabdata) != True:
			if os.makedirs(self.crontabdata, 0700):
				pass
			else:
				pass
				# FAILED TO CREATE DATADIR
			
		
		
	def __setup_timespec__ (self):
		self.special = {
			"@reboot"  : '@reboot',
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
			"1"        : "jan",
			"2"        : "feb",
			"3"        : "mar",
			"4"        : "apr",
			"5"        : "may",
			"6"        : "jun",
			"7"        : "jul",
			"8"        : "aug",
			"9"        : "sep",
			"10"       : "oct",
			"11"       : "nov",
			"12"       : "dec"
			}
		self.monthnumbers = {
			"jan"	: "1",
			"feb"	: "2",
			"mar"	: "3",
			"apr"	: "4",
			"may"	: "5",
			"jun"	: "6",
			"jul"	: "7",
			"aug"	: "8",
			"sep"	: "9",
			"oct"	: "10",
			"nov"	: "11",
			"dec"	: "12"
			}
			
		self.downames = {
			"0"        : "sun",
			"1"        : "mon",
			"2"        : "tue",
			"3"        : "wed",
			"4"        : "thu",
			"5"        : "fri",
			"6"        : "sat",
			"7"        : "sun"
			}
		
		self.downumbers = {
			"sun"	: "0",
			"mon"	: "1",
			"tue"	: "2",
			"wed"	: "3",
			"thu"	: "4",
			"fri"	: "5",
			"sat"	: "6",
			"sun"	: "7"
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

		# reboot?
		if expr != "@reboot":
				
		
			timerange = self.timeranges[type]

			# Replace alias names only if no leading and following alphanumeric and 
			# no leading slash is present. Otherwise terms like "JanJan" or 
			# "1Feb" would give a valid check. Values after a slash are stepwidths
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
		if self.check_command (command) == False:
			return False
			
		# update crontab
		if minute == "@reboot":
			record = "@reboot " + command
		else:
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
					
				#print "last_id" + str (last_id)
				job_id = last_id + 1
				#print "job_id" + str (job_id)
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
		#print f
		fh = open (f, 'w')
		fh.truncate (1)
		fh.seek (0)
		fh.write ("ver=" + str(self.crontabdatafileversion) + "\n")
		fh.write ("title=" + title + "\n")
		fh.write ("icon=" + icon +  "\n")
		fh.write ("desc=" + desc + "\n")
		if nooutput:
			fh.write ("nooutput=1\n")
		else:
			fh.write ("nooutput=0\n")
		fh.close ()	

		self.lines[linenumber] = record
		
		# TODO: let write trow an exception if failed
		self.__write__ ()
	
	
	def delete (self, linenumber, iter, job_id):
		# delete file
		f = os.path.join (self.crontabdata, job_id)
		if os.access(f, os.F_OK):
			os.unlink (f)
		
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
		if self.check_command (command) == False:
			return False
			
		if minute == "@reboot":
			record = "@reboot " + command
		else:
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
			if r == "":
				last_id = 1
			else:
				last_id = int (r)
				
			
			job_id = last_id + 1
			
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
			
		fh = open (f, 'w')
		fh.truncate (1)
		fh.seek (0)
		fh.write ("ver=" + str(self.crontabdatafileversion) + "\n")
		fh.write ("title=" + title + "\n")
		fh.write ("icon=" + icon +  "\n")
		fh.write ("desc=" + desc + "\n")
		if nooutput:
			fh.write ("nooutput=1\n")
		else:
			fh.write ("nooutput=0\n")
		
		fh.close ()
				
		record = record + " # JOB_ID_" + str (job_id)
			
		self.lines.append (record)
		
		# TODO: let write trow an exception if failed
		self.__write__ ()
		

	#check command for problems
	def check_command (self, command):
		# check if % is part of the command and if it is escaped, and the escapor not escaped.
		i = command.find ("%")
		while i != -1:
			escaped = 0
			part = command[0:i]
			command = command[i + 1:]
			e = part.rfind ("\\")
			while (e != -1) and (e == len(part) - 1):
				escaped = escaped + 1
				part = part[0:len(part) - 1]
				e = part.rfind ("\\")
				
			if (escaped % 2 == 0):
				return False
				
			i = command.find ("%")
		return True
		
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
					(minute, hour, day, month, weekday, command, comment, job_id, title, icon, desc, nooutput) = array_or_false[1]
					
					time = minute + " " + hour + " " + day + " " + month + " " + weekday

					#make the command smaller if the lenght is to long
					preview = self.__make_preview__ (command)
				
					#add task to treemodel in mainWindow
					data.append([title, self.__easy__ (minute, hour, day, month, weekday), preview, line, linecount, time, self, icon, job_id, "", "","", _("Recurrent"), "crontab", nooutput])
				
				
			linecount = linecount + 1	
		
		
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
	def parse (self, line, nofile = False):
		# nofile: no datafile for title and icon available
		
		# Format of gnome-schedule job line
		# * * * * * ls -l >/dev/null >2&1 # JOB_ID_1
		
		# Return types
		# 0: Special expression
		# 1: Enivornment variable
		# 2: Standard expression
		# 3: Comment
		
		origline = line
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
			special_expression, line = self.get_exp_sec (line)
								
			if special_expression == "@reboot":
				minute = "@reboot"
				hour = "@reboot"
				dom = "@reboot"
				moy = "@reboot"
				dow = "@reboot"
			else:

				if special_expression in self.special:
					expr = self.special[special_expression]
					line = expr + " " + line

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
			# Crontab bug? Let's not support
			# dom behaves like minute
			"""
			dom = self.day
			if dom.isdigit() == False:
				dom = dom.lower ()
				for day in self.scheduler.downumbers:
					dom = dom.replace (day, self.scheduler.downumbers[day])
			"""
			try:
				self.__check_field_format__ (dom, "day")
			except ValueError, ex:
				print _("Failed to parse the Day of Month field, possibly due to a bug in crontab.")
				return
					
			# Month of Year
			moy, line = self.get_exp_sec (line)
			if moy.isdigit () == False:
				moy = moy.lower ()
				for m in self.monthnumbers:
					moy = moy.replace (m, self.monthnumbers[m])
					
			
			# Day of Week
			dow, line = self.get_exp_sec (line)
			if dow.isdigit() == False:
				dow = dow.lower ()
				for day in self.downumbers:
					dow = dow.replace (day, self.downumbers[day])
			
			
		
		command = line.strip ()
		
		# Retrive jobid
		i = comment.find ('JOB_ID_')
		if (i != -1):			
			job_id = int (comment[i + 7:].rstrip ())
		else:
			job_id = False
		
		# Retrive title and icon data
		if nofile == False:
			if job_id:
				ver, title, icon, desc, nooutput = self.get_job_data (job_id)
			else:
				ver = 1
				title = ""
				icon = ""
				desc = ""
				nooutput = 0
			
			if nooutput != 0:
				# remove devnull part of command
				# searching reverse, and only if nooutput is saved in the datafile
				pos = command.rfind (self.nooutputtag)
				if pos != -1:
					command = command[:pos]
			
			# support older datafiles/entries without removing the no output tag	
			if ver <= 1:
				# old version, no output declaration in datafile, migration
				pos = command.rfind (self.nooutputtag)
				if pos != -1:
					command = command[:pos]
					nooutput = 1
				else:
					nooutput = 0
			
			command = command.strip ()	
				
				
			return [2, [minute, hour, dom, moy, dow, command, comment, job_id, title, icon, desc, nooutput]]
		else:
			return minute, hour, dom, moy, dow, command
		
	def get_job_data (self, job_id):
		f = os.path.join (self.crontabdata, str (job_id))
		if os.access (f, os.R_OK):
			fh = open (f, 'r')
			d = fh.read ()
				
			ver_p = d.find ("ver=")
			if ver_p == -1:
				ver = 1
			else:
				ver_s = d[ver_p + 4:d.find ("\n")]
				d = d[d.find ("\n") + 1:]
				ver = int (ver_s)
				
			title = d[6:d.find ("\n")]
			d = d[d.find ("\n") + 1:]
			
			icon = d[5:d.find ("\n")]
			d = d[d.find ("\n") + 1:]
			
			desc = d[5:d.find ("\n")]
			d = d[d.find ("\n") + 1:]
			
			if ver >= 2:
				nooutput_str = d[9:d.find ("\n")]
				if (nooutput_str == "0") or (nooutput_str == "1"):
					nooutput = int (nooutput_str)
				else:
					nooutput = 0
			else:
				nooutput = 0
			
			fh.close ()
			
			return ver, title, icon, desc, nooutput
			
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

