# addWindow.py - UI code for adding an at record
# Copyright (C) 2004, 2005 Philip Van Hoof <me at pvanhoof dot be>
# Copyright (C) 2004, 2005, 2006, 2007 Gaute Hope <eg at gaute dot vetsj dot com>
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
import gobject
import gnome

#python modules
import os
import re
import time
import calendar

#custom modules
import config
import preset


class AtEditor:
	def __init__(self, parent, backend, scheduler):
		self.ParentClass = parent
		self.xml = self.ParentClass.xml
		self.backend = backend
		self.scheduler = scheduler
		

		self.widget = self.xml.get_widget("at_editor")
		self.widget.connect("delete-event", self.widget.hide_on_delete)
		
		self.mode = 0 # 0 = add, 1 = edit, 2 = template

		self.button_save = self.xml.get_widget ("at_button_save")
		self.button_cancel = self.xml.get_widget ("at_button_cancel")
		self.entry_title = self.xml.get_widget ("at_entry_title")
		self.text_task = self.xml.get_widget ("at_text_task")
		self.text_task_buffer = self.text_task.get_buffer()
		self.button_add_template = self.xml.get_widget ("at_button_template")
		self.button_calendar = self.xml.get_widget ("at_button_calendar")

		self.spin_hour = self.xml.get_widget ("at_spin_hour")
		self.spin_minute = self.xml.get_widget ("at_spin_minute")
		self.spin_year = self.xml.get_widget ("at_spin_year")
		self.spin_month = self.xml.get_widget ("at_spin_month")
		self.spin_day = self.xml.get_widget ("at_spin_day")

			

		self.xml.signal_connect("on_at_button_cancel_clicked", self.on_button_cancel_clicked)
		self.xml.signal_connect("on_at_button_save_clicked", self.on_button_save_clicked)

		self.xml.signal_connect("on_at_text_task_popup_menu", self.on_text_task_popup_menu)
		self.xml.signal_connect("on_at_text_task_key_release_event", self.on_text_task_change)

		self.xml.signal_connect("on_at_entry_title_changed", self.on_entry_title_changed)

		self.xml.signal_connect("on_at_button_save_clicked", self.on_button_save_clicked)
		self.xml.signal_connect("on_at_button_cancel_clicked", self.on_button_cancel_clicked)
		self.xml.signal_connect ("on_at_button_calendar_clicked", self.on_button_calendar_clicked)
		self.xml.signal_connect ("on_at_button_template_clicked", self.on_button_template_clicked)
		
		self.xml.signal_connect("on_at_spin_hour_changed", self.on_spin_hour_changed)
		self.xml.signal_connect("on_at_spin_minute_changed", self.on_spin_minute_changed)
		self.xml.signal_connect ("on_at_spin_year_change", self.on_spin_year_cheanged)
		self.xml.signal_connect ("on_at_spin_month_change", self.on_spin_month_changed)
		self.xml.signal_connect ("on_at_spin_day_change", self.on_spin_day_changed)
		
		

		self.backend.add_scheduler_type("at")

	def showadd (self, mode):
		print "add"
		self.__reset__ ()
		self.title = _("Untitled")
		self.mode = 0 # add new task
		self.widget.set_title(_("Create a New Scheduled Task"))
		self.widget.set_transient_for(self.ParentClass.widget)
		self.widget.set_position(gtk.WIN_POS_CENTER_ON_PARENT)
		self.widget.show_all()
		
		self.__update_textboxes__()

	def showedit (self, record, job_id, iter, mode):
		print "showedit"
		self.mode = 1 # edit task
		self.job_id = job_id
		self.date = self.ParentClass.treemodel.get_value(iter, 9)
		print "got date: " + self.date
		self.time = self.ParentClass.treemodel.get_value(iter, 12)
		self.title = self.ParentClass.treemodel.get_value(iter, 0)
		self.class_id = self.ParentClass.treemodel.get_value(iter, 9)
		self.user = self.ParentClass.treemodel.get_value(iter, 10)
		self.command = self.ParentClass.treemodel.get_value(iter, 3)
		# removing beginning newlines.. wherever they come from..
		i = self.command.find ('\n', 0)
		while i == 0:
			self.command = self.command[1:]
			i = self.command.find ('\n', 0)
			
		print "date: ", self.date, "time: ", self.time
		#parse 	
		(hour, minute, day, month, year) = self.__parse_time__(self.time, self.date)
		print "runat"
		self.runat = self.time + " " + day + "." + month + "." + year
		print "cal sel month"
		self.spin_year.set_value (int (year))
		self.spin_month.set_value (int (month))
		self.spin_day.set_value (int (day))

		self.spin_hour.set_value(int(hour))
		self.spin_minute.set_value(int(minute))
		self.widget.set_title(_("Edit a Scheduled Task"))
		print "update textboxes"
		self.__update_textboxes__ ()
		self.parentiter = iter
		self.widget.set_transient_for(self.ParentClass.widget)
		self.widget.set_position(gtk.WIN_POS_CENTER_ON_PARENT)
		self.widget.show ()

		print "showedit done"
		
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
	
	def on_text_task_change (self, *args):
		start = self.text_task_buffer.get_start_iter()
		end = self.text_task_buffer.get_end_iter()
		self.command = self.text_task_buffer.get_text(start, end)


	def on_entry_title_changed (self, *args):
		self.title = self.title_entry.get_text()

	def on_calendar_day_selected (self, *args):		
		self.__update_time_cal__()

	def on_calendar_month_changed (self, *args):
		self.__update_time_cal__()
	
	def on_calendar_year_changed (self, *args):
		self.__update_time_cal__()

	def on_hour_spinbutton_changed (self, *args):
		self.__update_time_cal__()

	def on_spin_minute_changed (self, *args):
		minute = self.spin_minute.get_text ()
		if minute.isdigit ():
			minute = int (minute)
			if minute < 10:
				minute = "0" + str (minute)
			else:
				minute = str (minute)
		else:
			self.spin_minute.set_text (self.minute)
			
		self.__update_time_cal__()

	
	def __update_time_cal__ (self):
		if self.NOACTION != True:
			(year, month, day) = self.calendar.get_date()
			hour = self.hour_spinbutton.get_text()
			minute = self.minute_spinbutton.get_text()
			month = month + 1 #months start at 0
			year = str(year)
			if hour.isdigit():
				hour = int(hour)
			else:
				return False

			if minute.isdigit():
				minute = int(minute)
			else:
				return False
	
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

			self.runat = hour + ":" + minute + " " + day + "." + month + "." + year
			#print self.runat
			self.noupdate = True
			if self.combo_trigger == False:
				self.__update_textboxes__()

			self.noupdate = False


	def __update_time_combo__ (self):
		if self.NOACTION != True:

			#update variables, set calendar
			runat = self.combobox_entry.get_text ()
			self.runat = runat
			regexp = re.compile("([0-9][0-9]):([0-9][0-9])\ ([0-9][0-9])\.([0-9][0-9])\.([0-9][0-9][0-9][0-9])")
			runat_g = regexp.match(self.runat)
			if runat_g:

				(hour, minute, day, month, year) =  runat_g.groups()
				year = int(year)
				month = int(month)
				day = int(day)
				self.calendar.select_month(month - 1, year)
				self.calendar.select_day(day)
				self.hour_spinbutton.set_value(int(hour))
				self.minute_spinbutton.set_value(int(minute))

			self.__update_textboxes__ (0)

				
	def on_combobox_changed (self, *args):
		if self.NOACTION != True:
			if self.noupdate == False:	
				self.combo_trigger = True
				self.__update_time_combo__()
				self.combo_trigger = False


	def popup_error_no_digit (self, field):
		box_popup = gtk.MessageDialog (self.widget, gtk.DIALOG_MODAL, gtk.MESSAGE_INFO, gtk.BUTTONS_OK, _("In one or both of the fields hour and minute there was entered a letter or a number out of range. Remember an hour only has 60 minutes and a day only 24 hours."))
		box_popup.set_response_sensitive(gtk.RESPONSE_OK, True)
		run = box_popup.run ()
		box_popup.hide ()
		field.set_text ("0")
		 
	def template_doesnot_exist (self, message):
		box = gtk.MessageDialog(self.widget, gtk.DIALOG_MODAL, gtk.MESSAGE_INFO, gtk.BUTTONS_OK, message)
		box.set_response_sensitive(gtk.RESPONSE_OK, True)
		run = box.run()
		box.hide()

			
	def on_delete_button_clicked (self, *args):
		firstiter = self.template_combobox_model.get_iter_first()
		notemplate = self.template_combobox_model.get_value(firstiter,0)
		entry = self.template_combobox.get_child().get_text()
		if notemplate != entry:
			iter = self.template_combobox.get_active_iter ()
			if iter != None:
				template = self.template_combobox_model.get_value(iter, 2)
				icon_uri, command, timeexpression, title, name, nooutput = template
				self.template_combobox.set_active (0)
				self.backend.removetemplate ("at", name)
			else: 
				self.template_doesnot_exist(_("The preset has not been saved"))
		else:
			self.template_doesnot_exist(_("To delete a preset, you first need to select one"))


	def on_save_button_clicked (self, *args):
		# Uses SaveTemplate (will call it if OK is pressed)
		firstiter = self.template_combobox_model.get_iter_first()
		notemplate = self.template_combobox_model.get_value(firstiter,0)
		entry = self.template_combobox.get_child().get_text()
		if notemplate != entry:
			self.__SaveTemplate__ (self.template_combobox.get_child().get_text())
		else:
			self.template_doesnot_exist(_("To save a preset, you first have to choose a name for it"))
		
		
	def __SaveTemplate__ (self, template_name):
		#TODO: validate record
		self.backend.savetemplate ("at", template_name, self.runat, self.title, self.icon, self.command, 0)
			
	
	def __reload_templates__ (self):

		self.template_names = self.backend.gettemplatenames ("at")
		if not (self.template_names == None or len (self.template_names) <= 0):
			active = self.template_combobox.get_active ()
			if active == -1:
				active = 0
	
		self.template_combobox_model.clear ()
		self.template_combobox_model.append ([_("Don't use a preset"), None, None])
		

		if self.template_names == None or len (self.template_names) <= 0:
			active = 0
			# self.remove_button.set_sensitive (False)
			# self.save_button.set_sensitive (False)
			self.template_combobox.set_active (0)
		else:
			
			for template_name in self.template_names:
				thetemplate = self.backend.gettemplate ("at",template_name)
				icon_uri, command, runat, title, name, nooutput  = thetemplate
				#print "icon_uri: " + icon_uri
				#print "command: " + command
				#print "runat: " + runat
				#print "title: " + title
				#print "name: " + name
				self.template_combobox_model.append([name, template_name, thetemplate])
						
			# self.remove_button.set_sensitive (True)
			
		self.template_combobox.set_active (active)
		

	def on_template_combobox_entry_changed (self, widget):
		if self.NOACTION != True:
			firstiter = self.template_combobox_model.get_iter_first()
			notemplate = self.template_combobox_model.get_value(firstiter,0)
			entry = self.template_combobox.get_child().get_text()
			# if notemplate != entry:
				# self.save_button.set_sensitive (True)
			# else:
				# self.save_button.set_sensitive (False)
	

	def on_template_combobox_changed (self, *args):
		if self.NOACTION != True:
			if self.noevents == False:
				iter = self.template_combobox.get_active_iter ()
				if iter == None:
					return
				template = self.template_combobox_model.get_value(iter, 2)
				if template != None:
					# self.remove_button.set_sensitive (True)
					icon_uri, command, runat, title, name, nooutput = template
					try:
						pixbuf = gtk.gdk.pixbuf_new_from_file_at_size (icon_uri, 48, 48)
						self.template_image.set_from_pixbuf(pixbuf)
						self.icon = icon_uri
					except (gobject.GError, TypeError):
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
					# self.remove_button.set_sensitive (False)
					# self.save_button.set_sensitive (False)
					self.__loadicon__ ()

					self.__reset__ ()
	
	
	def on_image_button_clicked (self, *args):
		preview = gtk.Image()
		preview.show()
		iconopendialog = gtk.FileChooserDialog(_("Choose an Icon for this Scheduled Task"), self.widget, gtk.FILE_CHOOSER_ACTION_OPEN, (gtk.STOCK_OK, gtk.RESPONSE_ACCEPT, gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT), "")
		
		# Preview stuff appears to be highly unstable :-(
		# 2005-12-23, gauteh: seems to work ok now.
		
		iconopendialog.set_preview_widget(preview)
		iconopendialog.connect("update-preview", self.update_preview_cb, preview)
		res = iconopendialog.run()
		if res != gtk.RESPONSE_REJECT:
			self.icon = iconopendialog.get_filename()
		iconopendialog.destroy ()

		self.__update_textboxes__ ()

	def update_preview_cb(self, file_chooser, preview):
		filename = file_chooser.get_preview_filename()
		
		try:
			pixbuf = gtk.gdk.pixbuf_new_from_file_at_size(filename, 128, 128)
			preview.set_from_pixbuf(pixbuf)
			have_preview = True
			
		except:
			have_preview = False
		
		file_chooser.set_preview_widget_active(have_preview)
			
		return


	def __loadicon__ (self):
		try:
			pixbuf = gtk.gdk.pixbuf_new_from_file_at_size (self.defaultIcon, 48, 48)
			self.icon = self.defaultIcon
		except gobject.GError:
			pixbuf = gtk.Widget.render_icon (self.widget, gtk.STOCK_MISSING_IMAGE, self.template_image_size, None)
			self.icon = ""

		self.template_image.set_from_pixbuf(pixbuf)

	
	def __reset__ (self):
		self.title = "Untitled"
		self.command = ""
		self.icon = self.defaultIcon

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
		
		self.runat = str(hour) + ":" + str(minute) + " " + str(day) + "." + str(month) + "." + str(year)
		self.calendar.select_month(month - 1, year)
		
		self.calendar.select_day(day)
		self.hour_spinbutton.set_value(int(hour))
		self.minute_spinbutton.set_value(int(minute))

		self.__update_textboxes__ () #update_textboxes inside
		

	def __update_textboxes__(self, update_runat = 1):

		self.noevents = True
		if self.title == None:
			self.title = "Untitled"

		self.title_entry.set_text(self.title)
		self.script_textview_buffer.set_text(self.command)
		if update_runat:
			if self.combobox_entry.get_text() != self.runat:
				self.combobox_entry.set_text(self.runat)

		try:
			pixbuf = gtk.gdk.pixbuf_new_from_file_at_size (self.icon, 48, 48)
			self.template_image.set_from_pixbuf(pixbuf)
		except (gobject.GError, TypeError):
			self.__loadicon__ ()

		self.noevents = False


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


	def on_at_help_button_clicked (self, *args):
		try:
			gnome.help_display_with_doc_id (
					self.ParentClass.gprogram, '',
					'gnome-schedule.xml',
					'myapp-adding-once')
		except gobject.GError, error:
			dialog = gtk.MessageDialog (
					self.widget,
					gtk.DIALOG_DESTROY_WITH_PARENT,
					gtk.MESSAGE_ERROR, gtk.BUTTONS_CLOSE)
			dialog.set_markup ("<b>" + _("Could not display help") + "</b>")
			dialog.format_secondary_text ("%s" % error)
			dialog.run ()
			dialog.destroy ()


	def on_cancel_button_clicked (self, *args):
		self.widget.hide()
		


	def __WrongRecordDialog__ (self, x):
		self.wrongdialog = gtk.MessageDialog(self.widget, gtk.DIALOG_MODAL|gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_ERROR, gtk.BUTTONS_OK, (_("This is an invalid record! The problem could be: %s") % (x)))
		self.wrongdialog.run()
		self.wrongdialog.destroy()


	def on_ok_button_clicked (self, *args):
		(validate, reason) = self.scheduler.checkfield(self.runat)
		if validate == False:
			self.__WrongRecordDialog__ (reason)
			return
		
		
		if self.editing != False:
			self.scheduler.update (self.job_id, self.runat, self.command, self.title, self.icon)
		else:
			self.scheduler.append (self.runat, self.command, self.title, self.icon)
		
		self.ParentClass.schedule_reload ()
			
		self.widget.hide ()
		
