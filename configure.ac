AC_INIT(configure.ac)
AM_INIT_AUTOMAKE(gnome-schedule, 1.0)

AC_PROG_INTLTOOL

dnl *******************************
dnl Internationalization
dnl ******************************* 
GETTEXT_PACKAGE=atomix
AC_DEFINE_UNQUOTED(GETTEXT_PACKAGE, "$GETTEXT_PACKAGE")
AC_SUBST(GETTEXT_PACKAGE)

dnl Add the languages which your application supports here.
ALL_LINGUAS=""

AM_GLIB_GNU_GETTEXT

AC_OUTPUT([
Makefile
po/Makefile.in])

dnl src/Makefile
dnl doc/Makefile
dnl pixmaps/Makefile

