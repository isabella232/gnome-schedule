bin_SCRIPTS = gnome-schedule

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
	editor.py \
	schedule.py \
	lang.py \
	support.py

uidir = $(datadir)/gnome-schedule
ui_DATA = gnome-schedule.glade

DISTCLEANFILES = \
	$(bin_SCRIPTS) \
	config.py

EXTRA_DIST =  \
	$(bin_SCRIPTS) \
	$(gnomeschedule_PYTHON) \
	$(ui_DATA)
