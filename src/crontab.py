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
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.

#python modules
import re
import os
import tempfile

#custom modules
import lang
import config

##
## I18N
##
import gettext
domain = 'gnome-schedule'
gettext.bindtextdomain(domain)
gettext.textdomain(domain)
_ = gettext.gettext


class Crontab:
	def __init__(self):
		#default preview length
		self.preview_len = 50
		
		self.nooutputtag = ">/dev/null 2>&1"
		self.crontabRecordRegex = re.compile('([^\s]+)\s([^\s]+)\s([^\s]+)\s([^\s]+)\s([^\s]+)\s([^#\n$]*)(\s#\s([^\n$]*)|$)')
		
	def set_rights(self, root, user, uid, gid):
		self.root =	root
		self.user = user
		self.uid = uid
		self.gid = gid
	
	def get_type (self):
		return "crontab"
	
	def checkfield (self, field, type, regex):
		m = regex.match (field)
		num = 0
		num1 = 0
		num2 = 0
		if m != None:
			# print m.groups()
			# 10 * * * * command
			# */2 * * * * command
			if m.groups()[1] != None or m.groups()[2] != None:
				if m.groups()[1] != None:
					num = int (m.groups()[1])
				else:
					num = int (m.groups()[2])
				# Should not be translatable!
				if type=="minute":
					if num > 59 or num < 0:
						raise Exception('fixed', self.translate_frequency (type), _("must be between 0 and 59"))
				if type=="hour":
					if num > 23 or num < 0:
						raise Exception('fixed', self.translate_frequency (type), _("must be between 0 and 23"))
				if type=="day":
					if num > 31 or num < 1:
						raise Exception('fixed', self.translate_frequency (type), _("must be between 1 and 31"))
				if type=="month":
					if num > 12 or num < 1:
						raise Exception('fixed', self.translate_frequency (type), _("must be between 1 and 12"))
				if type=="weekday":
					if num > 7 or num < 0:
						raise Exception('fixed', self.translate_frequency (type), _("must be between 0 and 7"))

			# 1-10 * * * * command
			if m.groups()[3] != None and m.groups()[4] != None:
				num1 = int (m.groups()[3])
				num2 = int (m.groups()[4])
				if type=="minute":
					if num1 > 59 or num1 < 0 or num2 > 59 or num2 < 0:
						raise Exception('range', self.translate_frequency (type), _("must be between 0 and 59"))
				if type=="hour":
					if num1 > 23 or num1 < 0 or num2 > 23 or num2 < 0:
						raise Exception('range', self.translate_frequency (type), _("must be between 0 and 23"))
				if type=="day":
					if num1 > 31 or num1 < 1 or num2 > 31 or num2 < 1:
						raise Exception('range', self.translate_frequency (type), _("must be between 1 and 31"))
				if type=="month":
					if num1 > 12 or num1 < 1 or num2 > 12 or num2 < 1:
						raise Exception('range', self.translate_frequency (type), _("must be between 1 and 12"))
				if type=="weekday":
					if num1 > 7 or num1 < 0 or num2 > 7 or num2 < 0:
						raise Exception('range', self.translate_frequency (type), _("must be between 0 and 7"))

			# 1,2,3,4 * * * * command
			if m.groups()[5] != None:
				fields = m.groups()[5].split (",")
				for fieldx in fields:
					try:
						num = int (fieldx)
					except:
						raise Exception('steps', self.translate_frequency (type), _("%s is not a number") % (fieldx))

					if type=="minute":
						if num > 59 or num < 0:
							raise Exception('steps', self.translate_frequency (type), _("must be between 0 and 59"))
					if type=="hour":
						if num > 23 or num < 0:
							raise Exception('steps', self.translate_frequency (type), ("must be between 0 and 23"))
					if type=="day":
						if num > 31 or num < 1:
							raise Exception('steps', self.translate_frequency (type), _("must be between 1 and 31"))
					if type=="month":
						if num > 12 or num < 1:
							raise Exception('steps', self.translate_frequency (type), _("must be between 1 and 12"))
					if type=="weekday":
						if num > 7 or num < 0:
							raise Exception('steps', self.translate_frequency (type), _("must be between 0 and 7"))
		else:
			raise Exception(_("Unknown"), self.translate_frequency (type), _("Invalid"))


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
	
		##if written:
		#self.ParentClass.treemodel.set_value (parentiter, 1, easystring)
		#if nooutput:
		#	space = " "
		#	if command[len(command)-1] == " ":
		#		space = ""
		#	self.ParentClass.treemodel.set_value (parentiter, 2, self.__make_preview__ (command + space + self.nooutputtag))
		#else:
		#		self.ParentClass.treemodel.set_value (parentiter, 2, self.__make_preview__ (command))
			
		#self.ParentClass.treemodel.set_value (parentiter, 5, minute + " " + hour + " " + day + " " + month + " " + weekday)

		#self.ParentClass.treemodel.set_value (parentiter, 0, title)
		#if icon != None:
		#	self.ParentClass.treemodel.set_value (parentiter, 6, gtk.gdk.pixbuf_new_from_file_at_size (icon, 21, 21))

		#self.ParentClass.treemodel.set_value (parentiter, 3, record)
		##


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

		# TODO: getRoot withit
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
				
				data.append([title, self.__easy__ (minute, hour, day, month, weekday), preview, line, linecount, time, self, icon, "", "", "","", _("Frequency"), "crontab"])
				
				
			linecount = linecount + 1	
		
		print data
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
					# TODO: shouldn't be gnome specific
					icon = "/usr/share/icons/gnome/48x48/mimetypes/gnome-mime-application.png"
					
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
				print "ERROR: Failed to parse crontab record"
		return False

	
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
		
		#TODO needs exception handler
		

	#if a command his lenght is to long the last part is removed 
	#XXX if the beginning is just a long path it's maybe better to cut there
	#XXX instead of in the front .../bin/updatedb instead of /dfdffd/bin/upda...
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

