# template.py: Handles the link to the template data stored in gconf
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

#pygtk
import gconf

#python modules
import os

#gnome-schedule
import config

class Template:
    def __init__ (self, parent, configbackend):
        self.parent = parent
        self.configbackend = configbackend
        self.gconf_client = self.configbackend.gconf_client
        

    def removetemplate_at (self, template_id):
        installed = self.gconf_client.get_string("/apps/gnome-schedule/templates/at/installed")
        newstring = installed
        if installed != None:
            first = True
            newstring = "   "

            for t in installed.split (", "):
                if t != str (template_id):
                    if first == True:
                        newstring = t
                        first = False
                    else:
                        newstring = newstring + ", " + t
        
        self.gconf_client.unset("/apps/gnome-schedule/templates/at/%s/title" % (str (template_id)))
        self.gconf_client.unset("/apps/gnome-schedule/templates/at/%s/command" % (str (template_id)))
        self.gconf_client.unset ("/apps/gnome-schedule/templates/at/%s/output" % (str (template_id)))
            
        if newstring == "   ":
            self.gconf_client.unset ("/apps/gnome-schedule/templates/at/installed")
        else:
            self.gconf_client.set_string("/apps/gnome-schedule/templates/at/installed", newstring)
            
    def removetemplate_crontab (self, template_id): 
        installed = self.gconf_client.get_string("/apps/gnome-schedule/templates/crontab/installed")
        newstring = installed
        if installed != None:
            first = True
            newstring = "   "

            for t in installed.split (", "):
                if t != str (template_id):
                    if first == True:
                        newstring = t
                        first = False
                    else:
                        newstring = newstring + ", " + t
        
        self.gconf_client.unset("/apps/gnome-schedule/templates/crontab/%s/title" % (str (template_id)))
        self.gconf_client.unset("/apps/gnome-schedule/templates/crontab/%s/command" % (str (template_id)))
        self.gconf_client.unset("/apps/gnome-schedule/templates/crontab/%s/timeexpression" % (str (template_id)))
        self.gconf_client.unset("/apps/gnome-schedule/templates/crontab/%s/output" % (str (template_id)))
            
        if newstring == "   ":
            self.gconf_client.unset ("/apps/gnome-schedule/templates/crontab/installed")
        else:
            self.gconf_client.set_string("/apps/gnome-schedule/templates/crontab/installed", newstring)
        
    
    def create_new_id_crontab (self):
        i = self.gconf_client.get_int ("/apps/gnome-schedule/templates/crontab/last_id")
        if i == None:
            self.gconf_client.set_int ("/apps/gnome-schedule/templates/crontab/last_id", 1)
            return 1
        else:
            i = i + 1
            self.gconf_client.set_int ("/apps/gnome-schedule/templates/crontab/last_id", i)
            return i
            
    def savetemplate_crontab (self, template_id, title, command, output, timeexpression):   

        if (template_id == 0):
            template_id = self.create_new_id_crontab ()
            
        self.gconf_client.set_string("/apps/gnome-schedule/templates/crontab/%s/timeexpression" % (str (template_id)), timeexpression)
        self.gconf_client.set_string("/apps/gnome-schedule/templates/crontab/%s/title" % (str (template_id)), title)
        self.gconf_client.set_string("/apps/gnome-schedule/templates/crontab/%s/command" % (str (template_id)), command)
        self.gconf_client.set_int("/apps/gnome-schedule/templates/crontab/%s/output" % (str (template_id)), output)
        
        installed = self.gconf_client.get_string("/apps/gnome-schedule/templates/crontab/installed")
        if installed == None:
            installed = str(template_id)
        else:
            found = False

            for t in installed.split (", "):
                if t == str (template_id):
                    found = True
        
            if found == False:
                installed = installed + ", " + str (template_id)
                
        self.gconf_client.unset ("/apps/gnome-schedule/templates/crontab/installed")
        self.gconf_client.set_string("/apps/gnome-schedule/templates/crontab/installed", installed)
        self.parent.template_manager.reload_tv ()
        self.parent.template_chooser.reload_tv ()
        
        
    def gettemplateids (self, type):
        strlist = self.gconf_client.get_string("/apps/gnome-schedule/templates/" + type + "/installed")
        if strlist != None:

            list = strlist.split (", ")
            return list
        else:
            return None


    def gettemplate (self, type, template_id):
        if type == "crontab":
            try:
                command = self.gconf_client.get_string("/apps/gnome-schedule/templates/crontab/%s/command" % (str (template_id)))
                title = self.gconf_client.get_string("/apps/gnome-schedule/templates/crontab/%s/title" % (str (template_id)))
                output = self.gconf_client.get_int("/apps/gnome-schedule/templates/" + type + "/%s/output" % (str (template_id)))
                timeexpression = self.gconf_client.get_string("/apps/gnome-schedule/templates/" + type + "/%s/timeexpression" % (template_id))
                return template_id, title, command, output, timeexpression
    
            except Exception, ex:
                return False
                
        elif type == "at":
            try:
                command = self.gconf_client.get_string("/apps/gnome-schedule/templates/at/%s/command" % (str (template_id)))
                title = self.gconf_client.get_string("/apps/gnome-schedule/templates/at/%s/title" % (str (template_id)))
                output = self.gconf_client.get_int ("/apps/gnome-schedule/templates/at/%s/output" % (str (template_id)))
                return template_id, title, command, output
    
            except Exception, ex:
                return False

    def create_new_id_at (self):
        i = self.gconf_client.get_int ("/apps/gnome-schedule/templates/at/last_id")
        if i == 0:
            self.gconf_client.set_int ("/apps/gnome-schedule/templates/at/last_id", 1)
            return 1
        else:
            i = i + 1
            self.gconf_client.set_int ("/apps/gnome-schedule/templates/at/last_id", i)
            return i    

    def savetemplate_at (self, template_id, title, command, output):
        print "savetemplate"

        if (template_id == 0):
            template_id = self.create_new_id_at ()
            print "got new id"
            
        self.gconf_client.set_string("/apps/gnome-schedule/templates/at/%s/title" % (str (template_id)), title)
        self.gconf_client.set_string("/apps/gnome-schedule/templates/at/%s/command" % (str (template_id)), command)
        self.gconf_client.set_int ("/apps/gnome-schedule/templates/at/%s/output" % ( str(template_id)), output)

        
        installed = self.gconf_client.get_string("/apps/gnome-schedule/templates/at/installed")
        if installed == None:
            installed = str(template_id)
        else:
            found = False

            for t in installed.split (", "):
                if t == str (template_id):
                    found = True
        
            if found == False:
                installed = installed + ", " + str (template_id)
                
        self.gconf_client.unset ("/apps/gnome-schedule/templates/at/installed")
        self.gconf_client.set_string("/apps/gnome-schedule/templates/at/installed", installed)
        self.parent.template_manager.reload_tv ()
        self.parent.template_chooser.reload_tv ()
        
    # TODO: output
    def format_at (self, title, command, output):
        command = self.parent.at.__make_preview__ (command, 0)
        s = "<b>" + _("Title:") + "</b> " + title + "\n<b>" + _("Command:") + "</b> " + command
        if output > 0:
            s = (s + " <i>(%s)</i>") % (str (self.parent.output_strings [2]))

        return s
        
    def format_crontab (self, title, command, output, timeexpression):
        command = self.parent.crontab.__make_preview__ (command)
        if self.parent.edit_mode == "simple":
            # hehe.. :)
            timeexpression = timeexpression + " echo hehe"
            minute, hour, dom, moy, dow, hehe = self.parent.crontab.parse (timeexpression, True)
            timeexpression = self.parent.crontab.__easy__ (minute, hour, dom, moy, dow)

        s = "<b>" + _("Title:") + "</b> " + title + "\n<b>" + _("Run:") + "</b> " + timeexpression + "\n<b>" + _("Command:") + "</b> " + command

        if output > 0:
            s = (s + " <i>(%s)</i>") % (str (self.parent.output_strings[output]))
        
        return s
