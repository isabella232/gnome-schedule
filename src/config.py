version = "@VERSION@"
image_dir = "@prefix@/share/pixmaps"
glade_dir = "@prefix@/share/gnome-schedule"
doc_dir = "@prefix@/share/doc/gnome-schedule-@VERSION@"
gnomehelpbin = "@GNOMEHELP_CONFIG@"
crontabbin = "@CRONTAB_CONFIG@"

def getCrontabbin ():
	return crontabbin

def getGnomehelpbin ():
	return gnomehelpbin

def getVersion ():
	return version

def getImagedir ():
	return image_dir

def getGladedir ():
	return glade_dir

def getDocdir ():
	return doc_dir
