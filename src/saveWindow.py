# setuserWindow.py - UI code for changing user
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
import string
import pwd

##
## I18N
##
from rhpl.translate import _, N_
import rhpl.translate as translate
domain = 'gnome-schedule'
translate.textdomain (domain)
gtk.glade.bindtextdomain(domain)

class SaveWindow:
	def __init__(self, parent):
		self.ParentClass = parent
		self.xml = self.ParentClass.xml
		self.editor = self.ParentClass.editor
		self.widget = self.ParentClass.savewidget
		self.widget.connect("delete-event", self.on_cancel_button_clicked)

		self.cancel_button = self.xml.get_widget ("save_cancel_button")
		self.ok_button = self.xml.get_widget ("save_ok_button")
		self.save_entry = self.xml.get_widget("save_entry")

		self.xml.signal_connect("on_save_cancel_button_clicked", self.on_cancel_button_clicked)
		self.xml.signal_connect("on_save_ok_button_clicked", self.on_ok_button_clicked)

		self.populateCombobox ()

	def ShowSaveWindow (self, editor):
		self.editor = editor
		self.widget.show_all()

	def populateCombobox (self):
		pass

	def on_cancel_button_clicked (self, *args):
		self.widget.hide()
		return gtk.TRUE

	def on_ok_button_clicked (self, *args):
		self.editor.SaveTemplate (self.save_entry.get_text())
		self.widget.hide ()
		return gtk.TRUE
