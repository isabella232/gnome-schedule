#!/usr/bin/python2

# scheduleapplet.py: contains code for the gnome-schedule applet
# Copyright (C) 2004, 2005 Philip Van Hoof <me at freax dot org>
# Copyright (C) 2004, 2005 Gaute Hope <eg at gaute dot eu dot org>
# Copyright (C) 2004, 2005 Kristof Vansant <de_lupus at pandora dot be>

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
import pygtk
import gtk
import gnome.applet
import gobject
import sys

import config
import mainWindow

class ScheduleApplet(gnome.applet.Applet):
	
	
	
	def __init__(self, applet, iid):
		self.__gobject_init__()

		
			
		gnome.program_init ("gnome-schedule", config.getVersion())

		
		
		self.applet = applet

		self.__loadIcon__()

		self.ev_box = gtk.EventBox()
		self.ev_box.connect("button-press-event", self.button_press)
		self.ev_box.add(self.iconPixbuf)
		self.ev_box.show()
		

		self.applet.add(self.ev_box)
		
	
		
		
		self.applet.show_all()

	
	def __loadIcon__(self):
		if os.access("../pixmaps/gnome-schedule.png", os.F_OK):
			self.iconPixbuf = gtk.gdk.pixbuf_new_from_file ("../pixmaps/gnome-schedule.png")
		else:
			try:
				self.iconPixbuf = gtk.gdk.pixbuf_new_from_file (config.getImagedir() + "/gnome-schedule.png")
			except:
				print "ERROR: Could not load icon"

	def button_press(self, event):
		pass

		
	def cleanup(self,event):
		del self.applet

gobject.type_register(ScheduleApplet)

#factory
def schedule_applet_factory(applet, iid):
    ScheduleApplet(applet,iid)
    return True
    
gnome.applet.bonobo_factory("OAFIID:GNOME_schedule_Factory",
                                ScheduleApplet.__gtype__, 
                                "hello", "0", schedule_applet_factory)
