gnome-schedule
--------------

* See the file `COPYING` for the license.
* See the `AUTHORS` file for the authors of this tool
* See the `INSTALL` file for information about installing this tool
* Check out the `doc/` directory for user documentation

Dependencies
------------

 GNOME Schedule needs (at least):

* `at`
* `crontab`
* `Python`
* `PyGTK` >= 2.3
* `Python GConf`
* `su`

Support
-------

* Mailinglists: You can talk to the developers and some other users
     of `gnome-schedule` here:
     
  http://lists.sourceforge.net/mailman/listinfo/gnome-schedule-users

  There is also a development list here:
  
  http://lists.sourceforge.net/mailman/listinfo/gnome-schedule-devel

INSTALL from source:
-------------------------------------------------------------
* Because some people dislike the fact that manually compiled
  applications tamper with their distribution which is managed by the
  packaging system in use. We understand this and therefore made it
  possible to install the application outside of any default prefix.

* If you want to use the sources pulled from the subversion server you need `automake-1.7` and `gnome-common`.

* The following commands will install `gnome-schedule` on a system that has `Python` and `automake-1.7` and some tools like `gmake` installed.

```
 $ git clone https://gitlab.gnome.org/GNOME/gnome-schedule.git
 $ pushd gnome-schedule
 $ ./autogen.sh --prefix=/usr/local
 $ make
 $ make install
 # and to start gnome-schedule:

 $ /usr/local/bin/gnome-schedule

 # You can read the script to know how to start the Python-script
 # manually. If PyGTK is not installed in your default prefix,
 # you, in case you are planning not to use the script, would have
 # to set the PYTHONPATH environment variable first! The generated
 # script, however, will do all this for you (if you use the script).
```

Important notes
---------------
If you have previous records in `at`, `gnome-schedule` may have problems reading them and they are marked with `DANGEROUS PARSE` in the list if a unsecure method was used. There are no risk that the record will be lost or damaged unless you open it for editing and press apply, but we have tested many different setups and it should work fine.

Some comments right after existing records in `crontab` may return weird results for title and icon, normally this doesn't damage anything.


Compiling and HACKING
---------------------

  GNOME Schedule is written using the programming language Python
  and uses the PyGTK and Python-GConf bindings.

  You can talk to the developers of gnome-schedule about development
  related issues here:

* http://lists.sourceforge.net/mailman/listinfo/gnome-schedule-devel

  To compile GNOME Schedule from git you will also need

* A git client
* `autoconf` and the other `auto*` tools (version >= 1.7)
* `gnome-common` which you can pull from the git.gnome.org

  To run GNOME Schedule from the source directory

* Enter `src/`
* run `python gnome-schedule.py --debug`

	This will use images and datafiles from the current directory. Remember this is only for debugging and might not always work as expected.


## To make contributions you should first read
* `HACKING`
* `AUTHORS`
* The source code itself :-)

## To help with translations

* Check out the `po/` directory. You can use gTranslator and
	the other intl tools for translations. You should contact
	the GNOME Translation team as they are the responsible
	organisation for the translation of the GNOME desktop
* Check out the help/ directory for translations of the documentation
* Other than only the generated po-files you should also
	check out the file `src/lang.py`
