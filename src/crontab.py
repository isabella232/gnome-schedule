# crontab.py - code to interfere with crontab
# Copyright (C) 2004, 2005 Philip Van Hoof <me at freax dot org>
# Copyright (C) 2004, 2005 Gaute Hope <eg at gaute dot eu dot org>

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

import gtk
import re
import os
import sys
import tempfile
import config
import mainWindow
import gobject
import crontabEditorHelper
import crontabEditor
import lang

##
## I18N
##
from rhpl.translate import _, N_
import rhpl.translate as translate
domain = 'gnome-schedule'
translate.textdomain (domain)
gtk.glade.bindtextdomain(domain)

class Crontab:
	def __init__(self, parent):
		self.crontabRecordRegex = re.compile('([^\s]+)\s([^\s]+)\s([^\s]+)\s([^\s]+)\s([^\s]+)\s([^#\n$]*)(\s#\s([^\n$]*)|$)')
		self.ParentClass = parent
		self.xml = self.ParentClass.xml
		self.nooutputtag = ">/dev/null 2>&1"

		self.ParentClass.treemodel = self.createtreemodel ()
		self.editorwidget = self.xml.get_widget("crontabEditor")
		self.editorhelperwidget = self.xml.get_widget("crontabEditorHelper")
		self.editor = crontabEditor.CrontabEditor (self.ParentClass, self)
		self.editorhelper = crontabEditorHelper.CrontabEditorHelper(self, self.editor)

		self.editorwidget.hide()
		self.editorhelperwidget.hide()


		self.read()
		return

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

	def geteditor (self):
		return self.editor

	def createtreemodel (self):
		# [0 Title, 1 Frequency, 2 Command, 3 Crontab record, 4 Line number, 5 Time]
		# ["Restart app", "Every day", "/opt/bin/restart.pl", "* 1 * * * /opt/bin/restart.pl # Title=Restart App", 3, 0 * * * *]
		return gtk.ListStore(gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_INT, gobject.TYPE_STRING)

	def switchview (self, mode = "simple", init = 0):
		if mode == "simple":
			#cleaning up columns
			if init != 1:
				i = 2
				while i > - 1:
					temp = self.ParentClass.treeview.get_column(i)
					self.ParentClass.treeview.remove_column(temp)
					i = i -1
				
			# Setting up the columns
			col = gtk.TreeViewColumn(_("Title"), gtk.CellRendererText(), text=0)
			self.ParentClass.treeview.append_column(col)
			col = gtk.TreeViewColumn(_("Frequency"), gtk.CellRendererText(), text=1)
			self.ParentClass.treeview.append_column(col)
			col = gtk.TreeViewColumn(_("Command"), gtk.CellRendererText(), text=2)
			col.set_spacing(235)
			self.ParentClass.treeview.append_column(col)

		elif mode == "advanced":
			#cleaning up columns
			if init != 1:
				i = 2
				while i > - 1:
					temp = self.ParentClass.treeview.get_column(i)
					self.ParentClass.treeview.remove_column(temp)
					i = i -1
			
			# Setting up the columns
			col = gtk.TreeViewColumn(_("Frequency"), gtk.CellRendererText(), text=5)
			self.ParentClass.treeview.append_column(col)
			col = gtk.TreeViewColumn(_("Command"), gtk.CellRendererText(), text=2)
			self.ParentClass.treeview.append_column(col)
			col = gtk.TreeViewColumn(_("Title"), gtk.CellRendererText(), text=0)
			col.set_spacing(235)
			self.ParentClass.treeview.append_column(col)	
		return

	def createpreview (self, minute, hour, day, month, weekday, command):
		return minute + " " + hour + " " + day + " " + month + " " + weekday + " " + command

	def getstandardvalue (self):
		return "* * * * * "+ _("command")

	def getfrequency (self, minute, hour, day, month, weekday):
		index = _("use advanced")
		# index = 0

		# Must be translatable, it's the actual content of the combobox-entry
		if minute == "*" and hour == "*" and month == "*" and day == "*" and weekday == "*":
			index = self.translate_frequency ("minute")
			# index = 1
		if minute == "0" and hour == "*" and month == "*" and day == "*" and weekday == "*":
			index = self.translate_frequency ("hour")
			# index = 2
		if minute == "0" and hour == "0" and month == "*" and day == "*" and weekday == "*":
			index = self.translate_frequency ("day")
			# index = 3
		if minute == "0" and hour == "0" and month == "*" and day == "1" and weekday == "*":
			index = self.translate_frequency ("month")
			# index = 4
		if minute == "0" and hour == "0" and month == "*" and day == "*" and weekday == "0":
			index = self.translate_frequency ("week")

		return index
		
	def checkfield (self, field, type, regex):
		# print type
		# print field

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
						raise Exception('fixed', self.translate_frequency (type), _("must be between 59 and 0"))
				if type=="hour":
					if num > 23 or num < 0:
						raise Exception('fixed', self.translate_frequency (type), _("must be between 23 and 0"))
				if type=="day":
					if num > 31 or num < 1:
						raise Exception('fixed', self.translate_frequency (type), _("must be between 31 and 1"))
				if type=="month":
					if num > 12 or num < 1:
						raise Exception('fixed', self.translate_frequency (type), _("must be between 12 and 1"))
				if type=="weekday":
					if num > 7 or num < 0:
						raise Exception('fixed', self.translate_frequency (type), _("must be between 7 and 0"))

			# 1-10 * * * * command
			if m.groups()[3] != None and m.groups()[4] != None:
				num1 = int (m.groups()[3])
				num2 = int (m.groups()[4])
				if type=="minute":
					if num1 > 59 or num1 < 0 or num2 > 59 or num2 < 0:
						raise Exception('range', self.translate_frequency (type), _("must be between 59 and 0"))
				if type=="hour":
					if num1 > 23 or num1 < 0 or num2 > 23 or num2 < 0:
						raise Exception('range', self.translate_frequency (type), _("must be between 23 and 0"))
				if type=="day":
					if num1 > 31 or num1 < 1 or num2 > 31 or num2 < 1:
						raise Exception('range', self.translate_frequency (type), _("must be between 31 and 1"))
				if type=="month":
					if num1 > 12 or num1 < 1 or num2 > 12 or num2 < 1:
						raise Exception('range', self.translate_frequency (type), _("must be between 12 and 1"))
				if type=="weekday":
					if num1 > 7 or num1 < 0 or num2 > 7 or num2 < 0:
						raise Exception('range', self.translate_frequency (type), _("must be between 7 and 0"))

			# 1,2,3,4 * * * * command
			if m.groups()[5] != None:
				thefield = m.groups()[5] + field[len(field)-1]
				# thefield = "1,2,3,4"
				fields = thefield.split (",")
				for field in fields:
					num = int (field)
					# print num
					if type=="minute":
						if num > 59 or num < 0:
							raise Exception('steps', self.translate_frequency (type), _("must be between 59 and 0"))
					if type=="hour":
						if num > 23 or num < 0:
							raise Exception('steps', self.translate_frequency (type), ("must be between 23 and 0"))
					if type=="day":
						if num > 31 or num < 1:
							raise Exception('steps', self.translate_frequency (type), _("must be between 31 and 1"))
					if type=="month":
						if num > 12 or num < 1:
							raise Exception('steps', self.translate_frequency (type), _("must be between 12 and 1"))
					if type=="weekday":
						if num > 7 or num < 0:
							raise Exception('steps', self.translate_frequency (type), _("must be between 7 and 0"))
		else:
			raise Exception(_("Unknown"), self.translate_frequency (type), _("Invalid"))

	def write (self):
		tmpfile = tempfile.mkstemp ("", "/tmp/crontab.", "/tmp")
		fd, path = tmpfile
		tmp = os.fdopen(fd, 'w')
		count = 0
		for line in self.lines:

			## Ignore the first three comments:

			## DO NOT EDIT THIS FILE - edit the master and reinstall.
			## (/tmp/crontab.XXXXXX installed on Xxx Xxx  x xx:xx:xx xxxx)
			## (Cron version -- $Id$)

			if count < 3 and len(line) > 1 and line[0] == "#":
				# print "Ignored:" + line
				pass
			else:
				tmp.write (line)
				if line[len(line)-1] != '\n':
					tmp.write ("\n")
			count = count + 1

		tmp.close ()

		if self.ParentClass.root:
			# print config.getCrontabbin () + " -u " + self.ParentClass.user + " " + path
			os.system (config.getCrontabbin () +" -u " + self.ParentClass.user + " " + path)
		else:
			# print config.getCrontabbin () + " " + path
			os.system (config.getCrontabbin () + " " + path)

		os.unlink (path)
		return

	def update (self, linenumber, record, parentiter, nooutput, title):
		# The GUI
		minute, hour, day, month, weekday, command, tit = self.parse (record)
		
		self.ParentClass.treemodel.set_value (parentiter, 0, title)
		easystring = self.easy (minute, hour, day, month, weekday)


		
		self.ParentClass.treemodel.set_value (parentiter, 1, easystring)
		if nooutput:
			space = " "
			if command[len(command)-1] == " ":
				space = ""		
			self.ParentClass.treemodel.set_value (parentiter, 2, command + space + self.nooutputtag)
			record = record + space + self.nooutputtag
		else:
			self.ParentClass.treemodel.set_value (parentiter, 2, command)
			
		self.ParentClass.treemodel.set_value (parentiter, 5, minute + " " + hour + " " + day + " " + month + " " + weekday)

		record = record + " # " + title	
		
		self.ParentClass.treemodel.set_value (parentiter, 3, record)
		# The crontab itself
		self.lines[linenumber] = record
		self.write ()

	def delete (self, linenumber):
		number = 0
		newlines = list ()
		for line in self.lines:
			if number != linenumber:
				newlines.append (line)
			#else:
				# print "remove"
			number = number + 1

		self.lines = newlines
		self.write ()

	def append (self, record, nooutput, title):
		if nooutput:
			space = " "
			if record[len(record)-1] == " ":
				space = ""
			record = record + space + self.nooutputtag
		
		record = record + " # " + title		
		self.lines.append (record)
		self.write ()

	def read (self):
		if self.ParentClass.root:
			execute = config.getCrontabbin () + " -l -u " + self.ParentClass.user
		else:
			execute = config.getCrontabbin () + " -l"

		p = re.compile('^(.*)\s(.*)\s(.*)\s(.*)\s(.*)\s(.*)[\s#\s(.*)|]$')
		self.linecount = 0
		self.lines = os.popen(execute).readlines()
		for line in self.lines:
			array_or_false = self.parse (line)
			if array_or_false != gtk.FALSE:
				(minute, hour, day, month, weekday, command, title) = array_or_false
				time = minute + " " + hour + " " + day + " " + month + " " + weekday
				iter = self.ParentClass.treemodel.append([title, self.easy (minute, hour, day, month, weekday), command, line, self.linecount, time])
			self.linecount = self.linecount + 1
		return

	def parse (self, line):
		if len (line) > 1 and line[0] != '#':
			m = self.crontabRecordRegex.match(line)
			if m != None:
					# print m.groups()
					minute = m.groups ()[0]
					hour = m.groups ()[1]
					day = m.groups ()[2]
					month = m.groups ()[3]
					weekday = m.groups ()[4]
					command = m.groups ()[5]
					title = m.groups ()[7]
					if title == None:
						title = _("Untitled")

					return minute, hour, day, month, weekday, command, title
		return gtk.FALSE

	def easy (self, minute, hour, day, month, weekday):
		return lang.translate_crontab_easy (minute, hour, day, month, weekday)
