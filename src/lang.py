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
language = os.environ['LANG']

def translate_nth (nth):
	if language.find ("nl") != -1:
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


def translate_crontab_easy (minute, hour, day, month, weekday):
	#if language.find ("whatever") != -1:
	#	return translate_crontab_easy_whatever (minute, hour, day, month, weekday)
	#else:
	return translate_crontab_easy_en (minute, hour, day, month, weekday)

def timeval (hour, minute, seconds = None):
	#if language.find ("whatever") != -1:
	#	return timeval_whatever (hour, minute, seconds)
	#else:
	return timeval_en (hour, minute, seconds)

def timeval_en (hour, minute, seconds):
	if int (minute) < 10:
		minute = "0" + minute
	if int (hour) < 10:
		hour = "0" + hour
	if seconds != None:
		if int (seconds) < 10:
			seconds = "0" + seconds
		return (_("%s%s:%s:%s%s") % (_(""), hour, minute, seconds, _("")))
	else:
		return (_("%s%s:%s%s") % (_(""), hour, minute, _("")))

def translate_crontab_easy_en (minute, hour, day, month, weekday):
	# * means "every"
	# x-y means happens every instance between x and y
	# x means happens at
	# */x means happens every xth 
	# 1,2,3,4 means happens the 1st, 2e, 3th and 4th
	if minute == "*" and hour == "*" and month == "*" and day == "*" and weekday == "*":
		return _("Every minute")

	if minute != "*" and hour == "*" and month == "*" and day == "*" and weekday == "*":
		return (_("Every %s minute of every hour") % (translate_nth (minute)))

	if hour != "*" and month == "*" and day == "*" and weekday == "*":
		if minute == "0":
			return (_("Every %s hour of the day") % (translate_nth (hour)))
		elif minute != "*":
			return (_("Every day at %s") % (timeval (hour, minute)))
		elif minute == "*":
			return (_("Every minute during the %s hour") % (translate_nth (hour)))
	
	if month == "*" and day != "*" and weekday == "*":
		if minute == "0" and hour == "0":
			return (_("Every %s day of the month") % (translate_nth (day)))
		elif minute != "*" and hour != "*":
			return (_("At %s every %s day of the month") % (timeval (hour, minute), translate_nth (day)))
		elif minute == "*" and hour != "*":
			return (_("Every minute of the %s hour every %s day of the month") % (translate_nth (hour), translate_nth (day)))
		elif minute != "*" and hour == "*":
			return (_("At the %s minute of every hour every %s day of the month") % (translate_nth (minute), translate_nth (day)))

	if month != "*" and weekday == "*":
		if minute == "0" and hour == "0" and day == "1":
			return (_("Every %s month of the year") % (translate_nth (month)))
		elif minute != "*" and hour != "*" and day != "*":
			return (_("At the %s day on %s every %s month of the year") % (translate_nth (day), timeval (hour, minute), translate_nth (month)))


	if month == "*" and day == "*" and weekday != "*":
		if minute == "0" and hour == "0":
			return (_("Every %s day of the week") % (translate_nth (weekday)))
		elif minute != "*" and hour != "*":
			return (_("Every %s day of the week at %s") % (translate_nth (weekday), timeval  (hour, minute)))

	return minute + " " + hour + " " + day + " " + month + " " + weekday
