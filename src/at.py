# at.py - code to interfere with at
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
import sys
import tempfile
import commands
import time

#custom modules
import config


##
## I18N
##
import gettext
domain = 'gnome-schedule'
gettext.bindtextdomain(domain)
gettext.textdomain(domain)
_ = gettext.gettext


class At:
	def __init__(self,root,user,uid,gid):
	
		#default preview length
		self.preview_len = 50
		self.root =	root
		self.set_rights(user,uid,gid)

		self.atRecordRegex = re.compile('([^\s]+)\s([^\s]+)\s([^\s]+)\s([^\s]+)\s([^\s]+)')
		self.atRecordRegexAdd = re.compile('([^\s]+)\s([^\s]+)\s')
		self.atRecordRegexAdded = re.compile('[^\s]+\s([0-9]+)\sat')
		
	def set_rights(self,user,uid,gid):
		self.user = user
		self.uid = uid
		self.gid = gid

	
	def get_type (self):
		return "at"

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
					script, title, icon, prelen, dangerous = self.__prepare_script__ (script)
					#removing ending newlines, but keep one
					#if a date before this is selected the record is removed, this creates an error, and generally if the script is of zero length
					if len(script) < 2:
						done = 1
					else:
						done = 0

					while done == 0:
						if script[-1] == "\n":
							script = script[0:-1]
						else:
							done = 1

					return job_id, date, time, class_id, user, script, title, icon, prelen, dangerous
		else:
			if len (line) > 1 and line[0] != '#':
				m = self.atRecordRegexAdd.match(line)
				if m != None:
					# print m.groups()
					job = m.groups ()[0]
					job_id = m.groups ()[1]
					return job_id

		return False


	def checkfield (self, runat):
		#TODO: fix bug $0:19 2004-12-8$ not valid by regexp
		print "$" + runat + "$"
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
				return False, "hour"
			
			if minute > 60 or minute < 0:
				return False, "minute"
			
			if hour < chour or (hour == chour and minute < cminute): plussday = True
			else: plussday = False

			if year < cyear:
				return False, "year"

			if (month < cmonth and year <= cyear):
				return False, "month"


			if (day < cday and month <= cmonth) or (plussday == True and day < cday + 1 and month <= cmonth):
				return False, "day"

		elif runat_g2:

			(hour, minute) =  runat_g2.groups()
			hour = int(hour)
			minute = int(minute)
			if hour > 24 or hour < 0:
				return False, "hour"
	
			if minute > 60 or minute < 0:
				return False, "minute"


		elif runat_g3:

			(year, month, day) =  runat_g3.groups()
			year = int(year)
			month = int(month)
			day = int(day)
			if year < cyear:
				return False, "year"
			if month < cmonth:
				return False, "month"
			if day < cday:
				return False, "day"

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
				return False, "other"

		return True, "ok"
	
	#TODO merge code of append and update	
	def append (self, runat, command, title, icon):
		tmpfile = tempfile.mkstemp ()
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
		
		temp = None

		# TODO: get this info
		if self.root == 1:
			if self.user != "root":
				#changes the ownership
				os.chown(path, self.uid, self.gid)
				execute = config.getSubin() + " " + self.user + " -c \"" + config.getAtbin() + " " + runat + " -f " + path + " && exit\""
				temp = commands.getoutput(execute)
			else:
				execute = config.getAtbin() + " " + runat + " -f " + path
				temp = commands.getoutput(execute)
		else:
			execute = config.getAtbin() + " " + runat + " -f " + path
			temp = commands.getoutput(execute)

		os.unlink (path)
		return temp


	def update (self, job_id, runat, command, title, icon):
		#remove old
		execute = config.getAtrmbin() + " " + str(job_id)
		commands.getoutput(execute)
		
		#add new
		tmpfile = tempfile.mkstemp ()
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

		# TODO: get this info
		if self.root == 1:
			if self.user != "root":
				#changes the ownership
				os.chown(path, self.uid, self.gid)
				execute = config.getSubin() + " " + self.ParentClass.user + " -c \"" + config.getAtbin() + " " + runat + " -f " + path + " && exit\""
				temp = commands.getoutput(execute)

		else:
			execute = config.getAtbin() + " " + runat + " -f " + path
			temp = commands.getoutput(execute)

		os.unlink (path)
		

	def delete (self, jobid, iter):
		if jobid:
			execute = config.getAtrmbin()+ " " + str(jobid)
			commands.getoutput(execute)
			
				
	
	def read (self):
		
		data = []
		#do 'atq'
		execute = config.getAtqbin ()
		self.lines = os.popen(execute).readlines()
		print self.lines
		for line in self.lines:
			
			array_or_false = self.parse (line)
			if array_or_false != False:
				(job_id, date, time, class_id, user, lines, title, icon, prelen, dangerous) = array_or_false

				#if icon != None:
				#	try:
				#		icon_pix = gtk.gdk.pixbuf_new_from_file_at_size (icon, 21, 21)
				#		
				#	except:
				#		icon_pix = None
				#else:
				#	icon_pix = None

				preview = self.__make_preview__ (lines, prelen)
				if dangerous == 1:
						preview = "DANGEROUS PARSE: " + preview
				#chopping of title and icon stuff from script
				lines = lines[prelen:]
					
				timestring = _("%s%s%s %s%s%s") % ("", date, "", "", time, "")
				timestring_show = _("At ") + timestring #_("%sAt%s%s") % (_(""), _(""), timestring, _(""))
				
				# TODO: looks like it could be one append
				if self.root == 1:
					if self.user == user:
						data.append([title, timestring_show, preview, lines, int(job_id), timestring, self, icon, date, class_id, user, time, _("Defined"), "at"])
					else: 
						#print "Record omitted, not current user"
						pass
				else:
					data.append([title, timestring_show, preview, lines, int(job_id), timestring, self, icon, date, class_id, user, time, "Defined", "at"])

				print "added" + job_id	
			
		return data

			

	def __prepare_script__ (self, script):
	
		# It looks like at prepends a bunch of stuff to each script
		# Luckily it delimits that using two newlines
		# So assuming that at never prepends two newlines unless
		# it's done prepending, we will start recording the custom commands
		# once the first two lines have been found

		#Later: It now seems like this is incorrect, and may vary upon distribution. I therefore determine the prepended stuff by making a test job and then removing the length of it. in gentoo it adds to newlines at the end of the script

		dangerous = 0
		string = "TITLE="
		titlestart = script.find(string)
		#print titlestart
		if titlestart != -1:
			script = script[titlestart:]
			prelen = 0

			# If the string contains TITLE=
			string = "TITLE="
			titlestart = script.find(string)
			if titlestart != -1:
				titleend = script.find("\n", titlestart)
				title = script[titlestart + len(string):titleend]
				#remeber the length to remove this from the preview
				prelen = len(title) + 7

			# If the string contains ICON=
			string = "ICON="
			iconstart = script.find ("ICON=") 
			if iconstart != -1:
				iconend = script.find ("\n", iconstart)
				icon = script[(iconstart + len(string)):iconend]
				prelen = prelen + len(icon) + 6
			
			else:
				# TODO: shouldn't be gnome specific
				icon = "/usr/share/icons/gnome/48x48/mimetypes/gnome-mime-application.png"
		else:
			#print "method 2"
			dangerous = 1
			#tries method 2

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
				# TODO: shouldn't be gnome specific
				icon = "/usr/share/icons/gnome/48x48/mimetypes/gnome-mime-application.png"

		return script, title, icon, prelen, dangerous


	def __make_preview__ (self, lines, prelen, preview_len = 0):
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
		if len(result) < 2:
			done = 1
		else:
			done = 0
		while done == 0:
			if result[-1] == ";":
				result = result[0:-1]
			else:
				done = 1
		#remove beginning newlines
		if len(result) < 2:
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
