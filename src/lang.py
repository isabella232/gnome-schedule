# -*- coding: UTF-8 -*-
# Don't touch the first line :-) unless you know why and you need to touch
# it for your language. Also if you changed the formatting using your
# editor (and tested everything, haha)

#pygtk modules
import gtk

#python modules
import os

# Dear translators,

# This file is yours. YOU people do whatever you wan't with it. You can
# fix spelling problems, add comments, add code and functionality. You
# don't have to inform me about changes (you can commit if you have such
# an account on GNOME) yet you CAN ask the programmers for assistance.

# Yes yours. Really

# No seriously, it's yours. Yeah, yours. It's your file. You do whatever
# you want with this file. I mean it. Yes...

# If you don't have access you can create a diff file and send it to the
# AUTHORS: cd src/; cvs diff -u lang.py > language.diff  and we will
# weed it out for you. We will provide you with the best assistance
# possible.

# WHY, WHY THE HELL WHY??? WHHHAAAYYYY??????!!!!!!
# ------------------------------------------------

# Most languages will not have to do all this, but some do.
# http://lists.gnome.org/archives/gnome-i18n/2004-June/msg00089.html

# To get numeric nth translations correct, some languages need to get
# things like the gender and wording correct. The only way to do
# this is to code it.

# Therefor I am making it possible for those languages to code it, in
# this file.

# Read through the comments of the implementations of other languages
# and don't touch the implementation for English unless you know what
# you are doing.

# If your language 'can' get correctly translated by using only the po
# files, it means that you don't have to touch these files at all. In
# that case the advice is simple: don't touch it. hehe :)

##
## I18N
##
import gettext
domain = 'gnome-schedule'
gettext.bindtextdomain(domain)
gettext.textdomain(domain)
_ = gettext.gettext


#fallback to english if the LANG env variable is not present
try:
	language = os.environ['LANG']
except:
	language = "en"


def nothing (nothing):
	pass
nothing (_("To the translator: Read src/lang.py !!! (yeah it's for you, not for the user. YES FOR YOU, the translator. YES:) really!"))


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

	tennumbers = [ _("zero"), _("ten"), _("twenty"), _("thirty"), _("forty"), _("fifty"), _("sixty"), _("seventy"), _("eighty"), _("ninety") ]

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
# So I had to add a new table with the written version of tne numbers.
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
		# dutch-people write that "e" a bit different. This "en" is a lot
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
		# to describe the remainder. We use a normal written version of
		# the number.
		return add + numbers[remainder]+between+tennumbers [tennumber]+"ste"
	elif nth > 100 or nth < -100:
		return string(nth) + "de"

# Add your language here:
#def translate_nth_whatever (nth):
#	pass


# These are a bit more difficult and are only here for the languages
# that have to adjust gender and other specifics to the sentence when
# using nth numeric values in sentences. If it's not needed for your
# language (for example, it's not needed for dutch), then don't change
# anything and do your translation in the po-files only.

# This translates a hour, minute and seconds to a digital-clock-display.
# As far as I know is the format internationally standarized.
# Still I am making it possible to translate this using both po-files
# and by defining your own version of it.
def timeval (hour, minute, seconds = None):
	#if language.find ("whatever") != -1:
	#	return timeval_whatever (hour, minute, seconds)
	#else:
	return timeval_en (hour, minute, seconds)

# So this is the English version. It will return "hh:mm:ss". As you can
# see I have added an empty translatable string at the beginning and end
# of what will be returned. You can use that in your language po-file to
# append or prepend something. If the gender of words in your sentences
# changes cause of or nth numeric written values or these date values,
# use the functions below to create a version for your language.
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
	
	# Add support for your language here
	
	if language.find ("en") != -1 or language == "C" or language.find ("us"):
		return translate_crontab_easy_en (minute, hour, day, month, weekday)
	elif language.find ("nl") != -1:
		return translate_crontab_easy_nl (minute, hour, day, month, weekday)
	else:
		return translate_crontab_easy_anylang (minute, hour, day, month, weekday)

def translate_crontab_easy_en (minute, hour, day, month, weekday):
	# * means "every"
	# x-y means happens every instance between x and y (not yet supported correctly)
	# x means happens at
	# *\x means happens every xth (not yet supported correctly)
	# 1,2,3,4 means happens the 1st, 2e, 3th and 4th
	
	# These are the two unsupported cases
	if minute.find ("\\") != -1 or hour.find ("\\") != -1 or day.find ("\\") != -1 or month.find ("\\") != -1 or weekday.find ("\\") != -1:
		return translate_crontab_easy_anylang (minute, hour, day, month, weekday)
	if minute.find ("-") != -1 or hour.find ("-") != -1 or day.find ("-") != -1 or month.find ("-") != -1 or weekday.find ("-") != -1:
		return translate_crontab_easy_anylang (minute, hour, day, month, weekday)
	if minute.find (",") != -1 or hour.find (",") != -1 or day.find (",") != -1 or month.find (",") != -1 or weekday.find (",") != -1:
		return translate_crontab_easy_anylang (minute, hour, day, month, weekday)
		
	# So if our case is supported:

	# If all are asterix, it means every minute :)
	if minute == "*" and hour == "*" and month == "*" and day == "*" and weekday == "*":
		return _("Every minute")

	# If only minute is filled in
	if minute != "*" and hour == "*" and month == "*" and day == "*" and weekday == "*":
		if minute == "0":
			return _("Every hour")
		else:
			return (_("Every %s minute of every hour") % (translate_nth (minute)))

	# Minute and hour cases
	if hour != "*" and month == "*" and day == "*" and weekday == "*":
		if minute == "0":
			return (_("Every %s hour of the day") % (translate_nth (hour)))
		elif minute != "*":
			return (_("Every day at %s") % (timeval (hour, minute)))
		elif minute == "*":
			return (_("Every minute during the %s hour") % (translate_nth (hour)))

	# Day, minute and hour cases
	if month == "*" and day != "*" and weekday == "*":
		if minute == "0" and hour == "0":
			return (_("Every %s day of the month") % (translate_nth (day)))
		elif minute != "*" and hour != "*":
			return (_("At %s every %s day of the month") % (timeval (hour, minute), translate_nth (day)))
		elif minute == "*" and hour != "*":
			return (_("Every minute of the %s hour every %s day of the month") % (translate_nth (hour), translate_nth (day)))
		elif minute != "*" and hour == "*":
			return (_("At the %s minute of every hour every %s day of the month") % (translate_nth (minute), translate_nth (day)))

	# Day, minute, hour and month cases
	if month != "*" and weekday == "*":
		if minute == "0" and hour == "0" and day == "1":
			return (_("Every %s month of the year") % (translate_nth (month)))
		elif minute != "*" and hour != "*" and day != "*":
			return (_("At the %s day on %s every %s month of the year") % (translate_nth (day), timeval (hour, minute), translate_nth (month)))
		elif minute == "*" and hour != "*" and day != "*":
			return (_("At the %s day every %s hour every %s month of the year") % (translate_nth (day), translate_nth (hour), translate_nth (month)))
		elif minute != "*" and hour == "*" and day == "*":
			return (_("Every day and every hour at the %s minute every %s month of the year") % (translate_nth (minute), translate_nth (month)))
		elif minute != "*" and hour != "*" and day == "*":
			return (_("Every day on %s every %s month of the year") % (timeval (hour, minute), translate_nth (month)))


	# Weekday cases
	if month == "*" and day == "*" and weekday != "*":
		if minute == "0" and hour == "0":
			return (_("Every %s day of the week") % (translate_nth (weekday)))
		elif minute != "*" and hour != "*":
			return (_("Every %s day of the week at %s") % (translate_nth (weekday), timeval  (hour, minute)))
		elif minute == "*" and hour != "*":
			return (_("Every %s day of the week the %s hour") % (translate_nth (weekday), translate_nth (hour)))
		elif minute != "*" and hour == "*":
			return (_("Every %s day of the week the %s minute of every hour") % (translate_nth (weekday), translate_nth (minute)))
		elif minute == "*" and hour == "*":
			return (_("Every %s day of the week every minute") % (translate_nth (weekday)))

	# If nothing got translated, we fall back to ...
	return translate_crontab_easy_anylang (minute, hour, day, month, weekday)

# It's in English but it's not used in the application if English is the
# language. This is for the non-supported languages. It should make it perfectly
# possible to translate these using po-files only. If not, feel free to
# modify the strings.
def translate_crontab_easy_anylang (minute, hour, day, month, weekday):
	retval = minute + " " + hour + " " + day + " " + month + " " + weekday

	if minute == "*" and hour == "*" and day == "*" and month == "*" and weekday == "*":
		retval = (_("Every minute, every hour, every day, every month, every weekday"))

	if minute != "*" and hour != "*" and day != "*" and month != "*" and weekday != "*":
		retval = (_("At minute: %s, hour %s, day: %s, month: %s, weekday: %s") % (minute, hour, day, month, weekday))

	if minute != "*" and hour != "*" and day != "*" and month != "*" and weekday == "*":
		retval = (_("At minute: %s, hour %s, day: %s, month: %s") % (minute, hour, day, month))
		
	if minute != "*" and hour != "*" and day != "*" and month == "*" and weekday == "*":
		retval = (_("At minute: %s, hour %s, day: %s, every month") % (minute, hour, day))
	if minute != "*" and hour != "*" and day == "*" and month != "*" and weekday == "*":
		retval = (_("At minute: %s, hour %s, every day, month: %s") % (minute, hour, month))
	if minute != "*" and hour == "*" and day != "*" and month != "*" and weekday == "*":
		retval = (_("At minute: %s, every hour, day: %s, month: %s") % (minute, day, month))
		
	if minute != "*" and hour != "*" and day == "*" and month == "*" and weekday == "*":
		retval = (_("At minute: %s, hour %s, every day, every month") % (minute, hour))
	if minute != "*" and hour == "*" and day != "*" and month == "*" and weekday == "*":
		retval = (_("At minute: %s, every hour, day: %s, every month") % (minute, day))
	if minute != "*" and hour == "*" and day == "*" and month != "*" and weekday == "*":
		retval = (_("At minute: %s, every hour, every day, month: %s") % (minute, month))
	if minute != "*" and hour == "*" and day == "*" and month == "*" and weekday == "*":
		retval = (_("At minute: %s, every hour, every day, every month") % (minute))
	
	if hour != "*" and minute == "*" and day != "*" and month == "*" and weekday == "*":
		retval = (_("Every minute, hour: %s, day: %s, month %s") % (hour, day, month))
	if hour != "*" and minute == "*" and day != "*" and month == "*" and weekday == "*":
		retval = (_("Every minute, hour %s, day: %s, every month") % (hour, day))
	if hour != "*" and minute == "*" and day == "*" and month != "*" and weekday == "*":
		retval = (_("Every minute, hour %s, every day, month: %s") % (hour, month))		
	if hour != "*" and minute == "*" and day == "*" and month == "*" and weekday == "*":
		retval = (_("Every minute, hour %s, every day, every month") % (hour))

	if day != "*" and minute == "*" and hour == "*" and month != "*" and weekday == "*":
		retval = (_("Every minute, every hour, day: %s, month: %s") % (day, month))
	if day != "*" and minute == "*" and hour == "*" and month == "*" and weekday == "*":
		retval = (_("Every minute, every hour, day: %s, every month") % (day))


	# TODO: Add more combinations
	
	return retval
