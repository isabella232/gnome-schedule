AC_INIT(src/gnome-schedule.py)
AM_INIT_AUTOMAKE(gnome-schedule, 0.9.0)

dnl check for python
dnl AM_PATH_PYTHON
AM_PATH_PYTHON

PKG_CHECK_MODULES(PYGTK, pygtk-2.0 >= 2.3)
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

AC_PATH_PROG(GNOMEHELP_CONFIG, gnome-help, no)
if test x$GNOMEHELP_CONFIG = xno; then
  AC_MSG_ERROR(Please install the application gnome-help)
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


AC_PATH_PROG(PYTHON_CONFIG, python, no)
if test x$PYTHON_CONFIG = xno; then
  AC_MSG_ERROR(Please install the application python)
fi

AC_PATH_PROG(SU_CONFIG, su, no)
if test x$BATCH_CONFIG = xno; then
  AC_MSG_ERROR(Please install the application su)
fi

AC_PATH_PROG(XSLTPROC, xsltproc, no)
if test "$XSLTPROC" = "no"; then
	AC_MSG_ERROR(xsltproc is required)
fi



dnl *******************************
dnl Internationalization
dnl ******************************* 
GETTEXT_PACKAGE=gnome-schedule
AC_DEFINE_UNQUOTED(GETTEXT_PACKAGE, "$GETTEXT_PACKAGE")
AC_SUBST(GETTEXT_PACKAGE)
AC_CONFIG_MACRO_DIR([src/m4])
GNOME_DOC_INIT

dnl Add the languages which your application supports here.
ALL_LINGUAS="bg ca cs da de el en_CA en_GB es fi fr hu it lt ne nl nn pa pt pt_BR rw sq sv uk zh_CN"

AM_GLIB_GNU_GETTEXT
AC_PROG_INTLTOOL

AC_OUTPUT([
Makefile
src/config.py
src/Makefile
src/gnome-schedule
pixmaps/Makefile
po/Makefile.in
desktop/Makefile
desktop/gnome-schedule.desktop
servers/Makefile
servers/GNOME_GnomeSchedule.server
help/Makefile
])
