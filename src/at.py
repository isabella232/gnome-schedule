# at.py - code to interfere with at
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
import sys
import tempfile
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

class At:
	def __init__(self, parent):
		self.atRecordRegex = re.compile('([^\s]+)\s([^\s]+)\s([^\s]+)\s([^\s]+)\s([^\s]+)')
		self.ParentClass = parent
		self.ParentClass.treemodel = self.createtreemodel ()
		self.xml = self.ParentClass.xml
		#reading at
		self.read ()


		#just for debugging
		self.editorwidget = self.xml.get_widget("crontabEditor")
		self.editorhelperwidget = self.xml.get_widget("crontabEditorHelper")
		self.editor = crontabEditor.CrontabEditor (self.ParentClass, self)
		self.editorhelper = crontabEditorHelper.CrontabEditorHelper(self, self.editor)

		return

	def geteditor (self):
		return self.editor

	def createtreemodel (self):
		# [0 Title, 1 date, 2 time, 3 class, 4 id, 5 user, 6 command preview(?)]
		# ["get file", "2004-06-17", "20:17", "a", 24, "wget http://..."]
		return gtk.ListStore(gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_STRING)
		
	def switchview (self, mode = "simple", init = 0):
		if mode == "simple":
			#cleaning up columns
			if init != 1:
				i = 4
				while i > - 1:
					temp = self.ParentClass.treeview.get_column(i)
					self.ParentClass.treeview.remove_column(temp)
					i = i -1
				
			# Setting up the columns
			self.col = gtk.TreeViewColumn(_("Title"), gtk.CellRendererText(), text=0)
			self.ParentClass.treeview.append_column(self.col)
			self.col = gtk.TreeViewColumn(_("Date"), gtk.CellRendererText(), text=1)
			self.ParentClass.treeview.append_column(self.col)
			self.col = gtk.TreeViewColumn(_("Time"), gtk.CellRendererText(), text=2)
			self.ParentClass.treeview.append_column(self.col)
			self.col = gtk.TreeViewColumn(_("Preview"), gtk.CellRendererText(), text=6)
			self.col.set_spacing(235)
			self.ParentClass.treeview.append_column(self.col)


		elif mode == "advanced":
			#cleaning up columns
			if init != 1:
				i = 3
				while i > - 1:
					temp = self.ParentClass.treeview.get_column(i)
					self.ParentClass.treeview.remove_column(temp)
					i = i -1
			
			# Setting up the columns
			self.col = gtk.TreeViewColumn(_("Date"), gtk.CellRendererText(), text=1)
			self.ParentClass.treeview.append_column(self.col)
			self.col = gtk.TreeViewColumn(_("Time"), gtk.CellRendererText(), text=2)
			self.ParentClass.treeview.append_column(self.col)
			self.col = gtk.TreeViewColumn(_("Id"), gtk.CellRendererText(), text=4)
			self.ParentClass.treeview.append_column(self.col)	
			self.col = gtk.TreeViewColumn(_("Class"), gtk.CellRendererText(), text=3)
			self.ParentClass.treeview.append_column(self.col)	
			self.col = gtk.TreeViewColumn(_("Preview"), gtk.CellRendererText(), text=6)
			self.col.set_spacing(235)
			self.ParentClass.treeview.append_column(self.col)

		
		return
		
	def createpreview (self, minute, hour, day, month, weekday, command):
		raise 'Not implemented'

	def getstandardvalue (self):
		raise 'Not implemented'
		
	def getfrequency (self, minute, hour, day, month, weekday):
		raise 'Not implemented'

	def checkfield (self, field, type, regex):
		raise Exception('Abstract method please override','','','')

	def write (self):
		raise 'Not implemented'

	def update (self, linenumber, record, nooutput, title):
		raise 'Not implemented'

	def delete (self, jobid):
		if jobid:
			execute = "atrm " + jobid
		#execute this
		#reread or delete from the list(preferably)		
			
		return

	def append (self, record, nooutput, title):
		raise 'Not implemented'

	def read (self):
		#do 'atq'
		execute = "atq"
		self.linecount = 0
		self.lines = os.popen(execute).readlines()
		for line in self.lines:
			array_or_false = self.parse (line)
			if array_or_false != gtk.FALSE:
				(job_id, date, time, class_id, user, command, title) = array_or_false
				iter = self.ParentClass.treemodel.append([title, date, time, class_id, job_id, user, command])
			self.linecount = self.linecount + 1
		return

	def parse (self, line):
		if len (line) > 1 and line[0] != '#':
			m = self.atRecordRegex.match(line)
			if m != None:
					print m.groups()
					job_id = m.groups ()[0]
					date = m.groups ()[1]
					time = m.groups ()[2]
					class_id = m.groups ()[3]
					user = m.groups ()[4]
					command = "no"
					title = "no"

					return job_id, date, time, class_id, user, command, title
		#left unchanged, the fields should be: user, job title, and id
		#would probably have to do a specific job check for each job 
		return gtk.FALSE

	def amountApp (self, amount):
		if amount == "1":
			return _("st.")
		else:
			return _("th.")

	def valToTimeVal (self, val):
		if val == "0" or val == "1" or val == "2" or val == "3" or val == "4" or val == "5" or val == "6" or val == "7" or val == "8" or val == "9":
			return "0" + val
		else:
			return val

	def easy (self, minute, hour, day, month, weekday):
		raise 'Not implemented'
