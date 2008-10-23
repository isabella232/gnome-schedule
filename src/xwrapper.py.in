#! @PYTHON@
# xwrapper.py - wrapper around X applications
# Copyright (C) 2004 - 2008  Gaute Hope <eg at gaute dot vetsj dot com>

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

#python
import sys
import os
import pwd

# g-s modules
import config
import crontab


##
## I18N
##
import gettext
gettext.install(config.GETTEXT_PACKAGE(), config.GNOMELOCALEDIR(), unicode=1)

poscorrect_isset = os.getenv ("POSIXLY_CORRECT", False)
manual_poscorrect = False
if poscorrect_isset == False:
	os.putenv ("POSIXLY_CORRECT", "enabled")
	manual_poscorrect = True
	
if (len (sys.argv) < 4):
	print _("Minium number of arguments is 4.")
	sys.exit ()

if sys.argv[1] == "c":
	job_type = 0
else:
	print _("Unknown type of job: Wrapper only useful on crontab tasks.")
	sys.exit ()

try:
	job_id = int (sys.argv[2])
except:
	print _("Invalid job id.")
	sys.exit ()
	
if job_id < 0:
	print _("Invalid job id.")
	sys.exit ()

i = 4
command = ""
while (i < len (sys.argv)):
	command = command + sys.argv[i]
	i = i + 1

if len (command) < 2:
	print _("Invalid command, must be longer than 2.")
	sys.exit ()

uid = os.geteuid ()
gid = os.getegid ()
user = pwd.getpwuid (uid)[0]
home_dir = pwd.getpwuid (uid)[5]
user_shell = pwd.getpwuid (uid)[6]
if uid == 0:
	is_root = True
else:
	is_root = False

# get data
if job_type == 0:
	c = crontab.Crontab (is_root, user, uid, gid, home_dir)
	success, ver, title, desc, nooutput, xoutput, display = c.get_job_data (job_id)
	if success == False:
		print _("Could not get job data, might be an old version - try recreating the task")
		sys.exit ()
	
	print _("Launching %s.." % title)
	if (xoutput == 0):
		print _("xoutput==0: Why am I launched?")
		sys.exit ()
	if (len (display) < 2):
		print :("len(display)<2: No proper DISPLAY variable")
		sys.exit ()
		
	#### TODO: LAUNCH ####
	ex = "export DISPLAY=" + display + " " + command
	os.system (ex)
	sys.exit ()
	
else:
	print _("I will never be displayed.")
	sys.exit ()
	
print _("xwrapper.py: completed")
		
	


