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
import gobject

#python modules
import pwd


##
## I18N
##
import gettext
domain = 'gnome-schedule'
gettext.bindtextdomain(domain)
gettext.textdomain(domain)
_ = gettext.gettext


class SetuserWindow:
	def __init__(self, parent):
		self.ParentClass = parent
		self.xml = self.ParentClass.xml
		self.widget = self.xml.get_widget("setuserWindow")
		self.widget.connect("delete-event", self.on_cancel_button_clicked)

		self.entUser = self.xml.get_widget("entUser")
		
		liststore = gtk.ListStore(gobject.TYPE_STRING)
		self.entUser.set_model(liststore)
		self.entUser.set_text_column(0)
		
				
		#fill combox with all the users
		pwd_info = pwd.getpwall()
		
		for info in pwd_info:
			self.entUser.append_text(info[0])
			
		self.cancel_button = self.xml.get_widget ("setuser_cancel_button")
		self.ok_button = self.xml.get_widget ("setuser_ok_button")
		self.xml.signal_connect("on_setuser_cancel_button_clicked", self.on_cancel_button_clicked)
		self.xml.signal_connect("on_setuser_ok_button_clicked", self.on_ok_button_clicked)
		
		
	#public function
	def ShowSetuserWindow (self):
		self.widget.show_all()


	def on_cancel_button_clicked (self, *args):
		self.widget.hide()


	def on_ok_button_clicked (self, *args):
		try:
			user = self.entUser.get_active_text()
			userdb = pwd.getpwnam(user)

			if user != self.ParentClass.user:
				#uid/gid
				self.ParentClass.uid = userdb[2]
				self.ParentClass.gid = userdb[3]
				self.ParentClass.user = user

				# clean treeview, reread crontab
				self.ParentClass.schedule_reload ()
			
			self.widget.hide()
			
		except Exception, ex:
			print ex
			self.dialog = gtk.MessageDialog(self.widget, gtk.DIALOG_MODAL|gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_ERROR, gtk.BUTTONS_OK, "No such user")
			self.dialog.run ()
			self.dialog.destroy ()
		