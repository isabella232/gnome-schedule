# addWindow.py - UI code for adding a crontab record
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

#pygtk modules
import gtk
import gobject
import gconf

#python modules
import re
import time
import calendar

#custom modules
import support
import preset

##
## I18N
##
import gettext
domain = 'gnome-schedule'
gettext.bindtextdomain(domain)
gettext.textdomain(domain)
_ = gettext.gettext


class AtEditor:
	def __init__(self, parent):
		self.ParentClass = parent
		self.xml = self.ParentClass.xml

		self.widget = self.xml.get_widget("atEditor")
		self.widget.connect("delete-event", self.on_cancel_button_clicked)
		
		self.fieldRegex = re.compile('^(\*)$|^([0-9]+)$|^\*\\\([0-9]+)$|^([0-9]+)-([0-9]+)$|(([0-9]+[|,])+)')
		self.nooutputRegex = re.compile('([^#\n$]*)>(\s|)/dev/null\s2>&1')
		#self.editing = gtk.FALSE
		self.noevents = gtk.FALSE
		self.NOACTION = gtk.FALSE	#getting alot of these now.. this is for abosultely noactions of the syncing and templates stuff
		self.noupdate = gtk.FALSE
		self.template_combobox_model = None
		self.first = 0
		self.combo_trigger = gtk.FALSE
	
		self.save_button = self.xml.get_widget ("at_save_button")
		self.remove_button = self.xml.get_widget ("at_delete_button")
		self.title_entry = self.xml.get_widget ("at_title_entry")
		self.script_textview = self.xml.get_widget ("at_script_textview")
		self.script_textview_buffer = self.script_textview.get_buffer()

		self.help_button = self.xml.get_widget ("at_help_button")
		self.cancel_button = self.xml.get_widget ("at_cancel_button")
		self.ok_button = self.xml.get_widget ("at_ok_button")
		self.image_button = self.xml.get_widget ("at_image_button")

		##template combobox config		
		self.template_combobox = self.xml.get_widget ("at_template_combobox")
		self.template_combobox_model = gtk.ListStore(gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_PYOBJECT)
		self.template_combobox.set_model (self.template_combobox_model)
		##
		
		self.template_image = self.xml.get_widget ("at_template_image")
		self.template_label = self.xml.get_widget ("at_template_label")
		
		self.calendar = self.xml.get_widget ("at_calendar")
		self.hour_spinbutton = self.xml.get_widget ("at_hour_spinbutton")
		self.minute_spinbutton= self.xml.get_widget ("at_minute_spinbutton")
		self.combobox = self.xml.get_widget ("at_combobox")
		self.combobox_entry = self.combobox.get_child()	
			
		self.template_combobox.get_child().connect ("changed", self.on_template_combobox_entry_changed)
		self.xml.signal_connect("on_at_help_button_clicked", self.on_help_button_clicked)
		self.xml.signal_connect("on_at_cancel_button_clicked", self.on_cancel_button_clicked)
		self.xml.signal_connect("on_at_ok_button_clicked", self.on_ok_button_clicked)

		self.xml.signal_connect("on_at_script_textview_popup_menu", self.on_script_textview_popup_menu)
		self.xml.signal_connect("on_at_script_textview_key_release_event", self.on_script_textview_change)
		self.xml.signal_connect("on_at_template_combobox_changed", self.on_template_combobox_changed)
		self.xml.signal_connect("on_at_title_entry_changed", self.on_title_entry_changed)

		self.xml.signal_connect("on_at_save_button_clicked", self.on_save_button_clicked)
		self.xml.signal_connect("on_at_delete_button_clicked", self.on_delete_button_clicked)
		self.xml.signal_connect("on_at_image_button_clicked", self.on_image_button_clicked)
		self.xml.signal_connect("on_at_calendar_day_selected", self.on_calendar_day_selected)
		self.xml.signal_connect("on_at_calendar_month_changed", self.on_calendar_month_changed)
		self.xml.signal_connect("on_at_calendar_year_changed", self.on_calendar_year_changed)
		self.xml.signal_connect("on_at_hour_spinbutton_changed", self.on_hour_spinbutton_changed)
		self.xml.signal_connect("on_at_minute_spinbutton_changed", self.on_minute_spinbutton_changed)
		self.xml.signal_connect("on_at_combobox_changed", self.on_combobox_changed)

		#gconf
		support.gconf_client.add_dir ("/apps/gnome-schedule/presets/at", gconf.CLIENT_PRELOAD_NONE)
		support.gconf_client.notify_add ("/apps/gnome-schedule/presets/at/installed", self.gconfkey_changed);


	def showadd (self, mode):
		self.NOACTION = gtk.TRUE
		self.__reset__ ()
		self.title = _("Untitled")
		self.editing = gtk.FALSE
		self.widget.set_title(_("Create a new scheduled task"))
		self.widget.show_all()
		
		self.__loadicon__ ()
		self.__reload_templates__ ()
		self.__update_textboxes__()
		self.NOACTION = gtk.FALSE

	def showedit (self, record, job_id, iter, mode):

		self.editing = gtk.TRUE
		self.NOACTION = gtk.TRUE

		self.job_id = job_id
		self.date = self.ParentClass.ParentClass.treemodel.get_value(iter, 9)
		self.time = self.ParentClass.ParentClass.treemodel.get_value(iter, 12)
		self.title = self.ParentClass.ParentClass.treemodel.get_value(iter, 0)
		self.icon = self.ParentClass.ParentClass.treemodel.get_value(iter, 8) 
		self.class_id = self.ParentClass.ParentClass.treemodel.get_value(iter, 9)
		self.user = self.ParentClass.ParentClass.treemodel.get_value(iter, 10)
		self.command = self.ParentClass.ParentClass.treemodel.get_value(iter, 3)
		self.runat = self.time + " " + self.date
		#parse 	
		(hour, minute, day, month, year) = self.__parse_time__(self.time, self.date)
		self.calendar.select_month(int(month) - 1, int(year))
		self.calendar.select_day(int(day))
		self.hour_spinbutton.set_text(hour)
		self.minute_spinbutton.set_text(minute)
		self.widget.set_title(_("Edit a scheduled task"))
		self.__update_textboxes__ ()
		self.parentiter = iter
		self.widget.show ()
		self.__reload_templates__ ()
		self.NOACTION = gtk.FALSE

	def on_worded_label_event (self, *args):
		#TODO highlight on mouseover
		pass

	def on_defined_label_event (self, *args):
		#TODO highlight on mouseover
		# enable control_option on click
		pass

	def on_script_textview_popup_menu (self, *args):
		#TODO show at_script_menuons: install t
		# don't forget to attach eventhandling to this popup
		pass
	
	def on_script_textview_change (self, *args):
		start = self.script_textview_buffer.get_start_iter()
		end = self.script_textview_buffer.get_end_iter()
		self.command = self.script_textview_buffer.get_text(start, end)


	def on_title_entry_changed (self, *args):
		self.title = self.title_entry.get_text()

	def on_calendar_day_selected (self, *args):		
		self.__update_time_cal__()

	def on_calendar_month_changed (self, *args):
		self.__update_time_cal__()
	
	def on_calendar_year_changed (self, *args):
		self.__update_time_cal__()

	def on_hour_spinbutton_changed (self, *args):
		self.__update_time_cal__()

	def on_minute_spinbutton_changed (self, *args):
		self.__update_time_cal__()

	
	def __update_time_cal__ (self):
		if self.NOACTION != gtk.TRUE:
			(year, month, day) = self.calendar.get_date()
			hour = self.hour_spinbutton.get_text()
			minute = self.minute_spinbutton.get_text()
			month = month + 1 #months start at 0
			year = str(year)
			if hour:
				hour = int(hour)
			else:
				return

			if minute:
				minute = int(minute)
			else:
				return
	
			if hour < 10:
				hour = "0" + str(hour)
			else:
				hour = str(hour)
	
			if minute < 10:
				minute = "0" + str(minute)
			else:
				minute = str(minute)
			
			if month < 10:
				month = "0" + str(month)
			else:
				month = str(month)

			if day < 10:
				day = "0" + str(day)
			else:
				day = str(day)

			self.runat = hour + ":" + minute + " " + year + "-" + month + "-" + day
			self.noupdate = gtk.TRUE
			if self.combo_trigger == gtk.FALSE:
				self.__update_textboxes__()

			self.noupdate = gtk.FALSE


	def __update_time_combo__ (self):
		if self.NOACTION != gtk.TRUE:

			#update variables, set calendar
			runat = self.combobox_entry.get_text ()
			self.runat = runat
			regexp = re.compile("([0-9][0-9]):([0-9][0-9])\ ([0-9][0-9][0-9][0-9])-([0-9][0-9])-([0-9][0-9])")
			runat_g = regexp.match(self.runat)
			if runat_g:

				(hour, minute, year, month, day) =  runat_g.groups()
				year = int(year)
				month = int(month)
				day = int(day)
				self.calendar.select_month(month - 1, year)
				self.calendar.select_day(day)
				self.hour_spinbutton.set_text(hour)
				self.minute_spinbutton.set_text(minute)

			self.__update_textboxes__ (0)

				
	def on_combobox_changed (self, *args):
		if self.NOACTION != gtk.TRUE:
			if self.noupdate == gtk.FALSE:	
				self.combo_trigger = gtk.TRUE
				self.__update_time_combo__()
				self.combo_trigger = gtk.FALSE


	def on_delete_button_clicked (self, *args):
		iter = self.template_combobox.get_active_iter ()
		template = self.template_combobox_model.get_value(iter, 2)
		icon_uri, command, timeexpression, title, name = template
		self.template_combobox.set_active (0)
		preset.removetemplate ("at", name)


	def on_save_button_clicked (self, *args):
		# Uses SaveTemplate (will call it if OK is pressed)
		self.__SaveTemplate__ (self.template_combobox.get_child().get_text())
		
		
	def __SaveTemplate__ (self, template_name):
		#TODO: validate record
		preset.savetemplate ("at", template_name, self.runat, self.title, self.icon, self.command)
			

	def gconfkey_changed (self, client, connection_id, entry, args):
		if self.NOACTION != gtk.TRUE:

			self.__reload_templates__ ()


	def __reload_templates__ (self):

		self.template_names = preset.gettemplatenames ("at")
		if not (self.template_names == None or len (self.template_names) <= 0):
			active = self.template_combobox.get_active ()
			if active == -1:
				active = 0
	
		self.template_combobox_model.clear ()
		self.template_combobox_model.append ([_("Don't use a preset"), None, None])
		

		if self.template_names == None or len (self.template_names) <= 0:
			active = 0
			self.remove_button.set_sensitive (gtk.FALSE)
			self.save_button.set_sensitive (gtk.FALSE)
			self.template_combobox.set_active (0)
		else:
			
			for template_name in self.template_names:
				thetemplate = preset.gettemplate ("at",template_name)
				icon_uri, command, runat, title, name  = thetemplate
				#print "icon_uri: " + icon_uri
				#print "command: " + command
				#print "runat: " + runat
				#print "title: " + title
				#print "name: " + name
				self.template_combobox_model.append([name, template_name, thetemplate])
						
			self.remove_button.set_sensitive (gtk.TRUE)
			
		self.template_combobox.set_active (active)
		

	def on_template_combobox_entry_changed (self, widget):
		if self.NOACTION != gtk.TRUE:
			firstiter = self.template_combobox_model.get_iter_first()
			notemplate = self.template_combobox_model.get_value(firstiter,0)
			entry = self.template_combobox.get_child().get_text()
			if notemplate != entry:
				self.save_button.set_sensitive (gtk.TRUE)
			else:
				self.save_button.set_sensitive (gtk.FALSE)
	

	def on_template_combobox_changed (self, *args):
		if self.NOACTION != gtk.TRUE:
			if self.noevents == gtk.FALSE:
				iter = self.template_combobox.get_active_iter ()
				if iter == None:
					return
				template = self.template_combobox_model.get_value(iter, 2)
				if template != None:
					self.remove_button.set_sensitive (gtk.TRUE)
					icon_uri, command, runat, title, name = template
					if icon_uri != None:
						pixbuf = gtk.gdk.pixbuf_new_from_file_at_size (icon_uri, 60, 60)
						self.template_image.set_from_pixbuf(pixbuf)
						self.icon = icon_uri
					else:
						self.__loadicon__ ()
					self.title = title
					self.command = command
					if runat != None:
						self.runat = runat

						self.__update_textboxes__ ()

						self.on_combobox_changed()
					else:		
						self.__update_textboxes__ ()
				else:
					self.remove_button.set_sensitive (gtk.FALSE)
					self.save_button.set_sensitive (gtk.FALSE)
					self.__loadicon__ ()

					self.__reset__ ()
	
	
	def on_image_button_clicked (self, *args):
		preview = gtk.Image()
		preview.show()
		iconopendialog = gtk.FileChooserDialog(_("Pick an icon for this scheduled task"), self.widget, gtk.FILE_CHOOSER_ACTION_OPEN, (gtk.STOCK_OK, gtk.RESPONSE_ACCEPT, gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT), "")
		# Preview stuff appears to be highly unstable :-(
		# iconopendialog.set_preview_widget(preview)
		# iconopendialog.connect("update-preview", self.update_preview_cb, preview)
		res = iconopendialog.run()
		if res != gtk.RESPONSE_REJECT:
			self.icon = iconopendialog.get_filename()
		iconopendialog.destroy ()

		self.__update_textboxes__ ()

#	def update_preview_cb(self, file_chooser, preview):
#		filename = file_chooser.get_preview_filename()
#		try:
#			pixbuf = gtk.gdk.pixbuf_new_from_file_at_size(filename, 128, 128)
#			preview.set_from_pixbuf(pixbuf)
#			have_preview = gtk.TRUE
#		except:
#			have_preview = gtk.FALSE
#			file_chooser.set_preview_widget_active(have_preview)
#		return


	def __loadicon__ (self):
		nautilus_icon = support.nautilus_icon ("i-executable")
		if nautilus_icon != None:
			pixbuf = gtk.gdk.pixbuf_new_from_file_at_size (nautilus_icon, 60, 60)
			self.template_image.set_from_pixbuf(pixbuf)
			self.icon = nautilus_icon
		else:
			pixbuf = gtk.gdk.pixbuf_new_from_file_at_size ("/usr/share/icons/gnome/48x48/mimetypes/gnome-mime-application.png", 60, 60)
			self.template_image.set_from_pixbuf(pixbuf)
			self.icon = "/usr/share/icons/gnome/48x48/mimetypes/gnome-mime-application.png"

	
	def __reset__ (self):
		self.title = "Untitled"
		self.command = ""
		self.icon = "/usr/share/icons/gnome/48x48/mimetypes/gnome-mime-application.png"

		ctime = time.gmtime()
		year = ctime[0]
		month = ctime[1]
		day = ctime[2]
		hour = ctime[3]
		minute = ctime[4]
		


		firstday, ndays = calendar.monthrange(year,month)
		
		if day == ndays:
			if month != 12:
				month = month + 1
			else:
				month = 1
				year = year + 1
			day = 1
		else:
			day = day + 1
		
		self.runat = str(hour) + ":" + str(minute) + " " + str(year) + "-" + str(month) + "-" + str(day)
		self.calendar.select_month(month - 1, year)
		
		self.calendar.select_day(day)
		self.hour_spinbutton.set_text(str(hour))
		self.minute_spinbutton.set_text(str(minute))

		self.__update_textboxes__ () #update_textboxes inside
		

	def __update_textboxes__(self, update_runat = 1):

		self.noevents = gtk.TRUE
		if self.title == None:
			self.title = "Untitled"

		self.title_entry.set_text(self.title)
		self.script_textview_buffer.set_text(self.command)
		if update_runat:
			if self.combobox_entry.get_text() != self.runat:
				self.combobox_entry.set_text(self.runat)

		if self.icon != None:
			pixbuf = gtk.gdk.pixbuf_new_from_file_at_size (self.icon, 60, 60)
			self.template_image.set_from_pixbuf(pixbuf)

		else:
			self.__loadicon__ ()

		self.noevents = gtk.FALSE


	def __parse_time__ (self, time, date):
		regexp_date = re.compile("([0-9][0-9][0-9][0-9])-([0-9][0-9])-([0-9][0-9])")
		regexp_time = re.compile("([0-9][0-9]):([0-9][0-9])")

		time_g = regexp_time.match(time)
		if time_g:
			(hour, minute) = time_g.groups()

		date_g = regexp_date.match(date)
		if date_g:
			(year, month, day) = date_g.groups()	
		
		return hour, minute, day, month, year


	def on_help_button_clicked (self, *args):
		help_page = "file://" + config.getDocdir() + "/addingandediting.html"
		path = config.getGnomehelpbin ()
		pid = os.fork()
		if not pid:
			os.execv(path, [path, help_page])


	def on_cancel_button_clicked (self, *args):
		self.widget.hide()
		return gtk.TRUE


	def __WrongRecordDialog__ (self, x):
		self.wrongdialog = gtk.MessageDialog(self.widget, gtk.DIALOG_MODAL|gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_ERROR, gtk.BUTTONS_OK, (_("This is an invalid record! The problem could be: %s ") % (x)))
		self.wrongdialog.run()
		self.wrongdialog.destroy()


	def on_ok_button_clicked (self, *args):
		(validate, reason) = self.ParentClass.checkfield(self.runat)
		if validate == gtk.FALSE:
			self.__WrongRecordDialog__ (reason)
			return
		# TODO: Fill record
		
		if self.editing != gtk.FALSE:
			self.ParentClass.update (self.job_id, self.runat, self.command, self.title, self.icon)
				
		else:
			self.ParentClass.append (self.runat, self.command, self.title, self.icon)
			
		self.widget.hide ()
