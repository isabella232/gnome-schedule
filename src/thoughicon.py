# ToughIconTheme
# Try to load an icon from the current icon theme. if this fails try to load
# from the default gnome theme. if this fails to try to use the buildin
# MISSING_IMAGE stock icon. and as a last fallback set the icon to None
#
# Picked up from: http://people.ubuntu.com/~mvo/bzr/gnome-app-install/gai--main/
# http://people.ubuntu.com/~mvo/bzr/gnome-app-install/gai--main/COPYING
#

import gtk
import gobject
import pygtk
from warnings import warn

class ToughIconTheme:
    def __init__(self):
        self.fallback = gtk.IconTheme()
        self.fallback.set_custom_theme("hicolor")
        self.crystal = gtk.IconTheme()
        self.crystal.set_custom_theme("crystal")
        self.gnome = gtk.IconTheme()
        self.gnome.set_custom_theme("gnome")
        self.default = gtk.icon_theme_get_default()
        self.themes = [self.default, self.gnome, self.fallback, self.crystal]
        self._internal_cache = {}

    def load_icon(self, icon, size=48, flags=0):
        for theme in self.themes:
            try:
                return theme.load_icon(icon, size, flags)
            except:
                continue
        return self.fallback.load_icon(gtk.STOCK_MISSING_IMAGE, size, flags)
        #raise IOError, "Icon '%s' not found" % icon

    def prepend_search_path(self, path):
        for theme in self.themes:
            try:
                theme.prepend_search_path(path)
            except:
                continue
        return 

    def lookup_icon(self,  name, size, flags=0):
        for theme in self.themes:
            info = theme.lookup_icon(name, size, flags)
            if info != None:
                return info
        return None

    def get_icon_sizes(self, icon_name):
        for theme in self.themes:
            try:
                return theme.get_icon_sizes(icon_name)
            except:
                continue
        return None

    def has_icon(self, icon_name):
        for theme in self.themes:
            if theme.has_icon(icon_name) == True:
                return True
        return False

    def _getIcon(self, name, size):
        cache_name = "%s-%s" % (name, size)
        if self._internal_cache.has_key(cache_name):
            return self._internal_cache[cache_name]
        if name is None or name == "":
            warn(_("ICON: Using dummy icon"))
            name = "applications-other"
        if name.startswith("/"):
            warn(_("ICON: Doesn't handle absolute paths: '%s'" % name))
            name = "applications-other"
        if name.find(".") != -1:
            import os.path
            # splitting off extensions in all cases broke evolution's icon
            # hopefully no common image extensions will ever have len != 3
            if len(os.path.splitext(name)[1]) == (3 + 1): # extension includes '.'
                name = os.path.splitext(name)[0]
        if not self.has_icon(name):
            warn(_("ICON: Icon '%s' is not in theme" % name))
            name = "applications-other"
        # FIXME: mvo: this try: except is a hack to work around 
        #             ubuntu #6858 (icon is no longer in cache after removal)
        #             of a pkg. correct is probably to reload the icontheme
        #             (or something)
        try:
            icon = self.load_icon(name, size, 0)
        except gobject.GError:
            icon = self.load_icon("applications-other", size, 0)
            name = "applications-other"
        if icon.get_width() != size:
            warn(_("ICON: Got badly sized icon for %s" % name))
            icon = icon.scale_simple(size, size, gtk.gdk.INTERP_BILINEAR)
        
        info = self.lookup_icon(name, size, gtk.ICON_LOOKUP_NO_SVG | gtk.ICON_LOOKUP_USE_BUILTIN)
        if info is None:
            info = self.lookup_icon("applications-other", size, gtk.ICON_LOOKUP_NO_SVG | gtk.ICON_LOOKUP_USE_BUILTIN)
            if info is None:
                filename = None
            else:
                filename = info.get_filename()
        else:
            filename = info.get_filename()
        self._internal_cache[cache_name] = icon
        return icon
        
