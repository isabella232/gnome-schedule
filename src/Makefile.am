bin_SCRIPTS = gnome-schedule

gnomescheduledir = $(prefix)/share/gnome-schedule
gnomeschedule_PYTHON = \
	gnome-schedule.py \
	config.py \
	mainWindow.py \
	addWindow.py \
	addWindowHelp.py \
	setuserWindow.py \
	crontab.py

uidir = $(datadir)/gnome-schedule
ui_DATA = gnome-schedule.glade

DISTCLEANFILES = \
	$(ui_DATA) \
	$(bin_SCRIPTS)

EXTRA_DIST =  \
	$(bin_SCRIPTS) \
	$(gnomeschedule_PYTHON) \
	$(ui_DATA)
