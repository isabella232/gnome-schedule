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
import lang
import atEditor
import commands



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
		self.atRecordRegexAdd = re.compile('([^\s]+)\s([^\s]+)\s')

		self.ParentClass = parent
		
		self.xml = self.ParentClass.xml

		#init at
		self.init ()

		#reading at
		self.read ()


		self.editorwidget = self.xml.get_widget("atEditor")
#		self.editorhelperwidget = self.xml.get_widget("crontabEditorHelper")
		self.editor = atEditor.AtEditor (self.ParentClass, self)
		#self.editorhelper = crontabEditorHelper.CrontabEditorHelper(self, self.editor)

		self.editorwidget.hide()
	
		return

	def init (self):
		#find common start of all scripts with a test job
		runat = "tomorrow"
		command = ""
		tmpfile = tempfile.mkstemp ("", "/tmp/at.", "/tmp")
		fd, path = tmpfile
		tmp = os.fdopen(fd, 'w')
		tmp.write (command + "\n")
		execute = "at " + runat + " -f " + path
		line = commands.getoutput(execute)
		tmp.close ()
		os.unlink (path)
		#get output and jobid
		job_id = self.parse(line, 1)
		
		#get the job
		execute = "at -c " + job_id
		self.atPre = commands.getoutput(execute)
				
		#delete it
		execute = "atrm " + job_id
		commands.getoutput(execute)

	def removetemplate (self, template_name):
		raise 'Not implemented'

	def savetemplate (self, template_name, record, nooutput, title, icon):
		raise 'Not implemented'

	def gettemplatenames (self):
		raise 'Not implemented'

	def gettemplate (self, template_name):
		raise 'Not implemented'

	# Pass this to lang.py
	def translate_frequency (self, frequency):
		raise 'Not implemented'

	def geteditor (self):
		return self.editor


	def createpreview (self, minute, hour, day, month, weekday, command):
		raise 'Not implemented'

	def getstandardvalue (self):
		raise 'Not implemented'
		
	def getfrequency (self, minute, hour, day, month, weekday):
		raise 'Not implemented'

	def checkfield (self, field, type, regex):
		raise Exception('Abstract method please override','','','')


	def update (self, runat, command, job_id):
		#remove old
		execute = "atrm " + job_id
		commands.getoutput(execute)
		
		#add new
		tmpfile = tempfile.mkstemp ("", "/tmp/at.", "/tmp")
		fd, path = tmpfile
		tmp = os.fdopen(fd, 'w')
		tmp.write (command + "\n")
		tmp.close ()
		execute = "at " + runat + " -f " + path
		temp = commands.getoutput(execute)
		os.unlink (path)

	def delete (self, jobid):
		if jobid:
			execute = "atrm " + jobid
		commands.getoutput(execute)
		
			
		return

	def append (self, runat, command):
		tmpfile = tempfile.mkstemp ("", "/tmp/at.", "/tmp")
		fd, path = tmpfile
		tmp = os.fdopen(fd, 'w')
		tmp.write (command + "\n")
		tmp.close ()
		execute = "at " + runat + " -f " + path
		temp = commands.getoutput(execute)
		os.unlink (path)


		return

	def read (self):
		#do 'atq'
		execute = "atq"
		self.lines = os.popen(execute).readlines()
		for line in self.lines:
			array_or_false = self.parse (line)
			if array_or_false != gtk.FALSE:
				(job_id, date, time, class_id, user, title, command) = array_or_false
				icon_pix = None
				iter = self.ParentClass.treemodel.append([title, time + " " + date, command, int(job_id), 0, time, icon_pix, self, date, class_id, user, "Defined"])
				print int(job_id)

		#["None(not suported yet)", "12:50 2004-06-25", "", "35", "", "12:50", icon, at instance, "2004-06-25", "a", "drzap", "at"]
		
		return
	
	def parse (self, line, output = 0):
		if output == 0:
			if len (line) > 1 and line[0] != '#':
				m = self.atRecordRegex.match(line)
				if m != None:
					print m.groups()
					job_id = m.groups ()[0]
					date = m.groups ()[1]
					time = m.groups ()[2]
					class_id = m.groups ()[3]
					user = m.groups ()[4]
					command = "Not supported"
					title = "Not supported"
					return job_id, date, time, class_id, user, title, command
		else:
			if len (line) > 1 and line[0] != '#':
				m = self.atRecordRegexAdd.match(line)
				if m != None:
					print m.groups()
					job = m.groups ()[0]
					job_id = m.groups ()[1]
					return job_id
		#left unchanged, the fields should be: user, job title, and id
		#would probably have to do a specific job check for each job 
		return gtk.FALSE


	def easy (self, minute, hour, day, month, weekday):
		raise 'Not implemented'
