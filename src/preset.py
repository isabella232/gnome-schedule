
# Copyright (C) 2004, 2005 Philip Van Hoof <me at freax dot org>
# Copyright (C) 2004, 2005 Gaute Hope <eg at gaute dot eu dot org>
# Copyright (C) 2004, 2005 Kristof Vansant <de_lupus at pandora dot be>

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
import gconf

#python modules
import string
import os

class ConfigBackend:
	
	def __init__(self, parent, type):
		
		self.parent = parent
		self.type = "gconf"
		
		self.gconf_client = gconf.client_get_default()
		self.gconf_client.add_dir ("/apps/gnome-schedule", gconf.CLIENT_PRELOAD_NONE)		
		self.gconf_client.notify_add ("/apps/gnome-schedule/advanced", self.on_gconfkey_advanced_changed)

		
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


	def add_scheduler_type(self,type):
		#crontab
		self.gconf_client.add_dir ("/apps/gnome-schedule/presets/" + type, gconf.CLIENT_PRELOAD_NONE)
		self.gconf_client.notify_add ("/apps/gnome-schedule/presets/" + type + "/installed", self.on_gconfkey_editor_changed);


	def on_gconfkey_editor_changed (self, client, connection_id, entry, args):
		# TODO: dirty hack
		self.parent.at_editor.__reload_templates__ ()
		self.parent.crontab_editor.__reload_templates__ ()
		#pass


	def removetemplate (self,type, template_name):
		template_name_c = self.__replace__ (template_name)
	
		installed = self.gconf_client.get_string("/apps/gnome-schedule/presets/" + type + "/installed")
		newstring = installed
		if installed != None:
			first = gtk.TRUE
			newstring = "   "
			for t in string.split (installed, ", "):
				if t != template_name_c:
					if first == gtk.TRUE:
						newstring = t
						first = gtk.FALSE
					else:
						newstring = newstring + ", " + t
		
		self.gconf_client.unset("/apps/gnome-schedule/presets/" + type + "/%s/name" % (template_name_c))
		self.gconf_client.unset("/apps/gnome-schedule/presets/" + type + "/%s/icon_uri" % (template_name_c))
		self.gconf_client.unset("/apps/gnome-schedule/presets/" + type + "/%s/command" % (template_name_c))
		self.gconf_client.unset("/apps/gnome-schedule/presets/" + type + "/%s/title" % (template_name_c))
		self.gconf_client.unset("/apps/gnome-schedule/presets/" + type + "/%s/timeexpression" % (template_name_c))
			
		if newstring == "   ":
			self.gconf_client.unset ("/apps/gnome-schedule/presets/" + type + "/installed")
		else:
			self.gconf_client.set_string("/apps/gnome-schedule/presets/" + type + "/installed", newstring)
		

	def __replace__ (self, template_name_c):
		for a in " ,	;:/\\\"'!@#$%^&*()-_+=|?<>.][{}":
			template_name_c = string.replace (template_name_c, a, "-")
			
		return template_name_c
	
	
	def savetemplate (self,type, template_name, timeexpression, title, icon, command):	
		template_name_c = self.__replace__ (template_name)
		
		self.gconf_client.set_string("/apps/gnome-schedule/presets/" + type + "/%s/timeexpression" % (template_name_c), timeexpression)
		self.gconf_client.set_string("/apps/gnome-schedule/presets/" + type + "/%s/name" % (template_name_c), template_name)
		self.gconf_client.set_string("/apps/gnome-schedule/presets/" + type + "/%s/icon_uri" % (template_name_c), icon)
		self.gconf_client.set_string("/apps/gnome-schedule/presets/" + type + "/%s/command" % (template_name_c), command)
		self.gconf_client.set_string("/apps/gnome-schedule/presets/" + type + "/%s/title" % (template_name_c), title)
		
		installed = self.gconf_client.get_string("/apps/gnome-schedule/presets/" + type + "/installed")
		if installed == None:
			installed = template_name_c
		else:
			found = gtk.FALSE
			for t in string.split (installed, ", "):
				if t == template_name_c:
					found = gtk.TRUE
		
			if found == gtk.FALSE:
				installed = installed + ", " + template_name_c
				
		self.gconf_client.unset ("/apps/gnome-schedule/presets/" + type + "/installed")
		self.gconf_client.set_string("/apps/gnome-schedule/presets/" + type + "/installed", installed)
		
		
	def gettemplatenames (self,type):
		strlist = self.gconf_client.get_string("/apps/gnome-schedule/presets/" + type + "/installed")
		if strlist != None:
			list = string.split (strlist, ", ")
			return list
		else:
			return None


	def gettemplate (self, type, template_name):
		try:
			icon_uri = self.gconf_client.get_string("/apps/gnome-schedule/presets/" + type + "/%s/icon_uri" % (template_name))
			command = self.gconf_client.get_string("/apps/gnome-schedule/presets/" + type + "/%s/command" % (template_name))
			title = self.gconf_client.get_string("/apps/gnome-schedule/presets/" + type + "/%s/title" % (template_name))
			name = self.gconf_client.get_string("/apps/gnome-schedule/presets/" + type + "/%s/name" % (template_name))
			timeexpression = self.gconf_client.get_string("/apps/gnome-schedule/presets/" + type + "/%s/timeexpression" % (template_name))
			return icon_uri, command, timeexpression, title, name
	
		except Exception, ex:
			return ex, ex, ex, ex, ex
			
	def nautilus_icon (self, type):
		#XXX I don't like this fixed paths maybe put them in config.py?
		_nautdir = "/usr/share/pixmaps/nautilus"
		_pixdir = "/usr/share/pixmaps"
		theme = self.gconf_client.get_string("/desktop/gnome/file_views/icon_theme")
		if type == "x-directory/":
			if theme:
				newicon = "%s/%s/i-directory.png" % (_nautdir,theme)
			else:
				newicon = "%s/gnome-folder.png" % _pixdir
		
			if os.path.isfile(newicon):
				return newicon
			return None
		else:
			icontmp = type.replace('/','-')
			if theme:
				newicon = "%s/%s/gnome-%s.png" % (_nautdir,theme,icontmp)
				if os.path.isfile(newicon):
					return newicon
				else:
					newicon = "%s/%s/%s.png" % (_nautdir,theme,icontmp)
					if os.path.isfile(newicon):
						return newicon
					else:
						newicon = "%s/document-icons/gnome-%s.png" % (_nautdir,icontmp)
						if os.path.isfile(newicon):
							return newicon
			return None

