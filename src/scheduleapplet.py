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
pygtk.require("2.0")
import gtk
import gtk.glade
import gnome
import gnome.ui
import gnome.applet
import gobject
import sys
import signal
import os

import config
import mainWindow


class ScheduleApplet(gnome.applet.Applet):
	
	
	
	def __init__(self, applet, iid):
		self.__gobject_init__()
		import gettext
		gettext.install(config.GETTEXT_PACKAGE(), config.GNOMELOCALEDIR(), unicode=1)

		
			
		gnome.program_init ("gnome-schedule", config.getVersion())

		
		
		self.applet = applet

		self.__loadIcon__()
		

		self.ev_box = gtk.EventBox()
		self.image = gtk.Image()
		self.image.set_from_pixbuf(self.iconPixbuf)
		self.ev_box.add(self.image)
		self.ev_box.show()
		

		self.applet.add(self.ev_box)
		
	

		self.create_menu()
		
	
		

		
		
	
		
		
		self.applet.show_all()

		self.main_loaded = False

	
	def __loadIcon__(self):
		if os.access("../pixmaps/gnome-schedule.png", os.F_OK):
			self.iconPixbuf = gtk.gdk.pixbuf_new_from_file_at_size ("../pixmaps/gnome-schedule.png", 19, 19)
		else:
			try:
				self.iconPixbuf = gtk.gdk.pixbuf_new_from_file_at_size (config.getImagedir() + "/gnome-schedule.png", 19, 19)
			except:
				print "ERROR: Could not load icon"

	def read_xml(self):
		if os.access("gnome-schedule-applet.xml", os.F_OK):
			f = open("gnome-schedule-applet.xml", 'r')
		else:
			try:
				f = open(config.getGladedir() + "/gnome-schedule-applet.xml", 'r')
			except:
				print "ERROR: Could not load menu xml file"

		xml = f.read()
		f.close()
		return xml

		
	def create_menu(self):
		self.verbs = [ 	("show_main", self.show_main_window), 
						("add", self.add_task),
						("help", self.show_help),
						("about", self.show_about)
					]
		self.propxml = self.read_xml()
		self.applet.setup_menu(self.propxml, self.verbs, None)
			
		
				

		

	def show_main_window(self, *args):
		if self.main_loaded == False:
			self.main_loaded = True
			self.main_window = mainWindow.main(None, True)
		else:
			self.main_window.schedule_reload("all")
			self.main_window.widget.show()

	def add_task(self, *args):
		if self.main_loaded == False:
			self.show_main_window()
			self.main_window.widget.hide()
		self.main_window.on_add_scheduled_task_menu_activate()

		
	def show_help(self, *args):
		if self.main_loaded == False:
			self.show_main_window()
			self.main_window.widget.hide()
		self.main_window.on_manual_menu_activate()

	def show_about(self, *args):
		if self.main_loaded == False:
			self.show_main_window()
			self.main_window.widget.hide()
		self.main_window.on_about_menu_activate()

gobject.type_register(ScheduleApplet)

#factory
def schedule_applet_factory(applet, iid):
    ScheduleApplet(applet,iid)
    return True
  
if len(sys.argv) > 1 and sys.argv[1] == "run-in-window":
    main_window = gtk.Window(gtk.WINDOW_TOPLEVEL)
    main_window.set_title("Gnome schedule applet")
    main_window.connect("destroy", gtk.main_quit) 
    app = gnome.applet.Applet()
    schedule_applet_factory(app, None)
    app.reparent(main_window)
    main_window.show_all()
    gtk.main()

else: 
	gnome.applet.bonobo_factory("OAFIID:GNOME_schedule_Factory",
                                ScheduleApplet.__gtype__, 
                                "hello", "0", schedule_applet_factory)
