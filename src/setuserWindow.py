# setuserWindow.py - UI code for changing user
# Copyright (C) 2004, 2005  Philip Van Hoof <me at pvanhoof dot be>
# Copyright (C) 2004 - 2009 Gaute Hope <eg at gaute dot vetsj dot com>
# Copyright (C) 2004, 2005  Kristof Vansant <de_lupus at pandora dot be>
#
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

#pygtk modules
import gtk
import gobject

#python modules
import pwd


class SetuserWindow:
    def __init__(self, parent):
        self.ParentClass = parent
        self.xml = self.ParentClass.xml
        self.widget = self.xml.get_widget("setuserWindow")
        self.widget.connect("delete-event", self.widget.hide_on_delete)

        ##comboxEntry
        self.entUser = self.xml.get_widget("entUser")

        liststore = gtk.ListStore(gobject.TYPE_STRING)
        self.entUser.set_model(liststore)
        self.entUser.set_text_column(0)

        #entryCompletion
        # TODO: make it only possible for the user to type something that is in the list
        self.entry = self.entUser.child
        self.entry.set_text(self.ParentClass.user)
        completion = gtk.EntryCompletion()
        self.entry.set_completion(completion)
        completion.set_model(liststore)
        completion.set_text_column(0)

        #fill combox with all the users
        pwd_info = pwd.getpwall()

        for info in pwd_info:
            self.entUser.append_text(info[0])
        ##

        self.cancel_button = self.xml.get_widget ("setuser_cancel_button")
        self.ok_button = self.xml.get_widget ("setuser_ok_button")
        self.xml.signal_connect("on_setuser_cancel_button_clicked", self.on_cancel_button_clicked)
        self.xml.signal_connect("on_setuser_ok_button_clicked", self.on_ok_button_clicked)


    #public function
    def ShowSetuserWindow (self):
        self.widget.set_transient_for(self.ParentClass.widget)
        self.widget.set_position(gtk.WIN_POS_CENTER_ON_PARENT)
        self.widget.show_all()


    def on_cancel_button_clicked (self, *args):
        self.widget.hide()


    def on_ok_button_clicked (self, *args):

        user = self.entry.get_text()
        try:
            self.ParentClass.changeUser(user)
            self.widget.hide()

        except Exception, ex:
            print ex
            self.dialog = gtk.MessageDialog(self.widget, gtk.DIALOG_MODAL|gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_ERROR, gtk.BUTTONS_OK, _("No such user"))
            self.dialog.run ()
            self.dialog.destroy ()

