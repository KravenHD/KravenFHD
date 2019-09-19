# -*- coding: utf-8 -*-

#  Color Selection Tool
#
#  Coded/Modified/Adapted by Team Kraven
#  Based on VTi and/or OpenATV image source code
#  Thankfully inspired by MyMetrix by iMaxxx
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

from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Screens.Standby import TryQuitMainloop
from Components.ActionMap import ActionMap
from Components.config import config, configfile, ConfigYesNo, ConfigSubsection, getConfigListEntry, ConfigSelection, ConfigSlider
from Components.ConfigList import ConfigListScreen
from Components.Sources.StaticText import StaticText
from Components.Input import Input
from Components.Label import Label
from Components.Sources.CanvasSource import CanvasSource
import gettext
from enigma import getDesktop, eTimer
from Tools.Directories import resolveFilename, SCOPE_LANGUAGE, SCOPE_PLUGINS
from Components.Language import language
from os import environ

#############################################################

DESKTOP_WIDTH = getDesktop(0).size().width()

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

def translateBlock(block):
	for x in TranslationHelper:
		if block.__contains__(x[0]):
			block = block.replace(x[0], x[1])

#############################################################

class KravenFHDColorSelection(ConfigListScreen, Screen):

	if DESKTOP_WIDTH <= 1280:
	  skin = """
<screen name="KravenFHDColorSelection" position="0,0" size="1280,720" flags="wfNoBorder" backgroundColor="#FF000000">
  <widget backgroundColor="#00000000" source="Title" render="Label" font="Regular;28" foregroundColor="#00f0a30a" position="286,260" size="540,36" valign="center" transparent="1" zPosition="1" />
  <widget backgroundColor="#00000000" source="Title" render="Label" font="Regular;28" foregroundColor="#00ffffff" position="844,260" size="150,36" halign="right" transparent="1" valign="center">
    <convert type="KravenFHDColorInfo">Kraven</convert>
  </widget>
  <widget backgroundColor="#00000000" name="config" font="Regular;22" foregroundColor="#00ffffff" itemHeight="30" position="286,312" size="708,90" enableWrapAround="1" transparent="1" zPosition="2" />
  <widget backgroundColor="#00000000" source="preview" render="Canvas" position="0,0" size="1280,720" zPosition="-2" />
  <widget backgroundColor="#00000000" source="key_red" render="Label" font="Regular;20" foregroundColor="#00ffffff" position="286,415" size="220,26" valign="center" transparent="1" zPosition="1" />
  <widget backgroundColor="#00000000" source="key_green" render="Label" font="Regular;20" foregroundColor="#00ffffff" position="536,415" size="220,26" valign="center" transparent="1" zPosition="1" />
  <eLabel backgroundColor="#00E61805" position="281,442" size="150,5" />
  <eLabel backgroundColor="#005FE500" position="531,442" size="150,5" />
  <eLabel backgroundColor="#00000000" position="266,250" size="748,220" transparent="0" zPosition="-1" />
</screen>
"""
	else:
	  skin = """
<screen name="KravenFHDColorSelection" position="0,0" size="1920,1080" flags="wfNoBorder" backgroundColor="#FF000000">
  <widget backgroundColor="#00000000" source="Title" render="Label" font="Regular;42" foregroundColor="#00f0a30a" position="429,390" size="810,54" valign="center" transparent="1" zPosition="1" />
  <widget backgroundColor="#00000000" source="Title" render="Label" font="Regular;42" foregroundColor="#00ffffff" position="1266,390" size="225,54" halign="right" transparent="1" valign="center">
    <convert type="KravenFHDColorInfo">Kraven</convert>
  </widget>
  <widget backgroundColor="#00000000" name="config" font="Regular;32" foregroundColor="#00ffffff" itemHeight="45" position="429,468" size="1062,135" enableWrapAround="1" transparent="1" zPosition="2" />
  <widget backgroundColor="#00000000" source="preview" render="Canvas" position="0,0" size="1920,1080" zPosition="-2" />
  <widget backgroundColor="#00000000" source="key_red" render="Label" font="Regular;30" foregroundColor="#00ffffff" position="429,622" size="330,39" valign="center" transparent="1" zPosition="1" />
  <widget backgroundColor="#00000000" source="key_green" render="Label" font="Regular;30" foregroundColor="#00ffffff" position="804,622" size="330,39" valign="center" transparent="1" zPosition="1" />
  <ePixmap backgroundColor="#00000000" pixmap="KravenFHD/buttons/key_red1.png" position="421,663" size="300,7" alphatest="blend" />
  <ePixmap backgroundColor="#00000000" pixmap="KravenFHD/buttons/key_green1.png" position="796,663" size="300,7" alphatest="blend" />
  <eLabel backgroundColor="#00000000" position="399,375" size="1122,330" transparent="0" zPosition="-1" />
</screen>
"""

	def __init__(self, session, title = "", color = ""):
		self.session = session
		Screen.__init__(self, session)

		list = []
		ConfigListScreen.__init__(self, list)

		self["actions"] = ActionMap(["KravenFHDConfigActions", "OkCancelActions", "DirectionActions", "ColorActions", "InputActions"],
		{
			"upUp": self.keyUpLong,
			"downUp": self.keyDownLong,
			"up": self.keyUp,
			"down": self.keyDown,
			"left": self.keyLeft,
			"right": self.keyRight,
			"green": self.save,
			"ok": self.save,
			"red": self.exit,
			"cancel": self.exit
		}, -1)

		self["key_red"] = StaticText(_("Exit"))
		self["key_green"] = StaticText(_("Save Color"))
		self["Title"] = StaticText(_("Color Selection"))
		self["preview"] = CanvasSource()
		
		self.newcolor=color

		self.newcolor = self.newcolor[-6:]
		config.plugins.KravenFHD.SelfColorR.value = int(self.newcolor[0:2], 16)
		config.plugins.KravenFHD.SelfColorG.value = int(self.newcolor[2:4], 16)
		config.plugins.KravenFHD.SelfColorB.value = int(self.newcolor[4:6], 16)
		
		self.timer = eTimer()
		self.timer.callback.append(self.colorselectionlist)
		self.mylist()

	def mylist(self):
		self.timer.start(100, True)

	def colorselectionlist(self):
		list = []
		list.append(getConfigListEntry(_("red"), config.plugins.KravenFHD.SelfColorR))
		list.append(getConfigListEntry(_("green"), config.plugins.KravenFHD.SelfColorG))
		list.append(getConfigListEntry(_("blue"), config.plugins.KravenFHD.SelfColorB))

		self["config"].list = list
		self["config"].l.setList(list)

		self.showColor(self.RGB(int(config.plugins.KravenFHD.SelfColorR.value), int(config.plugins.KravenFHD.SelfColorG.value), int(config.plugins.KravenFHD.SelfColorB.value)))
		self.newcolor=str(hex(config.plugins.KravenFHD.SelfColorR.value)[2:4]).zfill(2) + str(hex(config.plugins.KravenFHD.SelfColorG.value)[2:4]).zfill(2) + str(hex(config.plugins.KravenFHD.SelfColorB.value)[2:4]).zfill(2)

	def keyLeft(self):
		ConfigListScreen.keyLeft(self)
		self.mylist()

	def keyRight(self):
		ConfigListScreen.keyRight(self)
		self.mylist()

	def keyDown(self):
		if self.gete2distroversion() in ("VTi","teamblue"):
			pass
		elif self.gete2distroversion() == "openatv":
			self["config"].instance.moveSelection(self["config"].instance.moveDown)
			self.mylist()

	def keyUp(self):
		if self.gete2distroversion() in ("VTi","teamblue"):
			pass
		elif self.gete2distroversion() == "openatv":
			self["config"].instance.moveSelection(self["config"].instance.moveUp)
			self.mylist()

	def keyUpLong(self):
		self["config"].instance.moveSelection(self["config"].instance.moveUp)
		self.mylist()

	def keyDownLong(self):
		self["config"].instance.moveSelection(self["config"].instance.moveDown)
		self.mylist()

	def save(self):
		self.close(self.newcolor)
		return

	def exit(self):
		self.close(None)
		return

	def gete2distroversion(self):
		try:
			from boxbranding import getImageDistro
			if getImageDistro() == "openatv":
				return "openatv"
			elif getImageDistro() == "teamblue":
				return "teamblue"
			elif getImageDistro() == "VTi":
				return "VTi"
		except ImportError:
			return "VTi"

	def showColor(self,actcolor):
		c = self["preview"]
		c.fill(0,0,1920,1080,actcolor)
		c.flush()

	def RGB(self,r,g,b):
		return (r<<16)|(g<<8)|b
