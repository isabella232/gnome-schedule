serverdir = $(libdir)/bonobo/servers
server_in_files = GNOME_schedule.server.in
server_DATA = $(server_in_files:.server.in=.server)

$(server_in_files): $(server_in_files:.server.in=.server.in.in)
	sed -e "s|\@LIBEXECDIR\@|$(libexecdir)|" $< > $@

@INTLTOOL_SERVER_RULE@

DISTCLEANFILES = $(server_DATA)

EXTRA_DIST = $(server_in_files)
