
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

#python modules
import string

#private modules
import support


def removetemplate (type, template_name):
	template_name_c = __replace__ (template_name)
	
	installed = support.gconf_client.get_string("/apps/gnome-schedule/presets/" + type + "/installed")
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

		
	support.gconf_client.unset("/apps/gnome-schedule/presets/" + type + "/%s/name" % (template_name_c))
	support.gconf_client.unset("/apps/gnome-schedule/presets/" + type + "/%s/icon_uri" % (template_name_c))
	support.gconf_client.unset("/apps/gnome-schedule/presets/" + type + "/%s/command" % (template_name_c))
	support.gconf_client.unset("/apps/gnome-schedule/presets/" + type + "/%s/title" % (template_name_c))
	support.gconf_client.unset("/apps/gnome-schedule/presets/" + type + "/%s/timeexpression" % (template_name_c))
			
	if newstring == "   ":
		support.gconf_client.unset ("/apps/gnome-schedule/presets/" + type + "/installed")
	else:
		support.gconf_client.set_string("/apps/gnome-schedule/presets/" + type + "/installed", newstring)
		
		
	
def __replace__ (template_name_c):
	for a in " ,	;:/\\\"'!@#$%^&*()-_+=|?<>.][{}":
		template_name_c = string.replace (template_name_c, a, "-")
			
	return template_name_c
	
	
def savetemplate (type, template_name, timeexpression, title, icon, command):	
	template_name_c = __replace__ (template_name)
		
	support.gconf_client.set_string("/apps/gnome-schedule/presets/" + type + "/%s/timeexpression" % (template_name_c), timeexpression)
	support.gconf_client.set_string("/apps/gnome-schedule/presets/" + type + "/%s/name" % (template_name_c), template_name)
	support.gconf_client.set_string("/apps/gnome-schedule/presets/" + type + "/%s/icon_uri" % (template_name_c), icon)
	support.gconf_client.set_string("/apps/gnome-schedule/presets/" + type + "/%s/command" % (template_name_c), command)
	support.gconf_client.set_string("/apps/gnome-schedule/presets/" + type + "/%s/title" % (template_name_c), title)
		
	installed = support.gconf_client.get_string("/apps/gnome-schedule/presets/" + type + "/installed")
	if installed == None:
		installed = template_name_c
	else:
		found = gtk.FALSE
		for t in string.split (installed, ", "):
			if t == template_name_c:
				found = gtk.TRUE
				
			if found == gtk.FALSE:
				installed = installed + ", " + template_name_c
				
	support.gconf_client.unset ("/apps/gnome-schedule/presets/" + type + "/installed")
	support.gconf_client.set_string("/apps/gnome-schedule/presets/" + type + "/installed", installed)
		
		
	
def gettemplatenames (type):
	strlist = support.gconf_client.get_string("/apps/gnome-schedule/presets/" + type + "/installed")
	if strlist != None:
		list = string.split (strlist, ", ")
		return list
	else:
		return None


def gettemplate (type, template_name):
	try:
		icon_uri = support.gconf_client.get_string("/apps/gnome-schedule/presets/" + type + "/%s/icon_uri" % (template_name))
		command = support.gconf_client.get_string("/apps/gnome-schedule/presets/" + type + "/%s/command" % (template_name))
		title = support.gconf_client.get_string("/apps/gnome-schedule/presets/" + type + "/%s/title" % (template_name))
		name = support.gconf_client.get_string("/apps/gnome-schedule/presets/" + type + "/%s/name" % (template_name))
		timeexpression = support.gconf_client.get_string("/apps/gnome-schedule/presets/" + type + "/%s/timeexpression" % (template_name))
		return icon_uri, command, timeexpression, title, name

	except Exception, ex:
		return ex, ex, ex, ex, ex
	
