#! /bin/sh

# packtranslations.sh: Used to pack a tarball with translations for Launchpad
#
# Copyright (C) 2007 - 2008 Gaute Hope <eg at gaute dot vetsj dot com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Library General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

tar=/bin/tar

echo -e "pactranslations.sh: Simple script to pack the translation files in a tar archive for use on launchpad. Should be used from the po/ sub-directory."
echo "Copyright (c) 2007, 2008 Gaute Hope <eg@gaute.vetsj.com>"

if [ "$1" ]
then
	if [ "$1" = "pack" ]
	then
		echo "Packing.."
		rm -f gnome-schedule.l10n.tar.gz
		make Makefile gnome-schedule.pot > update_log 2>&1
		$tar cvzf gnome-schedule.l10n.tar.gz *.po *.pot >> update_log 2>&1
		echo "Done, there is a log in ./update_log"
	elif [ $1 = "clean" ]
	then
		echo -n "Cleaning.."
		rm gnome-schedule.l10n.tar.gz
		rm update_log
		echo "done"
	else 	
		echo "Usage: ./packtranslations.sh [ pack | clean ]"
		echo -e "Remember to run the configure script before this one, otherwise some files will be missing.\n"		
	fi
else
	echo "Usage: ./packtranslations.sh [ pack | clean ]"
	echo -e "Remember to run the configure script before this one, otherwise some files will be missing.\n"
fi

