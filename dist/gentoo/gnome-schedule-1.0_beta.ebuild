P="gnome-schedule-1.0_beta"
PN="gnome-schedule"
PV="1.0"
SLOT="0"
LICENSE="GPL"
KEYWORDS="x86"
DESCRIPTION="A graphical tool for configuring at and crontab"
SRC_URI="ftp://gaute.eu.org/pub/gnome-schedule/${P}.tar.bz2"
A="${P}.tar.bz2"
HOMEPAGE="http://gnome-schedule.sourceforge.net"
IUSE="+gnome +gtk"
S=${WORKDIR}/gnome-schedule
RDEPEND=">=sys-apps/at-3 
		>=sys-apps/vixie-cron-3 
		>=pygtk-2.3 >=python-2.3 
		>=gnome-python-2	
		>=gnome-common-2.4"
DEPEND="${RDEPEND}"

src_compile() {
  ./autogen.sh --prefix=/usr
  emake
}

src_install() {
  einfo "Installing.."
  einstall

  ewarn "gnome-schedule was developed using the CVS version of PyGtk(2.4), this may cause problems on early versions of PyGtk-2.3"
  einfo "If you have previous records in at, gnome-schedule may have problems reading them. They are marked as DANGROUS PARSE in the list if a unsecure method was used. This will not damage the record, and if you open one pressing cancel in the script editor will not change anything."
}
