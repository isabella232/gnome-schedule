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
import time
import support
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
		template_name_c = self.replace (template_name)
		
		installed = support.gconf_client.get_string("/apps/gnome-schedule/templates/at/installed")
		newstring = installed
		if installed != None:
			first = gtk.TRUE
			newstring = "   "
			for t in string.split (installed, ", "):
				if t != template_name_c:
					if first == gtk.TRUE:
						newstring = t
						first = gtk.FALSE
					else:
						newstring = newstring + ", " + t

		support.gconf_client.unset("/apps/gnome-schedule/templates/at/%s/name" % (template_name_c))
		support.gconf_client.unset("/apps/gnome-schedule/templates/at/%s/icon_uri" % (template_name_c))

		support.gconf_client.unset("/apps/gnome-schedule/templates/at/%s/runat" % (template_name_c))
		support.gconf_client.unset("/apps/gnome-schedule/templates/at/%s/title" % (template_name_c))
		support.gconf_client.unset("/apps/gnome-schedule/templates/at/%s/command" % (template_name_c))
		
		if newstring == "   ":
			support.gconf_client.unset ("/apps/gnome-schedule/templates/at/installed")
		else:
			support.gconf_client.set_string("/apps/gnome-schedule/templates/at/installed", newstring)
	[0-9]

	def replace (self, template_name_c):
		for a in " ,	;:/\\\"'!@#$%^&*()-_+=|?<>.][{}":
			template_name_c = string.replace (template_name_c, a, "-")
		return template_name_c

	def savetemplate (self, template_name, runat, title, icon, command):
		template_name_c = self.replace (template_name)
		
		support.gconf_client.set_string("/apps/gnome-schedule/templates/at/%s/name" % (template_name_c), template_name)
		support.gconf_client.set_string("/apps/gnome-schedule/templates/at/%s/icon_uri" % (template_name_c), icon)
		support.gconf_client.set_string("/apps/gnome-schedule/templates/at/%s/runat" % (template_name_c), runat)
		support.gconf_client.set_string("/apps/gnome-schedule/templates/at/%s/title" % (template_name_c), title)
		support.gconf_client.set_string("/apps/gnome-schedule/templates/at/%s/command" % (template_name_c), command)
		
		installed = support.gconf_client.get_string("/apps/gnome-schedule/templates/at/installed")
		if installed == None:
			installed = template_name_c
		else:
			found = gtk.FALSE
			for t in string.split (installed, ", "):
				if t == template_name_c:
					found = gtk.TRUE

			if found == gtk.FALSE:
				installed = installed + ", " + template_name_c

		support.gconf_client.unset ("/apps/gnome-schedule/templates/at/installed")
		support.gconf_client.set_string("/apps/gnome-schedule/templates/at/installed", installed)
		return

	def gettemplatenames (self):
		#try:
			strlist = support.gconf_client.get_string("/apps/gnome-schedule/templates/at/installed")
			if strlist != None:
				list = string.split (strlist, ", ")
				return list
			else:
				return None
		#except:
		#	return None

	def gettemplate (self, template_name):
		try:
			icon_uri = support.gconf_client.get_string("/apps/gnome-schedule/templates/at/%s/icon_uri" % (template_name))
			
			runat = support.gconf_client.get_string("/apps/gnome-schedule/templates/at/%s/runat" % (template_name))
			title = support.gconf_client.get_string("/apps/gnome-schedule/templates/at/%s/title" % (template_name))
			name = support.gconf_client.get_string("/apps/gnome-schedule/templates/at/%s/name" % (template_name))
			command = support.gconf_client.get_string("/apps/gnome-schedule/templates/at/%s/command" % (template_name))
			return icon_uri,  runat, title, name, command
		except Exception, ex:
			return ex, ex, ex, ex, ex




	# Pass this to lang.py
	def translate_frequency (self, frequency):
		raise 'Not implemented'

	def geteditor (self):
		return self.editor



	def checkfield (self, runat):
		regexp1 = re.compile("([0-9][0-9]):([0-9][0-9])\ ([0-9][0-9][0-9][0-9])-([0-9][0-9])-([0-9][0-9])")
		regexp2 = re.compile("([0-9][0-9]):([0-9][0-9])")
		regexp3 = re.compile("([0-9][0-9][0-9][0-9])-([0-9][0-9])-([0-9][0-9])")
		runat_g1 = regexp1.match(runat)
		runat_g2 = regexp2.match(runat)
		runat_g3 = regexp3.match(runat)
		ctime = time.gmtime()
		cyear = ctime[0]
		cmonth = ctime[1]
		cday = ctime[2]
		chour = ctime[3]
		cminute = ctime[4]

	
		if runat_g1:

			(hour, minute, year, month, day) =  runat_g1.groups()
			hour = int(hour)
			minute = int(minute)
			year = int(year)
			month = int(month)
			day = int(day)

			if hour > 24 or hour < 0:
				return gtk.FALSE, "hour"
			
			if minute > 60 or minute < 0:
				return gtk.FALSE, "minute"
			
			if hour < chour or (hour == chour and minute < cminute): plussday = gtk.TRUE
			else: plussday = gtk.FALSE

			if year < cyear:
				return gtk.FALSE, "year"
			if month < cmonth:
				return gtk.FALSE, "month"

			if day < cday or (plussday == gtk.TRUE and day < cday + 1):
				return gtk.FALSE, "day"

		elif runat_g2:

			(hour, minute) =  runat_g2.groups()
			hour = int(hour)
			minute = int(minute)
			if hour > 24 or hour < 0:
				return gtk.FALSE, "hour"
	
			if minute > 60 or minute < 0:
				return gtk.FALSE, "minute"


		elif runat_g3:

			(year, month, day) =  runat_g3.groups()
			year = int(year)
			month = int(month)
			day = int(day)
			if year < cyear:
				return gtk.FALSE, "year"
			if month < cmonth:
				return gtk.FALSE, "month"
			if day < cday:
				return gtk.FALSE, "day"


		else:
			#lowercase
			runat = runat.lower()

			#some timespecs:
			days = ['sun','mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sunday','monday','tuesday','wednesday','thursday','friday','saturday']
			relative_days = ['tomorrow','next week','today']
			relative_hour = ['noon','teatime','midnight','next hour']
			relative_minute = ['next minute']
			relative_month = ['next month']
			
			if runat in days:
				pass
			elif runat in relative_days:
				pass
			elif runat in relative_hour:
				pass
			elif runat in relative_minute:
				pass
			elif runat in relative_month:
				pass
			else:
				return gtk.FALSE, "other"

		return gtk.TRUE, "ok"


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

	def delete (self, jobid, iter):
		if jobid:
			execute = config.getAtrmbin()+ " " + str(jobid)
			commands.getoutput(execute)
			result = self.ParentClass.treemodel.remove(iter)
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
		#print execute
		#print temp
		os.unlink (path)
		return temp

	def read (self):
		#do 'atq'
		execute = config.getAtqbin ()
		self.lines = os.popen(execute).readlines()
		count = 0
		for line in self.lines:
			array_or_false = self.parse (line)
			if array_or_false != gtk.FALSE:
				(job_id, date, time, class_id, user, lines, title, icon, prelen) = array_or_false

				if icon != None:
					try:
						icon_pix = gtk.gdk.pixbuf_new_from_file_at_size (icon, 21, 21)
						
					except:
						icon_pix = None
				else:
					icon_pix = None



				
				preview = self.make_preview (lines, prelen)
				
				#chopping of title and icon stuff from script
				lines = lines[prelen:]
					
				timestring = _("%s%s%s %s%s%s") % (_(""), date, _(""), _(""), time, _(""))
				timestring_show = "At " + timestring #_("%sAt%s%s") % (_(""), _(""), timestring, _(""))
				if self.ParentClass.root == 1:
					if self.ParentClass.user == user:
						iter = self.ParentClass.treemodel.append([title, timestring_show, preview, lines, int(job_id), timestring, icon_pix, self, icon, date, class_id, user, time, "Defined", "at"])
					else: 
						print "Record omitted, not current user"
				else:
					iter = self.ParentClass.treemodel.append([title, timestring_show, preview, lines, int(job_id), timestring, icon_pix, self, icon, date, class_id, user, time, "Defined", "at"])

				print "Read at job: " + str(job_id)
				count = count + 1
				#print title + " " + timestring + " " + preview + " " + job_id + " " + date + " " +  class_id + " " + user 
				# print int(job_id)

		#["None(not suported yet)", "12:50 2004-06-25", "", "35", "", "12:50", icon, at instance, "2004-06-25", "a", "drzap", "at"]
		print "-- Total at jobs: " + str(count)
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

		method = 2

		if method == 1:
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

		elif method == 2:
			string = " || {\n	 echo 'Execution directory inaccessible' >&2\n	 exit 1\n}\n"
			string_len = len(string)
			start = script.find(string)
			start = start + string_len

			script = script[start:]

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
			#print "short preview"
			result = lines[prelen:(-1 - prelen)]

		result = result.replace("\n",";")
		#remove ending newlines, not if result len = 0
		if len(result) <= 0:
			done = 1
		else:
			done = 0
		while done == 0:
			if result[-1] == ";":
				result = result[0:-1]
			else:
				done = 1
		#remove beginning newlines
		if len(result) <= 0:
			done = 1
		else:
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
					#if a date before this is selected the record is removed, this creates an error, and generally if the script is of zero length
					if len(script) == 0:
						done = 1
					else:
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
