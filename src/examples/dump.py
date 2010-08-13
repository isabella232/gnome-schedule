# dump.py - This just dumps crontab tasks with their info to stdout 
# Copyright (C) 2010  Gaute Hope <eg at gaute dot vetsj dot com>
#
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

sys.path.append ("../")
sys.path.append ("./")

# g-s modules
import config
import crontab

# NEEDED FOR SUBMODULES
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

uid = os.geteuid ()
gid = os.getegid ()
user = pwd.getpwuid (uid)[0]
home_dir = pwd.getpwuid (uid)[5]
user_shell = pwd.getpwuid (uid)[6]
if uid == 0: is_root = True
else: is_root = False

# CRONTAB
c = crontab.Crontab (is_root, user, uid, gid, home_dir)
tasks = c.read ()
print "Crontab tasks:"
for task in tasks:
  print "Task:         ", task[0]
  print "When:         ", task[1], "[", task[5], "]"
  print "Command:      ", task[2]
  print "Crontab line: ", task[3].strip()
  print "Job ID:       ", task[8]
  print "Type:         ", task[12], "[", task[13], "]"
  print ""

sys.exit ()

