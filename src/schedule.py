# schedule.py - abstract schedule interfae
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
import re
import os
import sys
import tempfile
import config
import mainWindow
import gettext
##
## I18N
##
#from rhpl.translate import _, N_
#import rhpl.translate as translate
domain = 'gnome-schedule'
#translate.textdomain (domain)
gettext.bindtextdomain(domain)
gettext.textdomain(domain)
_ = gettext.gettext
gtk.glade.bindtextdomain(domain)

class Schedule:
	def __init__(self, parent):
		self.ParentClass = parent
		self.read()
		return

	def make_preview (self, str):
		raise 'Abstract method please override'

	def savetemplate (self, template_name, record, nooutput, title, icon):
		raise 'Abstract method please override'

	def gettemplatenames (self):
		raise 'Abstract method please override'

	def gettemplate (self, template_name):
		raise 'Abstract method please override'

	def translate_frequency (self, frequency):
		raise 'Abstract method please override'

	def geteditor (self):
		raise 'Abstract method please override'

	def createtreemodel (self):
		raise 'Abstract method please override'

	def switchview (self, mode = "simple", init = 0):
		raise 'Abstract method please override'

	def createpreview (self, minute, hour, day, month, weekday, command):
		raise 'Abstract method please override'

	def getstandardvalue (self):
		raise 'Abstract method please override'

	def getfrequency (self, minute, hour, day, month, weekday):
		raise 'Abstract method please override'

	def checkfield (self, field, type, regex):
		raise Exception('Abstract method please override','','','')

	def write (self):
		raise 'Abstract method, please override' 

	def update (self, linenumber, record, parentiter, nooutput, title, icon):
		raise 'Abstract method, please override' 

	def delete (self, linenumber):
		raise 'Abstract method, please override' 

	def append (self, record, nooutput, title, icon):
		raise 'Abstract method, please override' 

	def read (self):
		raise 'Abstract method, please override'

	def parse (self, line):
		raise 'Abstract method, please override'

	def easy (self, minute, hour, day, month, weekday):
		raise 'Abstract method, please override'
