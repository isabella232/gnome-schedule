AC_INIT(src/gnome-schedule.py)
AM_INIT_AUTOMAKE(gnome-schedule, 1.0)

AC_PROG_INTLTOOL

AM_PATH_PYTHON

PKG_CHECK_MODULES(PYGTK, pygtk-2.0)
AC_SUBST(PYGTK_CFLAGS)
AC_SUBST(PYGTK_LIBS)

AC_PATH_PROG(GNOMEHELP_CONFIG, gnome-help, no)
if test x$GNOMEHELP_CONFIG = xno; then
  AC_MSG_ERROR(Please install the application gnome-help)
fi

AC_PATH_PROG(CRONTAB_CONFIG, crontab, no)
if test x$crontab_CONFIG = xno; then
  AC_MSG_ERROR(Please install the application crontab)
fi

dnl AC_DEFINE_UNQUOTED (GNOMEHELP_CONFIG, "$GNOMEHELP_CONFIG")
dnl AC_DEFINE_UNQUOTED (CRONTAB_CONFIG, "$CRONTAB_CONFIG")


dnl *******************************
dnl Internationalization
dnl ******************************* 
GETTEXT_PACKAGE=gnome-schedule
AC_DEFINE_UNQUOTED(GETTEXT_PACKAGE, "$GETTEXT_PACKAGE")
AC_SUBST(GETTEXT_PACKAGE)

dnl Add the languages which your application supports here.
ALL_LINGUAS="pt_BR sv"

AM_GLIB_GNU_GETTEXT

AC_OUTPUT([
Makefile
src/config.py
src/Makefile
src/gnome-schedule
doc/Makefile
pixmaps/Makefile
po/Makefile.in])
