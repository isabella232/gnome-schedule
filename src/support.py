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
