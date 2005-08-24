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

class ScheduleApplet(gnome.applet.Applet):
	def __init__(self):
		self.__gobject_init__()
		

	def init (self):
		self.set_applet_flags(gnome.applet.EXPAND_MIRROR)
		
		self.toggle = gtk.ToggleButton()
		self.applet_tooltips = gtk.Tooltips()
		self.setup_menu_from_file (None, config.getGladedir() + "gnome-schedule-applet.xml", None, [(_("About"), self._showAboutDialog), ("Pref", self._openPrefs)])

		button_box = gtk.HBox()
		button_box.pack_start(gtk.Label(_("Schedule")))
		self.arrow = gtk.Arrow(gtk.ARROW_DOWN, gtk.SHADOW_IN)
		button_box.pack_start(self.arrow)
	
		self.toggle.add(button_box)
        
		self.add(self.toggle)
		self.toggle.connect("toggled", self._onToggle)
		self.toggle.connect("button-press-event", self._onButtonPress)
        
		self.show_all()

		return True
    
	def _showAboutDialog(self, uicomponent, verb):
		pass

	def _showPrefDialog(self):
        	pass
		
	def _openPrefs(self, uicomponent, verb):
		pass
        
	def _onToggle(self, toggle):
		if toggle.get_active():
			self.poster_window.positionWindow()            
			self.poster_window.show()
			self.poster.grab_focus()
		else:
			self.poster_window.hide()

	def _onEntryPosted(self):
		self.toggle.set_active(False)

	def _onButtonPress(self, toggle, event):
		if event.button != 1:
			toggle.stop_emission("button-press-event")
            
	def _createToolTip(self,client):
		pass

        

gobject.type_register(ScheduleApplet)


def foo(applet, iid):
    print "Returning schedule applet"
    return applet.init()
    
gnome.applet.bonobo_factory("OAFIID:GNOME_schedule_Factory", ScheduleApplet.__gtype__, "gnome-schedule", "0", foo)

print "Done waiting in factory, returning... If this seems wrong, perhaps there is another copy of the GNOME_schedule factory running?"
