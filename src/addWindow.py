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

#pygtk modules
import gtk

##
## I18N
##
import gettext
domain = 'gnome-schedule'
gettext.bindtextdomain(domain)
gettext.textdomain(domain)
_ = gettext.gettext

class AddWindow:
	def __init__(self, parent):
		self.ParentClass = parent
		self.xml = self.ParentClass.xml
		self.widget = self.xml.get_widget ("addWindow")
		self.widget.connect("delete-event", self.on_cancel_button_clicked)

		self.cancel_button = self.xml.get_widget ("select_cancel_button")
		self.ok_button = self.xml.get_widget ("select_ok_button")
		self.at_radio = self.xml.get_widget("at_radio")
		self.crontab_radio = self.xml.get_widget("crontab_radio")
		self.crontab_radio.set_active (gtk.TRUE)
		self.xml.signal_connect("on_select_cancel_button_clicked", self.on_cancel_button_clicked)
		self.xml.signal_connect("on_select_ok_button_clicked", self.on_ok_button_clicked)

		self.populateCombobox ()

	def ShowAddWindow (self):
		self.widget.show_all()

	def populateCombobox (self):
		pass

	def on_cancel_button_clicked (self, *args):
		self.widget.hide()
		return gtk.TRUE

	def on_ok_button_clicked (self, *args):
		self.widget.hide()
		if self.crontab_radio.get_active ():
			self.ParentClass.editor = self.ParentClass.crontab_editor
			self.ParentClass.editor.showadd (self.ParentClass.edit_mode)
		else:
			self.ParentClass.editor = self.ParentClass.at_editor
			self.ParentClass.editor.showadd (self.ParentClass.edit_mode)

		
		return gtk.TRUE
