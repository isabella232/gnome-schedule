# at.py - code to interfere with at
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
import sys
import tempfile
import commands
import time
import datetime
import locale

#custom modules
import config


class At:
	def __init__(self,root,user,uid,gid,user_home_dir):
	
		#default preview length
		self.preview_len = 50
		self.root =	root
		self.set_rights(user,uid,gid, user_home_dir)
		self.user_home_dir = user_home_dir


		# 16       2006-01-08 13:01 a gaute
		# 7       Sun Jan  8 13:01:00 2006 a pvanhoof
		# 1	2006-04-26 08:54 a gaute
		# 14	2006-09-21 10:54 a gaute
		# 3	Tue May  8 01:01:00 2007 a gaute

		self.atRecordRegex = [ 
			re.compile('([0-9]+)\s([0-9]4-[0-9]2-[0-9]2)\s([0-9]2:[0-9]2)\s([a]1)\s(.*)'),
			re.compile('([^\s]+)\s((.*)\s(..:..:..\s....)|([^\s]+)\s([^\s]+))\s([^\s]+)\s([^\s]+)'), 
			re.compile('([^\s]+)\s([^\s]+)\s([^\s]+)\s([^\s]+)\s([^\s]+)'),
			re.compile('^([\d]+)[\t]([\w]{3,3}[\s][\w]{3,3}[\s]*[\d]+[\s][\d]{2,2}[:][\d]{2,2}[:][\d]{2,2}[\s][\d]{4,4})[\s]([\w])[\s]([\w]+)')
			]
			

		# after you add a job, this line is printed to stderr
		# job 10 at 2006-09-18 12:38
		self.atRecordRegexAdd = re.compile('^job\s([0-9]+)\sat')
		
		self.atRecordRegexAdded = re.compile('[^\s]+\s([0-9]+)\sat')
		self.nooutput = 0
		self.SCRIPT_DELIMITER = "###### ---- GNOME_SCHEDULE_SCRIPT_DELIMITER #####"
		
		self.atdatafileversion = 2
		self.atdata = self.user_home_dir + "/.gnome/gnome-schedule/at"
		if os.path.exists(self.atdata) != True:
			if os.makedirs(self.atdata, 0700):
				pass
			else:
				pass
				# FAILED TO CREATE DATADIR
				
		self.currentlocale = locale.getlocale (locale.LC_ALL)
		
	def set_rights(self,user,uid,gid, ud):
		self.user = user
		self.uid = uid
		self.gid = gid
		self.user_home_dir = ud
		self.atdata = self.user_home_dir + "/.gnome/gnome-schedule/at"

	
	def get_type (self):
		return "at"

	def standard_locale (self):
		locale.setlocale (locale.LC_ALL, 'C')
	
	def restore_locale (self):
		locale.setlocale (locale.LC_ALL, self.currentlocale)
		
	def parse (self, line, output = True):
		if (output == True):
			if len (line) > 1 and line[0] != '#':
				regexp = 0
				m = self.atRecordRegex[0].match(line)
				if m == None:
					m = self.atRecordRegex[3].match(line)
					if m != None:
						#print "regexp: 3"
						regexp = 3
						
					else:
						m = self.atRecordRegex[2].match(line)
						if m != None:
							#print "regexp: 2"
							regexp = 2
						else:
							m = self.atRecordRegex[1].match(line)
							if m != None:
								#print "regexp: 1"
								regexp = 1
							else:
								# Exception
								#print "regexp: failed"
								return False
						
				else:
					regexp = 0
					#print "regexp: 0"
					
					
				if m != None:
					#print m.groups ()
					
					if regexp == 3:
						job_id = m.groups ()[0]
						
						self.standard_locale ()
						try:
							dt = datetime.datetime.strptime (m.groups ()[1], "%a %b  %d %H:%M:%S %Y")
							#print "datetime, first try succeseeded"
						except:	
							try:
								dt = datetime.datetime.strptime (m.groups ()[1], "%a %b %d %H:%M:%S %Y")
								#print "datetime, second try succseeded"
							except:
								#print "datetime failed to parse"
								self.restore_locale ()
								return False
						
						self.restore_locale ()
					
						date = dt.strftime ("%Y-%m-%d")
						time = dt.strftime ("%H:%M:%S")
						class_id = m.groups ()[2]
						user = m.groups ()[3]
						
					else:
						job_id = m.groups ()[0]
						date = m.groups ()[4]
						time = m.groups ()[5]
						class_id = m.groups ()[6]
						user = m.groups ()[7]
					execute = config.getAtbin() + " -c " + job_id
					# read lines and detect starter
					script = os.popen(execute).read()
					script, prelen, dangerous = self.__prepare_script__ (script)
					
					title, desc = self.get_job_data (int (job_id))
					#removing ending newlines, but keep one
					#if a date in the past is selected the record is removed by at, this creates an error, and generally if the script is of zero length
					# TODO: complain about it as well
					
					if len(script) < 2:
						done = 1
					else:
						done = 0

					while done == 0:
						if script[-1] == "\n":
							script = script[0:-1]
						else:
							done = 1

					return job_id, date, time, class_id, user, script, title, prelen, dangerous
		elif (output == False):
			if len (line) > 1 and line[0] != '#':
				m = self.atRecordRegexAdd.search(line)
				#print "Parsing line: " + line
				if m != None:
					#print "Parse successfull, groups: "
					#print m.groups()
					job_id = m.groups ()[0]
					return int(job_id)
				else:
					return False

		return False
		# TODO: throw exception

	def get_job_data (self, job_id):
		f = os.path.join (self.atdata, str (job_id))
		if os.access (f, os.R_OK):
			fh = open (f, 'r')
			d = fh.read ()
				
			d = d.strip ()
			
			ver_p = d.find ("ver=")
			if ver_p == -1:
				ver = 1
			else:
				ver_s = d[ver_p + 4:d.find ("\n")]
				d = d[d.find ("\n") + 1:]
				ver = int (ver_s)
				
			title = d[6:d.find ("\n")]
			d = d[d.find ("\n") + 1:]
			
			# icons out
			if ver < 2 or ver == 3:
				icon = d[5:d.find ("\n")]
				d = d[d.find ("\n") + 1:]
			
			desc = d[5:d.find ("\n")]
			d = d[d.find ("\n") + 1:]
			
			fh.close ()
			
			return title, desc
			
		else: 
			return "", ""
			
	def write_job_data (self, job_id, title, desc):
		# Create and write data file
		f = os.path.join (self.atdata, str(job_id))
		#print f
		fh = open (f, 'w')
		fh.truncate (1)
		fh.seek (0)
		fh.write ("ver=" + str(self.atdatafileversion) + "\n")
		fh.write ("title=" + title + "\n")
		fh.write ("desc=" + desc + "\n")
		fh.close ()
			
	def checkfield (self, runat):
		#TODO: fix bug $0:19 2004-12-8$ not valid by regexp
		# print "$" + runat + "$"
		#regexp1 = re.compile("([0-9][0-9]):([0-9][0-9])\ ([0-9][0-9])\.([0-9][0-9])\.([0-9][0-9][0-9][0-9])")
		#print "Testing: " + runat
		regexp1 = re.compile ("([0-9][0-9]):([0-9][0-9])\ ([0-9][0-9][0-9][0-9])\-([0-9][0-9])\-([0-9][0-9])")
		regexp2 = re.compile("([0-9][0-9]):([0-9][0-9])")
		regexp3 = re.compile("([0-9][0-9])\.([0-9][0-9])\.([0-9][0-9][0-9][0-9])")
		
		runat_g1 = regexp1.match(runat)
		runat_g2 = regexp2.match(runat)
		runat_g3 = regexp3.match(runat)
		ctime = time.localtime()
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
			
			if month > 12 or month < 0:
				return False, "month"
				
			if day > 31 or day < 0:
				return False, "day"
				
			if year < 0:
				return False, "year"
				
			if year >= cyear: 
				if year == cyear:
					syear = True
					if (month >= cmonth):
						if month == cmonth:
							smonth = True
							if day >= cday:
								if day == cday:
									sday = True
									if hour >= chour:
										if hour == chour:
											shour = True
											if minute <= cminute:
												return False, "minute"
										else:
											shour = False
									else:
										return False, "hour"
								else:
									sday = False
							else:
								return False, "day"
						else:
							smonth = False
					else:
						return False, "month"
				else:
					syear = False
			else:
				return False, "year"

		elif runat_g2:

			(hour, minute) =  runat_g2.groups()
			hour = int(hour)
			minute = int(minute)
			if hour > 24 or hour < 0:
				return False, "hour"
	
			if minute > 60 or minute < 0:
				return False, "minute"


		elif runat_g3:

			(day, month, year) =  runat_g3.groups()
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

		
	def append (self, runat, command, title):
		tmpfile = tempfile.mkstemp ()
		fd, path = tmpfile
		tmp = os.fdopen(fd, 'w')
		tmp.write (self.SCRIPT_DELIMITER + "\n")
		tmp.write (command + "\n")
		tmp.close ()
		
		temp = None

		self.standard_locale ()
		if self.root == 1:
			if self.user != "root":
				#changes the ownership
				os.chown(path, self.uid, self.gid)
				execute = config.getSubin() + " " + self.user + " -c \"" + config.getAtbin() + " " + runat + " -f " + path + " && exit\""
				child_stdin, child_stdout, child_stderr = os.popen3(execute)
			else:
				execute = config.getAtbin() + " " + runat + " -f " + path
				child_stdin, child_stdout, child_stderr = os.popen3(execute)
		else:
			execute = config.getAtbin() + " " + runat + " -f " + path
			child_stdin, child_stdout, child_stderr = os.popen3(execute)


		self.restore_locale ()
		err = child_stderr.readlines ()
		job_id = 0
		for line in err:
			t = self.parse (line, False)
			if t != False:
				job_id = t
		
		#print job_id
		
		desc = ""
		self.write_job_data (job_id, title, desc)
		
		os.unlink (path)


	def update (self, job_id, runat, command, title):
		#print "update" + str (job_id) + runat + command + title
		#remove old
		f = os.path.join (self.atdata, str (job_id))
		if os.access (f, os.F_OK):
			os.unlink (f)
		execute = config.getAtrmbin()+ " " + str(job_id)
		commands.getoutput(execute)
		
		#add new
		tmpfile = tempfile.mkstemp ()
		fd, path = tmpfile
		tmp = os.fdopen(fd, 'w')
		#if title:
	#		tmp.write("TITLE=" + title + "\n")
	#	else:
#			tmp.write("TITLE=Untitled\n")
#		if icon:
#			tmp.write("ICON=" + icon + "\n")
#		else:
#			tmp.write("ICON=None\n")
		tmp.write (self.SCRIPT_DELIMITER + "\n")
		tmp.write (command + "\n")
		tmp.close ()

		self.standard_locale ()
		if self.root == 1:
			if self.user != "root":
				#changes the ownership
				os.chown(path, self.uid, self.gid)
				execute = config.getSubin() + " " + self.ParentClass.user + " -c \"" + config.getAtbin() + " " + runat + " -f " + path + " && exit\""
				child_stdin, child_stdout, child_stderr = os.popen3(execute)
			else:
				execute = config.getAtbin() + " " + runat + " -f " + path
				child_stdin, child_stdout, child_stderr = os.popen3(execute)
		else:
			execute = config.getAtbin() + " " + runat + " -f " + path
			child_stdin, child_stdout, child_stderr = os.popen3(execute)

		self.restore_locale ()
		err = child_stderr.readlines ()
		job_id = 0
		for line in err:
			t = self.parse (line, False)
			if t != False:
				job_id = t
		
		#print job_id
		
		desc = ""
		self.write_job_data (job_id, title, desc)
		
		os.unlink (path)
		

	def delete (self, job_id, iter):
		if job_id:
			# delete file
			f = os.path.join (self.atdata, str(job_id))
			if os.access(f, os.F_OK):
				os.unlink (f)
			execute = config.getAtrmbin()+ " " + str(job_id)
			commands.getoutput(execute)
			
				
	def read (self):
		
		data = []
		#do 'atq'
		execute = config.getAtqbin ()
		self.lines = os.popen(execute).readlines()
		for line in self.lines:
			
			array_or_false = self.parse (line)
			#print array_or_false
			if array_or_false != False:
				(job_id, date, time, class_id, user, lines, title, prelen, dangerous) = array_or_false

			
				preview = self.__make_preview__ (lines, prelen)
				if dangerous == 1:
						preview = _("DANGEROUS PARSE: %(preview)s") % {'preview':  preview}
				#chopping of script delimiter
				lines = lines[prelen:]
				lines.strip ()
					
				timestring = "%s %s" % (date, time)
				# TODO: localize time and date formats
				timestring_show = _("On %(date)s at %(time)s") % {'date': date, 'time': time}
				
				# TODO: looks like it could be one append
				if self.root == 1:
					if self.user == user:
						data.append([title, timestring_show, preview, lines, int(job_id), timestring, self, None, date, class_id, user, time, _("Once"), "at", self.nooutput, timestring])
					else: 
						#print "Record omitted, not current user"
						pass
				else:
					data.append([title, timestring_show, preview, lines, int(job_id), timestring, self, None, date, class_id, user, time, _("Once"), "at", self.nooutput, timestring])

				#print _("added %(id)s") % { "id": job_id	}
			else:
				print _("Warning: a line in atq's output didn't parse")	
		
		return data

	
	def __prepare_script__ (self, script):
	
		# It looks like at prepends a bunch of stuff to each script
		# Luckily it delimits that using two newlines
		# So assuming that at never prepends two newlines unless
		# it's done prepending, we will start recording the custom commands
		# once the first two lines have been found

		#Later: It now seems like this is incorrect, and may vary upon distribution. I therefore determine the prepended stuff by making a test job and then removing the length of it. in gentoo it adds to newlines at the end of the script

		dangerous = 0
		string = self.SCRIPT_DELIMITER
		scriptstart = script.find(string)
		#print titlestart
		if scriptstart != -1:
			script = script[scriptstart:]				
			prelen = len(self.SCRIPT_DELIMITER) + 1

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
				icon = None 

		return script, prelen, dangerous


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
		
