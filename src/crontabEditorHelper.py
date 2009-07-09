# crontabEditorHelper.py - UI code for help window for adding a crontab record
# Copyright (C) 2004, 2005  Philip Van Hoof <me at pvanhoof dot be>
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
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02110-1301, USA.

#pygtk modules
import gtk

#python modules
import re


class CrontabEditorHelper:
    def __init__(self, parent):
        self.ParentClass = parent

        self.xml = self.ParentClass.xml

        self.NoExpressionEvents = False
        self.fieldRegex = self.ParentClass.fieldRegex

        self.widget = self.xml.get_widget("crontabEditorHelper")
        self.widget.connect("delete-event", self.widget.hide_on_delete)

        self.radAll = self.xml.get_widget("radAll")
        self.radEvery = self.xml.get_widget("radEvery")
        self.radRange = self.xml.get_widget("radRange")
        self.radFix = self.xml.get_widget("radFix")
        self.radOth = self.xml.get_widget ("radOth")

        self.entExpression = self.xml.get_widget("entExpression")
        self.entEvery = self.xml.get_widget("entEvery")
        self.entFix = self.xml.get_widget("entFix")
        self.entRangeStart = self.xml.get_widget("entRangeStart")
        self.entRangeEnd = self.xml.get_widget("entRangeEnd")

        self.header = self.xml.get_widget("label_crontab_editor_title")

        self.lblEveryEntity = self.xml.get_widget("lblEveryEntity")
        self.lblFixEntity = self.xml.get_widget("lblFixEntity")

        #connect the radiobuttons toggle
        self.xml.signal_connect("on_btnCancel_clicked", self.btnCancel_clicked)
        self.xml.signal_connect("on_btnOk_clicked", self.btnOk_clicked)
        self.xml.signal_connect("on_radAll_toggled", self.RadioButtonChange)
        self.xml.signal_connect("on_radEvery_toggled", self.RadioButtonChange)
        self.xml.signal_connect("on_radRange_toggled", self.RadioButtonChange)
        self.xml.signal_connect("on_radFix_toggled", self.RadioButtonChange)
        self.xml.signal_connect("on_radOth_toggled", self.RadioButtonChange)

        #connect the changes of a combo or entry
        self.xml.signal_connect("on_entFix_changed", self.anyEntryChanged)
        self.xml.signal_connect("on_entEvery_changed", self.anyEntryChanged)
        self.xml.signal_connect("on_entRangeStart_changed", self.anyEntryChanged)
        self.xml.signal_connect("on_entRangeEnd_changed", self.anyEntryChanged)
        self.xml.signal_connect("on_entExpression_changed", self.entExpressionChanged)

        self.widgetgroups = { "radAll":  [],
                      "radEvery":["entEvery", "lblEveryEntity"],
                      "radRange":["entRangeStart", "entRangeEnd",
                          "lblRangeStart", "lblRangeEnd"],
                      "radFix":  ["entFix", "lblFixEntity"],
                      "radOth":  ["entExpression",
                          "lblExpression"] }


    def populateLabels(self, field):
        #put the apropiate values in the labels describing entitys, and the 'at' combobox

        if field == "minute":
            self.entRangeEnd.set_text ("59")
            self.entRangeStart.set_text ("0")
            self.entFix.set_text("0")
            self.radAll.set_label(_("Every minute"))

        if field == "hour":
            self.entRangeEnd.set_text ("23")
            self.entRangeStart.set_text ("0")
            self.entFix.set_text("0")
            self.radAll.set_label(_("Every hour"))

        if field == "day":
            self.entRangeEnd.set_text ("31")
            self.entRangeStart.set_text ("1")
            self.entFix.set_text("1")
            self.radAll.set_label(_("Every day"))

        if field == "month":
            self.entRangeEnd.set_text ("12")
            self.entRangeStart.set_text ("1")
            self.entFix.set_text("1")
            self.radAll.set_label(_("Every month"))

        if field == "weekday":
            self.entRangeEnd.set_text ("7")
            self.entRangeStart.set_text ("0")
            self.entFix.set_text("0")
            self.radAll.set_label(_("Every weekday"))


        self.entEvery.set_text("2")
        self.entExpression.set_text ("*")

        self.trans_field = self.ParentClass.scheduler.translate_frequency (field)



        self.do_label_magic ()


    def show (self, field, expression):
        self.field = field
        self.populateLabels(field)

        m = self.fieldRegex.match (expression)
        self.radOth.set_active (True)

        self.NoExpressionEvents = True
        self.entExpression.set_text (expression)

        if m != None:
            if m.groups()[0] != None:
                self.radAll.set_active (True)
            # 10 * * * * command
            # */2 * * * * command
            if m.groups()[1] != None or m.groups()[2] != None:
                if m.groups()[1] != None:
                    self.radFix.set_active (True)
                    self.entFix.set_text (m.groups()[1])
                else:
                    self.radEvery.set_active (True)
                    self.entEvery.set_text (m.groups()[2])

            # 1-10 * * * * command
            if m.groups()[3] != None and m.groups()[4] != None:
                self.radRange.set_active (True)
                self.entRangeStart.set_text(m.groups()[3])
                self.entRangeEnd.set_text (m.groups()[4])

            # Unused
            # 1,2,3,4 * * * * command
            # if m.groups()[5] != None:
                # self.radOth.set_active (True)
                # fields = m.groups()[5].split (",")

        self.NoExpressionEvents = False

        #show the form
        if field == "minute":
            self.widget.set_title(_("Edit minute"))
        elif field == "hour":
            self.widget.set_title(_("Edit hour"))
        elif field == "day":
            self.widget.set_title(_("Edit day"))
        elif field == "month":
            self.widget.set_title(_("Edit month"))
        elif field == "weekday":
            self.widget.set_title(_("Edit weekday"))

        self.widget.set_transient_for(self.ParentClass.widget)
        self.widget.set_position(gtk.WIN_POS_CENTER_ON_PARENT)
        self.widget.show_all()


    def btnOk_clicked(self, *args):
        #move expression to field in editor and hide
        expression = self.entExpression.get_text()
        try:
            self.ParentClass.scheduler.checkfield (expression, self.field)
        except ValueError, ex:
            x, y, z = ex
            self.wrongdialog = gtk.MessageDialog(self.widget, gtk.DIALOG_MODAL|gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_ERROR, gtk.BUTTONS_OK, (_("This is invalid. Reason: %s") % (z)))
            self.wrongdialog.run()
            self.wrongdialog.destroy()
            return

        if self.field == "minute": self.ParentClass.minute_entry.set_text(expression)
        if self.field == "hour": self.ParentClass.hour_entry.set_text(expression)
        if self.field == "day": self.ParentClass.day_entry.set_text(expression)
        if self.field == "month": self.ParentClass.month_entry.set_text(expression)
        if self.field == "weekday": self.ParentClass.weekday_entry.set_text(expression)

        self.widget.hide()


    def btnCancel_clicked(self, *args):
        #hide
        self.widget.hide()
        #return True


    def RadioButtonChange(self, widget):
        self.NoExpressionEvents = True
        self.do_label_magic ()
        name = widget.get_name()
        if widget.get_active():
            if name == "radAll":
                self.entExpression.set_text("*")
            elif name == "radEvery":
                self.entExpression.set_text("*/" + self.entEvery.get_text())
            elif name == "radRange":
                self.entExpression.set_text(self.entRangeStart.get_text() + "-" + self.entRangeEnd.get_text())
            elif name == "radFix":
                self.entExpression.set_text(self.entFix.get_text())
        self.NoExpressionEvents = False

        for groupname, widgetlist in self.widgetgroups.iteritems():
            state = groupname == name
            for widgetname in widgetlist:
                widget = self.xml.get_widget(widgetname)
                widget.set_sensitive(state)


    def do_label_magic (self):
        translated = ["", ""]
        if self.field == "minute":
            #minute
            translated[0] = _("At an exact minute")
            translated[1] = _("Minute:")
        elif self.field == "hour":
            #hour
            translated[0] = _("At an exact hour")
            translated[1] = _("Hour:")
        elif self.field == "day":
            #day
            translated[0] = _("On a day")
            translated[1] = _("Day:")
        elif self.field == "month":
            #month
            translated[0] = _("In a month")
            translated[1] = _("Month:")
        elif self.field == "weekday":
            #weekday
            translated[0] = _("On a weekday")
            translated[1] = _("Weekday:")

        self.radFix.set_label (translated[0])
        self.lblFixEntity.set_label (translated[1])

        translated[0] = _("In a step width")
        if self.field == "minute":
            translated[1] = _("Minutes:")
        elif self.field == "hour":
            translated[1] = _("Hours:")
        elif self.field == "day":
            translated[1] = _("Days:")
        elif self.field == "month":
            translated[1] = _("Months:")
        elif self.field == "weekday":
            translated[1] = _("Weekdays:")

        self.radEvery.set_label (translated[0])
        self.lblEveryEntity.set_label (translated[1])


    def entExpressionChanged(self, *args):
        if self.NoExpressionEvents == False:
            self.radOth.set_active (True)


    def anyEntryChanged(self, *args):
        self.NoExpressionEvents = True
        self.do_label_magic ()
        #create a easy read line for the expression view, put the command into the edit box
        if self.radAll.get_active():
                self.entExpression.set_text("*")
        if self.radEvery.get_active():
                self.entExpression.set_text("*/" + self.entEvery.get_text())
        if self.radRange.get_active():
                self.entExpression.set_text(self.entRangeStart.get_text() + "-" + self.entRangeEnd.get_text())
        if self.radFix.get_active ():
                self.entExpression.set_text(self.entFix.get_text())
        self.NoExpressionEvents = False
