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
		self.widget = self.xml.get_widget("atEditor")
		self.widget.connect("delete-event", self.on_cancel_button_clicked)

		self.fieldRegex = re.compile('^(\*)$|^([0-9]+)$|^\*\\\([0-9]+)$|^([0-9]+)-([0-9]+)$|(([0-9]+[|,])+)')

		#self.editorhelperwidget = self.ParentClass.editorhelperwidget
		self.nooutputRegex = re.compile('([^#\n$]*)>(\s|)/dev/null\s2>&1')
		
		self.editing = gtk.FALSE
		
		
		self.template_combobox = self.xml.get_widget ("at_template_combobox")
		self.save_button = self.xml.get_widget ("at_save_button")
		self.delete_button = self.xml.get_widget ("at_delete_button")
		self.title_entry = self.xml.get_widget ("at_title_entry")
		self.script_textview = self.xml.get_widget ("at_script_textview")
		self.nooutput_checkbutton = self.xml.get_widget ("at_nooutput_checkbutton")
		self.help_button = self.xml.get_widget ("at_help_button")
		self.cancel_button = self.xml.get_widget ("at_cancel_button")
		self.ok_button = self.xml.get_widget ("at_ok_button")
		self.image_button = self.xml.get_widget ("at_image_button")
		self.template_icon = self.xml.get_widget ("at_template_icon")
		self.control_option = self.xml.get_widget ("at_control_option")
		self.wording = self.xml.get_widget ("at_wording_option")
		self.calendar = self.xml.get_widget ("at_calendar")
		self.hour_spinbutton = self.xml.get_widget ("at_hour_spinbutton")
		self.minute_spinbutton= self.xml.get_widget ("at_minute_spinbutton")
		self.combobox = self.xml.get_widget ("at_combobox")
		
	def on_remove_button_clicked (self, *args):
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
			self.template_image.set_from_file(nautilus_icon)
			self.icon = nautilus_icon
		else:
			self.template_image.set_from_file("/usr/share/icons/gnome/48x48/mimetypes/gnome-mime-application.png")
			self.icon = "/usr/share/icons/gnome/48x48/mimetypes/gnome-mime-application.png"

	def reset (self):
		self.runat = "tomorrow"
		self.commands = ""
		self.title = ""
		self.date = ""
		self.time = ""
		self.update_textboxes()
		return

	def update_textboxes (self):
		# TODO
		return		

			
	def showedit (self, record, job_id, iter, mode):
		self.reload_templates ()
		self.editing = gtk.TRUE
		
		(self.script, self.title, self.icon, self.date, self.time) = record
		
		self.widget.set_title(_("Edit a scheduled task"))
		self.update_textboxes ()
		self.set_frequency_combo ()
		self.parentiter = iter
		self.widget.show ()
		self.update_textboxes ()
		
		#switch to advanced tab if required
		if mode == "advanced":
			self.notebook.set_current_page(1)
		else:
			self.notebook.set_current_page(0)



	def check_field_format (self, field, type):
		try:
			self.schedule.checkfield (field, type, self.fieldRegex)
		except Exception, ex:
			raise ex

	def showadd (self, mode):
		self.reset ()
		self.runat = "tomorrow"
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
		# TODO: Validate record
		# TODO: Fill recorc
		if self.editing != gtk.FALSE:
			self.schedule.update (self.job_id, record, self.parentiter, self.nooutput, self.title, self.icon)
			print "Edited"		
		else:
			self.schedule.append (record, self.nooutput, self.title, self.icon)
			self.ParentClass.schedule_reload ()
			print "Added"
	
		self.widget.hide ()
