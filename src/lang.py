# -*- coding: UTF-8 -*-
import os
import gtk
##
## I18N
##
from rhpl.translate import _, N_
import rhpl.translate as translate
domain = 'gnome-schedule'
translate.textdomain (domain)
gtk.glade.bindtextdomain(domain)

def translate_nth (nth):
	lang = os.environ['LANG']
	if lang.find ("nl") != -1:
		return translate_nth_nl (nth)
	#elif lang.find ("whatever") != -1:
	#	return translate_nth_whatever (nth)
	else:
		return translate_nth_en (nth)

def translate_nth_en (nth):
	nth = int(nth)
	twenty_nths = [ _("zeroth"),
					_("first"), _("second"), _("third"), _("fourth"), _("fifth"), 
					_("sixth"), _("seventh"), _("eighth"), _("ninth"), _("tenth"),
					_("eleventh"), _("twelfth"), _("thirteenth"), _("fourteenth"), _("fifteenth"),
					_("sixteenth"), _("seventeenth"), _("eighteenth"), _("nineteenth"), _("twentieth")
				]

	tennumbers = [ _("zero"), _("ten"), _("twenty"), _("thirty"), _("fourthy"), _("fifthy"), _("sixty"), _("seventy"), _("eighty"), _("ninety") ]

	print nth
	if nth <= 20 >= 0:
		return twenty_nths[nth]
	elif nth < 0 and nth >= -20:
		return "minus " + twenty_nths[nth]
	elif nth > -100 and nth < -20:
		tennumber = nth / 10
		rest = nth - (tennumber*10)
		return "minus " + tennumbers [tennumber] + " " + twenty_nths[rest]
	elif nth > 20 and nth < 100:
		tennumber = nth / 10
		rest = nth - (tennumber*10)
		return tennumbers [tennumber] + " " + twenty_nths[rest]
	elif nth > 100 or nth < -100:
		return string(nth) + "th."

def translate_nth_nl (nth):
	nth = int(nth)
	numbers = [ "één", "twee", "drie", "vier", "vijf", "zes", "zeven", "acht", "negen" ]
	twenty_nths = [ "nulde",
					"eerste", "tweede", "derde", "vierde", "vijfde", 
					"zesde", "zevende", "achste", "negende", "tiende",
					"elfde", "twaalfde", "dertiende", "veertiende", "vijftiende",
					"sestiende", "zeventiende", "achtiende", "negentiende", "twintigste"
				]

	tennumbers = [ "nul", "tien", "twintig", "dertig", "veertig", "vijftig", "zestig", "zeventig", "tachtig", "negentig" ]

	print nth
	if nth <= 20 >= 0:
		return twenty_nths[nth]
	elif nth < 0 and nth >= -20:
		return "min " + twenty_nths[nth]
	elif nth > -100 and nth < -20:
		tennumber = nth / 10
		rest = nth - (tennumber*10)
		return "min " + numbers[rest]+"en"+tennumbers [tennumber]+"ste"
	elif nth > 20 and nth < 100:
		tennumber = nth / 10
		rest = nth - (tennumber*10)
		return numbers[rest]+"en"+tennumbers [tennumber]+"ste"
	elif nth > 100 or nth < -100:
		return string(nth) + "ste"

#def translate_nth_whatever (nth):
#	pass
