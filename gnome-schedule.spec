Summary: Crontab server and at configuration tool
Name: gnome-schedule
Version: 0.7.0_Beta
Release: 1
URL: http://gaute.eu.org/stasj/cronconf
License: GPL
ExclusiveOS: Linux
Group: System Environment/Base
BuildRoot: %{_tmppath}/%{name}-%{version}-root
BuildArch: noarch
Source0: %{name}-%{version}.tar.bz2
BuildRequires: desktop-file-utils
BuildRequires: gettext
Obsoletes: redhat-config-schedule
Requires: pygtk2
Requires: pygtk2-libglade
Requires: python
Requires: usermode >= 1.36
Requires: crontab
Requires: libuser
Requires: htmlview

%description
gnome-schedule is a graphical user interface for creating, 
modifying, and deleting crontab and at records.

%prep
%setup -q

%build
make

%install
make INSTROOT=$RPM_BUILD_ROOT install

desktop-file-install --vendor system --delete-original       \
  --dir $RPM_BUILD_ROOT%{_datadir}/applications             \
  --add-category X-Red-Hat-Base       \
  --add-category X-Red-Hat-ServerConfig       \
  $RPM_BUILD_ROOT%{_datadir}/applications/gnome-schedule.desktop

%find_lang %name

%clean
rm -rf $RPM_BUILD_ROOT

%preun
if [ -d /usr/share/gnome-schedule ] ; then
  rm -rf /usr/share/gnome-schedule/*.pyc
fi

%files -f %{name}.lang
%defattr(-,root,root)
#%doc COPYING
%doc doc/*
/usr/bin/gnome-schedule
%dir /usr/share/gnome-schedule
/usr/share/gnome-schedule/*
%attr(0644,root,root) %{_datadir}/applications/gnome-schedule.desktop
%attr(0644,root,root) %{_datadir}/icons/hicolor/48x48/apps/gnome-schedule.png
%attr(0644,root,root) %config /etc/security/console.apps/gnome-schedule
%attr(0644,root,root) %config /etc/pam.d/gnome-schedule

%changelog
* Tue Jun 1 2004 Philip Van Hoof <spam at freax dot org>
- packaging

* Tue Jun 1 2004 Gaute Hope <eg at gaute dot eu dot org>
- Initial coding

