# addWindow.py - UI code for adding an at record
# Copyright (C) 2004, 2005  Philip Van Hoof <me at pvanhoof dot be>
# Copyright (C) 2004 - 2008 Gaute Hope <eg at gaute dot vetsj dot com>
# Copyright (C) 2004, 2005  Kristof Vansant <de_lupus at pandora dot be>

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


class AtEditor:
	def __init__(self, parent, backend, scheduler, template):
		self.ParentClass = parent
		self.xml = self.ParentClass.xml
		self.backend = backend
		self.scheduler = scheduler
		self.template = template
		

		self.widget = self.xml.get_widget("at_editor")
		self.xml.signal_connect("on_at_editor_delete", self.on_button_cancel_clicked)
		
		self.mode = 0 # 0 = add, 1 = edit, 2 = template

		self.button_save = self.xml.get_widget ("at_button_save")
		self.button_cancel = self.xml.get_widget ("at_button_cancel")
		self.entry_title = self.xml.get_widget ("at_entry_title")
		self.text_task = self.xml.get_widget ("at_text_task")
		self.text_task_buffer = self.text_task.get_buffer()
		self.button_add_template = self.xml.get_widget ("at_button_template")
		self.at_vbox_time = self.xml.get_widget ("at_vbox_time")
		

		self.spin_hour = self.xml.get_widget ("at_spin_hour")
		self.spin_minute = self.xml.get_widget ("at_spin_minute")
		self.spin_year = self.xml.get_widget ("at_spin_year")
		self.spin_month = self.xml.get_widget ("at_spin_month")
		self.spin_day = self.xml.get_widget ("at_spin_day")
		
		self.title_box = self.xml.get_widget ("title_box")
		
		self.image_icon = gtk.Image ()
		self.image_icon.set_from_pixbuf (self.ParentClass.bigiconat)
		self.title_box.pack_start (self.image_icon, False, False, 0)
		self.title_box.reorder_child (self.image_icon, 0)
		self.image_icon.show ()
		
		self.cal_button = self.xml.get_widget ("cal_button")
		self.cal_hbox = gtk.HBox ()
		self.arrow = gtk.Arrow (gtk.ARROW_DOWN, gtk.SHADOW_OUT)
		self.cal_label = gtk.Label (_("Calendar"))
		self.cal_hbox.add (self.cal_label)
		self.cal_hbox.add (self.arrow)
		self.cal_button.add (self.cal_hbox)
		self.cal_button.show_all ()
		
		self.xml.signal_connect ("on_cal_button_toggled", self.on_cal_button_toggled)
		
		self.cal_loaded = False
		self.x, self.y = self.widget.get_position ()
		self.height, self.width = self.widget.get_size ()
		self.cal_active = True
		
		self.xml.signal_connect ("on_at_editor_size_changed", self.on_at_editor_size_changed)
		
		self.xml.signal_connect("on_at_button_cancel_clicked", self.on_button_cancel_clicked)
		self.xml.signal_connect("on_at_button_save_clicked", self.on_button_save_clicked)

		self.xml.signal_connect("on_at_text_task_popup_menu", self.on_text_task_popup_menu)
		self.xml.signal_connect("on_at_text_task_key_release_event", self.on_text_task_change)

		self.xml.signal_connect("on_at_entry_title_changed", self.on_entry_title_changed)

		self.xml.signal_connect("on_at_button_cancel_clicked", self.on_button_cancel_clicked)
		self.xml.signal_connect ("on_at_button_template_clicked", self.on_button_template_clicked)
		
		self.xml.signal_connect("on_at_spin_hour_changed", self.on_spin_hour_changed)
		self.xml.signal_connect("on_at_spin_minute_changed", self.on_spin_minute_changed)
		self.xml.signal_connect ("on_at_spin_year_changed", self.on_spin_year_changed)
		self.xml.signal_connect ("on_at_spin_month_changed", self.on_spin_month_changed)
		self.xml.signal_connect ("on_at_spin_day_changed", self.on_spin_day_changed)
		
		
	def showadd (self):
		self.button_save.set_label (gtk.STOCK_ADD)
		self.__reset__ ()
		self.title = _("Untitled")
		self.mode = 0 # add new task
		self.widget.set_title(_("Create a New Scheduled Task"))
		self.widget.set_transient_for(self.ParentClass.widget)
		self.widget.set_position(gtk.WIN_POS_CENTER_ON_PARENT)
		self.__setup_calendar__ ()
		self.widget.show_all ()
		
		self.__update_textboxes__()
	
	def showadd_template (self, title, command):
		self.button_save.set_label (gtk.STOCK_ADD)
		self.__reset__ ()
		self.title = title
		self.command = command
		self.mode = 0 # add new task
		self.widget.set_title(_("Create a New Scheduled Task"))
		self.widget.set_transient_for(self.ParentClass.widget)
		self.widget.set_position(gtk.WIN_POS_CENTER_ON_PARENT)
		self.__setup_calendar__ ()
		self.widget.show_all ()
		
		self.__update_textboxes__()
	
	def showedit_template (self, id, title, command):
		self.button_save.set_label (gtk.STOCK_ADD)
		self.__reset__ ()
		self.tid = id
		self.title = title
		self.command = command
		self.mode = 2 # edit template
		
		self.widget.set_title(_("Edit template"))
		self.widget.set_transient_for(self.ParentClass.widget)
		self.widget.set_position(gtk.WIN_POS_CENTER_ON_PARENT)
		self.__setup_calendar__ ()
		self.widget.show_all ()
		
		# grey out time settings
		self.at_vbox_time.hide ()
		
		# save and cancel buttons
		self.button_save.set_label (gtk.STOCK_SAVE)
		self.button_add_template.hide ()
		
		self.__update_textboxes__()
		
	def showedit (self, record, job_id, iter):
		self.button_save.set_label (gtk.STOCK_APPLY)
		self.mode = 1 # edit task
		self.job_id = job_id
		self.date = self.ParentClass.treemodel.get_value(iter, 9)
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
			
		#parse 	
		(hour, minute, day, month, year) = self.__parse_time__(self.time, self.date)
		self.runat = hour + ":" + minute  + " " + year + "-" + month + "-" + day 
		self.spin_year.set_value (int (year))
		self.spin_month.set_value (int (month))
		self.spin_day.set_value (int (day))

		self.spin_hour.set_value(int(hour))
		self.spin_minute.set_value(int(minute))
		self.widget.set_title(_("Edit a Scheduled Task"))
		
		self.__update_textboxes__ ()
		self.parentiter = iter
		self.widget.set_transient_for(self.ParentClass.widget)
		self.widget.set_position(gtk.WIN_POS_CENTER_ON_PARENT)
		self.__setup_calendar__ ()
		self.widget.show_all ()

		

	def on_cal_lost_focus (self, *args):
		self.__hide_calendar__ ()
		
	def on_at_editor_size_changed (self, *args):
		if self.cal_button.get_active ():
			x, y = self.widget.get_position ()
			height, width = self.widget.get_size ()
			if ((x != self.x) or (y != self.y) or (height != self.height) or (width != self.width)):
				self.__hide_calendar__ ()
				
		
		
			
	def on_cal_button_toggled (self, *args):
		if self.cal_button.get_active ():
			self.__show_calendar__ ()
		else:
			self.__hide_calendar__ ()
	
	
	def __setup_calendar__ (self):
		if self.cal_loaded == False:
			self.xml.signal_connect ("on_cal_lost_focus", self.on_cal_lost_focus)
			self.xml.signal_connect ("on_cal_window_destroy", self.__destroy_calendar__) # its actually not destroyed, but deleted
		
			self.xml.signal_connect ("on_cal_day_selected_dc", self.on_cal_day_selected_dc)
			self.xml.signal_connect ("on_cal_day_selected", self.on_cal_day_selected)
		
			self.cal_window = self.xml.get_widget ("cal_window")
			self.calendar = self.xml.get_widget ("calendar")
			self.cal_window.hide_all ()
			self.cal_loaded = True
		
	def __destroy_calendar__ (self):
		self.cal_window.hide_all ()
		return True

	def on_cal_day_selected (self, *args):
		if self.cal_active:
			year, month, day = self.calendar.get_date ()
			self.spin_year.set_value (int (year))
			self.spin_month.set_value (int (month) + 1)
			self.spin_day.set_value (int (day))
		
	def on_cal_day_selected_dc (self, *args):
		self.__hide_calendar__ ()
				
	def __show_calendar__ (self):
		x, y = self.widget.get_position ()
		button_rect = self.cal_button.get_allocation ()
		x = x + button_rect.x
		y = y + button_rect.y + button_rect.height
		self.cal_window.move (x, y)
		self.widget.set_modal (False)
		self.x, self.y = self.widget.get_position ()
		self.height, self.width = self.widget.get_size ()
		self.cal_active = False
		self.calendar.select_month (self.spin_month.get_value_as_int () -1 , self.spin_year.get_value_as_int ())
		self.calendar.select_day (self.spin_day.get_value_as_int ())
		self.cal_active = True
		self.cal_window.show_all ()
		
	def __hide_calendar__ (self):
		self.cal_window.hide_all ()
		self.cal_button.set_active (False)
		self.widget.set_modal (True)
		
	def on_worded_label_event (self, *args):
		#TODO highlight on mouseover
		pass

	def on_defined_label_event (self, *args):
		#TODO highlight on mouseover
		# enable control_option on click
		pass

	def on_text_task_popup_menu (self, *args):
		#TODO show at_script_menuons: install t
		# don't forget to attach eventhandling to this popup
		pass
		

	
	def on_text_task_change (self, *args):
		start = self.text_task_buffer.get_start_iter()
		end = self.text_task_buffer.get_end_iter()
		self.command = self.text_task_buffer.get_text(start, end)


	def on_entry_title_changed (self, *args):
		self.title = self.entry_title.get_text()

	def on_spin_day_changed (self, *args):		
		self.__update_time_cal__()

	def on_spin_month_changed (self, *args):
		self.__update_time_cal__()
	
	def on_spin_year_changed (self, *args):
		self.__update_time_cal__()

	def on_spin_hour_changed (self, *args):
		self.__update_time_cal__()

	def on_spin_minute_changed (self, *args):
		self.__update_time_cal__()

	
	def __update_time_cal__ (self):
		year = self.spin_year.get_text ()
		month = self.spin_month.get_text ()
		day = self.spin_day.get_text ()
		hour = self.spin_hour.get_text()
		minute = self.spin_minute.get_text()

		year = str(year)
		
		if hour.isdigit():
			hour = int(hour)
		else:
			return False
			
		if minute.isdigit():
			minute = int(minute)
		else:
			return False
			
		if day.isdigit ():
			day = int (day)
		else:
			return False
		
		if month.isdigit ():
			month = int (month)
		else:
			return False
		
		if year.isdigit () == False:
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

		self.runat = hour + ":" + minute + " " + year + "-" + month + "-" + day


	def popup_error_no_digit (self, field):
		box_popup = gtk.MessageDialog (self.widget, gtk.DIALOG_MODAL, gtk.MESSAGE_INFO, gtk.BUTTONS_OK, _("In one or both of the fields hour and minute there was entered a letter, or a number out of range. Remember an hour only has 60 minutes and a day only 24 hours."))
		box_popup.set_response_sensitive(gtk.RESPONSE_OK, True)
		run = box_popup.run ()
		box_popup.hide ()
		field.set_text ("0")


	def __reset__ (self):
		self.title = _("Untitled")
		self.command = ""

		ctime = time.localtime()
		year = ctime[0]
		month = ctime[1]
		day = ctime[2]
		hour = ctime[3]
		minute = ctime[4]
		
		self.runat = str(hour) + ":" + str(minute) + " " + str (year) + "-" + str (month) + "-" + str(day)

		self.spin_hour.set_value(int(hour))
		self.spin_minute.set_value(int(minute))
		self.spin_year.set_value (int (year))
		self.spin_month.set_value (int (month))
		self.spin_day.set_value (int (day))

		self.__update_textboxes__ ()
		

	def __update_textboxes__(self, update_runat = 1):

		if self.title == None:
			self.title = _("Untitled")

		self.entry_title.set_text(self.title)
		self.text_task_buffer.set_text(self.command)

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


	def on_button_cancel_clicked (self, *args):
		self.__destroy_calendar__ ()
		self.widget.hide()
		return True
		

	def __WrongRecordDialog__ (self, x):
		self.wrongdialog = gtk.MessageDialog(self.widget, gtk.DIALOG_MODAL|gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_ERROR, gtk.BUTTONS_OK, (_("This is an invalid record! The problem could be: %s") % (x)))
		self.wrongdialog.run()
		self.wrongdialog.destroy()

	def on_button_template_clicked (self, *args):
		self.template.savetemplate_at (0, self.title, self.command)
		self.widget.hide ()

	def on_button_save_clicked (self, *args):
		if self.mode == 2:
			self.template.savetemplate_at (self.tid, self.title, self.command)
			self.ParentClass.template_manager.reload_tv ()
			self.widget.hide ()
			return
			
		(validate, reason) = self.scheduler.checkfield(self.runat)
		if validate == False:
			self.__WrongRecordDialog__ (reason)
			return
		
		if (self.backend.get_not_inform_working_dir_at() != True):
			dia2 = gtk.MessageDialog (self.widget, gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_WARNING, gtk.BUTTONS_NONE, _("Note about working directory of executed tasks:\n\nOne-time tasks will be run from the directory where Gnome schedule is run from (normally the home directory)."))
			dia2.add_buttons ("_Don't show again", gtk.RESPONSE_CLOSE, gtk.STOCK_OK, gtk.RESPONSE_OK, gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL)
			dia2.set_title (_("Warning: Working directory of executed tasks"))
			response = dia2.run ()
			if response == gtk.RESPONSE_CANCEL:
				dia2.destroy ()
				del dia2
				return
			elif response == gtk.RESPONSE_CLOSE:
				self.backend.set_not_inform_working_dir_at (True)
			else:
				pass
			dia2.destroy ()
			del dia2
		
		if self.mode == 1:
			self.scheduler.update (self.job_id, self.runat, self.command, self.title)
		else:
			self.scheduler.append (self.runat, self.command, self.title)
		
		self.ParentClass.schedule_reload ()
			
		self.widget.hide ()
		
