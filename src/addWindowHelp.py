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

import mainWindow
import addWindow
import gtk
import pwd
import string
import crontab
import re
import gobject

class AddWindowHelp:
	def __init__(self, parent, addwindow):
		self.ParentClass = parent
		self.AddWindow = addwindow
		
		#get some widgets and connect them
		self.widget = self.ParentClass.addhelpwidget
		self.xml = self.ParentClass.xml

		self.widget.connect("delete-event", self.btnCancel_clicked)
		self.radAll = self.xml.get_widget("radAll")
		self.radEvery = self.xml.get_widget("radEvery")
		self.radRange = self.xml.get_widget("radRange")
		self.radAt = self.xml.get_widget("radAt")
		self.radFix = self.xml.get_widget("radFix")

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

		#connect the changes of a combo or entry
		self.xml.signal_connect("on_entFix_changed", self.anyEntryChanged)
		self.xml.signal_connect("on_entEvery_changed", self.anyEntryChanged)
		self.xml.signal_connect("on_entRangeStart_changed", self.anyEntryChanged)
		self.xml.signal_connect("on_entRangeEnd_changed", self.anyEntryChanged)

		return

	def populateLabels(self, field):
		#put the apropiate values in the labels describing entitys, and the 'at' combobox
		self.radAll.set_label("Happens all " + field + "s")
		self.lblEveryEntity.set_text(field)
		self.lblFixEntity.set_text(field)
		if field == "minute":
			self.entRangeEnd.set_text ("59")
		if field == "hour":
			self.entRangeEnd.set_text ("59")
		if field == "day":
			self.entRangeEnd.set_text ("31")
		if field == "month":
			self.entRangeEnd.set_text ("12")
		if field == "weekday":
			self.entRangeEnd.set_text ("7")

		self.do_label_magic ()

		return

	def showAll(self, field):
		self.field = field
		#show the form
		self.widget.set_title(("Edit timeexpression for: " + field))
		self.populateLabels(field)
		self.widget.show_all()
		return

	def btnOk_clicked(self, *args):
		#move expression to field in addwindow and hide
		expression = self.entExpression.get_text()
		if self.field == "minute": self.AddWindow.minute_entry.set_text(expression)
		if self.field == "hour": self.AddWindow.hour_entry.set_text(expression)
		if self.field == "day": self.AddWindow.day_entry.set_text(expression)
		if self.field == "month": self.AddWindow.month_entry.set_text(expression)
		if self.field == "weekday": self.AddWindow.weekday_entry.set_text(expression)
		
		self.widget.hide()
		return

	def btnCancel_clicked(self, *args):
		#hide
		self.widget.hide()
		return gtk.TRUE

	def RadioButtonChange(self, widget):
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

		return

	def do_label_magic (self):
		try:
			entFixValue = int (self.entFix.get_text())
			if entFixValue == 1:
				self.lblFixEntity.set_label ("st. " + self.field)
			else:
				self.lblFixEntity.set_label ("th. " + self.field)
		except:
			pass

		try:
			entEveryValue = int (self.entEvery.get_text())
			if entEveryValue > 1:
				self.lblEveryEntity.set_label (self.field + "s")
			else:
				self.lblEveryEntity.set_label ("st. " + self.field)
		except:
			pass

	def anyEntryChanged(self, *args):
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

			
		return
