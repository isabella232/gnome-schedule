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
import gnome
import gobject
import string
import os
import re
import gtk.glade
import support
import gconf
import setuserWindow
import schedule
import crontab
import at
import addWindow
import sys
import time
import config
import editor
import gettext
import time
from os import popen

##
## I18N
##
#from rhpl.translate import _, N_
#import rhpl.translate as translate
domain = 'gnome-schedule'
#translate.textdomain (domain)
gettext.bindtextdomain(domain)
gettext.textdomain(domain)
_ = gettext.gettext
gtk.glade.bindtextdomain(domain)

##
## Icon for windows
##
iconPixbuf = None
try:
	# print config.getImagedir() + "/gnome-schedule.png"
	iconPixbuf = gtk.gdk.pixbuf_new_from_file(config.getImagedir() + "/gnome-schedule.png")
except:
	pass


##
## The MainWindow class
##
class main:
	def __init__(self, debug_flag=None):
		self.debug_flag = debug_flag

		if os.access("gnome-schedule.glade", os.F_OK):
			self.xml = gtk.glade.XML ("gnome-schedule.glade", domain="gnome-schedule")
		else:
			self.xml = gtk.glade.XML (config.getGladedir() + "/gnome-schedule.glade", domain="gnome-schedule")
		
		# self.saveWindow = None

		self.widget = self.xml.get_widget("mainWindow")
		self.treeview = self.xml.get_widget("treeview")
		self.set_user_menu = self.xml.get_widget("self_user_menu")
		self.add_button = self.xml.get_widget ("add_button")
		self.prop_button = self.xml.get_widget ("prop_button")
		self.del_button = self.xml.get_widget ("del_button")
		self.help_button = self.xml.get_widget ("help_button")
		self.btnSetUser = self.xml.get_widget("btnSetUser")
		

		#read the user
		self.readUser()

		self.editor = None
		self.schedule = None

		#inittializing the treeview
		# [0 Title, 1 Frequency, 2 Command, 3 Crontab record, 4 ID, 5 Time, 6 Icon, 7 scheduled instance, 8 date, 9 class_id, 10 user, 11 time, 12 type, 13 crontab/at]

		#for at this would be like: ["None(not suported yet)", "12:50 2004-06-25", "", "35", "", "12:50", icon, at instance, "2004-06-25", "a", "drzap", "at"]

		#for crontab it would be: ["untitled", "every hour", "ls /", "0 * * * * ls / # untitled", "5", "0 * * * *", icon, crontab instance, "", "", "", "crontab"]

		self.treemodel = gtk.ListStore(gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_INT, gobject.TYPE_STRING, gobject.TYPE_PYOBJECT, gobject.TYPE_PYOBJECT, gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_STRING)

		self.treeview.set_model (self.treemodel)
		self.switchView("simple", 1)
		self.treeview.get_selection().connect("changed", self.onTreeViewSelectRow)
		self.treeview.get_selection().unselect_all()
		
		start = time.time()
		print "###--- start load: [" + str(start) + "] ---###"
		self.crontab = crontab.Crontab(self)
		self.at = at.At(self)
		end = time.time()
		diff = end - start
		print "###--- end load: [" + str(end) + "] - Duration: " + str(diff) + " ---###"

		
		self.crontab_editor = self.crontab.geteditor ()
		self.at_editor = self.at.geteditor ()
				
		self.treeview.set_rules_hint(gtk.TRUE)
		self.treeview.columns_autosize()
		#self.widget.add_mask (GDK.BUTTON_PRESS_EVENT)
		self.treeview.connect ("button_press_event", self.treeview_button_press_event)
		
		self.add_scheduled_task_menu = self.xml.get_widget ("add_scheduled_task_menu")
		self.properties_menu = self.xml.get_widget ("properties_menu")
		self.delete_menu = self.xml.get_widget ("delete_menu")
		self.set_user_menu = self.xml.get_widget ("set_user_menu")
		self.quit_menu = self.xml.get_widget ("quit_menu")
		self.advanced_menu = self.xml.get_widget ("advanced_menu")
		self.about_menu = self.xml.get_widget ("about_menu")

		self.prop_button.set_sensitive (gtk.FALSE)
		self.del_button.set_sensitive (gtk.FALSE)
		self.properties_menu.set_sensitive (gtk.FALSE)
		self.delete_menu.set_sensitive (gtk.FALSE)
		self.haveitem = gtk.FALSE
		
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
		self.xml.signal_connect("on_treeview_key_press_event", self.on_treeview_key_pressed)

		support.gconf_client.add_dir ("/apps/gnome-schedule", gconf.CLIENT_PRELOAD_NONE)
		support.gconf_client.notify_add ("/apps/gnome-schedule/advanced", self.gconfkey_advanced_changed);
		
		self.advanced_menu.set_active (support.gconf_client.get_bool ("/apps/gnome-schedule/advanced"))
		
		


		self.widget.connect("delete_event", self.quit)
		self.widget.connect("destroy_event", self.quit)

		
		
		self.gconfkey_advanced_changed (support.gconf_client, None, "/apps/gnome-schedule/advanced", None)
		
		#set user window
		self.setuserwidget = self.xml.get_widget("setuserWindow")
		self.setuserwidget.hide()
		self.setuserWindow = setuserWindow.SetuserWindow (self)

		self.addwidget = self.xml.get_widget ("addWindow")
		self.addwidget.hide ()
		self.addWindow = addWindow.AddWindow (self)
	
		if self.root == 0:
			# hiding the 'set user' option if not root
			self.btnSetUser.hide()
		else:
			self.xml.signal_connect("on_btnSetUser_clicked", self.showSetUser)

		try:
			gtk.main ()
		except:
			gtk.mainloop()
		return
	

		

	def on_treeview_key_pressed (self, widget, event):
		key = gtk.gdk.keyval_name(event.keyval)
		print key
		if key == "Delete" or key == "KP_Delete":
			self.on_delete_menu_activate()
		return

	def treeview_button_press_event (self, widget, event):
		if event.type == gtk.gdk._2BUTTON_PRESS and self.haveitem == gtk.TRUE:
			self.on_prop_button_clicked (self, widget)
			
	def onTreeViewSelectRow (self, *args):
		try:
			store, iter = self.treeview.get_selection().get_selected()
			self.schedule = self.treemodel.get_value(iter, 7)
			self.editor = self.schedule.geteditor ()
			self.prop_button.set_sensitive (gtk.TRUE)
			self.del_button.set_sensitive (gtk.TRUE)
			self.properties_menu.set_sensitive (gtk.TRUE)
			self.delete_menu.set_sensitive (gtk.TRUE)
			self.haveitem = gtk.TRUE
		except:
			self.prop_button.set_sensitive (gtk.FALSE)
			self.del_button.set_sensitive (gtk.FALSE)
			self.properties_menu.set_sensitive (gtk.FALSE)
			self.delete_menu.set_sensitive (gtk.FALSE)
			self.haveitem = gtk.FALSE
	
	def cleancolumns (self, init):
		#cleaning up columns
		if init != 1:
			i = 3
			while i > - 1:
				temp = self.treeview.get_column(i)
				self.treeview.remove_column(temp)
				i = i -1
				
	def switchView(self, mode = "simple", init = 0):
		# TODO: Show the icon
		if mode == "simple":
			self.cleancolumns (init)		
			#col = gtk.TreeViewColumn(_("Icon"), gtk.CellRendererText(), text=6)
			#self.treeview.append_column(col)
			
			col = gtk.TreeViewColumn(_("Type"), gtk.CellRendererText(), text=12)
			col.set_sizing (gtk.TREE_VIEW_COLUMN_AUTOSIZE)
			self.treeview.append_column(col)

			col = gtk.TreeViewColumn(_("Title"), gtk.CellRendererText(), text=0)
			col.set_sizing (gtk.TREE_VIEW_COLUMN_AUTOSIZE)
			self.treeview.append_column(col)

			col = gtk.TreeViewColumn(_("Frequency or time"), gtk.CellRendererText(), text=1)
			col.set_sizing (gtk.TREE_VIEW_COLUMN_AUTOSIZE)
			self.treeview.append_column(col)

			col = gtk.TreeViewColumn(_("Preview"), gtk.CellRendererText(), text=2)
			col.set_sizing (gtk.TREE_VIEW_COLUMN_AUTOSIZE)
			#col.set_spacing(235)
			col.set_expand (gtk.TRUE)
			self.treeview.append_column(col)



		elif mode == "advanced":
			self.cleancolumns (init)		
			# col = gtk.TreeViewColumn(_("Icon"), gtk.CellRendererText(), text=6)
			# self.treeview.append_column(col)
			col = gtk.TreeViewColumn(_("Frequency or time"), gtk.CellRendererText(), text=5)
			col.set_resizable (gtk.TRUE)
			#col.set_sizing (gtk.TREE_VIEW_COLUMN_AUTOSIZE)
			self.treeview.append_column(col)

			col = gtk.TreeViewColumn(_("Preview"), gtk.CellRendererText(), text=2)
			col.set_resizable (gtk.TRUE)
			col.set_expand (gtk.TRUE)
			#col.set_sizing (gtk.TREE_VIEW_COLUMN_AUTOSIZE)
			#col.set_spacing(235)
			self.treeview.append_column(col)

			col = gtk.TreeViewColumn(_("Title"), gtk.CellRendererText(), text=0)
			col.set_resizable (gtk.TRUE)
			#col.set_sizing (gtk.TREE_VIEW_COLUMN_AUTOSIZE)
			self.treeview.append_column(col)

			col = gtk.TreeViewColumn(_("Type"), gtk.CellRendererText(), text=12)
			col.set_resizable (gtk.TRUE)
			#col.set_sizing (gtk.TREE_VIEW_COLUMN_AUTOSIZE)
			self.treeview.append_column(col)



		if self.root == 0:
			self.btnSetUser.hide()
		else:
			self.xml.signal_connect("on_btnSetUser_clicked", self.showSetUser)

		self.treeview.get_selection().unselect_all()
		self.edit_mode = mode

	def quit (self, *args):
		try:
			gtk.main_quit ()
		except:
			gtk.mainquit()

	def readUser (self):
		UID = os.geteuid()
		if UID == 0:
			self.root = 1
			self.user = "root"
			if len(sys.argv) == 2:
				self.user = sys.argv[1]
		else:
			self.root = 0
			self.user = os.environ['USER']

		return

	def schedule_reload (self):
		start = time.time()
		print "###--- start reload: [" + str(start) + "] ---###"
		self.treemodel.clear()
		self.crontab.read ()
		self.at.read ()
		end = time.time()
		diff = end - start
		print "###--- end reload: [" + str(end) + "] - Duration: " + str(diff) + " ---###"

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

	def gconfkey_advanced_changed (self, client, connection_id, entry, args):
		val = support.gconf_client.get_bool ("/apps/gnome-schedule/advanced")
		if val:
			self.switchView("advanced")
		else:
			self.switchView("simple")
		return

	def on_advanced_menu_activate (self, widget):
		support.gconf_client.set_bool ("/apps/gnome-schedule/advanced", widget.get_active())

	def on_about_menu_activate (self, *args):
		dlg = gnome.ui.About(_("System Schedule"),
			config.getVersion(),
			_("Copyright (c) 2004-2005 Gaute Hope."),
			_("This software is distributed under the GPL. "),
			["Philip Van Hoof <me at freax dot org>",
			"Gaute Hope <eg at gaute dot eu dot org>"], 
			[_("documented_by")],
			_("translator_credits"),
			iconPixbuf)

		dlg.set_transient_for(self.widget)
		dlg.set_position (gtk.WIN_POS_CENTER_ON_PARENT)
		dlg.show()

	def on_add_scheduled_task_menu_activate (self, *args):
		self.addWindow.ShowAddWindow ()

	def on_properties_menu_activate (self, *args):
		store, iter = self.treeview.get_selection().get_selected()
		self.schedule = self.treemodel.get_value(iter, 7)
		self.editor = self.schedule.geteditor ()
		
		if iter != None:
			record = self.treemodel.get_value(iter, 3)
			linenumber = self.treemodel.get_value(iter, 4)
			self.editor.showedit (record, linenumber, iter, self.edit_mode)

	def on_delete_menu_activate (self, *args):
		store, iter = self.treeview.get_selection().get_selected()

		self.schedule = self.treemodel.get_value(iter, 7)
		self.editor = self.schedule.geteditor ()
		
		
		if iter != None:
			record = self.treemodel.get_value(iter, 3)
			linenumber = self.treemodel.get_value(iter, 4)

			firstiter = self.treemodel.get_iter_first()
			self.schedule.delete (linenumber, iter)
			nextiter = self.treemodel.iter_next(iter)

			print nextiter
			print firstiter

			
			if nextiter == "None":
			#go first
				selection = self.treeview.get_selection()
				selection.select_iter(firstiter)
			else:
			#go next
				selection = self.treeview.get_selection()
				selection.select_iter(firstiter)
			
				

		return

	def on_quit_menu_activate (self, *args):
		self.quit ()

	def on_manual_menu_activate (self, *args):
		help_page = "file://" + config.getDocdir() + "/index.html"
		path = config.getGnomehelpbin ()
		pid = os.fork()
		if not pid:
			os.execv(path, [path, help_page])

	def showSetUser(self, *args):
		self.setuserWindow.ShowSetuserWindow()
		return
