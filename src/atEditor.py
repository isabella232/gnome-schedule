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
import schedule
import re
import gobject
import os
import config
##
## I18N
##
from rhpl.translate import _, N_
import rhpl.translate as translate
domain = 'gnome-schedule'
translate.textdomain (domain)
gtk.glade.bindtextdomain(domain)

class AtEditor:
	def __init__(self, parent, schedule):
		self.ParentClass = parent
		self.schedule = schedule
		
		self.xml = self.ParentClass.xml
		self.widget = self.ParentClass.editorwidget
		self.widget.connect("delete-event", self.on_cancel_button_clicked)

		self.fieldRegex = re.compile('^(\*)$|^([0-9]+)$|^\*\\\([0-9]+)$|^([0-9]+)-([0-9]+)$|(([0-9]+[|,])+)')

		self.editorhelperwidget = self.ParentClass.editorhelperwidget
		self.nooutputRegex = re.compile('([^#\n$]*)>(\s|)/dev/null\s2>&1')
		
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
		self.notebook = self.xml.get_widget("notebook")

		self.xml.signal_connect("on_add_help_button_clicked", self.on_add_help_button_clicked)
		self.xml.signal_connect("on_cancel_button_clicked", self.on_cancel_button_clicked)
		self.xml.signal_connect("on_ok_button_clicked", self.on_ok_button_clicked)
		self.xml.signal_connect("on_anyadvanced_entry_changed", self.on_anyadvanced_entry_changed)
		self.xml.signal_connect("on_anybasic_entry_changed", self.on_anybasic_entry_changed)
		self.xml.signal_connect("on_frequency_combobox_changed", self.on_frequency_combobox_changed)
		self.xml.signal_connect("on_chkNoOutput_toggled", self.on_anybasic_entry_changed)

		self.xml.signal_connect("on_fieldHelp_clicked", self.on_fieldHelp_clicked)

		self.nooutput = self.chkNoOutput.get_active()
		
	def showedit (self, record, linenumber, iter, mode):
		self.editing = gtk.TRUE
		self.linenumber = linenumber
		self.record = record
		(self.minute, self.hour, self.day, self.month, self.weekday, self.command, self.title) = self.schedule.parse (record)
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

		#switch to advanced tab if required
		if mode == "advanced":
			self.notebook.set_current_page(1)
		else:
			self.notebook.set_current_page(0)

	def frequency_combobox_keypress (self, *args):
		# Returning true will tell gtk that the signal has been processed
		# This basically makes the entry read-only
		return gtk.TRUE

	def check_field_format (self, field, type):
		try:
			self.schedule.checkfield (field, type, self.fieldRegex)
		except Exception, ex:
			raise ex

	def showadd (self, mode):
		self.reset ()

		self.minute = "*"
		self.hour = "*"
		self.day = "*"
		self.month = "*"
		self.weekday = "*"
		self.command = "ls"
		self.title = _("New scheduled task")
		self.update_textboxes ()
		self.set_frequency_combo()
		self.editing = gtk.FALSE
		self.widget.set_title(_("Create a new scheduled task"))
		self.widget.show_all()
		self.nooutput_label.hide ()
		self.nooutput = gtk.FALSE
		self.chkNoOutput.set_active (gtk.FALSE)
		#switch to advanced tab if required
		if mode == "advanced":
			self.notebook.set_current_page(1)
		else:
			self.notebook.set_current_page(0)


	def on_add_help_button_clicked (self, *args):
		help_page = "file://" + config.getDocdir() + "/addingandediting.html"
		path = config.getGnomehelpbin ()
		pid = os.fork()
		if not pid:
			os.execv(path, [path, help_page])

	def on_cancel_button_clicked (self, *args):
		self.widget.hide()
		return gtk.TRUE

	def on_ok_button_clicked (self, *args):
		try:
			self.check_field_format (self.minute, _("minute"))
			self.check_field_format (self.hour, _("hour"))
			self.check_field_format (self.day, _("day"))
			self.check_field_format (self.month, _("month"))
			self.check_field_format (self.weekday, _("weekday"))
		except Exception, ex:
			#x, y, z = ex
			x=""
			y=""
			z=""
			self.wrongdialog = gtk.MessageDialog(self.widget, gtk.DIALOG_MODAL|gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_ERROR, gtk.BUTTONS_OK, _("This is an invalid record! The problem could be at the ") + y + _(" field. Reason: ")+ z)
			self.wrongdialog.run()
			self.wrongdialog.destroy()
			return

		record = self.minute + " " + self.hour + " " + self.day + " " + self.month + " " + self.weekday + " " + self.command

		if self.editing != gtk.FALSE:
			self.schedule.update (self.linenumber, record, self.parentiter, self.nooutput, self.title)
		else:
			self.schedule.append (record, self.nooutput, self.title)
			self.ParentClass.treemodel.clear ()
			self.ParentClass.schedule.read ()

		self.widget.hide ()


	def set_frequency_combo (self):
		index = self.schedule.getfrequency (self.minute, self.hour, self.day, self.month, self.weekday)
		self.frequency_combobox.set_text (index)

	def reset (self):
		self.noevents = gtk.TRUE
		self.command_entry.set_text ("")
		self.title_entry.set_text ("")
		self.minute_entry.set_text ("")
		self.hour_entry.set_text ("")
		self.day_entry.set_text ("")
		self.month_entry.set_text ("")
		self.weekday_entry.set_text ("")
		self.setting_label.set_text (self.schedule.getstandardvalue())
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
		
		self.setting_label.set_text (self.schedule.createpreview(self.minute, self.hour, self.day, self.month, self.weekday, self.command))
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

		if temp == _("minute"):
			self.minute = "*"
			self.hour = "*"
			self.day = "*"
			self.month = "*"
			self.weekday = "*"
		elif temp == _("hour"):
			self.minute = "0"
			self.hour = "*"
			self.day = "*"
			self.month = "*"
			self.weekday = "*"
		elif temp == _("day"):
			self.minute = "0"
			self.hour = "0"
			self.day = "*"
			self.month = "*"
			self.weekday = "*"
		elif temp == _("month"):
			self.minute = "0"
			self.hour = "0"
			self.day = "1"
			self.month = "*"
			self.weekday = "*"
		elif temp == _("week"):
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
		if name == "btnMinuteHelp" :
			name = _("minute")
			expression = self.minute_entry.get_text()
		if name == "btnHourHelp" :
			name = _("hour")
			expression = self.hour_entry.get_text()
		if name == "btnDayHelp" :
			name = _("day")
			expression = self.day_entry.get_text()
		if name == "btnMonthHelp" :
			name = _("month")
			expression = self.month_entry.get_text()
		if name == "btnWeekdayHelp" :
			name = _("weekday")
			expression = self.weekday_entry.get_text()

		self.ParentClass.editorhelper.show (name, expression)
		return
