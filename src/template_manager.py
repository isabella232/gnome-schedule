# template_manager.py: the template manager window
# Copyright (C) 2004 - 2008 Gaute Hope <eg at gaute dot vetsj dot com>

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

# pygtk/python modules
import gtk
import gobject

class TemplateManager:
	def __init__ (self, parent, template):
		self.parent = parent
		self.template = template

		# setup window
		self.xml = self.parent.xml
		self.widget = self.xml.get_widget ("template_manager")
		self.widget.connect("delete-event", self.widget.hide_on_delete)
		
		self.title_box = self.xml.get_widget ("tm_title_box")
		
		self.image_icon = gtk.Image ()
		self.image_icon.set_from_pixbuf (self.parent.bigicontemplate)
		self.title_box.pack_start (self.image_icon, False, False, 0)
		self.title_box.reorder_child (self.image_icon, 0)
		self.image_icon.show ()
		
		self.treeview = self.xml.get_widget ("tm_treeview")
		self.button_use = self.xml.get_widget ("tm_button_use")
		self.button_cancel = self.xml.get_widget ("tm_button_cancel")
		
		self.xml.signal_connect ("on_tm_button_use_clicked", self.on_use_clicked)
		self.xml.signal_connect ("on_tm_button_cancel_clicked", self.on_cancel_clicked)
		self.xml.signal_connect ("on_tm_button_edit_clicked", self.on_edit_clicked)
		self.xml.signal_connect ("on_tm_button_delete_clicked", self.on_delete_clicked)
		self.xml.signal_connect ("on_tm_treeview_button_press_event", self.on_tv_pressed)
				
		# setup liststore
		# [template id, type, type-string, formatted text, icon/pixbuf]
		self.treemodel = gtk.ListStore (gobject.TYPE_INT, gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_STRING, gtk.gdk.Pixbuf)
		
		# setup treeview
		self.treeview.set_model (self.treemodel)
		self.treeview.set_headers_visible (True)
		
		
		rend1 = gtk.CellRendererPixbuf ()
		rend2 = gtk.CellRendererText ()
		
        	column = gtk.TreeViewColumn(_("Task"))
        	column.pack_start (rend1, True)
        	column.pack_end (rend2, True)
        	column.add_attribute (rend1, "pixbuf", 4)
        	column.add_attribute (rend2, "text", 2)
        	self.treeview.append_column(column)
		 
        			
        	rend = gtk.CellRendererText ()
        	column = gtk.TreeViewColumn(_("Description"), rend, markup=3)
        	self.treeview.append_column(column)  

	
	def reload_tv (self):
		self.treemodel.clear ()
		at = self.template.gettemplateids ("at")
		if at != None:
			for id in at:
				t = self.template.gettemplate ("at", int (id))
				if t != False:
					id2, title, command = t
					formatted = self.template.format_at (title, command)
					iter = self.treemodel.append ([int (id), "at", _("One-time"), formatted, self.parent.bigiconat])

		crontab = self.template.gettemplateids ("crontab")
		if crontab != None:
			for id in crontab:
				t = self.template.gettemplate ("crontab", int (id))
				if t != False:
					id2, title, command, nooutput, timeexpression = t
					formatted = self.template.format_crontab (title, command, nooutput, timeexpression)
					iter = self.treemodel.append ([int (id), "crontab", _("Recurrent"), formatted, self.parent.bigiconcrontab])
					
	def on_edit_clicked (self, *args):
		store, iter = self.treeview.get_selection().get_selected()
		if iter != None:
			type = self.treemodel.get_value(iter, 1)
			id = self.treemodel.get_value(iter, 0)
			if type == "at":
				t = self.template.gettemplate ("at", int (id))	
				if t != False:
					id2, title, command = t
					self.parent.at_editor.showedit_template (id2, title, command)
					
			elif type == "crontab":
				t = self.template.gettemplate ("crontab", int (id)	)
				if t != False:
					id2, title, command, nooutput, timeexpression = t
					self.parent.crontab_editor.showedit_template (id2, title, command, nooutput, timeexpression)
		self.reload_tv ()
		

	
	def on_delete_clicked (self, *args):
		store, iter = self.treeview.get_selection().get_selected()
		if iter != None:
			type = self.treemodel.get_value(iter, 1)
			id = self.treemodel.get_value(iter, 0)
			if type == "at":
				self.template.removetemplate_at (id)
			elif type == "crontab":
				self.template.removetemplate_crontab (id)
			
		self.reload_tv ()
		
		
				
	def show (self):
		# populate treeview
		self.reload_tv ()
		
		self.widget.set_transient_for(self.parent.widget)
		self.widget.set_position(gtk.WIN_POS_CENTER_ON_PARENT)
		self.widget.show_all ()
		
	def on_tv_pressed (self, widget, event):
		if event.type == gtk.gdk._2BUTTON_PRESS:
			self.on_edit_clicked(self, widget)
			
	def on_use_clicked (self, *args):
		store, iter = self.treeview.get_selection().get_selected()
		if iter != None:
			type = self.treemodel.get_value(iter, 1)
			id = self.treemodel.get_value(iter, 0)
			if type == "at":
				t = self.template.gettemplate ("at", int (id))	
				if t != False:
					id2, title, command = t
					self.parent.at_editor.showadd_template (title, command)
			elif type == "crontab":
				t = self.template.gettemplate ("crontab", int (id)	)
				if t != False:
					id2, title, command, nooutput, timeexpression = t
					self.parent.crontab_editor.showadd_template (title, command, nooutput, timeexpression)
		
			self.widget.hide ()
		
	def on_cancel_clicked (self, *args):
		self.widget.hide ()
	

		
		
