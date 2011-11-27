AC_INIT(src/gnome-schedule.py)
AM_INIT_AUTOMAKE(gnome-schedule, 2.2.0)

dnl check for python
dnl AM_PATH_PYTHON
dnl Until PyGtk supports Python 3 we look for Python 2 first
AC_PATH_PROG(PYTHON, python2 python2.7 python2.6 python2.5 python)
AM_PATH_PYTHON

PKG_CHECK_MODULES(PYGTK, pygtk-2.0 >= 2.6)
AC_SUBST(PYGTK_CFLAGS)
AC_SUBST(PYGTK_LIBS)


AC_PATH_PROG( PKGCONFIG, pkg-config, no, $PATH:/usr/bin:/usr/local/bin)
  if test "$PKGCONFIG" != "no" ; then
    AC_MSG_CHECKING([PYTHONPATH env variable for PyGTK])
    PYTHONPATH=$($PKGCONFIG --variable=pyexecdir pygtk-2.0)
    AC_SUBST([PYTHONPATH])
    AC_MSG_RESULT($PYTHONPATH)
  fi

export PYTHONPATH=$PYGTK_DIR:$PYTHONPATH
dnl check for libglade
AC_MSG_CHECKING(for gtk.glade)
prog="
import sys
try:
  import gtk.glade
except RuntimeError:
  sys.exit(0)
except ImportError:
  sys.exit(1)
sys.exit(0)
"

if $PYTHON -c "$prog" 1>&AC_FD_CC 2>&AC_FD_CC
then
  AC_MSG_RESULT(found)
else
  AC_MSG_RESULT(not found)
  AC_MSG_ERROR([You need to have python libglade bindings installed])
fi

PKG_CHECK_MODULES(GNOMEPYTHON, gnome-python-2.0 >= 2.12.0)

export PYTHONPATH=$PYGTK_DIR:$PYTHONPATH
dnl check for python-gconf
AC_MSG_CHECKING(for python gconf)
prog="
import sys
try:
  import gconf
except RuntimeError:
  sys.exit(0)
except ImportError:
  sys.exit(1)
sys.exit(0)
"

if $PYTHON -c "$prog" 1>&AC_FD_CC 2>&AC_FD_CC
then
  AC_MSG_RESULT(found)
else
  AC_MSG_RESULT(not found)
  AC_MSG_ERROR([You need to have python gconf bindings installed])
fi

AC_PATH_PROG(CRONTAB_CONFIG, crontab, no)
if test x$CRONTAB_CONFIG = xno; then
  AC_MSG_ERROR(Please install the application crontab)
fi

AC_PATH_PROG(AT_CONFIG, at, no)
if test x$AT_CONFIG = xno; then
  AC_MSG_ERROR(Please install the application at)
fi

AC_PATH_PROG(ATQ_CONFIG, atq, no)
if test x$ATQ_CONFIG = xno; then
  AC_MSG_ERROR(Please install the application atq)
fi

AC_PATH_PROG(ATRM_CONFIG, atrm, no)
if test x$ATRM_CONFIG = xno; then
  AC_MSG_ERROR(Please install the application atrm)
fi

AC_PATH_PROG(BATCH_CONFIG, batch, no)
if test x$BATCH_CONFIG = xno; then
  AC_MSG_ERROR(Please install the application batch)
fi

AC_PATH_PROG(SU_CONFIG, su, no)
if test x$BATCH_CONFIG = xno; then
  AC_MSG_ERROR(Please install the application su)
fi

AC_PATH_PROG(XSLTPROC, xsltproc, no)
if test "$XSLTPROC" = "no"; then
	AC_MSG_ERROR(xsltproc is required)
fi

dnl Enable applet, the applet is not compatible with GNOME 3
dnl and should be explicitily enabled.
AC_MSG_CHECKING(for whether to include GNOME panel applet..)
AC_ARG_ENABLE(applet,
              [  --enable-applet         enable applet for the GNOME panel (GNOME 2 only)],
              [applet=yes])

AM_CONDITIONAL([APPLET], [test x$applet = xyes])

if test "$applet" = "yes"; then
  AC_MSG_RESULT(yes)
else
  AC_MSG_RESULT(no)
fi


dnl *******************************
dnl Internationalization
dnl *******************************
GETTEXT_PACKAGE=gnome-schedule
AC_DEFINE_UNQUOTED(GETTEXT_PACKAGE, "$GETTEXT_PACKAGE")
AC_SUBST(GETTEXT_PACKAGE)
dnl AC_CONFIG_MACRO_DIR([m4])
GNOME_DOC_INIT

dnl Add the languages which your application supports here.
ALL_LINGUAS="ar bg ca cs da de dz el en_CA en_GB es eu fi fr gl gu hu it lt nb ne nl nn oc pa pl pt pt_BR ro ru rw sl sq sv uk vi zh_CN zh_HK zh_TW"

AM_GLIB_GNU_GETTEXT
AC_PROG_INTLTOOL

AC_OUTPUT([
Makefile
src/config.py
src/Makefile
src/gnome-schedule
src/gnome-schedule-export
src/gnome-schedule-import
icons/Makefile
po/Makefile.in
desktop/Makefile
desktop/gnome-schedule.desktop.in
servers/Makefile
servers/GNOME_GnomeSchedule.server.in
help/Makefile
])

