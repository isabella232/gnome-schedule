# -*- coding: UTF-8 -*-
# Don't touch the first line :-) unless you know why and you need to touch
# it for your language. Also if you changed the formatting using your
# editor (and tested everything, haha)

# python modules
import time
import warnings
warnings.filterwarnings("once", "Locale not supported by Python. Using the fallback 'C' locale.")

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
import locale
import gettext
domain = 'gnome-schedule'
gettext.bindtextdomain(domain)
gettext.textdomain(domain)
_ = gettext.gettext

# Fallback to english if locale setting is unknown
# or translation for this locale is not available
if gettext.find(domain) == None:
	language = "C"
else:
	language = ""
try:
	locale.setlocale(locale.LC_ALL, language)
except:
	warnings.warn_explicit("Locale not supported by Python. Using the fallback 'C' locale.", Warning, "localize.py", "32")

encoding = locale.getpreferredencoding(False)
language = locale.getlocale()[0]
if language == None:
	language = "C"

def nothing (nothing):
	pass
nothing (_("To the translator: Read src/lang.py !!! (yeah it's for you, not for the user. YES FOR YOU, the translator. YES:) really!"))

# Some locale stuff in this section to get 
# translated time expressions out of system. 
# Don't touch this. Change settings through gettext (po files) 
def lc_weekday (weekday):
	weekday = int(weekday)
	if weekday >= 0 and weekday < 7:
		weekday = str(weekday)
	else: 
		weekday = "0"
	timevalue = time.strptime(weekday, "%w")
	expression = time.strftime("%A", timevalue)
	return unicode(expression, encoding, 'ignore')

def lc_month (month):
	month = "%02d" % int(month)
	timevalue = time.strptime(month, "%m")
	expression = time.strftime("%B", timevalue)
	return unicode(expression, encoding, 'ignore')

def lc_date (day,month,year = None):
	day = "%02d" % int(day)
	month = "%02d" % int(month)
	if year == None:
		timevalue = time.strptime(("%s.%s" % (day, month)), "%d.%m")
		# Translators: Date format for expressions like "January 21"
		expression = time.strftime(_("%B %d"), timevalue)
	else:
		year = str(year)[-2:]
		year = "%02d" % int(year)
		timevalue = time.strptime(("%s.%s.%s" % (day, month, year)), "%d.%m.%y")
		# Translators: Date format for expressions like "January 21, 2005"
		expression = time.strftime(_("%B %d, %Y"), timevalue)
	return unicode(expression, encoding, 'ignore')

def lc_time (hour,minute,second = None):
	hour = "%02d" % int(hour)
	minute = "%02d" % int(minute)
	if second == None:
		timevalue = time.strptime(("%s:%s" % (hour, minute)), "%H:%M")
		# Translators: Time format without seconds
		expression = time.strftime(_("%H:%M"), timevalue)
	else:
		second = "%02d" % int(second)
		timevalue = time.strptime(("%s:%s:%s" % (hour, minute, second)), "%H:%M:%S")
		expression = time.strftime("%X", timevalue)
	return unicode(expression, encoding, 'ignore')


# To get numeric nth values translated add an elif statement for your language here
def lc_nth (nth):
	try:
		nth = int(nth)
	except:
		return nth

	if language == "C" or language.find("en") != -1:
		return lc_nth_en (nth)
	elif language.find ("nl") != -1:
		return lc_nth_nl (nth)
	elif language.find ("de") != -1:
		return lc_nth_de (nth)
	#elif lang.find ("whatever") != -1:
	#	return translate_nth_whatever (nth)
	else:
		return lc_nth_common (nth)

# Create a function like this for your method below, you can checkout
# the implementation for dutch and german below
# nth is a number (like 1, 2, 3). The function will return 
# an ordinal number like 'first' 'second' 'third', ... 
# or numerical expressions like '12th' '31st' '59th' ... 
def lc_nth_en (nth):
	ordnumbers = { 
		1: "first", 2: "second", 3: "third", 4: "fourth", 5: "fifth",
		6: "sixth", 7: "seventh", 8: "eighth", 9: "ninth", 10: "tenth" }

	ordappendix = { 1: "st", 2: "nd", 3: "rd" }

	if nth >= 1 and nth <= 10:
		return ordnumbers[nth]
	elif nth <= -1 and nth >= -10:
		nth = -nth
		return "minus %s" % (ordnumbers[nth])
	else:
		lastone = int(str(nth)[-1:])
		lasttwo = int(str(nth)[-2:])
		if lastone in range(1,4) and lasttwo not in range(11,14):
			return str(nth) + ordappendix[lastone]
		else:
			return str(nth) + "th"

# Dutch is a mix between German and English. They use appendixes like
# in English but the construction of words is germanic.
# Example for germanic way: 
# 124 would be constructed to "one hundred - four - and - twenty"
def lc_nth_nl (nth):
	ordnumbers = {
		1: "eerste", 2: "tweede", 3: "derde", 4: "vierde", 
		5: "vijfde", 6: "zesde", 7: "zevende", 8: "achste", 
		9: "negende", 10: "tiende", 11: "elfde", 12: "twaalfde" }

	if nth >= 1 and nth <= 12:
		return ordnumbers[nth]
	elif nth <= -1 and nth >= -12:
		nth = -nth
		return "min %s" % ordnumbers[nth]
	elif nth == 0:
		return "0de"
	else:
		lasttwo = int(str(nth)[-2:])
		if lasttwo in range(2,8) or lasttwo in range(9,20):
			return str(nth) + "de"
		else:
			return str(nth) + "ste" 		

# German is a little bit easier because they don't use 
# appendixes for numeric expressions. But endings of written
# ordinals can change. So you have to take care about forming
# the gettext messages (de.po) the correct way
def lc_nth_de (nth):
	ordnumbers = { 
		1: "ersten", 2: "zweiten", 3: "dritten", 4: "vierten", 
		5: "fünften", 6: "sechsten", 7: "siebenten", 8: "achten", 
		9: "neunten", 10: "zehnten", 11: "elften", 12: "zwölften" }

	if nth >= 1 and nth <= 12:
		return ordnumbers[nth]
	elif nth <= -1 and nth >= -12:
		nth = -nth
		return "minus %s" % ordnumbers[nth]
	else: 
		return str(nth) + "."

# This is the common way. It will return only numeric
# ordinals. The format for this can be changed through
# gettext (po files). Don't touch it.
def lc_nth_common (nth):
	# Translators: Format of numeric ordinal numbers. If this is not applicable for you read lang.py.
	return _("%d.") % nth


# So this is for the really really hard languages that have changing
# genders and word-ordering depending on the nth-numeric value.
# You can copy-and-paste the whole block and start adjusting it for your
# language. If you need assistance, read the AUTHORS file and try to
# contact us or use the mailinglists.
def translate_crontab_easy (minute, hour, day, month, weekday):
#	Add support for your language here
#	if language.find ("whatever") != -1:
#		return translate_crontab_easy_whatever (minute, hour, day, month, weekday)
#	else:	
		return translate_crontab_easy_common (minute, hour, day, month, weekday)

# Translate Crontab expressions to human readable ones.
# Don't touch this function. Copy and modify it to create a special translation.
# Changes on this function affects all translations made through po files.  
def translate_crontab_easy_common (minute, hour, day, month, weekday):
	# These are unsupported cases
	if minute.find ("/") != -1 or hour.find ("/") != -1 or day.find ("/") != -1 or month.find ("/") != -1 or weekday.find ("/") != -1:
		return translate_crontab_easy_fallback (minute, hour, day, month, weekday)
	if minute.find ("-") != -1 or hour.find ("-") != -1 or day.find ("-") != -1 or month.find ("-") != -1 or weekday.find ("-") != -1:
		return translate_crontab_easy_fallback (minute, hour, day, month, weekday)
	if minute.find (",") != -1 or hour.find (",") != -1 or day.find (",") != -1 or month.find (",") != -1 or weekday.find (",") != -1:
		return translate_crontab_easy_fallback (minute, hour, day, month, weekday)
		
	# So if our case is supported:

	# Minute and hour cases
	if month == "*" and day == "*" and weekday == "*":
		if minute == "0" and hour == "*":
			return _("At every full hour")
		elif minute == "*" and hour == "*":
			return _("At every minute")
		elif minute != "*" and hour == "*":
			return (_("At the %(minute)s minute of every hour") % { "minute": lc_nth(minute) } )
		elif minute == "*" and hour != "*":
			return (_("At every minute between %(time_from)s and %(time_to)s") % { "time_from": lc_time(hour, 0), "time_to": lc_time(hour, 59) } )
		elif hour != "*" and minute != "*":
			return (_("On every day at %(time)s") % { "time": lc_time(hour, minute) } )

	# Day cases
	if month == "*" and day != "*" and weekday == "*":
		if minute == "0" and hour == "*":
			return (_("On the %(monthday)s of every month at every full hour") % { "monthday": lc_nth(day) } )
		elif minute == "*" and hour == "*":
			return (_("On the %(monthday)s of every month at every minute") % { "monthday": lc_nth(day) } )
		elif minute != "*" and hour == "*":
			return (_("On the %(monthday)s of every month at the %(minute)s minute of every hour") % { "monthday": lc_nth(day), "minute": lc_nth(minute) } )
		elif minute == "*" and hour != "*":
			return (_("On the %(monthday)s of every month at every minute between %(time_from)s and %(time_to)s") % { "monthday": lc_nth(day), "time_from": lc_time(hour, 0), "time_to": lc_time(hour, 59) } )
		elif minute != "*" and hour != "*":
			return (_("On the %(monthday)s of every month at %(time)s") % { "monthday": lc_nth(day), "time": lc_time(hour, minute) } )

	# Month cases
	if month != "*" and weekday == "*" and day == "*":
		if minute == "0" and hour == "*":
			return (_("On every day in %(month)s at every full hour") % { "month": lc_month(month) } )
		elif minute == "*" and hour == "*":
			return (_("On every day in %(month)s at every minute") % { "month": lc_month(month) } )
		elif minute != "*" and hour == "*":
			return (_("On every day in %(month)s at the %(minute)s minute of every hour") % { "month": lc_month(month), "minute": lc_nth(minute) } )
		elif minute == "*" and hour != "*":
			return (_("On every day in %(month)s at every minute between %(time_from)s and %(time_to)s") % { "month": lc_month(month), "time_from": lc_time(hour, 0), "time_to": lc_time(hour, 59) } )
		elif minute != "*" and hour != "*":
			return (_("On every day in %(month)s at %(time)s") % { "month": lc_month(month), "time": lc_time(hour, minute) } )

	# Day and month cases
	if month != "*" and weekday == "*" and day != "*":
		if minute == "0" and hour == "*":
			return (_("Every year on %(date)s at every full hour") % { "date": lc_date(day,month) } )
		elif minute == "*" and hour == "*":
			return (_("Every year on %(date)s at every minute") % { "date": lc_date(day,month) } )
		elif minute != "*" and hour == "*":
			return (_("Every year on %(date)s at the %(minute)s minute of every hour") % { "date": lc_date(day,month), "minute": lc_nth(minute) } )
		elif minute == "*" and hour != "*":
			return (_("Every year on %(date)s at every minute between %(time_from)s and %(time_to)s") % { "date": lc_date(day,month), "time_from": lc_time(hour, 0), "time_to": lc_time(hour, 59) } )
		elif minute != "*" and hour != "*":
			return (_("Every year on %(date)s at %(time)s") % { "date": lc_date(day,month), "time": lc_time(hour, minute) } )

	# Weekday cases
	if month == "*" and day == "*" and weekday != "*":
		if minute == "0" and hour == "*":
			return (_("On every %(weekday)s at every full hour") % { "weekday": lc_weekday(weekday) } )
		elif minute == "*" and hour == "*":
			return (_("On every %(weekday)s at every minute") % { "weekday": lc_weekday(weekday) } )
		elif minute != "*" and hour == "*":
			return (_("On every %(weekday)s at the %(minute)s minute of every hour") % { "weekday": lc_weekday(weekday), "minute": lc_nth(minute) } )
		elif minute == "*" and hour != "*":
			return (_("On every %(weekday)s at every minute between %(time_from)s and %(time_to)s") % { "weekday": lc_weekday(weekday), "time_from": lc_time(hour, 0), "time_to": lc_time(hour, 59) } )
		elif minute != "*" and hour != "*":
			return (_("On every %(weekday)s at %(time)s") % { "weekday": lc_weekday(weekday), "time": lc_time(hour, minute) } )

	# Day and weekday cases
	if day != "*" and month == "*" and weekday != "*":
		if minute == "0" and hour == "*":
			return (_("On the %(monthday)s of every month and every %(weekday)s at every full hour") % { "monthday": lc_nth(day), "weekday": lc_weekday(weekday) } )
		elif minute == "*" and hour == "*":
			return (_("On the %(monthday)s of every month and every %(weekday)s at every minute") % { "monthday": lc_nth(day), "weekday": lc_weekday(weekday) } )
		elif minute != "*" and hour == "*":
			return (_("On the %(monthday)s of every month and every %(weekday)s at the %(minute)s minute of every hour") % { "monthday": lc_nth(day), "weekday": lc_weekday(weekday), "minute": lc_nth(minute) } )
		elif minute == "*" and hour != "*":
			return (_("On the %(monthday)s of every month and every %(weekday)s at every minute between %(time_from)s and %(time_to)s") % { "monthday": lc_nth(day), "weekday": lc_weekday(weekday), "time_from": lc_time(hour, 0), "time_to": lc_time(hour, 59) } )
		elif minute != "*" and hour != "*":
			return (_("On the %(monthday)s of every month and every %(weekday)s at %(time)s") % { "monthday": lc_nth(day), "weekday": lc_weekday(weekday), "time": lc_time(hour, minute) } )

	# Month and weekday cases
	if day == "*" and month != "*" and weekday != "*":
		if minute == "0" and hour == "*":
			return (_("On every %(weekday)s in %(month)s at every full hour") % { "weekday": lc_weekday(weekday), "month": lc_month(month) } )
		elif minute == "*" and hour == "*":
			return (_("On every %(weekday)s in %(month)s at every minute") % { "weekday": lc_weekday(weekday), "month": lc_month(month) } )
		elif minute != "*" and hour == "*":
			return (_("On every %(weekday)s in %(month)s at the %(minute)s minute of every hour") % { "weekday": lc_weekday(weekday), "month": lc_month(month), "minute": lc_nth(minute) } )
		elif minute == "*" and hour != "*":
			return (_("On every %(weekday)s in %(month)s at every minute between %(time_from)s and %(time_to)s") % { "weekday": lc_weekday(weekday), "month": lc_month(month), "time_from": lc_time(hour, 0), "time_to": lc_time(hour, 59) } )
		elif minute != "*" and hour != "*":
			return (_("On every %(weekday)s in %(month)s at %(time)s") % { "weekday": lc_weekday(weekday), "month": lc_month(month), "time": lc_time(hour, minute) } )

	# Day, month and weekday cases
	if day != "*" and month != "*" and weekday != "*":
		if minute == "0" and hour == "*":
			return (_("On every %(weekday)s in %(month)s and on %(date)s every year at every full hour") % { "weekday": lc_weekday(weekday), "month": lc_month(month), "date": lc_date(day,month) } )
		elif minute == "*" and hour == "*":
			return (_("On every %(weekday)s in %(month)s and on %(date)s every year at every minute") % { "weekday": lc_weekday(weekday), "month": lc_month(month), "date": lc_date(day,month) } )
		elif minute != "*" and hour == "*":
			return (_("On every %(weekday)s in %(month)s and on %(date)s every year at the %(minute)s minute of every hour") % { "weekday": lc_weekday(weekday), "month": lc_month(month), "date": lc_date(day,month), "minute": lc_nth(minute) } )
		elif minute == "*" and hour != "*":
			return (_("On every %(weekday)s in %(month)s and on %(date)s every year at every minute between %(time_from)s and %(time_to)s") % { "weekday": lc_weekday(weekday), "month": lc_month(month), "date": lc_date(day,month), "time_from": lc_time(hour, 0), "time_to": lc_time(hour, 59) } )
		elif minute != "*" and hour != "*":
			return (_("On every %(weekday)s in %(month)s and on %(date)s every year at %(time)s") % { "weekday": lc_weekday(weekday), "month": lc_month(month), "date": lc_date(day,month), "time": lc_time(hour, minute) } )

	# If nothing got translated, we fall back to ...
	return translate_crontab_easy_fallback (minute, hour, day, month, weekday)

# This is for cases that don't be covered by translate_crontab_easy
def translate_crontab_easy_fallback (minute, hour, day, month, weekday):
	if minute == "*":
		minute = _("every minute")
	else:
		minute = _("minute: ") + minute

	if hour == "*":
		hour = _("every hour")
	else:
		hour = _("hour: ") + hour

	if day == "*":
		day = _("every day of the month")
	else:
		day = _("day of the month: ") + day

	if month == "*":
		month = _("every month")
	else:
		month = _("month: ") + month

	if weekday == "*":
		weekday = ""
	else:
		weekday = _(", weekday: ") + weekday

	return _("At %(minute)s, %(hour)s, %(monthday)s, %(month)s%(weekday)s") % { "minute": minute, "hour": hour, "monthday": day, "month": month, "weekday": weekday }
