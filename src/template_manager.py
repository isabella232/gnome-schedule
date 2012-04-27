# template_manager.py: the template manager window
# Copyright (C) 2004 - 2009 Gaute Hope <eg at gaute dot vetsj dot com>
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

        self.treeview = self.xml.get_widget ("tm_treeview")
        self.button_use = self.xml.get_widget ("tm_button_use")
        hbox = gtk.HBox ()
        icon = gtk.Image ()
        icon.set_from_pixbuf (self.parent.normalicontemplate)
        label = gtk.Label (_("Use template"))
        icon.set_alignment (0.5, 0.5)
        label.set_justify (gtk.JUSTIFY_CENTER)
        label.set_alignment (0.5, 0.5)
        hbox.pack_start (icon, True, True, 0)
        hbox.pack_start (label, True, True, 0)
        self.button_use.add (hbox)
        self.button_use.show_all ()

        self.button_cancel = self.xml.get_widget ("tm_button_cancel")

        self.xml.signal_connect ("on_tm_button_new_clicked", self.on_new_clicked)
        self.xml.signal_connect ("on_tm_button_use_clicked", self.on_use_clicked)
        self.xml.signal_connect ("on_tm_button_cancel_clicked", self.on_cancel_clicked)
        self.xml.signal_connect ("on_tm_button_edit_clicked", self.on_edit_clicked)
        self.xml.signal_connect ("on_tm_button_delete_clicked", self.on_delete_clicked)
        self.xml.signal_connect ("on_tm_treeview_button_press_event", self.on_tv_pressed)

        self.button_edit = self.xml.get_widget ("tm_button_edit")
        self.button_delete = self.xml.get_widget ("tm_button_delete")

        self.treeview.get_selection().connect("changed", self.on_tv_changed)

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

    def on_tv_changed (self, *args):
        if self.treeview.get_selection().count_selected_rows() > 0 :
            value = True
        else:
            value = False
        self.button_use.set_sensitive (value)
        self.button_edit.set_sensitive (value)
        self.button_delete.set_sensitive (value)

    def reload_tv (self):
        self.treemodel.clear ()
        at = self.template.gettemplateids ("at")
        if at != None:
            for id in at:
                t = self.template.gettemplate ("at", int (id))
                if t != False:
                    id2, title, command, output = t
                    formatted = self.template.format_at (title, command, output)
                    iter = self.treemodel.append ([int (id), "at", _("One-time"), formatted, self.parent.bigiconat])

        crontab = self.template.gettemplateids ("crontab")
        if crontab != None:
            for id in crontab:
                t = self.template.gettemplate ("crontab", int (id))
                if t != False:
                    id2, title, command, output, timeexpression = t
                    formatted = self.template.format_crontab (title, command, output, timeexpression)
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
                    self.parent.at_editor.showedit_template (self.widget, id2, title, command)

            elif type == "crontab":
                t = self.template.gettemplate ("crontab", int (id)  )
                if t != False:
                    id2, title, command, output, timeexpression = t
                    self.parent.crontab_editor.showedit_template (self.widget, id2, title, command, output, timeexpression)
        self.reload_tv ()

    def on_new_clicked (self, *args):
        self.parent.addWindow.ShowAddWindow (self.widget, 1)

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



    def show (self, transient):
        # populate treeview
        self.reload_tv ()

        self.widget.set_transient_for(transient)
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
                    id2, title, command, output = t
                    self.parent.at_editor.showadd_template (self.widget, title, command, output)
            elif type == "crontab":
                t = self.template.gettemplate ("crontab", int (id)  )
                if t != False:
                    id2, title, command, output, timeexpression = t
                    self.parent.crontab_editor.showadd_template (self.widget, title, command, output, timeexpression)

            self.widget.hide ()

    def on_cancel_clicked (self, *args):
        self.widget.hide ()




