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

class KravenFHDAndroidPicon(Renderer):

	__module__ = __name__
	def __init__(self):
		Renderer.__init__(self)
		self.pngname = ''

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
                           self.pngname = '/usr/share/enigma2/KravenFHD/' + self.path + '/' + str(self.source.text) + '.png'
                           if not fileExists(self.pngname):
                              self.pngname = resolveFilename(SCOPE_CURRENT_SKIN, 'picon_default.png')
                           self.instance.setScale(1)
                           self.instance.setPixmapFromFile(self.pngname)
