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

	# If between 0 and 20 (this means that we already have it in a table)
	if nth <= 20 >= 0:
		return twenty_nths[nth]
	# Same as above but negative
	elif nth < 0 and nth >= -20:
		return (_("minus %s") % (twenty_nths[nth]))
	# If between -100 and -20 or between 20 and 100
	elif (nth > -100 and nth < -20) or (nth > 20 and nth < 100):
		# Divide by ten to get the "2" out of the "23"
		tennumber = nth / 10
		# To get the three just multiply the division result with 10
		# and subtract that value with the original value
		remainder = nth - (tennumber*10)
		# If the number is negative, add a minus
		if nth < 0:
			add = _("minus ")
		else:
			add = _("")
		# These are just some table-lookups and translation magic :)
		return (_("%s%s%s%s%s%s") % (_(""), add, tennumbers [tennumber], _("-"), twenty_nths[remainder], _("")))
	# Any other case (in this application this should never happen)
	elif nth > 100 or nth < -100:
		return (_("%sth.") % (string(nth)))

def translate_nth_nl (nth):
	nth = int(nth)

	numbers = [ "nul", "één", "twee", "drie", "vier", "vijf", "zes", "zeven", "acht", "negen" ]

	twenty_nths = [ "nulde",
					"eerste", "tweede", "derde", "vierde", "vijfde", 
					"zesde", "zevende", "achste", "negende", "tiende",
					"elfde", "twaalfde", "dertiende", "veertiende", "vijftiende",
					"sestiende", "zeventiende", "achtiende", "negentiende", "twintigste"
				]

	tennumbers = [ "nul", "tien", "twintig", "dertig", "veertig", "vijftig", "zestig", "zeventig", "tachtig", "negentig" ]

	if nth <= 20 >= 0:
		return twenty_nths[nth]
	elif nth < 0 and nth >= -20:
		return "min " + twenty_nths[nth]
	elif (nth > -100 and nth < -20) or (nth > 20 and nth < 100):
		tennumber = nth / 10
		remainder = nth - (tennumber*10)

		# Als het laatste karakter voor de middelste "en" een e is dan
		# moet er een trema op de e, anders niet
		if numbers[remainder][len(numbers[remainder])-1] == "e":
			between = "ën"
		else:
			between = "en"

		if nth < 0:
			add = "min "
		else:
			add = ""
		return add + numbers[remainder]+between+tennumbers [tennumber]+"ste"
	elif nth > 100 or nth < -100:
		return string(nth) + "de"

#def translate_nth_whatever (nth):
#	pass
