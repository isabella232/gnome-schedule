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
import config
import string
import gettext
##
## I18N
##
#from rhpl.translate import _, N_
#import rhpl.translate as translate
domain = 'gnome-schedule'
#translate.textdomain (domain)
gettext.bindtextdomain(domain)
gettext.textdomain(domain)
_ = gettext.gettext
gtk.glade.bindtextdomain(domain)

class At:
	def __init__(self, parent):
		self.atRecordRegex = re.compile('([^\s]+)\s([^\s]+)\s([^\s]+)\s([^\s]+)\s([^\s]+)')
		self.atRecordRegexAdd = re.compile('([^\s]+)\s([^\s]+)\s')
		self.atRecordRegexAdded = re.compile('[^\s]+\s([0-9]+)\sat')

		#getting default prepended stuff by at
		execute = "echo > /tmp/tmpat && at tomorrow -f /tmp/tmpat && rm /tmp/tmpat"
		temp = commands.getoutput(execute)
		startjob = temp.find("job")
		temp = temp[startjob:]
		m = self.atRecordRegex.match(temp)
		job = m.groups ()[0]
		job_id = m.groups ()[1]
		execute = "at -c " + job_id
		at_pre = commands.getoutput(execute)
		remjob = commands.getoutput("atrm + " + job_id)
		self.at_pre_len = len(at_pre) - 1

		#default preview length
		self.preview_len = 50
			

		self.ParentClass = parent
		self.xml = self.ParentClass.xml

		self.read ()

		self.editorwidget = self.xml.get_widget("atEditor")
		self.editor = atEditor.AtEditor (self.ParentClass, self)

		self.editorwidget.hide()
	
		return

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


	def update (self, job_id, runat, command, title, icon):
		#remove old
		execute = "atrm " + str(job_id)
		commands.getoutput(execute)
		
		#add new
		tmpfile = tempfile.mkstemp ("", "/tmp/at.", "/tmp")
		fd, path = tmpfile
		tmp = os.fdopen(fd, 'w')
		if title:
			tmp.write("TITLE=" + title + "\n")
		else:
			tmp.write("TITLE=Untitled\n")
		if icon:
			tmp.write("ICON=" + icon + "\n")
		else:
			tmp.write("ICON=None\n")
		tmp.write (command + "\n")
		tmp.close ()
		execute = config.getAtbin() + " " + runat + " -f " + path
		temp = commands.getoutput(execute)
		os.unlink (path)

	def delete (self, jobid):
		if jobid:
			execute = config.getAtrmbin()+ " " + str(jobid)
			commands.getoutput(execute)
		return

	def append (self, runat, command, title, icon):
		tmpfile = tempfile.mkstemp ("", "/tmp/at.", "/tmp")
		fd, path = tmpfile
		tmp = os.fdopen(fd, 'w')
		if title:
			tmp.write("TITLE=" + title + "\n")
		else:
			tmp.write("TITLE=Untitled\n")
		if icon:
			tmp.write("ICON=" + icon + "\n")
		else:
			tmp.write("ICON=None\n")

		tmp.write (command + "\n")
		tmp.close ()
		execute = config.getAtbin() + " " + runat + " -f " + path
		temp = commands.getoutput(execute)
		os.unlink (path)
		return temp

	def read (self):
		#do 'atq'
		execute = config.getAtqbin ()
		self.lines = os.popen(execute).readlines()
		for line in self.lines:
			array_or_false = self.parse (line)
			if array_or_false != gtk.FALSE:
				(job_id, date, time, class_id, user, lines, title, icon, prelen) = array_or_false

				if icon != None:
					try:
						icon_pix = gtk.gdk.pixbuf_new_from_file (icon)
					except:
						icon_pix = None
				else:
					icon_pix = None

				
				preview = self.make_preview (lines, prelen)
				
				#chopping of title and icon stuff from script
				lines = lines[prelen:]
					
				timestring = _("%s%s%s %s%s%s") % (_(""), date, _(""), _(""), time, _(""))
				iter = self.ParentClass.treemodel.append([title, timestring, preview, lines, int(job_id), timestring, icon_pix, self, date, class_id, user, time, "Defined", "at"])

				print "Read at job: " + str(job_id)
				#print title + " " + timestring + " " + preview + " " + job_id + " " + date + " " +  class_id + " " + user 
				# print int(job_id)

		#["None(not suported yet)", "12:50 2004-06-25", "", "35", "", "12:50", icon, at instance, "2004-06-25", "a", "drzap", "at"]
		return

	def ignore (self, testline):
		found = gtk.FALSE
		for line in self.ignore_lines:
			if line == testline:
				found = gtk.TRUE
				break
		return found

	def prepare_script (self, script):
	
		# It looks like at prepends a bunch of stuff to each script
		# Luckily it delimits that using two newlines
		# So assuming that at never prepends two newlines unless
		# it's done prepending, we will start recording the custom commands
		# once the first two lines have been found

		#Later: It now seems like this is incorrect, and may vary upon distribution. I therefore determine the prepended stuff by making a test job and then removing the length of it. in gentoo it adds to newlines at the end of the script

		
		script = script[self.at_pre_len:]

		prelen = 0
		# If the string contains TITLE=
		titlestart = script.find ("TITLE=")
		if titlestart != -1:
			titleend = script.find("\n", titlestart)
			title = script[(titlestart + 6):titleend]
			#remeber the length to remove this from the preview
			prelen = len(title) + 7
		else:
			title = "Untitled"
		# If the string contains ICON=
		iconstart = script.find ("ICON=") 
		if iconstart != -1:
			iconend = script.find ("\n", iconstart)
			icon = script[(iconstart + 5):iconend]
			
			prelen = prelen + len(icon) + 6
			
		else:
			icon = "None"

		

		# Else this is a line of the script
		#else:
		#	newlines.append (line)
		#	print line
		
		
		return script, title, icon, prelen

	def make_preview (self, lines, prelen, preview_len = 0):
		if preview_len == 0:
			preview_len = self.preview_len
		try:
			if prelen:
				result = lines[(0 + prelen):(preview_len + prelen)]
			else:
				result = lines[0:preview_len]
		except:
			print "short preview"
			result = lines[prelen:(-1 - prelen)]

		result = result.replace("\n",";")
		#remove ending newlines
		done = 0
		while done == 0:
			if result[-1] == ";":
				result = result[0:-1]
			else:
				done = 1
		#remove beginning newlines
		done = 0
		while done == 0:
			if result[0] == ";":
				result = result[1:]
			else:
				done = 1

		if len(result) >= preview_len :
			result = result + "..."

		return result

	def parse (self, line, output = 0):
		if output == 0:
			if len (line) > 1 and line[0] != '#':
				m = self.atRecordRegex.match(line)
				if m != None:
					# print m.groups()
					job_id = m.groups ()[0]
					date = m.groups ()[1]
					time = m.groups ()[2]
					class_id = m.groups ()[3]
					user = m.groups ()[4]
					execute = config.getAtbin() + " -c " + job_id
					# read lines and detect starter
					script = os.popen(execute).read()
					script, title, icon, prelen = self.prepare_script (script)
					#removing ending newlines, but keep one
					done = 0
					while done == 0:
						if script[-1] == "\n":
							script = script[0:-1]
						else:
							done = 1

					return job_id, date, time, class_id, user, script, title, icon, prelen
		else:
			if len (line) > 1 and line[0] != '#':
				m = self.atRecordRegexAdd.match(line)
				if m != None:
					# print m.groups()
					job = m.groups ()[0]
					job_id = m.groups ()[1]
					return job_id

		return gtk.FALSE


	def easy (self, minute, hour, day, month, weekday):
		raise 'Not implemented'
