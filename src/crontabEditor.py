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
import string
import re

#custom modules
import config
import support


##
## I18N
##
import gettext
domain = 'gnome-schedule'
gettext.bindtextdomain(domain)
gettext.textdomain(domain)
_ = gettext.gettext


class CrontabEditor:
	def __init__(self, parent, schedule):

		self.ParentClass = parent
		#crontab in this case
		self.schedule = schedule
		
		self.xml = self.ParentClass.xml
		#self.widget = self.schedule.editorwidget
		self.widget = self.xml.get_widget("crontabEditor")
		self.widget.connect("delete-event", self.on_cancel_button_clicked)

		#self.editorhelperwidget = self.schedule.editorhelperwidget

		self.fieldRegex = re.compile('^(\*)$|^([0-9]+)$|^\*\\\([0-9]+)$|^([0-9]+)-([0-9]+)$|(([0-9]+[|,])+)')
		self.nooutputRegex = re.compile('([^#\n$]*)>(\s|)/dev/null\s2>&1')
		
		self.editing = gtk.FALSE
		self.noevents = gtk.FALSE
		self.noentryevents = gtk.FALSE
		self.template_combobox_model = None
		
		##simple tab	
		self.notebook = self.xml.get_widget("notebook")
		self.template_image = self.xml.get_widget ("template_image")
		self.image_button = self.xml.get_widget ("image_button")
		self.template_label = self.xml.get_widget ("template_label")
		self.basic_table = self.xml.get_widget ("basic_table")
		
		self.save_button = self.xml.get_widget ("save_button")
		self.remove_button = self.xml.get_widget("remove_button")
		
		self.template_combobox = self.xml.get_widget ("template_combobox")
		self.template_combobox_model = gtk.ListStore(gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_PYOBJECT)
		#self.template_combobox.set_text_column (0)		
		self.template_combobox.set_model (self.template_combobox_model)
		
		self.title_entry = self.xml.get_widget ("title_entry")
		self.command_entry = self.xml.get_widget ("command_entry")
		self.nooutput_label = self.xml.get_widget ("nooutput_label")

		self.frequency_combobox = self.xml.get_widget ("frequency_combobox")
		self.frequency_combobox_model = gtk.ListStore (gobject.TYPE_STRING, gobject.TYPE_PYOBJECT)
		self.frequency_combobox_model.append([_("use advanced"), None])
		self.frequency_combobox_model.append([_("minute"), ["*", "*", "*", "*", "*"]])
		self.frequency_combobox_model.append([_("hour"), ["0", "*", "*", "*", "*"]])
		self.frequency_combobox_model.append([_("day"), ["0", "0", "*", "*", "*"]])
		self.frequency_combobox_model.append([_("month"), ["0", "0", "1", "*", "*"]])
		self.frequency_combobox_model.append([_("week"), ["0", "0", "*", "*", "1"]])
		self.frequency_combobox.set_model (self.frequency_combobox_model)
		
		self.chkNoOutput = self.xml.get_widget("chkNoOutput")
				
		self.help_button = self.xml.get_widget ("help_button")
		self.cancel_button = self.xml.get_widget ("cancel_button")
		self.ok_button = self.xml.get_widget ("ok_button")
		
		self.template_combobox.get_child().connect ("changed", self.on_template_combobox_entry_changed)
		self.xml.signal_connect("on_remove_button_clicked", self.on_remove_button_clicked)
		self.xml.signal_connect("on_add_help_button_clicked", self.on_add_help_button_clicked)
		self.xml.signal_connect("on_cancel_button_clicked", self.on_cancel_button_clicked)
		self.xml.signal_connect("on_ok_button_clicked", self.on_ok_button_clicked)
		self.xml.signal_connect("on_anyadvanced_entry_changed", self.on_anyadvanced_entry_changed)
		self.xml.signal_connect("on_anybasic_entry_changed", self.on_anybasic_entry_changed)
		self.xml.signal_connect("on_frequency_combobox_changed", self.on_frequency_combobox_changed)
		self.xml.signal_connect("on_chkNoOutput_toggled", self.on_anybasic_entry_changed)
		self.xml.signal_connect("on_image_button_clicked", self.on_image_button_clicked)
		self.xml.signal_connect("on_save_button_clicked", self.on_save_button_clicked)
		self.xml.signal_connect("on_fieldHelp_clicked", self.on_fieldHelp_clicked)
		self.xml.signal_connect("on_template_combobox_changed", self.on_template_combobox_changed)
		##
		
		##advanced tab
		self.minute_entry = self.xml.get_widget ("minute_entry")
		self.hour_entry = self.xml.get_widget ("hour_entry")
		self.day_entry = self.xml.get_widget ("day_entry")
		self.month_entry = self.xml.get_widget ("month_entry")
		self.weekday_entry = self.xml.get_widget ("weekday_entry")
				
		self.setting_label = self.xml.get_widget ("setting_label")
		##
		
		
		self.nooutput = self.chkNoOutput.get_active()
		self.loadicon ()
		self.reload_templates ()
		
		#gconf code
		support.gconf_client.add_dir ("/apps/gnome-schedule/presets/crontab", gconf.CLIENT_PRELOAD_NONE)
		support.gconf_client.notify_add ("/apps/gnome-schedule/presets/crontab/installed", self.gconfkey_changed);
		
		
	#remove template button
	def on_remove_button_clicked (self, *args):
		iter = self.template_combobox.get_active_iter ()
		template = self.template_combobox_model.get_value(iter, 2)
		icon_uri, command, frequency, title, name = template
		self.template_combobox.set_active (0)
		self.schedule.removetemplate (name)

		
	#save template	button
	def on_save_button_clicked (self, *args):
		# Uses SaveTemplate (will call it if OK is pressed)
		# self.ParentClass.saveWindow.ShowSaveWindow(self)
		self.SaveTemplate (self.template_combobox.get_child().get_text())


	#save template
	def SaveTemplate (self, template_name):
		try:
			# Type should not be translatable!
			self.check_field_format (self.minute, "minute")
			self.check_field_format (self.hour, "hour")
			self.check_field_format (self.day, "day")
			self.check_field_format (self.month, "month")
			self.check_field_format (self.weekday, "weekday")
		except Exception, ex:
			x, y, z = ex
			self.WrongRecordDialog (x, y, z)
			return

		record = self.minute + " " + self.hour + " " + self.day + " " + self.month + " " + self.weekday + " " + self.command
		self.schedule.savetemplate (template_name, record, self.nooutput, self.title, self.icon)


	#error dialog box 
	def WrongRecordDialog (self, x, y, z):
		self.wrongdialog = gtk.MessageDialog(self.widget, gtk.DIALOG_MODAL|gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_ERROR, gtk.BUTTONS_OK, (_("This is an invalid record! The problem could be at the %s field. Reason: %s") % (y, z)))
		self.wrongdialog.run()
		self.wrongdialog.destroy()


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
		self.template_combobox_model.append ([_("Don't use a preset"), None, None])

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
			pixbuf = gtk.gdk.pixbuf_new_from_file_at_size (nautilus_icon, 60, 60)
			self.template_image.set_from_pixbuf(pixbuf)
			self.icon = nautilus_icon
		else:
			pixbuf = gtk.gdk.pixbuf_new_from_file_at_size ("/usr/share/icons/gnome/48x48/mimetypes/gnome-mime-application.png", 60, 60)
			self.template_image.set_from_pixbuf(pixbuf)
			self.icon = "/usr/share/icons/gnome/48x48/mimetypes/gnome-mime-application.png"

	def showedit (self, record, linenumber, iter, mode):
		self.reload_templates ()
		self.editing = gtk.TRUE
		self.linenumber = linenumber
		self.record = record
		(self.minute, self.hour, self.day, self.month, self.weekday, self.command, self.title, self.icon) = self.schedule.parse (record)
		self.widget.set_title(_("Edit a scheduled task"))
		self.update_textboxes ()
		self.set_frequency_combo ()
		self.parentiter = iter
		self.widget.show ()
		
		
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

		self.template_combobox.set_active (0)
	
	def check_field_format (self, field, type):
		try:
			# Type should not be translatable!
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
		self.title = _("Untitled")
		self.update_textboxes ()
		self.set_frequency_combo()
		self.editing = gtk.FALSE
		self.widget.set_title(_("Create a new scheduled task"))
		self.widget.show ()
		self.nooutput_label.hide ()
		self.nooutput = gtk.FALSE
		self.loadicon ()
		self.reload_templates ()
		self.chkNoOutput.set_active (gtk.TRUE)
		
	def on_template_combobox_entry_changed (self, widget):
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
					pixbuf = gtk.gdk.pixbuf_new_from_file_at_size (icon_uri, 60, 60)
					self.template_image.set_from_pixbuf(pixbuf)
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
			# Type should not be translatable!
			self.check_field_format (self.minute, "minute")
			self.check_field_format (self.hour, "hour")
			self.check_field_format (self.day, "day")
			self.check_field_format (self.month, "month")
			self.check_field_format (self.weekday, "weekday")
		except Exception, ex:
			x, y, z = ex
			self.WrongRecordDialog (x, y, z)
			return

		record = self.minute + " " + self.hour + " " + self.day + " " + self.month + " " + self.weekday + " " + self.command

		if self.editing != gtk.FALSE:
			self.schedule.update (self.linenumber, record, self.parentiter, self.nooutput, self.title, self.icon)
			self.ParentClass.schedule_reload ("crontab")
		else:
			self.schedule.append (record, self.nooutput, self.title, self.icon)
			self.ParentClass.schedule_reload ("crontab")

		self.widget.hide ()


	def set_frequency_combo (self):
		#index = self.schedule.getfrequency (self.minute, self.hour, self.day, self.month, self.weekday)
		index = self.getfrequency (self.minute, self.hour, self.day, self.month, self.weekday)
		self.frequency_combobox.set_active (index)
		
	def getfrequency (self, minute, hour, day, month, weekday):
		# index = _("use advanced")
		index = 0

		# Must be translatable, it's the actual content of the combobox-entry
		if minute == "*" and hour == "*" and month == "*" and day == "*" and weekday == "*":
			# index = self.translate_frequency ("minute")
			index = 1
		if minute == "0" and hour == "*" and month == "*" and day == "*" and weekday == "*":
			# index = self.translate_frequency ("hour")
			index = 2
		if minute == "0" and hour == "0" and month == "*" and day == "*" and weekday == "*":
			# index = self.translate_frequency ("day")
			index = 3
		if minute == "0" and hour == "0" and month == "*" and day == "1" and weekday == "*":
			# index = self.translate_frequency ("month")
			index = 4
		if minute == "0" and hour == "0" and month == "*" and day == "*" and weekday == "0":
			# index = self.translate_frequency ("week")
			index = 5

		return index

	def reset (self):
		self.noevents = gtk.TRUE
		self.minute = "*"
		self.hour = "*"
		self.day = "*"
		self.month = "*"
		self.weekday = "*"
		self.command = "ls"
		self.title = _("Untitled")
		self.nooutput = gtk.FALSE
		self.nooutput_label.hide ()
		self.chkNoOutput.set_active (gtk.TRUE)
		self.update_textboxes ()
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
		if self.icon != None:
			pixbuf = gtk.gdk.pixbuf_new_from_file_at_size (self.icon, 60, 60)
			self.template_image.set_from_pixbuf(pixbuf)

		else:
			self.loadicon ()
		self.setting_label.set_text (self.schedule.createpreview(self.minute, self.hour, self.day, self.month, self.weekday, self.command))
		self.set_frequency_combo()
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
			self.template_combobox.set_active (0)
			self.update_textboxes ()

	def on_anybasic_entry_changed (self, *args):
		if self.noevents == gtk.FALSE:
			self.command = self.command_entry.get_text ()
			self.title = self.title_entry.get_text ()
			self.nooutput = self.chkNoOutput.get_active()
			self.update_textboxes ()

			if self.nooutput:
				self.nooutput_label.show ()
			else:
				self.nooutput_label.hide ()


	def on_frequency_combobox_changed (self, bin):
		iter = self.frequency_combobox.get_active_iter ()
		frequency = self.frequency_combobox_model.get_value(iter, 1)
		if frequency != None:
			self.minute, self.hour, self.day, self.month, self.weekday = frequency
			self.update_textboxes()

	def on_fieldHelp_clicked(self, widget, *args):
		name = widget.get_name()
		field = "minute"
		if name == "btnMinuteHelp" :
			field = "minute"
			expression = self.minute_entry.get_text()
		if name == "btnHourHelp" :
			field = "hour"
			expression = self.hour_entry.get_text()
		if name == "btnDayHelp" :
			field = "day"
			expression = self.day_entry.get_text()
		if name == "btnMonthHelp" :
			field = "month"
			expression = self.month_entry.get_text()
		if name == "btnWeekdayHelp" :
			field = "weekday"
			expression = self.weekday_entry.get_text()

		self.schedule.editorhelper.show (field, expression)
		return
