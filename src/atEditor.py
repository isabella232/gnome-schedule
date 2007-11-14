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
		
		self.title_box = self.xml.get_widget ("title_box")
		
		self.image_icon = gtk.Image ()
		self.image_icon.set_from_pixbuf (self.ParentClass.bigiconat)
		self.title_box.pack_start (self.image_icon, False, False, 0)
		self.title_box.reorder_child (self.image_icon, 0)
		
			

		self.xml.signal_connect("on_at_button_cancel_clicked", self.on_button_cancel_clicked)
		self.xml.signal_connect("on_at_button_save_clicked", self.on_button_save_clicked)

		self.xml.signal_connect("on_at_text_task_popup_menu", self.on_text_task_popup_menu)
		self.xml.signal_connect("on_at_text_task_key_release_event", self.on_text_task_change)

		self.xml.signal_connect("on_at_entry_title_changed", self.on_entry_title_changed)

		self.xml.signal_connect("on_at_button_cancel_clicked", self.on_button_cancel_clicked)
		self.xml.signal_connect ("on_at_button_calendar_clicked", self.on_button_calendar_clicked)
		self.xml.signal_connect ("on_at_button_template_clicked", self.on_button_template_clicked)
		
		self.xml.signal_connect("on_at_spin_hour_changed", self.on_spin_hour_changed)
		self.xml.signal_connect("on_at_spin_minute_changed", self.on_spin_minute_changed)
		self.xml.signal_connect ("on_at_spin_year_changed", self.on_spin_year_changed)
		self.xml.signal_connect ("on_at_spin_month_changed", self.on_spin_month_changed)
		self.xml.signal_connect ("on_at_spin_day_changed", self.on_spin_day_changed)
		
		

		self.backend.add_scheduler_type("at")

	def showadd (self, mode):
		print "add"
		self.button_save.set_label (gtk.STOCK_ADD)
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
		self.button_save.set_label (gtk.STOCK_APPLY)
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
		self.runat = self.time + " " + year + "-" + month + "-" + day 
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

	def on_text_task_popup_menu (self, *args):
		#TODO show at_script_menuons: install t
		# don't forget to attach eventhandling to this popup
		pass
		
	def on_button_calendar_clicked (self, *args):
		# TODO: bloddy popups..
		pass
	
	def on_button_template_clicked (self, *args):
		# TODO: ah.. templates.. sweet templates..
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
		print self.runat


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
		self.widget.hide()
		

	def __WrongRecordDialog__ (self, x):
		self.wrongdialog = gtk.MessageDialog(self.widget, gtk.DIALOG_MODAL|gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_ERROR, gtk.BUTTONS_OK, (_("This is an invalid record! The problem could be: %s") % (x)))
		self.wrongdialog.run()
		self.wrongdialog.destroy()


	def on_button_save_clicked (self, *args):
		print "ADD"
		(validate, reason) = self.scheduler.checkfield(self.runat)
		if validate == False:
			self.__WrongRecordDialog__ (reason)
			return
		
		
		if self.mode == 1:
			print "update"
			self.scheduler.update (self.job_id, self.runat, self.command, self.title)
		else:
			print "append"
			self.scheduler.append (self.runat, self.command, self.title)
		
		self.ParentClass.schedule_reload ()
			
		self.widget.hide ()
		
