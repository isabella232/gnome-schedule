# mainWindow.py - mainWindow of the crontab configuration tool
# Copyright (C) 2004 - 2011  Gaute Hope <eg at gaute dot vetsj dot com>
# Copyright (C) 2004, 2005   Philip Van Hoof <me at pvanhoof dot be>
# Copyright (C) 2004, 2005   Kristof Vansant <de_lupus at pandora dot be>
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

# i18n and locale has to be set up before glade in some cases
import lang

#pygtk modules
import gtk
import gtk.glade
import gobject

#python modules
import os
import pwd
import tempfile
import stat
import subprocess

#custom modules
import config
import crontab
import crontabEditor
import at
import atEditor
import setuserWindow
import addWindow
import data
import template
import template_chooser
import template_manager


gtk.glade.bindtextdomain(config.GETTEXT_PACKAGE(), config.GNOMELOCALEDIR())

##
## The MainWindow class
##
class main:
    def __init__(self, debug_flag=None, inapplet=False, manual_poscorrect=False):
        self.debug_flag = debug_flag
        self.inapplet = inapplet
        self.manual_poscorrect = manual_poscorrect

        self.__loadIcon__()
        self.__loadGlade__()

        self.editor = None
        self.schedule = None

        self.noevents = False

        # Common string representation for the different output modes
        self.output_strings = [
                                _("Default behaviour"),
                                _("Suppress output"),
                                _("X application"),
                                _("X application: suppress output"),
                        ]

        #start the backend where all the user configuration is stored
        self.backend = data.ConfigBackend(self, "gconf")
        self.template = template.Template (self, self.backend)


        ##configure the window
        self.widget = self.xml.get_widget("mainWindow")

        self.widget.connect("delete_event", self.__quit__)
        self.widget.connect("destroy_event", self.__quit__)

        self.widget.set_icon(self.iconPixbuf)

        #load state
        (x, y, h, w) = self.backend.get_window_state ()
        if (x and y):
            self.widget.move (x, y)
        if (h and w):
            self.widget.resize (h, w)

        self.widget.set_resizable (True)

        ##


        ##configure statusbar
        self.statusbar = self.xml.get_widget("statusbar")

        self.statusbarUser = self.statusbar.get_context_id("user")
        ##

        ##configure the toolbar
        self.toolbar = self.xml.get_widget ("toolbar")
        self.add_button = gtk.MenuToolButton (gtk.STOCK_NEW)

        self.add_button_menu = gtk.Menu ()
        self.add_button_menu_add_crontab = gtk.MenuItem ()
        self.add_button_menu_add_at = gtk.MenuItem ()
        self.add_button_menu_add_template = gtk.MenuItem ()

        self.recurrenthbox = gtk.HBox ()
        icon = gtk.Image ()
        icon.set_from_pixbuf (self.iconcrontab)
        label = gtk.Label (_("Recurrent task"))
        icon.set_alignment (0, 0.5)
        label.set_justify (gtk.JUSTIFY_LEFT)
        label.set_alignment (0, 0.5)
        self.recurrenthbox.pack_start (icon, False, False, 2)
        self.recurrenthbox.pack_start (label, True, True, 2)
        self.add_button_menu_add_crontab.add (self.recurrenthbox)

        self.onetimehbox = gtk.HBox ()
        icon = gtk.Image ()
        icon.set_from_pixbuf (self.iconat)
        label = gtk.Label (_("One-time task"))
        icon.set_alignment (0, 0.5)
        label.set_justify (gtk.JUSTIFY_LEFT)
        label.set_alignment (0, 0.5)
        self.onetimehbox.pack_start (icon, False, False, 2)
        self.onetimehbox.pack_start (label, True, True, 2)
        self.add_button_menu_add_at.add (self.onetimehbox)

        self.templatehbox = gtk.HBox ()
        icon = gtk.Image ()
        icon.set_from_pixbuf (self.icontemplate)
        label = gtk.Label (_("From template"))
        icon.set_alignment (0, 0.5)
        label.set_justify (gtk.JUSTIFY_LEFT)
        label.set_alignment (0, 0.5)
        self.templatehbox.pack_start (icon, False, False, 2)
        self.templatehbox.pack_start (label, True, True, 2)
        self.add_button_menu_add_template.add (self.templatehbox)

        self.add_button_menu.append (self.add_button_menu_add_crontab)
        self.add_button_menu.append (self.add_button_menu_add_at)
        self.add_button_menu.append (self.add_button_menu_add_template)

        self.add_button.set_menu (self.add_button_menu)

        self.toolbar.insert (self.add_button, 0)
        self.add_button.set_is_important (True)
        tip = gtk.Tooltips ()
        tip.enable ()

        self.add_button.set_tooltip (tip, _("Add a new task"), tip_private=None)
        self.add_button.show_all ()
        self.add_button_menu.show_all ()
        self.add_button_menu_add_crontab.show_all ()
        self.add_button_menu_add_at.show_all ()

        self.add_button.connect ("clicked", self.on_add_button_clicked)
        self.add_button_menu_add_crontab.connect ("activate", self.on_add_crontab_task)
        self.add_button_menu_add_at.connect ("activate", self.on_add_at_task)
        self.add_button_menu_add_template.connect ("activate", self.on_add_from_template)


        self.prop_button = self.xml.get_widget ("prop_button")
        self.del_button = self.xml.get_widget ("del_button")
        self.run_button = self.xml.get_widget ("run_button")
        self.help_button = self.xml.get_widget ("help_button")
        self.btnSetUser = self.xml.get_widget("btnSetUser")
        self.btnExit = self.xml.get_widget("btnExit")
        self.about_button = self.xml.get_widget ("about_button")
        self.edit_mode_button = self.xml.get_widget ("edit_mode_button")
        self.button_template = self.xml.get_widget ("button_m_template")

        icon = gtk.Image ()
        icon.set_from_pixbuf (self.normalicontemplate)
        self.button_template.set_icon_widget (icon)
        icon.show ()

        self.prop_button.set_sensitive (False)
        self.del_button.set_sensitive (False)
        self.run_button.set_sensitive (False)

        self.xml.signal_connect("on_prop_button_clicked", self.on_prop_button_clicked)
        self.xml.signal_connect("on_del_button_clicked", self.on_del_button_clicked)
        self.xml.signal_connect("on_help_button_clicked", self.on_help_button_clicked)
        self.xml.signal_connect("on_btnSetUser_clicked", self.on_btnSetUser_clicked)
        self.xml.signal_connect("on_about_menu_activate", self.on_about_menu_activate)
        self.xml.signal_connect("on_edit_mode_button_clicked", self.on_advanced_menu_activate)
        self.xml.signal_connect("on_btnExit_clicked", self.__quit__)
        self.xml.signal_connect("on_mainWindow_delete_event", self.__quit__)
        self.xml.signal_connect("on_run_button_clicked", self.on_run_button_clicked)

        self.xml.signal_connect ("on_button_m_template_clicked", self.on_template_manager_button)

        ##inittializing the treeview and treemodel
        ## somethins not rite here..:
        ## [0 Title, 1 Frequency, 2 Command, 3 Crontab record, 4 ID, 5 Time, 6 Icon, 7 scheduled instance, 8 icon path, 9 date, 10 class_id, 11 user, 12 time, 13 type, 14 crontab/at, 15 advanced time string]
        ##for at this would be like:

# ["untitled", "12:50 2004-06-25", "preview", "script", "job_id", "12:50", icon, at instance, icon_path, "2004-06-25", "a", "drzap", "at"]

        ##for crontab it would be:

# ["untitled", "every hour", "ls /", "0 * * * * ls / # untitled", "5", "0 * * * *", icon, crontab instance,icon_path, 1(job_id), "", "", "crontab"]
        self.treemodel = gtk.ListStore(gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_INT, gobject.TYPE_STRING, gtk.gdk.Pixbuf, gobject.TYPE_PYOBJECT, gobject.TYPE_STRING , gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_INT, gobject.TYPE_STRING)

        self.treeview = self.xml.get_widget("treeview")

        self.xml.signal_connect("on_treeview_button_press_event", self.on_treeview_button_press_event)
        self.xml.signal_connect("on_treeview_key_press_event", self.on_treeview_key_pressed)

        self.treeview.set_model (self.treemodel)
        self.treeview.get_selection().connect("changed", self.on_TreeViewSelectRow)

        #enable or disable advanced depending on user config
        self.noevents = True
        if self.backend.get_advanced_option():
            self.switchView("advanced")
            self.edit_mode_button.set_active (True)
        else:
            self.switchView("simple")
            self.edit_mode_button.set_active (False)
        self.noevents = False


        self.__initUser__()

        ##create crontab
        self.crontab = crontab.Crontab(self.root, self.user, self.uid, self.gid, self.user_home_dir)
        self.crontab_editor = crontabEditor.CrontabEditor(self, self.backend, self.crontab, self.template)
        ##

        ##create at
        self.at = at.At(self.root, self.user, self.uid, self.gid, self.user_home_dir, self.manual_poscorrect)
        self.at_editor = atEditor.AtEditor (self, self.backend, self.at, self.template)
        ##

        #set user window
        self.setuserWindow = setuserWindow.SetuserWindow (self)

        #set add window
        self.addWindow = addWindow.AddWindow (self)

        # template windows
        self.template_chooser = template_chooser.TemplateChooser (self, self.template)
        self.template_manager = template_manager.TemplateManager (self, self.template)

        self.schedule_reload ()

        self.timeout_handler_id = gobject.timeout_add(9000, self.update_schedule)

        # temporary files to be deleted
        self.temp_files = []

        if inapplet == False:
            gtk.main()


    def update_schedule(self):
        selection = self.treeview.get_selection()
        model, iter, = selection.get_selected()
        if iter:
            path = model.get_path(iter)
        self.schedule_reload ()
        if iter:
             selection.select_path(path)
        return True

    def changeUser(self,user):
        if user != self.user:
            self.__setUser__(user)
            #change user for the schedulers
            self.crontab.set_rights(self.user, self.uid, self.gid, self.user_home_dir)
            self.at.set_rights(self.user, self.uid, self.gid, self.user_home_dir)
            #adjust statusbar
            if self.root == 1:
                self.statusbar.push(self.statusbarUser, (_("Editing user: %s") % (self.user)))

            self.schedule_reload ()


    def __setUser__(self,user):
        userdb = pwd.getpwnam(user)
        self.user = user
        self.uid = userdb[2]
        self.gid = userdb[3]
        self.user_home_dir = userdb[5]
        self.user_shell = userdb[6]


    ## TODO: 2 times a loop looks to mutch
    def schedule_reload (self):
        self.treemodel.clear ()

        data = self.crontab.read ()
        if data != None:
            self.__fill__ (data)

        data = self.at.read ()
        if data != None:
            self.__fill__ (data)




    def __fill__ (self, records):
        for title, timestring_show, preview, lines, job_id, timestring, scheduler, icon, date, class_id, user, time, typetext, type, output, timestring_advanced in records:

            if scheduler.get_type() == "crontab":
                iter = self.treemodel.append([title, timestring_show, preview, lines, job_id, timestring, self.iconcrontab, scheduler, icon, date, class_id, user, time, typetext, type, output, timestring_advanced])
            elif scheduler.get_type() == "at":
                iter = self.treemodel.append([title, timestring_show, preview, lines, job_id, timestring, self.iconat, scheduler, icon, date, class_id, user, time, typetext, type, output, timestring_advanced])



    def __loadIcon__(self):
        if self.debug_flag:
            if os.access("../icons/gnome-schedule.svg", os.F_OK):
                self.iconPixbuf = gtk.gdk.pixbuf_new_from_file_at_size ("../icons/gnome-schedule.svg", 52, 52)
        else:
            try:
                self.iconPixbuf = gtk.gdk.pixbuf_new_from_file_at_size (config.getImagedir() + "/gnome-schedule.svg", 52, 52)
            except:
                print _("ERROR: Could not load icon")

        if self.debug_flag:
            if os.access ("../icons/crontab.svg", os.F_OK):
                self.iconcrontab = gtk.gdk.pixbuf_new_from_file_at_size ("../icons/crontab.svg", 19, 19)
                self.bigiconcrontab = gtk.gdk.pixbuf_new_from_file_at_size ("../icons/crontab.svg", 49, 49)
        else:
            try:
                self.iconcrontab = gtk.gdk.pixbuf_new_from_file_at_size (config.getImagedir() + "/crontab.svg", 19, 19)
                self.bigiconcrontab = gtk.gdk.pixbuf_new_from_file_at_size (config.getImagedir() + "/crontab.svg", 49, 49)
            except:
                print _("ERROR: Could not load icon")

        if self.debug_flag:
            if os.access ("../icons/calendar.svg", os.F_OK):
                self.iconcalendar = gtk.gdk.pixbuf_new_from_file_at_size ("../icons/calendar.svg", 19, 19)
                self.bigiconcalendar = gtk.gdk.pixbuf_new_from_file_at_size ("../icons/calendar.svg", 49, 49)
        else:
            try:
                self.iconcalendar = gtk.gdk.pixbuf_new_from_file_at_size (config.getImagedir() + "/calendar.svg", 19, 19)
                self.bigiconcalendar = gtk.gdk.pixbuf_new_from_file_at_size (config.getImagedir() + "/calendar.svg", 49, 49)
            except:
                print _("ERROR: Could not load icon")

        if self.debug_flag:
            if os.access ("../icons/template.svg", os.F_OK):
                self.icontemplate = gtk.gdk.pixbuf_new_from_file_at_size ("../icons/template.svg", 19, 19)
                self.normalicontemplate = gtk.gdk.pixbuf_new_from_file_at_size ("../icons/template.svg", 25, 25)
                self.bigicontemplate = gtk.gdk.pixbuf_new_from_file_at_size ("../icons/template.svg", 49, 49)
                self.pathicontemplate = "../icons/template.svg"
        else:
            try:
                self.icontemplate = gtk.gdk.pixbuf_new_from_file_at_size (config.getImagedir() + "/template.svg", 19, 19)
                self.normalicontemplate = gtk.gdk.pixbuf_new_from_file_at_size (config.getImagedir() + "/template.svg", 25, 25)
                self.bigicontemplate = gtk.gdk.pixbuf_new_from_file_at_size (config.getImagedir() + "/template.svg", 49, 49)
                self.pathicontemplate = config.getImagedir() + "/template.svg"
            except:
                print _("ERROR: Could not load icon")

        if self.debug_flag:
            if os.access ("../icons/at.svg", os.F_OK):
                self.iconat = gtk.gdk.pixbuf_new_from_file_at_size ("../icons/at.svg", 19, 19)
                self.bigiconat = gtk.gdk.pixbuf_new_from_file_at_size ("../icons/at.svg", 49, 49)
        else:
            try:
                self.iconat = gtk.gdk.pixbuf_new_from_file_at_size (config.getImagedir() + "/at.svg", 19, 19)
                self.bigiconat = gtk.gdk.pixbuf_new_from_file_at_size (config.getImagedir() + "/at.svg", 49, 49)
            except:
                print _("ERROR: Could not load icon")


    def __loadGlade__(self):
        if self.debug_flag:
            if os.access("gnome-schedule.glade", os.F_OK):
                try:
                    self.xml = gtk.glade.XML ("gnome-schedule.glade", domain="gnome-schedule")
                except:
                    print _("ERROR: Could not load glade file")
                    quit ()
        else:
            try:
                self.xml = gtk.glade.XML (config.getGladedir() + "/gnome-schedule.glade", domain="gnome-schedule")
            except:
                print _("ERROR: Could not load glade file")
                quit ()



    def __initUser__(self):
        self.uid = os.geteuid()
        self.gid = os.getegid()
        self.user = pwd.getpwuid(self.uid)[0]
        self.user_home_dir = pwd.getpwuid(self.uid)[5]
        self.user_shell = pwd.getpwuid(self.uid)[6]

        if self.uid != 0:
            self.btnSetUser.hide()
            self.statusbar.hide()
            self.root = 0
        else:
            self.root = 1
            self.btnSetUser.show()
            self.statusbar.show()
            self.statusbar.push(self.statusbarUser, (_("Editing user: %s") % (self.user)))


    #when the user selects a task, buttons get enabled
    def on_TreeViewSelectRow (self, *args):
        if self.treeview.get_selection().count_selected_rows() > 0 :
            value = True
        else:
            value = False

        self.prop_button.set_sensitive (value)
        self.del_button.set_sensitive (value)
        self.run_button.set_sensitive (value)



    #clean existing columns
    def __cleancolumns__ (self):
        columns = len(self.treeview.get_columns()) -1
        while columns > -1:
            temp = self.treeview.get_column(columns)
            self.treeview.remove_column(temp)
            columns = columns - 1


    #switch between advanced and simple mode
    def switchView(self, mode = "simple"):
        self.__cleancolumns__ ()

        self.treeview.get_selection().unselect_all()
        self.edit_mode = mode

        cell = gtk.CellRendererPixbuf()
        cell.set_fixed_size(21,21)
        cell2 = gtk.CellRendererText ()
        col = gtk.TreeViewColumn (_("Task"), None)
        col.pack_start (cell, True)
        col.pack_end (cell2, True)
        col.add_attribute (cell, "pixbuf", 6)
        if mode == "simple":
            col.add_attribute (cell2, "text", 13)
        else:
            col.add_attribute (cell2, "text", 14)

        self.treeview.append_column(col)

        if mode == "simple":

            col = gtk.TreeViewColumn(_("Description"), gtk.CellRendererText(), text=0)
            col.set_resizable (True)
            self.treeview.append_column(col)

            col = gtk.TreeViewColumn(_("Date and Time"), gtk.CellRendererText(), text=1)
            col.set_resizable (True)
            self.treeview.append_column(col)

            col = gtk.TreeViewColumn(_("Command preview"), gtk.CellRendererText(), text=2)
            col.set_resizable (True)
            col.set_expand (True)
            self.treeview.append_column(col)



        elif mode == "advanced":

            col = gtk.TreeViewColumn(_("Date and Time"), gtk.CellRendererText(), text=16)
            col.set_resizable (True)
            self.treeview.append_column(col)

            col = gtk.TreeViewColumn(_("Command preview"), gtk.CellRendererText(), text=2)
            col.set_resizable (True)
            col.set_expand (True)
            self.treeview.append_column(col)

            col = gtk.TreeViewColumn(_("Description"), gtk.CellRendererText(), text=0)
            col.set_resizable (True)
            self.treeview.append_column(col)



    def on_advanced_menu_activate (self, widget):
        if self.noevents == False:
            if self.backend.get_advanced_option():
                self.backend.set_advanced_option(0)
            else:
                self.backend.set_advanced_option(1)

    def on_add_at_task (self, *args):
        self.addWindow.mode = 0
        self.addWindow.on_button_at_clicked (*args)

    def on_add_crontab_task (self, *args):
        self.addWindow.mode = 0
        self.addWindow.on_button_crontab_clicked  (*args)

    def on_add_from_template (self, *args):
        self.addWindow.mode = 0
        self.addWindow.on_button_template_clicked  (*args)

    def on_template_manager_button (self, *args):
        self.template_manager.show (self.widget)

    def on_add_scheduled_task_menu_activate (self, *args):
        self.addWindow.ShowAddWindow (self.widget)

    def on_properties_menu_activate (self, *args):
        store, iter = self.treeview.get_selection().get_selected()

        try:
            #see what scheduler (at, crontab or ...)
            self.schedule = self.treemodel.get_value(iter, 7)



            record = self.treemodel.get_value(iter, 3)
            linenumber = self.treemodel.get_value(iter, 4)

            # TODO: dirty hacky
            if self.schedule.get_type() == "crontab":
                self.editor = self.crontab_editor
                job_id = self.treemodel.get_value (iter, 9)
                self.editor.showedit (self.widget, record, job_id, linenumber, iter)
            else:
                self.editor = self.at_editor
                self.editor.showedit (self.widget, record, linenumber, iter)

        except Exception, ex:
            print ex
            self.dialog = gtk.MessageDialog(self.widget, gtk.DIALOG_MODAL|gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_ERROR, gtk.BUTTONS_OK, _("Please select a task"))
            self.dialog.run ()
            self.dialog.destroy ()


    # TODO: looks not that clean (is broken)
    def on_delete_menu_activate (self, *args):
        dialog = gtk.MessageDialog(self.widget, gtk.DIALOG_MODAL|gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_QUESTION, gtk.BUTTONS_YES_NO, _("Do you want to delete this task?"))
        if (dialog.run() != gtk.RESPONSE_YES):
            dialog.destroy()
            del dialog
            return
        dialog.destroy()
        del dialog

        store, iter = self.treeview.get_selection().get_selected()

        try:
            #see what scheduler (at, crontab or ...)
            self.schedule = self.treemodel.get_value(iter, 7)

            # TODO: dirty hacky
            if self.schedule.get_type() == "crontab":
                self.editor = self.crontab_editor
            elif self.schedule.get_type() == "at":
                self.editor = self.at_editor

            record = self.treemodel.get_value(iter, 3)
            linenumber = self.treemodel.get_value(iter, 4)

            path = self.treemodel.get_path(iter)
            pathint = path[0]
            backpath = (pathint - 1,)

            if self.schedule.get_type() == "crontab":
                self.schedule.delete (linenumber, iter, self.treemodel.get_value(iter, 9))
            elif self.schedule.get_type() == "at":
                self.schedule.delete (linenumber, iter)

            self.schedule_reload()

            firstiter = self.treemodel.get_iter_first()
            try:
                nextiter = self.treemodel.get_iter(path)
                #go next
                selection = self.treeview.get_selection()
                selection.select_iter(nextiter)

            except:
                if backpath[0] > 0:
                    nextiter = self.treemodel.get_iter(backpath)
                    #go back
                    selection = self.treeview.get_selection()
                    selection.select_iter(nextiter)

                else:
                    if firstiter:
                        #go first
                        selection = self.treeview.get_selection()
                        selection.select_iter(firstiter)

        except Exception, ex:
            #print ex
            self.dialog = gtk.MessageDialog(self.widget, gtk.DIALOG_MODAL|gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_ERROR, gtk.BUTTONS_OK, _("Please select a task"))
            self.dialog.run ()
            self.dialog.destroy ()

    def on_set_user_menu_activate(self, *args):
        self.setuserWindow.ShowSetuserWindow()


    def on_btnSetUser_clicked(self, *args):
        self.on_set_user_menu_activate(self, args)

    def on_add_button_clicked (self, *args):
        self.on_add_scheduled_task_menu_activate (self, args)

    def on_prop_button_clicked (self, *args):
        self.on_properties_menu_activate (self, args)

    def on_del_button_clicked (self, *args):
        self.on_delete_menu_activate (self, args)

    def on_help_button_clicked (self, *args):
        self.on_manual_menu_activate (self, args)


    def on_treeview_key_pressed (self, widget, event):
        key = gtk.gdk.keyval_name(event.keyval)
        #remove task from list with DEL key
        if key == "Delete" or key == "KP_Delete":
            self.on_delete_menu_activate()
        #display properties with ENTER key
        if (key == "Return" or key == "KP_Return"):
            self.on_properties_menu_activate(self, widget)


    #double click on task to get properties
    def on_treeview_button_press_event (self, widget, event):
        if event.type == gtk.gdk._2BUTTON_PRESS:
            self.on_properties_menu_activate(self, widget)


    #about box
    def open_url (self, *args):
        gtk.show_uri(None, "http://gnome-schedule.sourceforge.net", 0)



    def on_run_button_clicked (self, *args):
        dialog = gtk.MessageDialog(self.widget, gtk.DIALOG_MODAL|gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_QUESTION, gtk.BUTTONS_NONE, _("Are you sure you want to run this task now?\n\nThis is used to preview the task and initiates a one-time run, this does not affect the normal scheduled run times."))
        dialog.add_buttons (gtk.STOCK_EXECUTE, gtk.RESPONSE_YES, gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL)
        dialog.set_title (_("Are you sure you want to run this task?"))
        if (dialog.run() != gtk.RESPONSE_YES):
            dialog.destroy()
            del dialog
            return
        dialog.destroy()
        del dialog

        if (self.backend.get_not_inform_working_dir() != True):
            dia2 = gtk.MessageDialog (self.widget, gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_WARNING, gtk.BUTTONS_NONE, _("Note about working directory of executed tasks:\n\nRecurrent tasks will be run from the home directory, one-time tasks from the directory where Gnome schedule was run from at the time of task creation (normally the home directory)."))
            dia2.add_buttons (_("_Don't show again"), gtk.RESPONSE_CLOSE, gtk.STOCK_OK, gtk.RESPONSE_OK, gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL)
            dia2.set_title (_("Warning: Working directory of executed tasks"))
            response = dia2.run ()
            if response == gtk.RESPONSE_CANCEL:
                dia2.destroy ()
                del dia2
                return
            elif response == gtk.RESPONSE_CLOSE:
                self.backend.set_not_inform_working_dir (True)
            else:
                pass
            dia2.destroy ()
            del dia2

        store, iter = self.treeview.get_selection().get_selected()

        try:
            # commands are at model[3]

            #see what scheduler (at, crontab or ...)
            self.schedule = self.treemodel.get_value(iter, 7)

            tmpfile = tempfile.mkstemp ()
            fd, path = tmpfile
            tmp = os.fdopen (fd, 'w')

            commands = self.treemodel.get_value(iter, 3)
            linenumber = self.treemodel.get_value(iter, 4)


            if self.schedule.get_type () == "at":
                script = os.popen (config.getAtbin () + " -c " + str (linenumber)).read ()
            elif self.schedule.get_type () == "crontab":
                script = self.schedule.parse (commands)[1][5]

            # left untranslated to protect against any 'translation attacks'..
            script = script + "\necho " + "Press ENTER to continue and close this window." + "\n"
            script = script + "read\nexit\n"
            tmp.write (script)
            tmp.flush ()
            self.temp_files.append ((tmp, path))

            if self.root == 1 and self.user != "root":
                execute = "su " + self.user + " -c \"" + self.user_shell + " " + path
                os.chown (path, self.uid, self.gid)
            else:
                execute = self.user_shell + " " + path

            os.chmod (path, stat.S_IEXEC | stat.S_IREAD)

            # unset POSIXLY_CORRECT if manually set, bug 612459
            if self.manual_poscorrect:
              del os.environ['POSIXLY_CORRECT']

            # get terminal and exec params
            terminal = None
            terminalparam = None
            try:
              tex = ['gsettings', 'get', 'org.gnome.desktop.default-applications.terminal', 'exec']
              terminal = subprocess.check_output (tex)

              tex = ['gsettings', 'get', 'org.gnome.desktop.default-applications.terminal', 'exec-arg']
              terminalparam = subprocess.check_output (tex)
            except Exception, ex:
              terminal = None
              terminalparam = None

              print ex
              self.dialog = gtk.MessageDialog(self.widget, gtk.DIALOG_MODAL|gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_ERROR, gtk.BUTTONS_OK, _("No default graphical terminal for GNOME could be found."))
              self.dialog.run ()
              self.dialog.destroy ()

              return


            tex = terminal.strip () + ' ' + terminalparam.strip () + ' ' + execute
            subprocess.Popen(tex, cwd = self.user_home_dir, shell=True)

            if self.manual_poscorrect:
              os.environ['POSIXLY_CORRECT'] = 'enabled'


        except Exception, ex:
            print ex
            self.dialog = gtk.MessageDialog(self.widget, gtk.DIALOG_MODAL|gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_ERROR, gtk.BUTTONS_OK, _("Please select a task!"))
            self.dialog.run ()
            self.dialog.destroy ()

    def on_about_menu_activate (self, *args):

        gtk.about_dialog_set_url_hook(self.open_url, "bogusbar")
        dlg = gtk.AboutDialog ()
        dlg.set_title (_("About Gnome Schedule"))
        dlg.set_name (_("Gnome Schedule"))
        dlg.set_version (config.getVersion())
        dlg.set_copyright (_("Copyright (c) %(year)s %(name)s.") % ({ 'year' : "2004-2015", 'name' : "Gaute Hope"}))
        #dlg.set_comments ()
        #dlg.set_license ()
        dlg.set_website ("http://gnome-schedule.sourceforge.net")
        dlg.set_website_label("http://gnome-schedule.sourceforge.net")
        dlg.set_authors (
            ["Gaute Hope <eg@gaute.vetsj.com>",
             "Philip Van Hoof <pvanhoof at gnome dot org>",
             "Kristof Vansant <de_lupus at pandora dot be>"]
            )
        dlg.set_documenters (
            ["Rodrigo Marcos Fombellida <rmarcos_geo@yahoo.es>"]
            )
        dlg.set_translator_credits (_("translator-credits"))
        dlg.set_logo (self.iconPixbuf)

        if (dlg.run() != gtk.RESPONSE_YES):
            dlg.destroy()
            del dlg
            return
        dlg.destroy()
        del dlg

    #open help
    def on_manual_menu_activate (self, *args):
        try:
            gtk.show_uri(None, 'ghelp:gnome-schedule', 0)
        except gobject.GError, error:
            dialog = gtk.MessageDialog (
                    self.widget,
                    gtk.DIALOG_DESTROY_WITH_PARENT,
                    gtk.MESSAGE_ERROR, gtk.BUTTONS_CLOSE)
            dialog.set_markup ("<b>" + _("Could not display help") + "</b>")
            dialog.format_secondary_text ("%s" % error)
            dialog.run ()
            dialog.destroy ()


    #quit program
    def __quit__(self, *args):
        for t in self.temp_files:
            f, p = t
            f.close ()
            os.remove (p)

        # save state
        x,y = self.widget.get_position ()
        h, w = self.widget.get_size ()
        self.backend.set_window_state(x, y, h, w)
        if self.inapplet:
            self.widget.hide ()
        else:
            gtk.main_quit ()
        return True

# vim : set sw=4 :

