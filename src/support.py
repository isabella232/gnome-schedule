#pygtk modules
import gconf

#python modules
import os

gconf_client = gconf.client_get_default()

# gtk.gdk.pixbuf_new_from_file (filename)


def nautilus_icon (type):
	#XXX I don't like this fixed paths maybe put them in config.py?
	_nautdir = "/usr/share/pixmaps/nautilus"
	_pixdir = "/usr/share/pixmaps"
	theme = gconf_client.get_string("/desktop/gnome/file_views/icon_theme")
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
