version = "1.0"
image_dir = "/usr/local/share/pixmaps"
glade_dir = "/usr/local/share/gnome-schedule"
doc_dir = "/usr/local/share/doc/gnome-schedule-1.0"
gnomehelpbin = "/usr/bin/gnome-help"
crontabbin = "/usr/bin/crontab"

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
