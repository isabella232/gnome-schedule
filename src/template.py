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
	
