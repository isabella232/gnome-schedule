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

import gtk
import pwd
import mainWindow
import string
import crontab
import re
import gobject
##
## I18N
##
from rhpl.translate import _, N_
import rhpl.translate as translate
domain = 'gnome-schedule'
translate.textdomain (domain)
gtk.glade.bindtextdomain(domain)

class AddWindow:
	def __init__(self, parent, crontab):
		self.ParentClass = parent
		self.crontab = crontab
		self.nooutputtag = ">/dev/null 2>&1"
		
		self.xml = self.ParentClass.xml
		self.widget = self.ParentClass.addwidget
		self.widget.connect("delete-event", self.on_cancel_button_clicked)

		self.editing = gtk.FALSE
		self.help_button = self.xml.get_widget ("help_button")
		self.cancel_button = self.xml.get_widget ("cancel_button")
		self.ok_button = self.xml.get_widget ("ok_button")
		self.title_entry = self.xml.get_widget ("title_entry")
		# Note that this is the entry inside the combobox
		self.frequency_combobox = self.xml.get_widget ("frequency_combobox").get_child()
		# Trick to make it read-only
		self.frequency_combobox.connect("key_press_event", self.frequency_combobox_keypress)

		self.basic_table = self.xml.get_widget ("basic_table")
		self.nooutput_label = self.xml.get_widget ("nooutput_label")
		self.command_entry = self.xml.get_widget ("command_entry")
		self.minute_entry = self.xml.get_widget ("minute_entry")
		self.hour_entry = self.xml.get_widget ("hour_entry")
		self.day_entry = self.xml.get_widget ("day_entry")
		self.month_entry = self.xml.get_widget ("month_entry")
		self.weekday_entry = self.xml.get_widget ("weekday_entry")
		self.setting_label = self.xml.get_widget ("setting_label")
		self.chkNoOutput = self.xml.get_widget("chkNoOutput")

		self.xml.signal_connect("on_help_button_clicked", self.on_help_button_clicked)
		self.xml.signal_connect("on_cancel_button_clicked", self.on_cancel_button_clicked)
		self.xml.signal_connect("on_ok_button_clicked", self.on_ok_button_clicked)
		self.xml.signal_connect("on_anyadvanced_entry_changed", self.on_anyadvanced_entry_changed)
		self.xml.signal_connect("on_anybasic_entry_changed", self.on_anybasic_entry_changed)
		self.xml.signal_connect("on_frequency_combobox_changed", self.on_frequency_combobox_changed)
		self.xml.signal_connect("on_chkNoOutput_toggled", self.on_anybasic_entry_changed)

		self.xml.signal_connect("on_fieldHelp_clicked", self.on_fieldHelp_clicked)

		self.nooutput = self.chkNoOutput.get_active()
		self.nooutputRegex = re.compile('([^#\n$]*)>(\s|)/dev/null\s2>&1')

	def showEditWindow (self, record, linenumber, iter):
		self.editing = gtk.TRUE
		self.linenumber = linenumber
		self.record = record
		(self.minute, self.hour, self.day, self.month, self.weekday, self.command, self.title) = self.crontab.parseRecord (record)
		self.widget.set_title(_("Edit a scheduled task"))
		self.update_textboxes ()
		self.set_frequency_combo ()
		self.parentiter = iter
		self.widget.show_all()
		
		m = self.nooutputRegex.match (self.command)
		if (m != None):
			self.nooutput_label.show ()
			self.command = m.groups()[0]
			self.command_entry.set_text (self.command)
			self.chkNoOutput.set_active (gtk.TRUE)
			self.nooutput = gtk.TRUE
		else:
			self.nooutput_label.hide ()
			self.chkNoOutput.set_active (gtk.FALSE)
			self.nooutput = gtk.FALSE

	def frequency_combobox_keypress (self, *args):
		# Returning true will tell gtk that the signal has been processed
		# This basically makes the entry read-only
		return gtk.TRUE

	def showAddWindow (self):
		self.reset ()

		self.minute = "*"
		self.hour = "*"
		self.day = "*"
		self.month = "*"
		self.weekday = "*"
		self.command = "ls"
		self.title = "New scheduled task"
		self.update_textboxes ()
		self.set_frequency_combo()
		self.editing = gtk.FALSE
		self.widget.set_title(_("Create a new scheduled task"))
		self.widget.show_all()
		self.nooutput_label.hide ()
		self.nooutput = gtk.FALSE
		self.chkNoOutput.set_active (gtk.FALSE)

	def on_help_button_clicked (self, *args):
		print "Help"

	def on_cancel_button_clicked (self, *args):
		self.widget.hide()
		return gtk.TRUE

	def on_ok_button_clicked (self, *args):
		space = " "
		if self.nooutput:
			if self.command[len(self.command)-1] == " ":
				space = ""
			record = self.minute + " " + self.hour + " " + self.day + " " + self.month + " " + self.weekday + " " + self.command + space + self.nooutputtag + " # " + self.title
		else:
			record = self.minute + " " + self.hour + " " + self.day + " " + self.month + " " + self.weekday + " " + self.command + " # " + self.title

		if self.editing != gtk.FALSE:
			self.crontab.updateLine (self.linenumber, record)
			self.ParentClass.treemodel.set_value (self.parentiter, 3, record)
			self.ParentClass.treemodel.set_value (self.parentiter, 0, self.title)
			easystring = self.crontab.easyString (self.minute, self.hour, self.day, self.month, self.weekday)
			self.ParentClass.treemodel.set_value (self.parentiter, 1, easystring)
			if self.nooutput:
				self.ParentClass.treemodel.set_value (self.parentiter, 2, self.command + space + self.nooutputtag)
			else:
				self.ParentClass.treemodel.set_value (self.parentiter, 2, self.command)
			self.ParentClass.treemodel.set_value (self.parentiter, 5, self.minute + " " + self.hour + " " + self.day + " " + self.month + " " + self.weekday)
		else:
			self.crontab.appendLine (record)
			self.ParentClass.treemodel.clear ()
			self.ParentClass.crontab.readCrontab ()

		self.widget.hide ()


	def set_frequency_combo (self):
		index = "use advanced"
		# index = 0

		if self.minute == "*" and self.hour == "*" and self.month == "*" and self.day == "*" and self.weekday == "*":
			index = "minute"
			# index = 1
		if self.minute == "0" and self.hour == "*" and self.month == "*" and self.day == "*" and self.weekday == "*":
			index = "hour"
			# index = 2
		if self.minute == "0" and self.hour == "0" and self.month == "*" and self.day == "*" and self.weekday == "*":
			index = "day"
			# index = 3
		if self.minute == "0" and self.hour == "0" and self.month == "*" and self.day == "1" and self.weekday == "*":
			index = "month"
			# index = 4
		if self.minute == "0" and self.hour == "0" and self.month == "*" and self.day == "*" and self.weekday == "0":
			index = "week"


		self.frequency_combobox.set_text (index)
		# self.frequency_combobox.set_active (index)


	def reset (self):
		self.noevents = gtk.TRUE
		self.command_entry.set_text ("")
		self.title_entry.set_text ("")
		self.minute_entry.set_text ("")
		self.hour_entry.set_text ("")
		self.day_entry.set_text ("")
		self.month_entry.set_text ("")
		self.weekday_entry.set_text ("")
		self.setting_label.set_text ("* * * * * command")
		self.noevents = gtk.FALSE

	def update_textboxes (self):
		self.noevents = gtk.TRUE
		self.chkNoOutput.set_active (self.nooutput)
		self.command_entry.set_text (self.command)
		self.title_entry.set_text (self.title)
		self.minute_entry.set_text (self.minute)
		self.hour_entry.set_text (self.hour)
		self.day_entry.set_text (self.day)
		self.month_entry.set_text (self.month)
		self.weekday_entry.set_text (self.weekday)
		self.setting_label.set_text (self.minute + " " + self.hour + " " + self.day + " " + self.month + " " + self.weekday + " " + self.command)
		# self.set_frequency_combo()
		self.noevents = gtk.FALSE

	def on_anyadvanced_entry_changed (self, *args):
		if self.noevents == gtk.FALSE:
			self.minute = self.minute_entry.get_text ()
			self.hour = self.hour_entry.get_text ()
			self.day = self.day_entry.get_text ()
			self.month = self.month_entry.get_text ()
			self.weekday = self.weekday_entry.get_text ()
			self.nooutput = self.chkNoOutput.get_active()
			# self.set_frequency_combo ()
			self.update_textboxes ()

	def on_anybasic_entry_changed (self, *args):
		if self.noevents == gtk.FALSE:
			self.command = self.command_entry.get_text ()
			self.title = self.title_entry.get_text ()
			self.nooutput = self.chkNoOutput.get_active()
			self.update_textboxes ()

			# self.noevents = gtk.TRUE
			#m = self.nooutputRegex.match (self.command)
			if self.nooutput:
				#if m == None:
					#if len (self.command) > 0 and self.command[len(self.command)-1] != " ":
					#	self.command = self.command + " "
					#self.command = self.command + self.nooutputtag
					#self.command_entry.set_text (self.command)
				self.nooutput_label.show ()
			else:
				#if m != None:
					#self.command = m.groups()[0]
					#self.command_entry.set_text (self.command)
				self.nooutput_label.hide ()
			# self.noevents = gtk.FALSE


	def on_frequency_combobox_changed (self, bin):
		temp = self.frequency_combobox.get_text()

		if temp == "minute":
			self.minute = "*"
			self.hour = "*"
			self.day = "*"
			self.month = "*"
			self.weekday = "*"
		elif temp == "hour":
			self.minute = "0"
			self.hour = "*"
			self.day = "*"
			self.month = "*"
			self.weekday = "*"
		elif temp == "day":
			self.minute = "0"
			self.hour = "0"
			self.day = "*"
			self.month = "*"
			self.weekday = "*"
		elif temp == "month":
			self.minute = "0"
			self.hour = "0"
			self.day = "1"
			self.month = "*"
			self.weekday = "*"
		elif temp == "week":
			self.minute = "0"
			self.hour = "0"
			self.day = "*"
			self.month = "*"
			self.weekday = "0"
		else:
			pass

		self.update_textboxes()

	def on_fieldHelp_clicked(self, widget, *args):
		name = widget.get_name()
		if name == "btnMinuteHelp" : name = "minute"
		if name == "btnHourHelp" : name = "hour"
		if name == "btnDayHelp" : name = "day"
		if name == "btnMonthHelp" : name = "month"
		if name == "btnWeekdayHelp" : name = "weekday"

		self.ParentClass.addHelpWindow.showAll(name)
		return
