#!/usr/bin/python2

# gnome-schedule.py - Contains the startup script for gnome-schedule
# Copyright (C) 2004, 2005 Philip Van Hoof <me at freax dot org>
# Copyright (C) 2004, 2005 Gaute Hope <eg at gaute dot eu dot org>

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

import sys
import signal
import config

if __name__ == "__main__":
	signal.signal (signal.SIGINT, signal.SIG_DFL)

debug_flag = None
if '--debug' in sys.argv:
	debug_flag = 1

try:
	import gtk
	import gnome
	import gnome.ui
	gnome.program_init ("gnome-schedule", config.getVersion())
except:
	print ("An error occured while loading the gtk, gnome and gnome.ui modules.")
	sys.exit(0)


import mainWindow
mainWindow = mainWindow.main(debug_flag)
