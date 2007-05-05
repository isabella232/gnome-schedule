# mainWindow.py - mainWindow of the crontab configuration tool
# Copyright (C) 2004, 2005 Philip Van Hoof <me at pvanhoof dot be>
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
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02110-1301, USA.

#pygtk modules
import gtk
import gtk.glade
import gobject

# TODO: gnome specific
import gnome
from gnome import url_show

#python modules
import os
import pwd

#custom modules
import config
import crontab
import crontabEditor
import at
import atEditor
import setuserWindow
import addWindow
import preset

gtk.glade.bindtextdomain(config.GETTEXT_PACKAGE(), config.GNOMELOCALEDIR())

##
## The MainWindow class
##
class main:
	def __init__(self, debug_flag=None, inapplet=False, gprogram = None):
		self.debug_flag = debug_flag
		self.inapplet = inapplet
		self.gprogram = gprogram
		
		self.__loadIcon__()
		self.__loadGlade__()
		
		self.editor = None
		self.schedule = None
		
			
		#start the backend where all the user configuration is stored
		self.backend = preset.ConfigBackend(self, "gconf")
		
		
		self.defaultIcon = self.backend.getDefaultIcon()
		
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

		self.prop_button.set_sensitive (False)
		self.del_button.set_sensitive (False)
		
		self.xml.signal_connect("on_add_button_clicked", self.on_add_button_clicked)
		self.xml.signal_connect("on_prop_button_clicked", self.on_prop_button_clicked)
		self.xml.signal_connect("on_del_button_clicked", self.on_del_button_clicked)
		self.xml.signal_connect("on_help_button_clicked", self.on_help_button_clicked)
		self.xml.signal_connect("on_btnSetUser_clicked", self.on_btnSetUser_clicked)
		self.xml.signal_connect("on_btnExit_clicked", self.__quit__)
		self.xml.signal_connect("on_mainWindow_delete_event", self.__quit__)
		
				
		##inittializing the treeview
		## [0 Title, 1 Frequency, 2 Command, 3 Crontab record, 4 ID, 5 Time, 6 Icon, 7 scheduled instance, 8 icon path, 9 date, 10 class_id, 11 user, 12 time, 13 type, 14 crontab/at]
		##for at this would be like: 
		
# ["untitled", "12:50 2004-06-25", "preview", "script", "job_id", "12:50", icon, at instance, icon_path, "2004-06-25", "a", "drzap", "at"]

		##for crontab it would be: 
		
# ["untitled", "every hour", "ls /", "0 * * * * ls / # untitled", "5", "0 * * * *", icon, crontab instance,icon_path, 1(job_id), "", "", "crontab"]
		self.treemodel = gtk.ListStore(gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_INT, gobject.TYPE_STRING, gtk.gdk.Pixbuf, gobject.TYPE_PYOBJECT, gobject.TYPE_STRING , gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_INT)
		
		self.treeview = self.xml.get_widget("treeview")
		
		self.xml.signal_connect("on_treeview_button_press_event", self.on_treeview_button_press_event)
		self.xml.signal_connect("on_treeview_key_press_event", self.on_treeview_key_pressed)
		
		self.treeview.set_model (self.treemodel)
						
		#when a selection is made
		self.treeview.get_selection().connect("changed", self.on_TreeViewSelectRow)
		
		# TODO: enable?
		#self.treeview.set_rules_hint(True)
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
		

		self.properties_menu.set_sensitive (False)
		self.delete_menu.set_sensitive (False)

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
		
		
		self.__initUser__()
		
		##create crontab
		self.crontab = crontab.Crontab(self.root,self.user, self.uid, self.gid)
		self.crontab_editor = crontabEditor.CrontabEditor(self,self.backend, self.crontab, self.defaultIcon)
		##
		
		##create at
		self.at = at.At(self.root,self.user, self.uid, self.gid)
		self.at_editor = atEditor.AtEditor (self, self.backend, self.at, self.defaultIcon)
		##
		
		#set user window
		self.setuserWindow = setuserWindow.SetuserWindow (self)
		
		#set add window
		self.addWindow = addWindow.AddWindow (self)
		
		# TODO: select first task from list?

		self.schedule_reload ()

		self.timeout_handler_id = gobject.timeout_add(9000, self.update_schedule)

		if inapplet == False:
			gtk.main()


	def update_schedule(self):
		selection = self.treeview.get_selection()
		model, iter, = selection.get_selected()
		if iter:
			path = model.get_path(iter)
		self.schedule_reload ()
		if iter:
			 selection.select_path(path)	
		return True

	def changeUser(self,user):
		if user != self.user:
			self.__setUser__(user)
			#change user for the schedulers
			self.crontab.set_rights(self.user, self.uid, self.gid)
			self.at.set_rights(self.user, self.uid, self.gid)
			#adjust statusbar
			if self.root == 1:
				self.statusbar.push(self.statusbarUser, (_("Editing user: %s") % (self.user)))
		
			self.schedule_reload ()
	
	
	def __setUser__(self,user):
		userdb = pwd.getpwnam(user)
		self.user = user
		self.uid = userdb[2]
		self.gid = userdb[3]
		
						
	## TODO: 2 times a loop looks to mutch
	def schedule_reload (self):
		self.treemodel.clear ()

		data = self.crontab.read ()
		if data != None:
			self.__fill__ (data)
			
		data = self.at.read ()
		if data != None:
			self.__fill__ (data)
						



	def __fill__ (self, records):
		for title, timestring_show, preview, lines, job_id, timestring, scheduler, icon, date, class_id, user, time, typetext, type, nooutput in records:
					
			if icon != None:
				try:
					icon_pix = gtk.gdk.pixbuf_new_from_file_at_size (icon, 21, 21)
				except:
					icon_pix = None
			else:
				icon_pix = None
			
			iter = self.treemodel.append([title, timestring_show, preview, lines, job_id, timestring, icon_pix, scheduler, icon, date, class_id, user, time, typetext, type, nooutput])

			
		
	##

	# TODO: pixbuf or pixmap? gtkImage
	def __loadIcon__(self):
		if os.access("../pixmaps/gnome-schedule.png", os.F_OK):
			self.iconPixbuf = gtk.gdk.pixbuf_new_from_file ("../pixmaps/gnome-schedule.png")
		else:
			try:
				self.iconPixbuf = gtk.gdk.pixbuf_new_from_file (config.getImagedir() + "/gnome-schedule.png")
			except:
				print _("ERROR: Could not load icon")


	def __loadGlade__(self):
		if os.access("gnome-schedule.glade", os.F_OK):
			self.xml = gtk.glade.XML ("gnome-schedule.glade", domain="gnome-schedule")
		else:
			try:
				self.xml = gtk.glade.XML (config.getGladedir() + "/gnome-schedule.glade", domain="gnome-schedule")
			except:
				print _("ERROR: Could not load glade file")

	
	
	def __initUser__(self):
		self.uid = os.geteuid() 
		self.gid = os.getegid()
		self.user = pwd.getpwuid(self.uid)[0]
		
		if self.uid != 0:
			self.set_user_menu.hide()
			self.statusbar.hide()	
			self.root = 0
		else:
			self.root = 1
			self.btnSetUser.show()
			self.statusbar.show()
			self.statusbar.push(self.statusbarUser, (_("Editing user: %s") % (self.user)))
				

	#when the user selects a task, buttons get enabled
	def on_TreeViewSelectRow (self, *args):
		if self.treeview.get_selection().count_selected_rows() > 0 :
			value = True
		else:
			value = False
			
		self.prop_button.set_sensitive (value)
		self.del_button.set_sensitive (value)
		self.properties_menu.set_sensitive (value)
		self.delete_menu.set_sensitive (value)
		
	
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
		cell2 = gtk.CellRendererText ()	
		col = gtk.TreeViewColumn (_("Task"), None)
		col.pack_start (cell, True)
		col.pack_end (cell2, True)
		col.add_attribute (cell, "pixbuf", 6)
		if mode == "simple":
			col.add_attribute (cell2, "text", 13)
		else:
			col.add_attribute (cell2, "text", 14)
			
		self.treeview.append_column(col)
		
		if mode == "simple":

			col = gtk.TreeViewColumn(_("Description"), gtk.CellRendererText(), text=0)
			col.set_resizable (True)
			self.treeview.append_column(col)

			col = gtk.TreeViewColumn(_("Date and Time"), gtk.CellRendererText(), text=1)
			col.set_resizable (True)
			self.treeview.append_column(col)

			col = gtk.TreeViewColumn(_("Command preview"), gtk.CellRendererText(), text=2)
			col.set_resizable (True)
			col.set_expand (True)
			self.treeview.append_column(col)


		elif mode == "advanced":
	
			col = gtk.TreeViewColumn(_("Date and Time"), gtk.CellRendererText(), text=5)
			col.set_resizable (True)
			self.treeview.append_column(col)

			col = gtk.TreeViewColumn(_("Command preview"), gtk.CellRendererText(), text=2)
			col.set_resizable (True)
			col.set_expand (True)
			self.treeview.append_column(col)

			col = gtk.TreeViewColumn(_("Description"), gtk.CellRendererText(), text=0)
			col.set_resizable (True)
			self.treeview.append_column(col)

	


	def on_advanced_menu_activate (self, widget):
		self.backend.set_advanced_option(widget.get_active())
	
	def on_add_scheduled_task_menu_activate (self, *args):
		self.addWindow.ShowAddWindow ()

	def on_properties_menu_activate (self, *args):
		store, iter = self.treeview.get_selection().get_selected()
		
		try:
			#see what scheduler (at, crontab or ...)
			self.schedule = self.treemodel.get_value(iter, 7)
			
			
		
			record = self.treemodel.get_value(iter, 3)
			linenumber = self.treemodel.get_value(iter, 4)
			
			# TODO: dirty hacky 
			if self.schedule.get_type() == "crontab":
				self.editor = self.crontab_editor
				job_id = self.treemodel.get_value (iter, 9)
				self.editor.showedit (record, job_id, linenumber, iter, self.edit_mode)
			else:
				self.editor = self.at_editor
				self.editor.showedit (record, linenumber, iter, self.edit_mode)

		except Exception, ex:
			print ex
			self.dialog = gtk.MessageDialog(self.widget, gtk.DIALOG_MODAL|gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_ERROR, gtk.BUTTONS_OK, _("Please select a task"))
			self.dialog.run ()
			self.dialog.destroy ()			
			

	# TODO: looks not that clean (is broken)
	def on_delete_menu_activate (self, *args):
		dialog = gtk.MessageDialog(self.widget, gtk.DIALOG_MODAL|gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_QUESTION, gtk.BUTTONS_YES_NO, _("Do you want to delete this task?"))
		if (dialog.run() != gtk.RESPONSE_YES):
			dialog.destroy()
			del dialog
			return
		dialog.destroy()
		del dialog
		
		store, iter = self.treeview.get_selection().get_selected()
	
		try:
			#see what scheduler (at, crontab or ...)
			self.schedule = self.treemodel.get_value(iter, 7)
			
			# TODO: dirty hacky 
			if self.schedule.get_type() == "crontab":
				self.editor = self.crontab_editor
			elif self.schedule.get_type() == "at":
				self.editor = self.at_editor

			record = self.treemodel.get_value(iter, 3)
			linenumber = self.treemodel.get_value(iter, 4)

			path = self.treemodel.get_path(iter)
			pathint = path[0]
			backpath = (pathint - 1,)
			
			if self.schedule.get_type() == "crontab":
				self.schedule.delete (linenumber, iter, self.treemodel.get_value(iter, 9))
			elif self.schedule.get_type() == "at":
				self.schedule.delete (linenumber, iter)
			
			self.schedule_reload()
			
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
						
		except Exception, ex:
			print ex
			self.dialog = gtk.MessageDialog(self.widget, gtk.DIALOG_MODAL|gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_ERROR, gtk.BUTTONS_OK, _("Please select a task"))
			self.dialog.run ()
			self.dialog.destroy ()

	def on_set_user_menu_activate(self, *args):
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


	def on_treeview_key_pressed (self, widget, event):
		key = gtk.gdk.keyval_name(event.keyval)
		#remove task from list with DEL key
		if key == "Delete" or key == "KP_Delete":
			self.on_delete_menu_activate()
		#display properties with ENTER key
		if (key == "Return" or key == "KP_Return"):
 			self.on_properties_menu_activate(self, widget)

	
	#double click on task to get properties
	def on_treeview_button_press_event (self, widget, event):
		if event.type == gtk.gdk._2BUTTON_PRESS:
			self.on_properties_menu_activate(self, widget)


 	#about box
 	def open_url (self, *args):
 		url_show("http://gnome-schedule.sourceforge.net")
 		
 	def on_about_menu_activate (self, *args):
 	
		gtk.about_dialog_set_url_hook(self.open_url, "bogusbar")
	 	dlg = gtk.AboutDialog ()
 		dlg.set_title (_("About Gnome Schedule"))
 		dlg.set_name (_("Gnome Schedule"))
 		dlg.set_version (config.getVersion())
 		dlg.set_copyright (_("Copyright (c) 2004-2007 Gaute Hope."))
 		#dlg.set_comments ()
 		#dlg.set_license ()
 		dlg.set_website ("http://gnome-schedule.sourceforge.net")
 		dlg.set_website_label("http://gnome-schedule.sourceforge.net")
 		dlg.set_authors (
 			["Philip Van Hoof <pvanhoof at gnome dot org>",
 			"Kristof Vansant <de_lupus at pandora dot be>",
 			"Gaute Hope <eg@gaute.vetsj.com>"]
 			)
 		dlg.set_documenters (
 			["Rodrigo Marcos Fombellida <rmarcos_geo@yahoo.es>"]
 			)
 		dlg.set_translator_credits (_("translator-credits"))
 		dlg.set_logo (self.iconPixbuf)
 		
		if (dlg.run() != gtk.RESPONSE_YES):
			dlg.destroy()
			del dlg
			return
		dlg.destroy()
		del dlg
 		 	
 	#open help
  	def on_manual_menu_activate (self, *args):
		try:
			gnome.help_display (
					'gnome-schedule', 
					'')
		except gobject.GError, error:
			dialog = gtk.MessageDialog (
					self.widget,
					gtk.DIALOG_DESTROY_WITH_PARENT,
					gtk.MESSAGE_ERROR, gtk.BUTTONS_CLOSE)
			dialog.set_markup ("<b>" + _("Could not display help") + "</b>")
			dialog.format_secondary_text ("%s" % error)
			dialog.run ()
			dialog.destroy ()


 	#quit program
 	def __quit__(self, *args):
 		if self.inapplet:
			self.widget.hide ()
		else:
			gtk.main_quit ()
		return True
		
