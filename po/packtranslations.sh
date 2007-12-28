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
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02110-1301, USA.

tar=/bin/tar

if [ "$1" ]
then
	if [ "$1" = "pack" ]
	then
		echo "Packing.."
		rm gnome-schedule.l10n.tar.gz
		$tar cvzf gnome-schedule.l10n.tar.gz *.po *.pot
		echo "Done"
	elif [ $1 = "clean" ]
	then
		echo -n "Cleaning.."
		rm gnome-schedule.l10n.tar.gz
		echo "done"
	fi
else
	echo -e "pactranslations.sh: Simple script to pack the translation files in a tar archive for use on launchpad\n"
	echo "Usage: ./packtranslations.sh [ pack | clean ]"
	echo "Copyright (c) 2007, 2008 Gaute Hope <eg@gaute.vetsj.com>"
fi

