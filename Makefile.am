SUBDIRS = src pixmaps doc po

intltool_extra = intltool-extract.in intltool-merge.in intltool-update.in

EXTRA_DIST = \
	ChangeLog README  		\
	gnome-schedule.desktop.in 


Applicationsdir = $(datadir)/applications
Applications_in_files = gnome-schedule.desktop.in
Applications_DATA = $(Applications_in_files:.desktop.in=.desktop)
@INTLTOOL_DESKTOP_RULE@

CLEANFILES = \
	configure.in \
	system-config-schedule.console \
	gnome-schedule.desktop \
	gnome-schedule.spec

DISTCLEANFILES =		\
	intltool-extract	\
	intltool-merge		\
	intltool-update		\
	po/.intltool-merge-cache

