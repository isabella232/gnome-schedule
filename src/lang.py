# -*- coding: UTF-8 -*-
import os
import gtk

# Dear translators,
# Most languages will not have to do all this, but some do.
# http://lists.gnome.org/archives/gnome-i18n/2004-June/msg00089.html

# To get numeric nth translation correct some languages need to get
# things like the gender and wording correct. The only way to do
# this is to code it. Often it can't be done using the po-files

# Therefor I am making it possible for those languages to code it, in
# this file.

# Read through the comments of the implementations for other languages
# and don't touch the implementations for English unless you know what
# you are doing.

# If you language can get correctly translated by using only the po files,
# it means that you don't have to touch these files at all.


##
## I18N
##
from rhpl.translate import _, N_
import rhpl.translate as translate
domain = 'gnome-schedule'
translate.textdomain (domain)
gtk.glade.bindtextdomain(domain)
language = os.environ['LANG']

# To get numeric nth values translated add an elif statement for your
# language here
def translate_nth (nth):
	if language.find ("nl") != -1:
		return translate_nth_nl (nth)
	#elif lang.find ("whatever") != -1:
	#	return translate_nth_whatever (nth)
	else:
		return translate_nth_en (nth)

# Create a function like this for your method below, you can checkout
# the implementation for dutch below: translate_nth_nl (nth)
# nth is a number (like 1, 2, 3). The function will return 'first'
# 'second' 'third', ...
def translate_nth_en (nth):
	try:
		nth = int(nth)
	except:
		return nth

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

# Dutch is pretty much the same as English, except that there are some
# special cases in spelling and that the ordering to form the word is
# a bit different. Dutch is also not using the 'nth' numeric to describe
# the (for example) 3 of 43, in stead it's using a normal written numeric.
# So I had to add a new table with the written version of tne numbers
def translate_nth_nl (nth):
	try:
		nth = int(nth)
	except:
		return nth

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
		# If the last character before the concatenation is a "e", we
		# dutch-people write that e a bit different. This "en" is a lot
		# like the "-" in English. It concatenates the tennumber with the
		# remainder.

		# Als het laatste karakter voor de middelste "en" een e is dan
		# moet er een trema op de e, anders niet. 
		if numbers[remainder][len(numbers[remainder])-1] == "e":
			between = "ën"
		else:
			between = "en"

		if nth < 0:
			add = "min "
		else:
			add = ""
		# Our ordering is also different, and we don't use the nth-number
		# to describe the remainder. We use a normal written version of the
		# number
		return add + numbers[remainder]+between+tennumbers [tennumber]+"ste"
	elif nth > 100 or nth < -100:
		return string(nth) + "de"

# Add your language here:
#def translate_nth_whatever (nth):
#	pass


# These are a bit more difficult and are only here for the languages that
# have to adjust gender and other specifics to the sentence when using
# nth numeric values in sentences. If it's not needed for your language
# (for example, it's not needed for dutch), then don't change anything and
# do your translation in the po-files only.

# This translates a hour, minute and seconds to a digital-clock-display
# hour. As far as I know is the format internationally standarized.
# Still I am making it possible to translate this using both po-files and
# by defining your own version of it.
def timeval (hour, minute, seconds = None):
	#if language.find ("whatever") != -1:
	#	return timeval_whatever (hour, minute, seconds)
	#else:
	return timeval_en (hour, minute, seconds)

# So this is the English version. It will return "hh:mm:ss". As you can
# see I have added an empty translatable string at the beginning and end
# of what will be returned. You can use that in your language to append
# or prepend something. If the gender of words in your sentences change
# cause of or nth numeric written values or these date values, use the
# functions below to create a version for your language.
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

# So this is for the really really hard languages that have changing
# genders and word-ordering depending on the nth-numeric value.
# You can copy-and-paste the whole block and start adjusting it for your
# language. If you need assistance, read the AUTHORS file and try to
# contact us or use the mailinglists.

def translate_crontab_easy (minute, hour, day, month, weekday):
	#if language.find ("whatever") != -1:
	#	return translate_crontab_easy_whatever (minute, hour, day, month, weekday)
	#else:
	return translate_crontab_easy_en (minute, hour, day, month, weekday)

def translate_crontab_easy_en (minute, hour, day, month, weekday):
	# * means "every"
	# x-y means happens every instance between x and y (not yet supported correctly)
	# x means happens at
	# *\x means happens every xth (not yet supported correctly)
	# 1,2,3,4 means happens the 1st, 2e, 3th and 4th
	if minute.find ("\\") != -1 or hour.find ("\\") != -1 or day.find ("\\") != -1 or month.find ("\\") != -1 or weekday.find ("\\") != -1:
		return minute + " " + hour + " " + day + " " + month + " " + weekday

	if minute.find ("-") != -1 or hour.find ("-") != -1 or day.find ("-") != -1 or month.find ("-") != -1 or weekday.find ("-") != -1:
		return minute + " " + hour + " " + day + " " + month + " " + weekday

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
		elif minute == "*" and hour != "*" and day != "*":
			return (_("At the %s day every % hour every %s month of the year") % (translate_nth (day), translate_nth (hour), translate_nth (month)))
		elif minute != "*" and hour == "*" and day == "*":
			return (_("Every day and every hour at the %s minute every %s month of the year") % (translate_nth (minute), translate_nth (month)))
		elif minute != "*" and hour != "*" and day == "*":
			return (_("Every day on %s every %s month of the year") % (timeval (hour, minute), translate_nth (month)))


	if month == "*" and day == "*" and weekday != "*":
		if minute == "0" and hour == "0":
			return (_("Every %s day of the week") % (translate_nth (weekday)))
		elif minute != "*" and hour != "*":
			return (_("Every %s day of the week at %s") % (translate_nth (weekday), timeval  (hour, minute)))
		# All other cases are strange, why define a day of the month if you are already defining the day of the week? :)
		# They are possible, yes, but I don't think that translations for such stuff is needed ...

	return minute + " " + hour + " " + day + " " + month + " " + weekday
