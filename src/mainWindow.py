# mainWindow.py - mainWindow of the crontab configuration tool
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
import gobject
import string
import os
import re
import gtk.glade
import addWindow
import setuserWindow
import crontab
import sys

from os import popen

##
## I18N
##
from rhpl.translate import _, N_
import rhpl.translate as translate
domain = 'gnome-schedule'
translate.textdomain (domain)
gtk.glade.bindtextdomain(domain)

##
## Icon for windows
##
iconPixbuf = None
try:
	iconPixbuf = gtk.gdk.pixbuf_new_from_file("/usr/share/gnome-schedule/pixmaps/gnome-schedule.png")
except:
	pass




##
## The MainWindow class
##
class main:
	def __init__(self, debug_flag=None):
		self.debug_flag = debug_flag
		# Setting up the glade stuff
		if os.access("gnome-schedule.glade", os.F_OK):
			self.xml = gtk.glade.XML ("gnome-schedule.glade", domain="gnome-schedule")
		else:
			self.xml = gtk.glade.XML ("/usr/share/gnome-schedule/gnome-schedule.glade", domain="gnome-schedule")

		self.readUser()


		self.widget = self.xml.get_widget("mainWindow")
		self.treeview = self.xml.get_widget("treeview")
		self.add_button = self.xml.get_widget ("add_button")
		self.prop_button = self.xml.get_widget ("prop_button")
		self.del_button = self.xml.get_widget ("del_button")
		self.help_button = self.xml.get_widget ("help_button")

		self.treeview.set_rules_hint(gtk.TRUE)
		self.treeview.columns_autosize()
		self.add_scheduled_task_menu = self.xml.get_widget ("add_scheduled_task_menu")
		self.properties_menu = self.xml.get_widget ("properties_menu")
		self.delete_menu = self.xml.get_widget ("delete_menu")
		self.set_user_menu = self.xml.get_widget ("set_user_menu")
		self.quit_menu = self.xml.get_widget ("quit_menu")
		self.advanced_menu = self.xml.get_widget ("advanced_menu")
		self.about_menu = self.xml.get_widget ("about_menu")

		self.xml.signal_connect("on_advanced_menu_activate", self.on_advanced_menu_activate)
		self.xml.signal_connect("on_about_menu_activate", self.on_about_menu_activate)
		self.xml.signal_connect("on_add_scheduled_task_menu_activate", self.on_add_scheduled_task_menu_activate)
		self.xml.signal_connect("on_properties_menu_activate", self.on_properties_menu_activate)
		self.xml.signal_connect("on_delete_menu_activate", self.on_delete_menu_activate)
		self.xml.signal_connect("on_quit_menu_activate", self.quit)
		self.xml.signal_connect("on_manual_menu_activate", self.on_manual_menu_activate)
		self.xml.signal_connect("on_add_button_clicked", self.on_add_button_clicked)
		self.xml.signal_connect("on_prop_button_clicked", self.on_prop_button_clicked)
		self.xml.signal_connect("on_del_button_clicked", self.on_del_button_clicked)
		self.xml.signal_connect("on_help_button_clicked", self.on_help_button_clicked)
		self.xml.signal_connect("on_btnExit_clicked", self.quit)

		if self.root != 1:
			self.set_user_menu.visible = gtk.FALSE
		else:
			self.xml.signal_connect("on_set_user_menu_activate", self.on_set_user_menu_activate)

		self.widget.connect("delete-event", self.quit)

		self.init_treeview()

		#initializing the crontab
		self.crontab = crontab.Crontab(self)

		#add window
		self.addwidget = self.xml.get_widget("addWindow")
		self.addwidget.hide()
		self.addWindow = addWindow.AddWindow (self, self.crontab)

		self.setuserwidget = self.xml.get_widget("setuserWindow")
		self.setuserwidget.hide()
		self.setuserWindow = setuserWindow.SetuserWindow (self)




		gtk.mainloop()
		return

	def init_treeview(self):
		# [0 Title, 1 Frequency, 2 Command, 3 Crontab record, 4 Line number]
		# ["Restart app", "Every day", "/opt/bin/restart.pl", "* 1 * * * /opt/bin/restart.pl # Title=Restart App", 3]
		self.treemodel = gtk.ListStore(gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_INT)
		self.treeview.set_model (self.treemodel)

		# Setting up the columns
		self.col = gtk.TreeViewColumn(_("Title"), gtk.CellRendererText(), text=0)
		self.treeview.append_column(self.col)
		self.col = gtk.TreeViewColumn(_("Frequency"), gtk.CellRendererText(), text=1)
		self.treeview.append_column(self.col)
		self.col = gtk.TreeViewColumn(_("Command"), gtk.CellRendererText(), text=2)
		self.col.set_spacing(235)
		self.treeview.append_column(self.col)

		self.widget.show_all()

		# self.treeview.get_selection().connect("changed", self.onTreeViewSelectRow)
		self.treeview.get_selection().unselect_all()

		return


	def quit (self, *args):
		gtk.mainquit()

	def readUser (self):
		UID = os.geteuid()
		if UID == 0:
			self.root = 1

			if len(sys.argv) == 2:
				self.user = sys.argv[1]
			else:
				self.user = "root"
		else:
			self.root = 0
			self.user = os.environ['USER']
		return







	def on_add_button_clicked (self, *args):
		self.on_add_scheduled_task_menu_activate (self, args)
		pass

	def on_prop_button_clicked (self, *args):
		self.on_properties_menu_activate (self, args)
		pass

	def on_del_button_clicked (self, *args):
		self.on_delete_menu_activate (self, args)
		pass

	def on_help_button_clicked (self, *args):
		self.on_manual_menu_activate (self, args)
		pass


	def on_advanced_menu_activate (self, *args):
		print "TODO: Advanced"
		pass

	def on_about_menu_activate (self, *args):
		dlg = gtk.MessageDialog (None, 0, gtk.MESSAGE_INFO, gtk.BUTTONS_OK,
			_("System Schedule @VERSION@\n A graphical interface for configuring the system schedule"))
		dlg.set_title(_("About"))
		dlg.set_default_size(100, 100)
		dlg.set_position (gtk.WIN_POS_CENTER)
		dlg.set_border_width(2)
		dlg.set_modal(gtk.TRUE)
		dlg.set_transient_for(self.main_window)
		dlg.set_icon(iconPixbuf)
		rc = dlg.run()
		dlg.destroy()


	def on_add_scheduled_task_menu_activate (self, *args):
		self.addWindow.showAddWindow ()
		pass

	def on_set_user_menu_activate (self, *args):
		self.setuserWindow.ShowSetuserWindow ()

	def on_properties_menu_activate (self, *args):
		store, iter = self.treeview.get_selection().get_selected()
		if iter != None:
			record = self.treemodel.get_value(iter, 3)
			linenumber = self.treemodel.get_value(iter, 4)
			self.addWindow.showEditWindow (record, linenumber, iter)
		pass

	def on_delete_menu_activate (self, *args):
		pass

	def on_quit_menu_activate (self, *args):
		pass

	def on_manual_menu_activate (self, *args):
		pass
