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
		self.widget = self.xml.get_widget("atEditor")
		self.widget.connect("delete-event", self.on_cancel_button_clicked)

		self.fieldRegex = re.compile('^(\*)$|^([0-9]+)$|^\*\\\([0-9]+)$|^([0-9]+)-([0-9]+)$|(([0-9]+[|,])+)')

		#self.editorhelperwidget = self.ParentClass.editorhelperwidget
		self.nooutputRegex = re.compile('([^#\n$]*)>(\s|)/dev/null\s2>&1')
		
		self.editing = gtk.FALSE
		self.help_button = self.xml.get_widget ("help_button")
		self.cancel_button = self.xml.get_widget ("cancel_button")
		self.ok_button = self.xml.get_widget ("ok_button")
		
		self.runat_entry = self.xml.get_widget("runat_entry")
		self.commands_textview = self.xml.get_widget("commands_textview")
		
		self.notebook = self.xml.get_widget("notebook")

		self.xml.signal_connect("on_add_help_button_clicked", self.on_add_help_button_clicked)
		self.xml.signal_connect("on_cancel_button_clicked", self.on_cancel_button_clicked)
		self.xml.signal_connect("on_ok_button_clicked", self.on_ok_button_clicked)
		self.xml.signal_connect("on_anyadvanced_entry_changed", self.on_anyadvanced_entry_changed)
		#self.xml.signal_connect("on_anybasic_entry_changed", self.on_anybasic_entry_changed)
		
		
		#self.xml.signal_connect("on_fieldHelp_clicked", self.on_fieldHelp_clicked)

	def reset (self):
		self.runat_entry.set_text("tomorrow")
		tmpbuffer = self.commands_textview.get_buffer()
		tmpbuffer.set_text("")

		
	def showedit (self, record, linenumber, iter, mode):
		print "not implemented.."
#	self.editing = gtk.TRUE
#		self.linenumber = linenumber
#		self.record = record
#		self.widget.set_title(_("Edit a scheduled task"))
#		self.update_textboxes ()
#		self.set_frequency_combo ()
#		self.parentiter = iter
#		self.widget.show_all()
		


		#switch to advanced tab if required
		#if mode == "advanced":
		#	self.notebook.set_current_page(1)
		#else:
		#	self.notebook.set_current_page(0)

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

		self.runat = "tomorrow"
		self.commands = ""
		self.title = _("New job")
		self.editing = gtk.FALSE
		self.widget.set_title(_("Create a new job"))
		self.widget.show_all()
		
		#switch to advanced tab if, only supported
		self.notebook.set_current_page(1)
	


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
		#try:
		#	self.check_field_format (self.minute, _("minute"))
		#	self.check_field_format (self.hour, _("hour"))
		#	self.check_field_format (self.day, _("day"))
		#	self.check_field_format (self.month, _("month"))
		#	self.check_field_format (self.weekday, _("weekday"))
		#except Exception, ex:
			#x, y, z = ex
		#	x=""
		#	y=""
		#	z=""
		#	self.wrongdialog = gtk.MessageDialog(self.widget, gtk.DIALOG_MODAL|gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_ERROR, gtk.BUTTONS_OK, _("This is an invalid record! The problem could be at the ") + y + _(" field. Reason: ")+ z)
		#	self.wrongdialog.run()
		#	self.wrongdialog.destroy()
		#	return

			
	
		self.schedule.append (self.runat, self.commands)
		self.ParentClass.treemodel.clear ()
		self.ParentClass.schedule.read ()

		self.widget.hide ()



	

	def on_anyadvanced_entry_changed (self, *args):
		if self.noevents == gtk.FALSE:
			self.runat = self.runat_entry.get_text ()
			tmpbuffer = self.commands_textview.get_buffer()
			self.commands = tmpbuffer.get_text(self.commands.get_start_iter(), self.commands.get_end_iter())
	
	def on_anybasic_entry_changed (self, *args):
		if self.noevents == gtk.FALSE:
			self.runat = self.runat_entry.get_text ()
			self.commands = self.commands_textview.get_buffer ()


	

	
