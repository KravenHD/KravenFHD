# WetterPicon
# Copyright (c) .:TBX:. 2015
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#

from Renderer import Renderer 
from enigma import ePixmap
from Components.config import config
from Tools.Directories import fileExists, SCOPE_CURRENT_SKIN, resolveFilename 

class KravenFHDWetterPicon(Renderer):

	__module__ = __name__
	def __init__(self):
		Renderer.__init__(self)
		self.pngname = ''
		self.userpath = "/usr/share/enigma2/Kraven-user-icons/"
		self.usericons = [
		("01d","32"),
		("01n","31"),
		("02d","30"),
		("02n","29"),
		("03d","28"),
		("03n","27"),
		("04d","26"),
		("04n","26"),
		("09d","11"),
		("09n","12"),
		("10d","10"),
		("10n","9"),
		("11d","4"),
		("11n","4"),
		("13d","16"),
		("13n","16"),
		("50d","20"),
		("50n","20"),
		("01","32"),
		("1","32"),
		("02","34"),
		("2","34"),
		("03","30"),
		("3","30"),
		("04","30"),
		("4","30"),
		("05","21"),
		("5","21"),
		("06","28"),
		("6","28"),
		("07","26"),
		("7","26"),
		("08","26"),
		("8","26"),
		("11","20"),
		("12","40"),
		("13","39"),
		("14","39"),
		("15","4"),
		("16","4"),
		("17","4"),
		("18","4"),
		("19","13"),
		("20","13"),
		("21","13"),
		("22","16"),
		("23","16"),
		("24","25"),
		("25","18"),
		("26","10"),
		("29","5"),
		("30","36"),
		("31","25"),
		("32","24"),
		("33","31"),
		("34","33"),
		("35","29"),
		("36","29"),
		("37","33"),
		("38","27"),
		("39","12"),
		("40","12"),
		("41","4"),
		("42","4"),
		("43","13"),
		("44","16")
		]

	def applySkin(self, desktop, parent):
		attribs = []
		for (attrib, value,) in self.skinAttributes:
			if attrib == 'path':
				self.path = value
			else:
				attribs.append((attrib, value))
		self.skinAttributes = attribs
		return Renderer.applySkin(self, desktop, parent)

	GUI_WIDGET = ePixmap

	def changed(self, what):
		if self.instance:
			if self.path:
				for pair in self.usericons:
					if pair[0] == str(self.source.text):
						break
				self.pngname = self.userpath + pair[1] + '.png'
				if not fileExists(self.pngname):
					self.pngname = '/usr/share/enigma2/KravenFHD/' + self.path + '/' + str(self.source.text) + '.png'
					if not fileExists(self.pngname):
						self.pngname = resolveFilename(SCOPE_CURRENT_SKIN, 'picon_default.png')
				self.instance.setScale(1)
				self.instance.setPixmapFromFile(self.pngname)
