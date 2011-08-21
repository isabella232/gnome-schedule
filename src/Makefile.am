bin_SCRIPTS = gnome-schedule gnome-schedule-export gnome-schedule-import

gnomescheduledir = $(prefix)/share/gnome-schedule
gnomeschedule_PYTHON = \
	gnome-schedule.py \
	gnome-schedule-export.py \
	gnome-schedule-import.py \
	db.py \
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
	data.py \
	template.py \
	template_chooser.py \
	template_manager.py \
	xwrapper.py

uidir = $(datadir)/gnome-schedule
ui_DATA = \
	gnome-schedule.glade


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

