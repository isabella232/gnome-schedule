#! /bin/bash
# Copyright (C) 2010  Gaute Hope <eg at gaute dot vetsj dot com>
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

# Checks if a task has been run since midnight; otherwise run it
# and update timestamp.

# State is saved in ~/.surerun; use at own risk and modify for your use.

# usage: ./surerun.sh title command *args

if [ $# -lt 2 ]; then
  echo "Not enough arguments given"
  exit 1
fi

title=$1
shift
command=$@

statedir=~/.surerun

midnight=$(date -d "00:00" +%s)

if [ -e "${statedir}/${title}" ]; then
  # exists, check last run
  lastrun=$(cat "${statedir}/${title}")
  echo "Last run: ${lastrun}"
else
  lastrun=0
fi

if [ "${lastrun}" -le "${midnight}" ]; then
  if [ ! -d "${statedir}" ]; then
    mkdir -p "${statedir}"
  fi
  date +%s > "${statedir}/${title}"

  # run task
  echo "Running: ${title}.."
  $@
fi


