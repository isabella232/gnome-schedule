# data.py: Contains the backend to the gconf database
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
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02110-1301, USA.

#pygtk modules
import gconf

#python modules
import os

#gnome-schedule
import config

class ConfigBackend:

    def __init__(self, parent, type):

        self.parent = parent
        self.type = "gconf"

        self.gconf_client = gconf.client_get_default()
        self.gconf_client.add_dir ("/apps/gnome-schedule", gconf.CLIENT_PRELOAD_NONE)
        self.gconf_client.notify_add ("/apps/gnome-schedule/advanced", self.on_gconfkey_advanced_changed)

    def get_not_inform_working_dir (self):
        if ((self.get_not_inform_working_dir_crontab () and self.get_not_inform_working_dir_at ()) or self.gconf_client.get_bool ("/apps/gnome-schedule/inform_working_dir")):
            return True
        else:
            return False


    def set_not_inform_working_dir (self, value):
        self.gconf_client.set_bool ("/apps/gnome-schedule/inform_working_dir", value)

    def get_not_inform_working_dir_crontab (self):
        return self.gconf_client.get_bool ("/apps/gnome-schedule/inform_working_dir_crontab")

    def set_not_inform_working_dir_crontab (self, value):
        self.gconf_client.set_bool ("/apps/gnome-schedule/inform_working_dir_crontab", value)

    def get_not_inform_working_dir_at (self):
        return self.gconf_client.get_bool ("/apps/gnome-schedule/inform_working_dir_at")

    def set_not_inform_working_dir_at (self, value):
        self.gconf_client.set_bool ("/apps/gnome-schedule/inform_working_dir_at", value)


    def set_window_state (self, x, y, height, width):
        self.gconf_client.set_int ("/apps/gnome-schedule/x", x)
        self.gconf_client.set_int ("/apps/gnome-schedule/y", y)
        self.gconf_client.set_int ("/apps/gnome-schedule/height", height)
        self.gconf_client.set_int ("/apps/gnome-schedule/width", width)

    def get_window_state (self):
        h = self.gconf_client.get_int ("/apps/gnome-schedule/height")
        w = self.gconf_client.get_int ("/apps/gnome-schedule/width")
        x = self.gconf_client.get_int ("/apps/gnome-schedule/x")
        y = self.gconf_client.get_int ("/apps/gnome-schedule/y")
        return x, y, h, w

    def get_advanced_option(self):
        return self.gconf_client.get_bool ("/apps/gnome-schedule/advanced")


    def set_advanced_option(self,value):
        self.gconf_client.set_bool ("/apps/gnome-schedule/advanced", value)


    def on_gconfkey_advanced_changed (self, client, connection_id, entry, args):
        val = self.gconf_client.get_bool ("/apps/gnome-schedule/advanced")
        if val:
            self.parent.switchView("advanced")
        else:
            self.parent.switchView("simple")



