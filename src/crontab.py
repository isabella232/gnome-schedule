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
import mainWindow
import re
import os

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
		self.crontabRecordRegex  = re.compile('([^\s]+)\s([^\s]+)\s([^\s]+)\s([^\s]+)\s([^\s]+)\s([^\s]+)(\s#\s(.*)|)')
		self.ParentClass = parent

	
		#reading crontab
		self.readCrontab()

		return

	def writeCrontab(self):
		if self.ParentClass.root:
			filename = "/tmp/crontab.XXXXXXXXXX"
			tmpfilename = mkstemp (filename)
			print tmpfilename
			print "sorry.. no support for writing other users crontabs yet.."
		else:
			crontab_w = os.popen('crontab', 'w')
			for line in self.lines
				crontab_w.write(line + "\n")

			crontab_w.close()
		return

	def updateLine (linenumber, record)
		self.lines[linenumber] = record
		self.writeCrontab ()

	def deleteLine (linenumber)
		self.lines.removeline (linenumber)
		self.writeCrontab ()

	def appendLine (record)
		self.lines.add (record)
		self.writeCrontab ()

	def readCrontab(self):
		if self.ParentClass.root:
			execute = "crontab -l -u " + self.user
		else:
			execute = "crontab -l"

		p = re.compile('^(.*)\s(.*)\s(.*)\s(.*)\s(.*)\s(.*)[\s#\s(.*)|]$')
		linecount = 0
		self.lines = os.popen(execute).readlines()
		for line in self.lines:
			array_or_false = self.parseRecord (line)
			if array_or_false != gtk.FALSE:
				(minute, hour, day, month, weekday, command, title) = array_or_false
				iter = self.ParentClass.treemodel.append([title, self.easyString (minute, hour, day, month, weekday), command, line, linecount])
			self.linecount = self.linecount + 1
		return

	def parseRecord (self, line):
		if len (line) > 1 and line[0] != '#':
			m = self.crontabRecordRegex.match(line)
			if m != None:
					print m.groups()
					minute = m.groups ()[0]
					hour = m.groups ()[1]
					day = m.groups ()[2]
					month = m.groups ()[3]
					weekday = m.groups ()[4]
					command = m.groups ()[5]
					title = m.groups ()[7]
					if title == None:
						title = "Untitled"

					return minute, hour, day, month, weekday, command, title
		return gtk.FALSE

	def amountApp (self, amount):
		if amount == "1":
			return "st."
		else:
			return "th."

	def easyString (self, minute, hour, day, month, weekday):
		if minute != "*" and hour == "*" and month == "*" and day == "*" and weekday == "*":
			return "Every " + minute + self.amountApp (minute) + " minute of every hour"
		if minute == "*" and hour != "*" and month == "*" and day == "*" and weekday == "*":
			return "Every " + hour + self.amountApp (hour) + " hour of the day"
		if minute == "*" and hour == "*" and month == "*" and day != "*" and weekday == "*":
			return "Every " + day + self.amountApp (day) + " day of the month"
		if minute == "*" and hour == "*" and month != "*" and day == "*" and weekday == "*":
			return "Every " + month + self.amountApp (month) + " month of the year"
		if minute == "*" and hour == "*" and month == "*" and day == "*" and weekday != "*":
			return "Every " + weekday + self.amountApp (weekday) + " day of the week"

		return minute + " " + hour + " " + day + " " + month + " " + weekday
