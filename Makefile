#License: GPL
#Copyright Red Hat Inc.  Jan 2001

VERSION=$(shell awk '/Version:/ { print $$2 }' gnome-schedule.spec)
CVSTAG=r$(subst .,-,$(VERSION))
SUBDIRS=po

PREFIX=/usr
DATADIR=${PREFIX}/share
MANDIR=${DATADIR}/man
PKGNAME = gnome-schedule
PKGDATADIR=${DATADIR}/${PKGNAME}
PKGIMAGEDIR=${PKGDATADIR}/pixmaps

PAMD_DIR        = /etc/pam.d
SECURITY_DIR    =/etc/security/console.apps

default: subdirs

subdirs:
	for d in $(SUBDIRS); do make -C $$d; [ $$? = 0 ] || exit 1; done

install:
	mkdir -p $(INSTROOT)/usr/bin
	mkdir -p $(INSTROOT)$(PKGDATADIR)
	mkdir -p $(INSTROOT)$(PKGIMAGEDIR)
	mkdir -p $(INSTROOT)$(PAMD_DIR)
	mkdir -p $(INSTROOT)$(SECURITY_DIR)
	mkdir -p $(INSTROOT)/usr/share/pixmaps
	mkdir -p $(INSTROOT)/usr/share/applications
	mkdir -p $(INSTROOT)/usr/share/icons/hicolor/48x48/apps
	install src/*.py $(INSTROOT)$(PKGDATADIR)
	for py in src/*.py ; do \
		sed -e s,@VERSION@,$(VERSION),g $${py} > $(INSTROOT)$(PKGDATADIR)/`basename $${py}` ; \
	done
	install src/*.glade $(INSTROOT)$(PKGDATADIR)
	install $(PKGNAME).pam $(INSTROOT)$(PAMD_DIR)/$(PKGNAME)
	install $(PKGNAME).console $(INSTROOT)$(SECURITY_DIR)/$(PKGNAME)
	install pixmaps/*.png $(INSTROOT)$(PKGIMAGEDIR)
	install pixmaps/${PKGNAME}.png $(INSTROOT)/usr/share/icons/hicolor/48x48/apps
	install ${PKGNAME}.desktop $(INSTROOT)/usr/share/applications/${PKGNAME}.desktop
	ln -sf consolehelper $(INSTROOT)/usr/bin/$(PKGNAME)
	for d in $(SUBDIRS); do \
	(cd $$d; $(MAKE) INSTROOT=$(INSTROOT) MANDIR=$(MANDIR) install) \
		|| case "$(MFLAGS)" in *k*) fail=yes;; *) exit 1;; esac; \
	done && test -z "$$fail"

archive:
	cvs tag -cFR $(CVSTAG) .
	@rm -rf /tmp/${PKGNAME}-$(VERSION) /tmp/${PKGNAME}
	@CVSROOT=`cat CVS/Root`; cd /tmp; cvs -d $$CVSROOT export -r$(CVSTAG) ${PKGNAME}
	@mv /tmp/${PKGNAME} /tmp/${PKGNAME}-$(VERSION)
	@dir=$$PWD; cd /tmp; tar --bzip2 -cSpf $$dir/${PKGNAME}-$(VERSION).tar.bz2 ${PKGNAME}-$(VERSION)
	@rm -rf /tmp/${PKGNAME}-$(VERSION)
	@echo "The archive is in ${PKGNAME}-$(VERSION).tar.bz2"

snapsrc: archive
	@rpmbuild -ta $(PKGNAME)-$(VERSION).tar.bz2

local:
	@rm -rf ${PKGNAME}-$(VERSION).tar.bz2
	@rm -rf /tmp/${PKGNAME}-$(VERSION) /tmp/${PKGNAME}
	@cd /tmp; cp -a ~/fedora/${PKGNAME} ${PKGNAME}
	@mv /tmp/${PKGNAME} /tmp/${PKGNAME}-$(VERSION)
	@dir=$$PWD; cd /tmp; tar --bzip2 -cSpf $$dir/${PKGNAME}-$(VERSION).tar.bz2 ${PKGNAME}-$(VERSION)
	@rm -rf /tmp/${PKGNAME}-$(VERSION)	
	@echo "The archive is in ${PKGNAME}-$(VERSION).tar.bz2"

clean:
	@rm -fv *~
	@rm -fv *.pyc
	@rm -fv src/*~




