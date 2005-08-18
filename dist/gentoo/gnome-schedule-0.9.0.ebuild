P="gnome-schedule-0.9.0"
PN="gnome-schedule"
PV="0.9.0"
SLOT="0"
LICENSE="GPL"
KEYWORDS="~x86"
DESCRIPTION="A graphical tool for configuring at and crontab"
SRC_URI="mirror://sourceforce/gnome-schedule/gnome-schedule-0.9.0.tar.bz2"
A="${P}.tar.bz2"
HOMEPAGE="http://gnome-schedule.sourceforge.net"
IUSE="+gnome +gtk +X"
S=${WORKDIR}/gnome-schedule
RDEPEND="
	>=sys-apps/at-3 
	>=sys-apps/vixie-cron-3 
	>=pygtk-2.4 
	>=python-2.4 
	>=gnome-python-2	
	>=gnome-common-2.4"

DEPEND="${RDEPEND}"

src_compile() {
  econf
  emake
}

src_install() {
  einstall

  ewarn "gnome-schedule was developed using the CVS version of PyGtk(2.4), this may cause problems on early versions of PyGtk-2.3"
  einfo "If you have previous records in at, gnome-schedule may have problems reading them. They are marked as DANGROUS PARSE in the list if a unsecure method was used. This will not damage the record, and if you open one for editing pressing cancel in the script editor will leave everything as it was."
}
