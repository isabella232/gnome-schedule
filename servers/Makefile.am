serverdir = $(libdir)/bonobo/servers
server_in_files = GNOME_GnomeSchedule.server.in
server_DATA = $(server_in_files:.server.in=.server)
@INTLTOOL_SERVER_RULE@


DISTCLEANFILES = $(server_DATA)

if APPLET
EXTRA_DIST = $(server_DATA)
endif
