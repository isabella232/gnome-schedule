bin_SCRIPTS = \
			gnome-schedule \
			scheduleapplet

gnomescheduledir = $(prefix)/share/gnome-schedule
gnomeschedule_PYTHON = \
	gnome-schedule.py \
	at.py \
	config.py \
	mainWindow.py \
	crontabEditorHelper.py \
	crontabEditor.py \
	setuserWindow.py \
	crontab.py \
	lang.py \
	addWindow.py \
	atEditor.py \
	preset.py \
	scheduleapplet.py
	

uidir = $(datadir)/gnome-schedule
ui_DATA = \
	gnome-schedule.glade \
	gnome-schedule-applet.xml

DISTCLEANFILES = \
	$(bin_SCRIPTS) \
	config.py \
	gnome-schedule.glade.bak \
	gnome-schedule.gladep.bak \
	gnome-schedule.gladep

EXTRA_DIST =  \
	$(bin_SCRIPTS) \
	$(gnomeschedule_PYTHON) \
	$(ui_DATA)
