P="gnome-schedule-2.0.0_rc1"
PN="gnome-schedule"
PV="2.0.0_rc1"
SLOT="0"
LICENSE="GPL"
KEYWORDS="~x86"
DESCRIPTION="A graphical tool for configuring at and crontab"
# SRC_URI="mirror://sourceforce/gnome-schedule/gnome-schedule-0.9.0.tar.bz2"
SRC_URI="http://gaute.vetsj.com/arkiv/2007-12-13%20-%20gnome-schedule-2.0.0-rc1/gnome-schedule-2.0.0-rc1.tar.gz"
A="${P}.tar.gz"
HOMEPAGE="http://gnome-schedule.sourceforge.net"
IUSE="+gnome +gtk +X"
S=${WORKDIR}/gnome-schedule-2.0.0-rc1
RDEPEND="
	>=sys-process/at-3 
	>=sys-process/vixie-cron-3 
	>=dev-python/pygtk-2.4 
	>=dev-lang/python-2.4 
	>=dev-python/gnome-python-2	
	>=gnome-base/gnome-common-2.4"

DEPEND="${RDEPEND}"

src_compile() {
  econf
  emake
}

src_install() {
  einstall

  einfo "If you have any previous records in at or crontab, gnome-schedule may have problems reading them. They are marked as DANGROUS PARSE in the list if a unsecure method was used. This will not damage the record, and if you open one for editing pressing cancel in the script editor will leave everything as it was."
}
