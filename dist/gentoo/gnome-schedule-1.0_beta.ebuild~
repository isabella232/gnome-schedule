P="gnome-schedule-1.0_beta"
PN="gnome-schedule"
PV="1.0"
SLOT="0"
LICENSE="GPL"
KEYWORDS="x86"
DESCRIPTION="A graphical tool to configure at and crontab"
SRC_URI="ftp://gaute.eu.org/pub/gnome-schedule/${P}.tar.bz2"
A="${P}.tar.bz2"
HOMEPAGE="http://gnome-schedule.sourceforge.net"
IUSE="+gnome +gtk"
S=${WORKDIR}/gnome-schedule
RDEPEND=">=sys-apps/at-3 >=sys-apps/vixie-cron-3 >=pygtk-2.3 >=python-2.3 >=gnome-python-2	>=gnome-common-2.4"
DEPEND="${RDEPEND}"

src_compile() {
  ewarn "This application was developed using the CVS version of pygtk since only that provided \
enough functions from gtk. You may have to download and install it."

  ./autogen.sh --prefix=/usr
  emake
}

src_install() {
  einfo "Installing.."
  einstall
}
