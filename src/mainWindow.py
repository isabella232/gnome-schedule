# mainWindow.py - mainWindow of the crontab configuration tool
# Copyright (C) 2004, 2005 Philip Van Hoof <me at freax dot org>
# Copyright (C) 2004, 2005 Gaute Hope <eg at gaute dot eu dot org>
# Copyright (C) 2004, 2005 Kristof Vansant <de_lupus at pandora dot be>

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

#pygtk modules
import gtk
import gtk.glade
import gobject

# TODO: gnome specific
import gnome

#python modules
import os

#custom modules
import config
import crontab
import crontabEditor
import at
import atEditor
import setuserWindow
import addWindow
import preset

##
## I18N
##
import gettext
domain = 'gnome-schedule'
gettext.bindtextdomain(domain)
gettext.textdomain(domain)
_ = gettext.gettext
gtk.glade.bindtextdomain(domain)

##
## The MainWindow class
##
class main:
	def __init__(self, debug_flag=None):
		self.debug_flag = debug_flag

		self.__loadIcon__()
		self.__loadGlade__()
		
		self.editor = None
		self.schedule = None
		self.haveitem = gtk.FALSE

		#start the backend where all the user configuration is stored
		self.backend = preset.ConfigBackend(self, "gconf")
		
		##configure the window
		self.widget = self.xml.get_widget("mainWindow")

		self.widget.connect("delete_event", self.__quit__)
		self.widget.connect("destroy_event", self.__quit__)
		self.widget.set_icon(self.iconPixbuf)
		##		


		##configure statusbar
		self.statusbar = self.xml.get_widget("statusbar")
		
		self.statusbarUser = self.statusbar.get_context_id("user")
		##
		
		##configure the toolbar	
		self.add_button = self.xml.get_widget ("add_button")
		self.prop_button = self.xml.get_widget ("prop_button")
		self.del_button = self.xml.get_widget ("del_button")
		self.help_button = self.xml.get_widget ("help_button")
		self.btnSetUser = self.xml.get_widget("btnSetUser")
		self.btnExit = self.xml.get_widget("btnExit")

		self.prop_button.set_sensitive (gtk.FALSE)
		self.del_button.set_sensitive (gtk.FALSE)
		
		self.xml.signal_connect("on_add_button_clicked", self.on_add_button_clicked)
		self.xml.signal_connect("on_prop_button_clicked", self.on_prop_button_clicked)
		self.xml.signal_connect("on_del_button_clicked", self.on_del_button_clicked)
		self.xml.signal_connect("on_help_button_clicked", self.on_help_button_clicked)
		self.xml.signal_connect("on_btnSetUser_clicked", self.on_btnSetUser_clicked)
		self.xml.signal_connect("on_btnExit_clicked", self.__quit__)
		
		#get user
		self.__readUser__()
		
		
		##inittializing the treeview
		## [0 Title, 1 Frequency, 2 Command, 3 Crontab record, 4 ID, 5 Time, 6 Icon, 7 scheduled instance, 8 icon path, 9 date, 10 class_id, 11 user, 12 time, 13 type, 14 crontab/at]
		##for at this would be like: ["untitled", "12:50 2004-06-25", "", "35", "", "12:50", icon, at instance, icon_path, "2004-06-25", "a", "drzap", "at"]
		##for crontab it would be: ["untitled", "every hour", "ls /", "0 * * * * ls / # untitled", "5", "0 * * * *", icon, crontab instance,icon_path, "", "", "", "crontab"]
		self.treemodel = gtk.ListStore(gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_INT, gobject.TYPE_STRING, gtk.gdk.Pixbuf, gobject.TYPE_PYOBJECT, gobject.TYPE_STRING , gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_STRING)
		
		self.treeview = self.xml.get_widget("treeview")
		
		self.xml.signal_connect("on_treeview_button_press_event", self.on_treeview_button_press_event)
		self.xml.signal_connect("on_treeview_key_press_event", self.on_treeview_key_pressed)
		
		self.treeview.set_model (self.treemodel)
						
		#when a selection is made
		self.treeview.get_selection().connect("changed", self.on_TreeViewSelectRow)
		
		# TODO: enable?
		#self.treeview.set_rules_hint(gtk.TRUE)
		##

		##configure the menu
		self.add_scheduled_task_menu = self.xml.get_widget ("add_scheduled_task_menu")
		self.properties_menu = self.xml.get_widget ("properties_menu")
		self.delete_menu = self.xml.get_widget ("delete_menu")
		self.set_user_menu = self.xml.get_widget ("set_user_menu")
		self.quit_menu = self.xml.get_widget ("quit_menu")
		
		self.advanced_menu = self.xml.get_widget ("advanced_menu")
		
		self.manual_menu = self.xml.get_widget ("manual_menu")
		self.about_menu = self.xml.get_widget ("about_menu")
		

		self.properties_menu.set_sensitive (gtk.FALSE)
		self.delete_menu.set_sensitive (gtk.FALSE)

		self.xml.signal_connect("on_add_scheduled_task_menu_activate", self.on_add_scheduled_task_menu_activate)
		self.xml.signal_connect("on_properties_menu_activate", self.on_properties_menu_activate)
		self.xml.signal_connect("on_delete_menu_activate", self.on_delete_menu_activate)
		self.xml.signal_connect("on_set_user_menu_activate",self.on_set_user_menu_activate)
		
		self.xml.signal_connect("on_quit_menu_activate", self.__quit__)
		
		self.xml.signal_connect("on_advanced_menu_activate", self.on_advanced_menu_activate)
	
		self.xml.signal_connect("on_manual_menu_activate", self.on_manual_menu_activate)
		self.xml.signal_connect("on_about_menu_activate", self.on_about_menu_activate)
		##


		#enable or disable advanced depending on user config
		self.advanced_menu.set_active (self.backend.get_advanced_option())
		if self.backend.get_advanced_option():
			self.switchView("advanced")
		else:
			self.switchView("simple")
		
		#setuser only shown if user = root		
		if self.root == 0:
			self.btnSetUser.hide()
			self.set_user_menu.hide()		
		##

		##create crontab
		self.crontab = crontab.Crontab(self)
		self.crontab_editor = self.crontab.geteditor ()
		##
		
		##create at
		self.at = at.At(self)
		self.at_editor = self.at.geteditor ()
		##
  
		#set user window
		self.setuserWindow = setuserWindow.SetuserWindow (self)
		
		#set add window
		self.addWindow = addWindow.AddWindow (self)
		
		#load the treeview with the tasks
		self.schedule_reload ("all")
			
		gtk.main()

	
	
	## TODO: 2 times a loop looks to mutch
	def schedule_reload (self, records = "all"):
		
		self.delarray = []
		
		#adjust statusbar
		if self.root == 1:
			self.statusbar.push(self.statusbarUser, (_("Editing user: ") + self.user))
			self.statusbar.show()	
		else:
			self.statusbar.hide()	
			
					
		if records == "crontab":
			self.treemodel.foreach(self.__delete_row__, "crontab")
			self.crontab.read()

		elif records == "at":
			self.treemodel.foreach(self.__delete_row__, "at")
			self.at.read()

		elif records == "all":
			self.treemodel.foreach(self.__delete_row__, "all")
			self.crontab.read ()
			self.at.read ()
	
		for iter in self.delarray:
			self.treemodel.remove(iter)


	def __delete_row__ (self, model, path, iter, record_type):
		if record_type == self.treemodel.get_value(iter, 14) or record_type == "all":
			self.delarray.append(iter)
	##


	# TODO: pixbuf or pixmap? gtkImage
	def __loadIcon__(self):
		if os.access("../pixmaps/gnome-schedule.png", os.F_OK):
			self.iconPixbuf = gtk.gdk.pixbuf_new_from_file ("../pixmaps/gnome-schedule.png")
		else:
			try:
				self.iconPixbuf = gtk.gdk.pixbuf_new_from_file (config.getImagedir() + "/gnome-schedule.png")
			except:
				print "ERROR: Could not load icon"


	def __loadGlade__(self):
		if os.access("gnome-schedule.glade", os.F_OK):
			self.xml = gtk.glade.XML ("gnome-schedule.glade", domain="gnome-schedule")
		else:
			try:
				self.xml = gtk.glade.XML (config.getGladedir() + "/gnome-schedule.glade", domain="gnome-schedule")
			except:
				print "ERROR: Could not load glade file"
		

	#when the user selects a task, buttons get enabled
	def on_TreeViewSelectRow (self, *args):
		if self.treeview.get_selection().count_selected_rows() > 0 :
			value = gtk.TRUE
		else:
			value = gtk.FALSE
			
		self.prop_button.set_sensitive (value)
		self.del_button.set_sensitive (value)
		self.properties_menu.set_sensitive (value)
		self.delete_menu.set_sensitive (value)
		self.haveitem = value

	
	#clean existing columns
	def __cleancolumns__ (self):
		columns = len(self.treeview.get_columns()) -1
		while columns > -1:
			temp = self.treeview.get_column(columns)
			self.treeview.remove_column(temp)
			columns = columns - 1
		 
	
	#switch between advanced and simple mode			
	def switchView(self, mode = "simple"):
		#TODO: experimental code + show icon?
		self.__cleancolumns__ ()
		
		self.treeview.get_selection().unselect_all()
		self.edit_mode = mode
		
		cell = gtk.CellRendererPixbuf()
		cell.set_fixed_size(21,21)	
		col = gtk.TreeViewColumn(_("Icon"), cell, pixbuf=6)
		self.treeview.append_column(col)
		
		if mode == "simple":

			col = gtk.TreeViewColumn(_("Type"), gtk.CellRendererText(), text=13)
			col.set_resizable (gtk.TRUE)
			self.treeview.append_column(col)

			col = gtk.TreeViewColumn(_("Title"), gtk.CellRendererText(), text=0)
			col.set_resizable (gtk.TRUE)
			self.treeview.append_column(col)

			col = gtk.TreeViewColumn(_("Frequency or time"), gtk.CellRendererText(), text=1)
			col.set_resizable (gtk.TRUE)
			self.treeview.append_column(col)

			col = gtk.TreeViewColumn(_("Preview"), gtk.CellRendererText(), text=2)
			col.set_resizable (gtk.TRUE)
			col.set_expand (gtk.TRUE)
			self.treeview.append_column(col)


		elif mode == "advanced":
	
			col = gtk.TreeViewColumn(_("Frequency or time"), gtk.CellRendererText(), text=5)
			col.set_resizable (gtk.TRUE)
			self.treeview.append_column(col)

			col = gtk.TreeViewColumn(_("Preview"), gtk.CellRendererText(), text=2)
			col.set_resizable (gtk.TRUE)
			col.set_expand (gtk.TRUE)
			self.treeview.append_column(col)

			col = gtk.TreeViewColumn(_("Title"), gtk.CellRendererText(), text=0)
			col.set_resizable (gtk.TRUE)
			self.treeview.append_column(col)

			col = gtk.TreeViewColumn(_("Type"), gtk.CellRendererText(), text=14)
			col.set_resizable (gtk.TRUE)
			self.treeview.append_column(col)
	


	def on_advanced_menu_activate (self, widget):
		self.backend.set_advanced_option(widget.get_active())
	
	def on_add_scheduled_task_menu_activate (self, *args):
		self.addWindow.ShowAddWindow ()

	def on_properties_menu_activate (self, *args):
		store, iter = self.treeview.get_selection().get_selected()
		
		if iter != None:
			#see what scheduler (at, crontab or ...)
			self.schedule = self.treemodel.get_value(iter, 7)
			self.editor = self.schedule.geteditor ()
		
			record = self.treemodel.get_value(iter, 3)
			linenumber = self.treemodel.get_value(iter, 4)
			self.editor.showedit (record, linenumber, iter, self.edit_mode)

	# TODO: looks not that clean :)
	def on_delete_menu_activate (self, *args):
		store, iter = self.treeview.get_selection().get_selected()
	
		if iter != None:
			#see what scheduler (at, crontab or ...)
			self.schedule = self.treemodel.get_value(iter, 7)
			self.editor = self.schedule.geteditor ()

			record = self.treemodel.get_value(iter, 3)
			linenumber = self.treemodel.get_value(iter, 4)

			path = self.treemodel.get_path(iter)
			pathint = path[0]
			backpath = (pathint - 1,)

			self.schedule.delete (linenumber, iter)
			firstiter = self.treemodel.get_iter_first()
			try:
				nextiter = self.treemodel.get_iter(path)
				#go next
				selection = self.treeview.get_selection()
				selection.select_iter(nextiter)

			except:
				if backpath[0] > 0:
					nextiter = self.treemodel.get_iter(backpath)
					#go back
					selection = self.treeview.get_selection()
					selection.select_iter(nextiter)

				else:
					if firstiter:
						#go first
						selection = self.treeview.get_selection()
						selection.select_iter(firstiter)

	def	on_set_user_menu_activate(self, *args):
		self.setuserWindow.ShowSetuserWindow()


	def on_btnSetUser_clicked(self, *args):
		self.on_set_user_menu_activate(self, args)
			
	def on_add_button_clicked (self, *args):
		self.on_add_scheduled_task_menu_activate (self, args)

	def on_prop_button_clicked (self, *args):
		self.on_properties_menu_activate (self, args)

	def on_del_button_clicked (self, *args):
		self.on_delete_menu_activate (self, args)

	def on_help_button_clicked (self, *args):
		self.on_manual_menu_activate (self, args)


	#remove task from list with DEL key
	def on_treeview_key_pressed (self, widget, event):
		key = gtk.gdk.keyval_name(event.keyval)
		if key == "Delete" or key == "KP_Delete":
			self.on_delete_menu_activate()

	# TODO: pressing enter on a listitem also should show properties
	# TODO: if there are items in the list the first one should get focus
	#double click on task to get properties
	def on_treeview_button_press_event (self, widget, event):
		if event.type == gtk.gdk._2BUTTON_PRESS and self.haveitem == gtk.TRUE:
			self.on_properties_menu_activate(self, widget)


	#see if root and get user
	def __readUser__(self):
		UID = os.geteuid()
		self.uid = UID
		self.gid = os.getegid()
		
		if UID == 0:
			self.root = 1
			self.user = "root"
		else:
			self.root = 0
			self.user = os.environ['USER']

 	#about box
 	def on_about_menu_activate (self, *args):
 		# TODO: should be using gtkAboutDialog
 		dlg = gnome.ui.About(_("Gnome Schedule"),
 			config.getVersion(),
 			_("Copyright (c) 2004-2005 Gaute Hope."),
 			_("This software is distributed under the GPL. "),
 			["Philip Van Hoof <me at freax dot org>",
 			"Kristof Vansant <de_lupus at pandora dot be>",
 			"Gaute Hope <eg at gaute dot eu dot org>"], 
 			[_("Some painfully bad documentation put\ntoghether from the far corners of Gaute Hope's mind.")],_("translator_credits"),self.iconPixbuf)
 
 		dlg.set_transient_for(self.widget)
 		dlg.set_position (gtk.WIN_POS_CENTER_ON_PARENT)
 		dlg.show()
 		 	
 	#open help
  	def on_manual_menu_activate (self, *args):
  		# TODO: correct way to do this?
  		help_page = "file://" + config.getDocdir() + "/index.html"
  		path = config.getGnomehelpbin ()
  		pid = os.fork()
  		if not pid:
  			os.execv(path, [path, help_page])
 		 		
 	#quit program
 	def __quit__(self, *args):
		gtk.main_quit ()
		
