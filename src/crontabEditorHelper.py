# addWindowhelp.py - UI code for help window for adding a crontab record
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
import re

##
## I18N
##
import gettext
domain = 'gnome-schedule'
gettext.bindtextdomain(domain)
gettext.textdomain(domain)
_ = gettext.gettext


class CrontabEditorHelper:
	def __init__(self, parent, editor):
		self.ParentClass = parent
		self.editor = editor
		
		self.xml = self.ParentClass.xml
		
		self.widget = self.xml.get_widget("crontabEditorHelper")
		self.widget.connect("delete-event", self.btnCancel_clicked)
		
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
		self.NoExpressionEvents = gtk.FALSE
		self.fieldRegex = self.ParentClass.editor.fieldRegex
		return

	def populateLabels(self, field):
		#put the apropiate values in the labels describing entitys, and the 'at' combobox

		if field == "minute":
			self.entRangeEnd.set_text ("59")
			self.entRangeStart.set_text ("0")
		if field == "hour":
			self.entRangeEnd.set_text ("23")
			self.entRangeStart.set_text ("0")
		if field == "day":
			self.entRangeEnd.set_text ("31")
			self.entRangeStart.set_text ("1")
		if field == "month":
			self.entRangeEnd.set_text ("12")
			self.entRangeStart.set_text ("1")
		if field == "weekday":
			self.entRangeEnd.set_text ("7")
			self.entRangeStart.set_text ("0")

		self.trans_field = self.editor.schedule.translate_frequency (field)

		self.radAll.set_label(_("Happens all ") + self.trans_field + _("s"))
		self.lblEveryEntity.set_text(self.trans_field)
		self.lblFixEntity.set_text(self.trans_field)
		self.radRange.set_label (_("Happens from ") + self.trans_field)

		self.do_label_magic ()

		return

	def show (self, field, expression):
		self.field = field
		self.populateLabels(field)

		m = self.fieldRegex.match (expression)
		self.radOth.set_active (gtk.TRUE)

		if m != None:
			self.NoExpressionEvents = gtk.TRUE
			self.entExpression.set_text (expression)
			if m.groups()[0] != None:
				self.radAll.set_active (gtk.TRUE)
			# 10 * * * * command
			# */2 * * * * command
			if m.groups()[1] != None or m.groups()[2] != None:
				if m.groups()[1] != None:
					self.radFix.set_active (gtk.TRUE)
					self.entFix.set_text (m.groups()[1])
				else:
					self.radEvery.set_active (gtk.TRUE)
					self.entEvery.set_text (m.groups()[2])

			# 1-10 * * * * command
			if m.groups()[3] != None and m.groups()[4] != None:
				self.radRange.set_active (gtk.TRUE)
				self.entRangeStart.set_text(m.groups()[3])
				self.entRangeEnd.set_text (m.groups()[4])

			# Unused
			# 1,2,3,4 * * * * command
			# if m.groups()[5] != None:
				# self.radOth.set_active (gtk.TRUE)
				# For some reason it's not grouping the last char :(
				# So we'll just append it, bah!
				# thefield = m.groups()[5] + expression[len(expression)-1]
				# thefield = "1,2,3,4"
				# fields = thefield.split (",")
			self.NoExpressionEvents = gtk.FALSE

		#show the form
		self.widget.set_title(_("Edit time expression for: ") + self.trans_field)
		self.widget.show_all()
		return

	def btnOk_clicked(self, *args):
		#move expression to field in editor and hide
		expression = self.entExpression.get_text()
		try:
			self.ParentClass.ParentClass.schedule.checkfield (expression, self.field, self.editor.fieldRegex)
		except Exception, ex:
			print ex
			x, y, z = ex
			self.wrongdialog = gtk.MessageDialog(self.widget, gtk.DIALOG_MODAL|gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_ERROR, gtk.BUTTONS_OK, (_("This is invalid. Reason: %s") % (z)))
			self.wrongdialog.run()
			self.wrongdialog.destroy()
			return

		if self.field == "minute": self.editor.minute_entry.set_text(expression)
		if self.field == "hour": self.editor.hour_entry.set_text(expression)
		if self.field == "day": self.editor.day_entry.set_text(expression)
		if self.field == "month": self.editor.month_entry.set_text(expression)
		if self.field == "weekday": self.editor.weekday_entry.set_text(expression)
		
		self.widget.hide()
		return

	def btnCancel_clicked(self, *args):
		#hide
		self.widget.hide()
		return gtk.TRUE

	def RadioButtonChange(self, widget):
		self.NoExpressionEvents = gtk.TRUE
		self.do_label_magic ()
		name = widget.get_name()
		if widget.get_active():
			if name == "radAll":
				self.entExpression.set_text("*")
			elif name == "radEvery":
				self.entExpression.set_text("*\\" + self.entEvery.get_text())
			elif name == "radRange":
				self.entExpression.set_text(self.entRangeStart.get_text() + "-" + self.entRangeEnd.get_text())
			elif name == "radFix":
				self.entExpression.set_text(self.entFix.get_text())
		self.NoExpressionEvents = gtk.FALSE
		return

	def do_label_magic (self):
		try:
			entFixValue = int (self.entFix.get_text())
			if entFixValue == 1:
				self.lblFixEntity.set_label (_("st. ") + self.trans_field)
			else:
				self.lblFixEntity.set_label (_("th. ") + self.trans_field)
		except:
			pass

		try:
			entEveryValue = int (self.entEvery.get_text())
			if entEveryValue > 1:
				self.lblEveryEntity.set_label (self.trans_field + _("s"))
			else:
				self.lblEveryEntity.set_label (_("st. ") + self.trans_field)
		except:
			pass

	def entExpressionChanged(self, *args):
		if self.NoExpressionEvents == gtk.FALSE:
			self.radOth.set_active (gtk.TRUE)

	def anyEntryChanged(self, *args):
		self.NoExpressionEvents = gtk.TRUE
		self.do_label_magic ()
		#create a easy read line for the expression view, put the command into the edit box
		if self.radAll.get_active():
				self.entExpression.set_text("*")
		if self.radEvery.get_active():
				self.entExpression.set_text("*\\" + self.entEvery.get_text())
		if self.radRange.get_active():
				self.entExpression.set_text(self.entRangeStart.get_text() + "-" + self.entRangeEnd.get_text())
		if self.radFix.get_active ():
				self.entExpression.set_text(self.entFix.get_text())
		self.NoExpressionEvents = gtk.FALSE
		return
