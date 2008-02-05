# gnome-schedule.py - Contains the startup script for gnome-schedule
# Copyright (C) 2004, 2005  Philip Van Hoof <me at pvanhoof dot be>
# Copyright (C) 2004 - 2008 Gaute Hope <eg at gaute dot vetsj dot com>
# Copyright (C) 2004, 2005  Kristof Vansant <de_lupus at pandora dot be>

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

#python modules
import sys
import signal
import os

#custom modules
import config
import mainWindow


##
## I18N
##
import gettext
gettext.install(config.GETTEXT_PACKAGE(), config.GNOMELOCALEDIR(), unicode=1)

os.putenv ("POSIXLY_CORRECT", "enabled")

if __name__ == "__main__":
	signal.signal (signal.SIGINT, signal.SIG_DFL)

debug_flag = None
if '--debug' in sys.argv:
	debug_flag = 1

try:
	import pygtk
  	#tell pyGTK, if possible, that we want GTKv2
  	pygtk.require("2.0")
  
except:
  #Some distributions come with GTK2, but not pyGTK
  pass

try:
  import gtk
  import gtk.glade
  # TODO: Gnome specific
  import gnome
  import gnome.ui
	
except:
  print _("You need to install pyGTK or GTKv2,\n"
          "or set your PYTHONPATH correctly.\n"
          "try: export PYTHONPATH= ")
  sys.exit(1)

props = { gnome.PARAM_APP_DATADIR : config.getPrefix() + "/share" }
pr = gnome.program_init ("gnome-schedule", config.getVersion(), properties=props)

mainWindow = mainWindow.main(debug_flag, False, pr)

