# -*- coding: utf-8 -*-

#  Remaining To Text Converter
#
#  Coded/Modified/Adapted by Team Kraven
#  Based on VTi and/or OpenATV image source code
#
#  This code is licensed under the Creative Commons 
#  Attribution-NonCommercial-ShareAlike 3.0 Unported 
#  License. To view a copy of this license, visit
#  http://creativecommons.org/licenses/by-nc-sa/3.0/ 
#  or send a letter to Creative Commons, 559 Nathan 
#  Abbott Way, Stanford, California 94305, USA.
#
#  If you think this license infringes any rights,
#  please contact Team Kraven at info@coolskins.de

from Components.Converter.Converter import Converter
from Components.Element import cached
from os import environ
from Tools.Directories import resolveFilename, SCOPE_LANGUAGE, SCOPE_PLUGINS
from Components.Language import language
import gettext

lang = language.getLanguage()
environ["LANGUAGE"] = lang[:2]
gettext.bindtextdomain("enigma2", resolveFilename(SCOPE_LANGUAGE))
gettext.textdomain("enigma2")
gettext.bindtextdomain("KravenFHD", "%s%s" % (resolveFilename(SCOPE_PLUGINS), "Extensions/KravenFHD/locale/"))

def _(txt):
	t = gettext.dgettext("KravenFHD", txt)
	if t == txt:
		t = gettext.gettext(txt)
	return t

class KravenFHDRemainingToText(Converter, object):
	DEFAULT = 0
	WITH_SECONDS = 1
	NO_SECONDS = 2
	IN_SECONDS = 3
	ONLY_MINUTES = 4
	REMAINING_MINUTES = 5

	def __init__(self, type):
		Converter.__init__(self, type)
		if type == "WithSeconds":
			self.type = self.WITH_SECONDS
		elif type == "NoSeconds":
			self.type = self.NO_SECONDS
		elif type == "InSeconds":
			self.type = self.IN_SECONDS
		elif type == "OnlyMinutes":
			self.type = self.ONLY_MINUTES
		elif type == "RemainingMinutes":
			self.type = self.REMAINING_MINUTES
		else:
			self.type = self.DEFAULT

	@cached
	def getText(self):
		time = self.source.time
		if time is None:
			return ""

		(duration, remaining) = self.source.time

		if self.type == self.WITH_SECONDS:
			if remaining is not None:
				return "%d:%02d:%02d" % (remaining / 3600, (remaining / 60) - ((remaining / 3600) * 60), remaining % 60)
			else:
				return "%02d:%02d:%02d" % (duration / 3600, (duration / 60) - ((duration / 3600) * 60), duration % 60)
		elif self.type == self.NO_SECONDS:
			if remaining is not None:
				return "+%d:%02d" % (remaining / 3600, (remaining / 60) - ((remaining / 3600) * 60) + 1)
			else:
				return "%02d:%02d" % (duration / 3600, (duration / 60) - ((duration / 3600) * 60))
		elif self.type == self.IN_SECONDS:
			if remaining is not None:
				return str(remaining)
			else:
				return str(duration)
		elif self.type == self.ONLY_MINUTES:
			if remaining is not None:
				return "+%d" % (remaining / 60 + 1)
			else:
				return "%d" % (duration / 60)
		elif self.type == self.REMAINING_MINUTES:
			if remaining is not None:
				return _('remaining: ') + "%d min" % (remaining / 60 + 1)
			else:
				return "%d min" % (duration / 60)
		elif self.type == self.DEFAULT:
			if remaining is not None:
				return "%d min" % (remaining / 60 + 1)
			else:
				return "%d min" % (duration / 60)
		else:
			return "???"

	text = property(getText)
