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
import commands
import gettext
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

class AtEditor:
	def __init__(self, parent, schedule):
		self.ParentClass = parent
		self.schedule = schedule
		self.xml = self.ParentClass.xml
		self.widget = self.xml.get_widget("atEditor")
		self.widget.connect("delete-event", self.on_cancel_button_clicked)
		self.fieldRegex = re.compile('^(\*)$|^([0-9]+)$|^\*\\\([0-9]+)$|^([0-9]+)-([0-9]+)$|(([0-9]+[|,])+)')
		self.nooutputRegex = re.compile('([^#\n$]*)>(\s|)/dev/null\s2>&1')
		self.editing = gtk.FALSE

		self.template_combobox = self.xml.get_widget ("at_template_combobox")
		self.save_button = self.xml.get_widget ("at_save_button")
		self.delete_button = self.xml.get_widget ("at_delete_button")
		self.title_entry = self.xml.get_widget ("at_title_entry")
		self.script_textview = self.xml.get_widget ("at_script_textview")
		self.script_textview_buffer = self.script_textview.get_buffer()
		self.nooutput_checkbutton = self.xml.get_widget ("at_nooutput_checkbutton")
		self.help_button = self.xml.get_widget ("at_help_button")
		self.cancel_button = self.xml.get_widget ("at_cancel_button")
		self.ok_button = self.xml.get_widget ("at_ok_button")
		self.image_button = self.xml.get_widget ("at_image_button")
		self.template_icon = self.xml.get_widget ("at_template_icon")
		self.control_option = self.xml.get_widget ("at_control_option")
		self.wording_option = self.xml.get_widget ("at_wording_option")
		self.calendar = self.xml.get_widget ("at_calendar")
		self.hour_spinbutton = self.xml.get_widget ("at_hour_spinbutton")
		self.minute_spinbutton= self.xml.get_widget ("at_minute_spinbutton")
		self.combobox = self.xml.get_widget ("at_combobox")
		self.combobox_entry = self.combobox.get_child()	
			
		self.xml.signal_connect("on_at_help_button_clicked", self.on_help_button_clicked)
		self.xml.signal_connect("on_at_cancel_button_clicked", self.on_cancel_button_clicked)
		self.xml.signal_connect("on_at_ok_button_clicked", self.on_ok_button_clicked)
		self.xml.signal_connect("on_worded_label_event", self.on_worded_label_event)
		self.xml.signal_connect("on_defined_label_event", self.on_defined_label_event)
		self.xml.signal_connect("on_at_script_textview_popup_menu", self.on_script_textview_popup_menu)
		self.xml.signal_connect("on_at_script_textview_key_release_event", self.on_script_textview_change)
		self.xml.signal_connect("on_at_template_combobox_changed", self.on_template_combobox_changed)
		self.xml.signal_connect("on_at_title_entry_changed", self.on_title_entry_changed)
		self.xml.signal_connect("on_at_nooutput_checkbutton_toggled", self.on_nooutput_checkbutton_toggled)
		self.xml.signal_connect("on_at_save_button_clicked", self.on_save_button_clicked)
		self.xml.signal_connect("on_at_delete_button_clicked", self.on_delete_button_clicked)
		self.xml.signal_connect("on_at_image_button_clicked", self.on_image_button_clicked)
		self.xml.signal_connect("on_at_calendar_day_selected", self.on_calendar_day_selected)
		self.xml.signal_connect("on_at_calendar_month_changed", self.on_calendar_month_changed)
		self.xml.signal_connect("on_at_calendar_year_changed", self.on_calendar_year_changed)
		self.xml.signal_connect("on_at_hour_spinbutton_changed", self.on_hour_spinbutton_changed)
		self.xml.signal_connect("on_at_minute_spinbutton_changed", self.on_minute_spinbutton_changed)
		self.xml.signal_connect("on_at_combobox_changed", self.on_combobox_changed)
		self.xml.signal_connect("on_at_control_option_toggled", self.on_control_option_toggled)
		self.xml.signal_connect("on_at_wording_option_toggled", self.on_wording_option_toggled)
	
		#for the addwindow to not jump more than one day ahead in time
		self.first = 0
				
	def on_worded_label_event (self, *args):
		# highlight on mouseover
		# enable wording_option on click
		pass

	def on_defined_label_event (self, *args):
		# highlight on mouseover
		# enable control_option on click
		pass

	def on_script_textview_popup_menu (self, *args):
		# show at_script_menu
		# don't forget to attach eventhandling to this popup
		pass
	
	def on_script_textview_change (self, *args):
		start = self.script_textview_buffer.get_start_iter()
		end = self.script_textview_buffer.get_end_iter()
		self.command = self.script_textview_buffer.get_text(start, end)
		return

	def on_title_entry_changed (self, *args):
		self.title = self.title_entry.get_text()
		return

	def on_nooutput_checkbutton_toggled (self, *args):
		# I don't know if this is needed at all
		pass

	def on_calendar_day_selected (self, *args):		
		if self.control_option.get_active():
			(year, month, day) = self.calendar.get_date()
			hour = self.hour_spinbutton.get_text()
			minute = self.minute_spinbutton.get_text()
			self.runat = hour + ":" + minute + " " + str(year) + "-" + str(month + 1) + "-" + str(day)
			self.update_textboxes()
		return

	def on_calendar_month_changed (self, *args):
		if self.control_option.get_active():
			(year, month, day) = self.calendar.get_date()
			hour = self.hour_spinbutton.get_text()
			minute = self.minute_spinbutton.get_text()
			self.runat = hour + ":" + minute + " " + str(year) + "-" + str(month + 1) + "-" + str(day)
			self.update_textboxes()
		return
	
	def on_calendar_year_changed (self, *args):
		if self.control_option.get_active():
			(year, month, day) = self.calendar.get_date()
			hour = self.hour_spinbutton.get_text()
			minute = self.minute_spinbutton.get_text()
			self.runat = hour + ":" + minute + " " + str(year) + "-" + str(month + 1) + "-" + str(day)
			self.update_textboxes()
		return


	def on_hour_spinbutton_changed (self, *args):
		if self.control_option.get_active():
			(year, month, day) = self.calendar.get_date()
			hour = self.hour_spinbutton.get_text()
			minute = self.minute_spinbutton.get_text()
			self.runat = hour + ":" + minute + " " + str(year) + "-" + str(month + 1) + "-" + str(day)
			self.update_textboxes()
		return

	def on_minute_spinbutton_changed (self, *args):
		if self.control_option.get_active():
			(year, month, day) = self.calendar.get_date()
			hour = self.hour_spinbutton.get_text()
			minute = self.minute_spinbutton.get_text()
			self.runat = hour + ":" + minute + " " + str(year) + "-" + str(month + 1) + "-" + str(day)
			self.update_textboxes() 
		return

	def on_combobox_changed (self, *args):
		# In this combobox for example "tomorrow" should be checked
		# for being possible or not
		if self.wording_option.get_active():
			self.runat = self.combobox_entry.get_text()

		pass

	def on_control_option_toggled (self, *args):
		# Disable combobox
		# enable the calendar en spinbuttons
		if self.control_option.get_active():
			(year, month, day) = self.calendar.get_date()
			hour = self.hour_spinbutton.get_text()
			minute = self.minute_spinbutton.get_text()
			self.runat = hour + ":" + minute + " " + str(year) + "-" + str(month + 1) + "-" + str(day)
			self.update_textboxes()


	def on_wording_option_toggled (self, *args):
		# Disable the calendar
		# enable the combobox
		pass

	def on_delete_button_clicked (self, *args):
		iter = self.template_combobox.get_active_iter ()
		template = self.template_combobox_model.get_value(iter, 2)
		icon_uri, command, frequency, title, name = template
		self.template_combobox.set_active (0)
		self.schedule.removetemplate (name)

	def on_save_button_clicked (self, *args):
		# Uses SaveTemplate (will call it if OK is pressed)
		# self.ParentClass.saveWindow.ShowSaveWindow(self)
		self.SaveTemplate (self.template_combobox.get_child().get_text())
		
	def SaveTemplate (self, template_name):
		# TODO: Validate record

		# TODO: Fill record something like: [script, time, date]
		self.schedule.savetemplate (template_name, record, self.nooutput, self.title, self.icon)

	def gconfkey_changed (self, client, connection_id, entry, args):
		self.reload_templates ()

	def reload_templates (self):
		self.template_names = self.schedule.gettemplatenames ()
		
		if self.template_names == None or len (self.template_names) <= 0:
			pass
		else:
			active = self.template_combobox.get_active ()
			if active == -1:
				active = 0
	
		self.template_combobox_model.clear ()
		self.template_combobox_model.append ([_("Don't use a template"), None, None])

		if self.template_names == None or len (self.template_names) <= 0:
			active = 0
			self.remove_button.set_sensitive (gtk.FALSE)
			self.save_button.set_sensitive (gtk.FALSE)
			self.template_combobox.set_active (0)
			# self.template_combobox.set_sensitive (gtk.FALSE)
			# self.template_label.set_sensitive (gtk.FALSE)
		else:
			
			for template_name in self.template_names:
				thetemplate = self.schedule.gettemplate (template_name)
				icon_uri, command, frequency, title, name = thetemplate
				self.template_combobox_model.append([name, template_name, thetemplate])
						
			#self.template_combobox.set_sensitive (gtk.TRUE)
			self.remove_button.set_sensitive (gtk.TRUE)
			#self.template_label.set_sensitive (gtk.TRUE)
				
		self.template_combobox.set_active (active)

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
		self.update_textboxes ()

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


	def loadicon (self):
		nautilus_icon = support.nautilus_icon ("i-executable")
		if nautilus_icon != None:
			#self.template_image.set_from_file(nautilus_icon)
			self.icon = nautilus_icon
		else:
			#self.template_image.set_from_file("/usr/share/icons/gnome/48x48/mimetypes/gnome-mime-application.png")
			self.icon = "/usr/share/icons/gnome/48x48/mimetypes/gnome-mime-application.png"
	
	def reset (self):
		self.title = "Untitled"
		self.command = ""
		self.icon = "None"
		(year, month, day) = self.calendar.get_date()
		hour = self.hour_spinbutton.get_text()
		minute = self.minute_spinbutton.get_text()
		if self.first == 1:
			pass
			print "first = 1"
		else:	
			self.calendar.select_day(day+1)
			self.first = 1

		(year, month, day) = self.calendar.get_date()
		hour = self.hour_spinbutton.get_text()
		minute = self.minute_spinbutton.get_text()

		self.runat = hour + ":" + minute + " " + str(year) + "-" + str(month+1) + "-" + str(day)
		self.update_textboxes()
		

	def update_textboxes(self):
		self.title_entry.set_text(self.title)
		self.script_textview_buffer.set_text(self.command)
		self.combobox_entry.set_text(self.runat)
		if self.icon != None:
			#self.template_image.set_from_file(self.icon)
			pass
		else:
			self.loadicon ()
		return

	def showedit (self, record, job_id, iter, mode):
		#self.reload_templates () # not supported yet
		self.editing = gtk.TRUE
		
		self.job_id = job_id
		self.date = self.ParentClass.treemodel.get_value(iter, 8)
		self.time = self.ParentClass.treemodel.get_value(iter, 5)
		self.title = self.ParentClass.treemodel.get_value(iter, 0)
		#self.icon = self.ParentClass.treemodel.get_value(iter, 6) #need the path to the icon somewhere
		self.icon = "None"
		self.class_id = self.ParentClass.treemodel.get_value(iter, 9)
		self.user = self.ParentClass.treemodel.get_value(iter, 10)
		self.command = self.ParentClass.treemodel.get_value(iter, 3)
		self.runat = self.time + " " + self.date	
		self.widget.set_title(_("Edit a scheduled task"))
		self.update_textboxes ()
		self.parentiter = iter
		self.widget.show ()
		self.update_textboxes ()



	def showadd (self, mode):
		self.reset ()
		self.title = _("Untitled")
		self.editing = gtk.FALSE
		self.widget.set_title(_("Create a new scheduled task"))
		self.widget.show_all()
		
		self.update_textboxes ()


	def on_template_combobox_entry_changed (self, *args):
		self.save_button.set_sensitive (gtk.TRUE)

	def on_template_combobox_changed (self, *args):
		if self.noevents == gtk.FALSE:
			iter = self.template_combobox.get_active_iter ()
			if iter == None:
				return
			template = self.template_combobox_model.get_value(iter, 2)
			if template != None:
				self.remove_button.set_sensitive (gtk.TRUE)
				icon_uri, command, frequency, title, name = template
				#if self.ParentClass.saveWindow != None:
				#	self.ParentClass.saveWindow.save_entry.set_text (name)
				if icon_uri != None:
					self.template_image.set_from_file (icon_uri)
					self.icon = icon_uri
				else:
					self.loadicon ()
				if frequency != None and command != None:
					if title != None:
						record = frequency + " " + command + " # " + title
					else:
						record = frequency + " " + command
				else:
					if frequency == None:
						frequency = "* * * * *"
					if command == None:
						command = _("command")
			
				m = self.nooutputRegex.match (command)
				if (m != None):
					self.nooutput_label.show ()
					command = m.groups()[0]
					self.noevents = gtk.TRUE
					self.chkNoOutput.set_active (gtk.TRUE)
					self.noevents = gtk.FALSE
					self.nooutput = gtk.TRUE
				else:
					self.nooutput_label.hide ()
					self.chkNoOutput.set_active (gtk.FALSE)
					self.nooutput = gtk.FALSE

				self.minute, self.hour, self.day, self.month, self.weekday, self.command, self.title, icon_ = self.schedule.parse (record)
				self.command = command
				self.update_textboxes ()
			else:
				self.remove_button.set_sensitive (gtk.FALSE)
				self.save_button.set_sensitive (gtk.FALSE)
				self.loadicon ()
				self.reset ()
		


	def on_help_button_clicked (self, *args):
		help_page = "file://" + config.getDocdir() + "/addingandediting.html"
		path = config.getGnomehelpbin ()
		pid = os.fork()
		if not pid:
			os.execv(path, [path, help_page])

	def on_cancel_button_clicked (self, *args):
		self.widget.hide()
		return gtk.TRUE

	def on_ok_button_clicked (self, *args):
		# TODO: Validate record
		# TODO: Fill record
		if self.editing != gtk.FALSE:
			self.schedule.update (self.job_id, self.runat, self.command, self.title, self.icon)
			self.ParentClass.schedule_reload ()
			print "Edited"		
		else:
			self.schedule.append (self.runat, self.command, self.title, self.icon)
			self.ParentClass.schedule_reload ()
			print "Added"
	
		self.widget.hide ()
