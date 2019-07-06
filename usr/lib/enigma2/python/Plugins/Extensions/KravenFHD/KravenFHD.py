# -*- coding: utf-8 -*-

#######################################################################
#
# KravenFHD by Team-Kraven
#
# Thankfully inspired by:
# MyMetrix
# Coded by iMaxxx (c) 2013
#
# This plugin is licensed under the Creative Commons
# Attribution-NonCommercial-ShareAlike 3.0 Unported License.
# To view a copy of this license, visit http://creativecommons.org/licenses/by-nc-sa/3.0/
# or send a letter to Creative Commons, 559 Nathan Abbott Way, Stanford, California 94305, USA.
#
#######################################################################

from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Screens.ChoiceBox import ChoiceBox
from Screens.Console import Console
from Screens.Standby import TryQuitMainloop
from Screens.VirtualKeyBoard import VirtualKeyBoard
from Components.ActionMap import ActionMap
from Components.AVSwitch import AVSwitch
from Components.config import config, configfile, ConfigYesNo, ConfigSubsection, getConfigListEntry, ConfigSelection, ConfigNumber, ConfigText, ConfigInteger, ConfigClock, ConfigSlider, ConfigBoolean
from Components.ConfigList import ConfigListScreen
from Components.Sources.StaticText import StaticText
from Components.Label import Label
from Components.Language import language
from os import environ, listdir, remove, rename, system, popen, path
from shutil import move, rmtree
from skin import parseColor
from Components.Pixmap import Pixmap
from Components.Label import Label
from Components.Sources.CanvasSource import CanvasSource
from Components.SystemInfo import SystemInfo
from PIL import Image, ImageFilter
import gettext, time, subprocess, re, requests
from enigma import ePicLoad, getDesktop, eConsoleAppContainer, eTimer
from Tools.Directories import fileExists, resolveFilename, SCOPE_LANGUAGE, SCOPE_PLUGINS
from copy import deepcopy
from ColorSelection import KravenFHDColorSelection

try:
	from boxbranding import getImageDistro
	if getImageDistro() in ("openatv","teamblue"):
		from lxml import etree
		from xml.etree.cElementTree import fromstring
except ImportError:
	brand = False
	from xml import etree
	from xml.etree.cElementTree import fromstring

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
	return block

#############################################################

ColorSelfList = [
	("F0A30A", _("amber")),
	("B27708", _("amber dark")),
	("1B1775", _("blue")),
	("0E0C3F", _("blue dark")),
	("7D5929", _("brown")),
	("3F2D15", _("brown dark")),
	("0050EF", _("cobalt")),
	("001F59", _("cobalt dark")),
	("1BA1E2", _("cyan")),
	("0F5B7F", _("cyan dark")),
	("FFEA04", _("yellow")),
	("999999", _("grey")),
	("3F3F3F", _("grey dark")),
	("70AD11", _("green")),
	("213305", _("green dark")),
	("A19181", _("Kraven")),
	("28150B", _("Kraven dark")),
	("6D8764", _("olive")),
	("313D2D", _("olive dark")),
	("C3461B", _("orange")),
	("892E13", _("orange dark")),
	("F472D0", _("pink")),
	("723562", _("pink dark")),
	("E51400", _("red")),
	("330400", _("red dark")),
	("000000", _("black")),
	("008A00", _("emerald")),
	("647687", _("steel")),
	("262C33", _("steel dark")),
	("6C0AAB", _("violet")),
	("1F0333", _("violet dark")),
	("ffffff", _("white")),
	("self", _("self"))
	]

BackgroundList = [
	("F0A30A", _("amber")),
	("B27708", _("amber dark")),
	("665700", _("amber very dark")),
	("1B1775", _("blue")),
	("0E0C3F", _("blue dark")),
	("03001E", _("blue very dark")),
	("7D5929", _("brown")),
	("3F2D15", _("brown dark")),
	("180B00", _("brown very dark")),
	("0050EF", _("cobalt")),
	("001F59", _("cobalt dark")),
	("000E2B", _("cobalt very dark")),
	("1BA1E2", _("cyan")),
	("0F5B7F", _("cyan dark")),
	("01263D", _("cyan very dark")),
	("FFEA04", _("yellow")),
	("999999", _("grey")),
	("3F3F3F", _("grey dark")),
	("1C1C1C", _("grey very dark")),
	("70AD11", _("green")),
	("213305", _("green dark")),
	("001203", _("green very dark")),
	("A19181", _("Kraven")),
	("28150B", _("Kraven dark")),
	("1D130B", _("Kraven very dark")),
	("6D8764", _("olive")),
	("313D2D", _("olive dark")),
	("161C12", _("olive very dark")),
	("C3461B", _("orange")),
	("892E13", _("orange dark")),
	("521D00", _("orange very dark")),
	("F472D0", _("pink")),
	("723562", _("pink dark")),
	("2F0029", _("pink very dark")),
	("E51400", _("red")),
	("330400", _("red dark")),
	("240004", _("red very dark")),
	("000000", _("black")),
	("008A00", _("emerald")),
	("647687", _("steel")),
	("262C33", _("steel dark")),
	("131619", _("steel very dark")),
	("6C0AAB", _("violet")),
	("1F0333", _("violet dark")),
	("11001E", _("violet very dark")),
	("ffffff", _("white"))
	]
	
TextureList = []

for i in range(1,50):
	n=str(i)
	if fileExists("/usr/share/enigma2/Kraven-user-icons/usertexture"+n+".png") or fileExists("/usr/share/enigma2/Kraven-user-icons/usertexture"+n+".jpg"):
		TextureList.append(("usertexture"+n,_("user texture")+" "+n))
for i in range(1,50):
	n=str(i)
	if fileExists("/usr/share/enigma2/KravenFHD/textures/texture"+n+".png") or fileExists("/usr/share/enigma2/KravenFHD/textures/texture"+n+".jpg"):
		TextureList.append(("texture"+n,_("texture")+" "+n))

BorderSelfList = deepcopy(ColorSelfList)
BorderSelfList.append(("none", _("off")))

BackgroundSelfList = deepcopy(BackgroundList)
BackgroundSelfList.append(("self", _("self")))

BackgroundSelfGradientList = deepcopy(BackgroundSelfList)
BackgroundSelfGradientList.append(("gradient", _("gradient")))

BackgroundSelfTextureList = deepcopy(BackgroundSelfList)
BackgroundSelfTextureList.append(("texture", _("texture")))

BackgroundSelfGradientTextureList = deepcopy(BackgroundSelfGradientList)
BackgroundSelfGradientTextureList.append(("texture", _("texture")))

LanguageList = [
	("de", _("German")),
	("en", _("English")),
	("ru", _("Russian")),
	("it", _("Italian")),
	("es", _("Spanish (es)")),
	("sp", _("Spanish (sp)")),
	("uk", _("Ukrainian (uk)")),
	("ua", _("Ukrainian (ua)")),
	("pt", _("Portuguese")),
	("ro", _("Romanian")),
	("pl", _("Polish")),
	("fi", _("Finnish")),
	("nl", _("Dutch")),
	("fr", _("French")),
	("bg", _("Bulgarian")),
	("sv", _("Swedish (sv)")),
	("se", _("Swedish (se)")),
	("zh_tw", _("Chinese Traditional")),
	("zh", _("Chinese Simplified (zh)")),
	("zh_cn", _("Chinese Simplified (zh_cn)")),
	("tr", _("Turkish")),
	("hr", _("Croatian")),
	("ca", _("Catalan"))
	]

TransList = [
	("00", "0%"),
	("0C", "5%"),
	("18", "10%"),
	("32", "20%"),
	("58", "35%"),
	("7E", "50%")
	]

config.plugins.KravenFHD = ConfigSubsection()
config.plugins.KravenFHD.Primetime = ConfigClock(default=time.mktime((0, 0, 0, 20, 15, 0, 0, 0, 0)))
config.plugins.KravenFHD.InfobarAntialias = ConfigSlider(default=10, increment=1, limits=(0,20))
config.plugins.KravenFHD.ECMLineAntialias = ConfigSlider(default=10, increment=1, limits=(0,20))
config.plugins.KravenFHD.ScreensAntialias = ConfigSlider(default=10, increment=1, limits=(0,20))
config.plugins.KravenFHD.SelfColorR = ConfigSlider(default=0, increment=15, limits=(0,255))
config.plugins.KravenFHD.SelfColorG = ConfigSlider(default=0, increment=15, limits=(0,255))
config.plugins.KravenFHD.SelfColorB = ConfigSlider(default=75, increment=15, limits=(0,255))

config.plugins.KravenFHD.customProfile = ConfigSelection(default="1", choices = [
				("1", _("1")),
				("2", _("2")),
				("3", _("3")),
				("4", _("4")),
				("5", _("5"))
				])

profList = [("default", _("0 (hardcoded)"))]
for i in range(1,21):
	n=name=str(i)
	if fileExists("/etc/enigma2/kravenfhd_default_"+n):
		if i==1:
			name="1 (@tomele)"
		elif i==2:
			name="2 (@örlgrey)"
		elif i==3:
			name="3 (@stony272)"
		elif i==4:
			name="4 (@Linkstar)"
		elif i==5:
			name="5 (@Rene67)"
		elif i==6:
			name="6 (@Mister-T)"
		profList.append((n,_(name)))
config.plugins.KravenFHD.defaultProfile = ConfigSelection(default="default", choices = profList)
				
config.plugins.KravenFHD.refreshInterval = ConfigSelection(default="60", choices = [
				("15", _("15")),
				("30", _("30")),
				("60", _("60")),
				("120", _("120")),
				("240", _("240")),
				("480", _("480"))
				])

config.plugins.KravenFHD.Volume = ConfigSelection(default="volume-border", choices = [
				("volume-original", _("original")),
				("volume-border", _("with Border")),
				("volume-left", _("left")),
				("volume-right", _("right")),
				("volume-top", _("top")),
				("volume-center", _("center"))
				])

config.plugins.KravenFHD.MenuColorTrans = ConfigSelection(default="32", choices = TransList)

config.plugins.KravenFHD.BackgroundColorTrans = ConfigSelection(default="32", choices = TransList)

config.plugins.KravenFHD.InfobarColorTrans = ConfigSelection(default="00", choices = TransList)

config.plugins.KravenFHD.BackgroundListColor = ConfigSelection(default="self", choices = BackgroundSelfGradientTextureList)
config.plugins.KravenFHD.BackgroundSelfColor = ConfigText(default="000000")
config.plugins.KravenFHD.BackgroundColor = ConfigText(default="000000")

config.plugins.KravenFHD.BackgroundAlternateListColor = ConfigSelection(default="000000", choices = BackgroundSelfList)
config.plugins.KravenFHD.BackgroundAlternateSelfColor = ConfigText(default="000000")
config.plugins.KravenFHD.BackgroundAlternateColor = ConfigText(default="000000")

config.plugins.KravenFHD.InfobarGradientListColor = ConfigSelection(default="self", choices = BackgroundSelfTextureList)
config.plugins.KravenFHD.InfobarGradientSelfColor = ConfigText(default="000000")
config.plugins.KravenFHD.InfobarGradientColor = ConfigText(default="000000")

config.plugins.KravenFHD.InfobarBoxListColor = ConfigSelection(default="self", choices = BackgroundSelfGradientTextureList)
config.plugins.KravenFHD.InfobarBoxSelfColor = ConfigText(default="000000")
config.plugins.KravenFHD.InfobarBoxColor = ConfigText(default="000000")

config.plugins.KravenFHD.InfobarAlternateListColor = ConfigSelection(default="000000", choices = BackgroundSelfList)
config.plugins.KravenFHD.InfobarAlternateSelfColor = ConfigText(default="000000")
config.plugins.KravenFHD.InfobarAlternateColor = ConfigText(default="000000")

config.plugins.KravenFHD.BackgroundGradientListColorPrimary = ConfigSelection(default="000000", choices = BackgroundSelfList)
config.plugins.KravenFHD.BackgroundGradientSelfColorPrimary = ConfigText(default="000000")
config.plugins.KravenFHD.BackgroundGradientColorPrimary = ConfigText(default="000000")

config.plugins.KravenFHD.BackgroundGradientListColorSecondary = ConfigSelection(default="000000", choices = BackgroundSelfList)
config.plugins.KravenFHD.BackgroundGradientSelfColorSecondary = ConfigText(default="000000")
config.plugins.KravenFHD.BackgroundGradientColorSecondary = ConfigText(default="000000")

config.plugins.KravenFHD.InfobarGradientListColorPrimary = ConfigSelection(default="000000", choices = BackgroundSelfList)
config.plugins.KravenFHD.InfobarGradientSelfColorPrimary = ConfigText(default="000000")
config.plugins.KravenFHD.InfobarGradientColorPrimary = ConfigText(default="000000")

config.plugins.KravenFHD.InfobarGradientListColorSecondary = ConfigSelection(default="000000", choices = BackgroundSelfList)
config.plugins.KravenFHD.InfobarGradientSelfColorSecondary = ConfigText(default="000000")
config.plugins.KravenFHD.InfobarGradientColorSecondary = ConfigText(default="000000")

config.plugins.KravenFHD.SelectionBackgroundList = ConfigSelection(default="0050EF", choices = ColorSelfList)
config.plugins.KravenFHD.SelectionBackgroundSelf = ConfigText(default="0050EF")
config.plugins.KravenFHD.SelectionBackground = ConfigText(default="0050EF")

config.plugins.KravenFHD.Font1List = ConfigSelection(default="ffffff", choices = ColorSelfList)
config.plugins.KravenFHD.Font1Self = ConfigText(default="ffffff")
config.plugins.KravenFHD.Font1 = ConfigText(default="ffffff")

config.plugins.KravenFHD.Font2List = ConfigSelection(default="F0A30A", choices = ColorSelfList)
config.plugins.KravenFHD.Font2Self = ConfigText(default="F0A30A")
config.plugins.KravenFHD.Font2 = ConfigText(default="F0A30A")

config.plugins.KravenFHD.IBFont1List = ConfigSelection(default="ffffff", choices = ColorSelfList)
config.plugins.KravenFHD.IBFont1Self = ConfigText(default="ffffff")
config.plugins.KravenFHD.IBFont1 = ConfigText(default="ffffff")

config.plugins.KravenFHD.IBFont2List = ConfigSelection(default="F0A30A", choices = ColorSelfList)
config.plugins.KravenFHD.IBFont2Self = ConfigText(default="F0A30A")
config.plugins.KravenFHD.IBFont2 = ConfigText(default="F0A30A")

config.plugins.KravenFHD.PermanentClockFontList = ConfigSelection(default="ffffff", choices = ColorSelfList)
config.plugins.KravenFHD.PermanentClockFontSelf = ConfigText(default="ffffff")
config.plugins.KravenFHD.PermanentClockFont = ConfigText(default="ffffff")

config.plugins.KravenFHD.SelectionFontList = ConfigSelection(default="ffffff", choices = ColorSelfList)
config.plugins.KravenFHD.SelectionFontSelf = ConfigText(default="ffffff")
config.plugins.KravenFHD.SelectionFont = ConfigText(default="ffffff")

config.plugins.KravenFHD.MarkedFontList = ConfigSelection(default="ffffff", choices = ColorSelfList)
config.plugins.KravenFHD.MarkedFontSelf = ConfigText(default="ffffff")
config.plugins.KravenFHD.MarkedFont = ConfigText(default="ffffff")

config.plugins.KravenFHD.ECMFontList = ConfigSelection(default="ffffff", choices = ColorSelfList)
config.plugins.KravenFHD.ECMFontSelf = ConfigText(default="ffffff")
config.plugins.KravenFHD.ECMFont = ConfigText(default="ffffff")

config.plugins.KravenFHD.ChannelnameFontList = ConfigSelection(default="ffffff", choices = ColorSelfList)
config.plugins.KravenFHD.ChannelnameFontSelf = ConfigText(default="ffffff")
config.plugins.KravenFHD.ChannelnameFont = ConfigText(default="ffffff")

config.plugins.KravenFHD.PrimetimeFontList = ConfigSelection(default="70AD11", choices = ColorSelfList)
config.plugins.KravenFHD.PrimetimeFontSelf = ConfigText(default="70AD11")
config.plugins.KravenFHD.PrimetimeFont = ConfigText(default="70AD11")

config.plugins.KravenFHD.ButtonTextList = ConfigSelection(default="ffffff", choices = ColorSelfList)
config.plugins.KravenFHD.ButtonTextSelf = ConfigText(default="ffffff")
config.plugins.KravenFHD.ButtonText = ConfigText(default="ffffff")

config.plugins.KravenFHD.AndroidList = ConfigSelection(default="000000", choices = ColorSelfList)
config.plugins.KravenFHD.AndroidSelf = ConfigText(default="000000")
config.plugins.KravenFHD.Android = ConfigText(default="000000")

config.plugins.KravenFHD.BorderList = ConfigSelection(default="ffffff", choices = ColorSelfList)
config.plugins.KravenFHD.BorderSelf = ConfigText(default="ffffff")
config.plugins.KravenFHD.Border = ConfigText(default="ffffff")

config.plugins.KravenFHD.ProgressList = ConfigSelection(default="C3461B", choices = [
				("F0A30A", _("amber")),
				("B27708", _("amber dark")),
				("1B1775", _("blue")),
				("0E0C3F", _("blue dark")),
				("7D5929", _("brown")),
				("3F2D15", _("brown dark")),
				("progress", _("colorfull")),
				("progress2", _("colorfull2")),
				("0050EF", _("cobalt")),
				("001F59", _("cobalt dark")),
				("1BA1E2", _("cyan")),
				("0F5B7F", _("cyan dark")),
				("FFEA04", _("yellow")),
				("999999", _("grey")),
				("3F3F3F", _("grey dark")),
				("70AD11", _("green")),
				("213305", _("green dark")),
				("A19181", _("Kraven")),
				("28150B", _("Kraven dark")),
				("6D8764", _("olive")),
				("313D2D", _("olive dark")),
				("C3461B", _("orange")),
				("892E13", _("orange dark")),
				("F472D0", _("pink")),
				("723562", _("pink dark")),
				("E51400", _("red")),
				("330400", _("red dark")),
				("000000", _("black")),
				("008A00", _("emerald")),
				("647687", _("steel")),
				("262C33", _("steel dark")),
				("6C0AAB", _("violet")),
				("1F0333", _("violet dark")),
				("ffffff", _("white")),
				("self", _("self"))
				])
config.plugins.KravenFHD.ProgressSelf = ConfigText(default="C3461B")
config.plugins.KravenFHD.Progress = ConfigText(default="C3461B")

config.plugins.KravenFHD.LineList = ConfigSelection(default="ffffff", choices = ColorSelfList)
config.plugins.KravenFHD.LineSelf = ConfigText(default="ffffff")
config.plugins.KravenFHD.Line = ConfigText(default="ffffff")

config.plugins.KravenFHD.IBLineList = ConfigSelection(default="ffffff", choices = ColorSelfList)
config.plugins.KravenFHD.IBLineSelf = ConfigText(default="ffffff")
config.plugins.KravenFHD.IBLine = ConfigText(default="ffffff")

config.plugins.KravenFHD.IBStyle = ConfigSelection(default="grad", choices = [
				("grad", _("gradient")),
				("box", _("box"))
				])

config.plugins.KravenFHD.InfoStyle = ConfigSelection(default="gradient", choices = [
				("gradient", _("gradient")),
				("primary", _("          Primary Color")),
				("secondary", _("          Secondary Color"))
				])

config.plugins.KravenFHD.InfobarTexture = ConfigSelection(default="texture1", choices = TextureList)

config.plugins.KravenFHD.BackgroundTexture = ConfigSelection(default="texture1", choices = TextureList)

config.plugins.KravenFHD.SelectionBorderList = ConfigSelection(default="ffffff", choices = BorderSelfList)
config.plugins.KravenFHD.SelectionBorderSelf = ConfigText(default="ffffff")
config.plugins.KravenFHD.SelectionBorder = ConfigText(default="ffffff")

config.plugins.KravenFHD.MiniTVBorderList = ConfigSelection(default="3F3F3F", choices = ColorSelfList)
config.plugins.KravenFHD.MiniTVBorderSelf = ConfigText(default="3F3F3F")
config.plugins.KravenFHD.MiniTVBorder = ConfigText(default="3F3F3F")

config.plugins.KravenFHD.AnalogStyle = ConfigSelection(default="00999999", choices = [
				("00F0A30A", _("amber")),
				("001B1775", _("blue")),
				("007D5929", _("brown")),
				("000050EF", _("cobalt")),
				("001BA1E2", _("cyan")),
				("00999999", _("grey")),
				("0070AD11", _("green")),
				("00C3461B", _("orange")),
				("00F472D0", _("pink")),
				("00E51400", _("red")),
				("00000000", _("black")),
				("00647687", _("steel")),
				("006C0AAB", _("violet")),
				("00ffffff", _("white"))
				])

config.plugins.KravenFHD.InfobarStyle = ConfigSelection(default="infobar-style-x3", choices = [
				("infobar-style-nopicon", _("no Picon")),
				("infobar-style-x1", _("X1")),
				("infobar-style-x2", _("X2")),
				("infobar-style-x3", _("X3")),
				("infobar-style-x4", _("X4")),
				("infobar-style-z1", _("Z1")),
				("infobar-style-z2", _("Z2")),
				("infobar-style-zz1", _("ZZ1")),
				("infobar-style-zz2", _("ZZ2")),
				("infobar-style-zz3", _("ZZ3")),
				("infobar-style-zz4", _("ZZ4")),
				("infobar-style-zzz1", _("ZZZ1")),
				("infobar-style-zzz2", _("ZZZ2"))
				])

config.plugins.KravenFHD.InfobarChannelName = ConfigSelection(default="none", choices = [
				("none", _("off")),
				("infobar-channelname-small", _("Name small")),
				("infobar-channelname-number-small", _("Name & Number small")),
				("infobar-channelname", _("Name big")),
				("infobar-channelname-number", _("Name & Number big"))
				])

config.plugins.KravenFHD.InfobarChannelName2 = ConfigSelection(default="none", choices = [
				("none", _("off")),
				("infobar-channelname-small", _("Name")),
				("infobar-channelname-number-small", _("Name & Number"))
				])

config.plugins.KravenFHD.IBFontSize = ConfigSelection(default="size-45", choices = [
				("size-33", _("small")),
				("size-39", _("middle")),
				("size-45", _("big"))
				])

config.plugins.KravenFHD.TypeWriter = ConfigSelection(default="runningtext", choices = [
				("typewriter", _("typewriter")),
				("runningtext", _("runningtext")),
				("none", _("off"))
				])

config.plugins.KravenFHD.alternativeChannellist = ConfigSelection(default="none", choices = [
				("on", _("on")),
				("none", _("off"))
				])

config.plugins.KravenFHD.ChannelSelectionHorStyle = ConfigSelection(default="cshor-minitv", choices = [
				("cshor-transparent", _("transparent")),
				("cshor-minitv", _("MiniTV"))
				])

config.plugins.KravenFHD.ChannelSelectionStyle = ConfigSelection(default="channelselection-style-minitv", choices = [
				("channelselection-style-nopicon", _("no Picon")),
				("channelselection-style-nopicon2", _("no Picon2")),
				("channelselection-style-xpicon", _("X-Picons")),
				("channelselection-style-zpicon", _("Z-Picons")),
				("channelselection-style-zzpicon", _("ZZ-Picons")),
				("channelselection-style-zzzpicon", _("ZZZ-Picons")),
				("channelselection-style-minitv", _("MiniTV left")),
				("channelselection-style-minitv4", _("MiniTV right")),
				("channelselection-style-minitv3", _("Preview")),
				("channelselection-style-nobile", _("Nobile")),
				("channelselection-style-nobile2", _("Nobile 2")),
				("channelselection-style-nobile-minitv", _("Nobile MiniTV")),
				("channelselection-style-nobile-minitv3", _("Nobile Preview")),
				("channelselection-style-minitv-picon", _("MiniTV Picon"))
				])

config.plugins.KravenFHD.ChannelSelectionStyle2 = ConfigSelection(default="channelselection-style-minitv", choices = [
				("channelselection-style-nopicon", _("no Picon")),
				("channelselection-style-nopicon2", _("no Picon2")),
				("channelselection-style-xpicon", _("X-Picons")),
				("channelselection-style-zpicon", _("Z-Picons")),
				("channelselection-style-zzpicon", _("ZZ-Picons")),
				("channelselection-style-zzzpicon", _("ZZZ-Picons")),
				("channelselection-style-minitv", _("MiniTV left")),
				("channelselection-style-minitv4", _("MiniTV right")),
				("channelselection-style-minitv3", _("Preview")),
				("channelselection-style-minitv33", _("Extended Preview")),
				("channelselection-style-minitv2", _("Dual TV")),
				("channelselection-style-minitv22", _("Dual TV 2")),
				("channelselection-style-nobile", _("Nobile")),
				("channelselection-style-nobile2", _("Nobile 2")),
				("channelselection-style-nobile-minitv", _("Nobile MiniTV")),
				("channelselection-style-nobile-minitv3", _("Nobile Preview")),
				("channelselection-style-nobile-minitv33", _("Nobile Extended Preview")),
				("channelselection-style-minitv-picon", _("MiniTV Picon"))
				])

config.plugins.KravenFHD.ChannelSelectionStyle3 = ConfigSelection(default="channelselection-style-minitv", choices = [
				("channelselection-style-nopicon", _("no Picon")),
				("channelselection-style-nopicon2", _("no Picon2")),
				("channelselection-style-xpicon", _("X-Picons")),
				("channelselection-style-zpicon", _("Z-Picons")),
				("channelselection-style-zzpicon", _("ZZ-Picons")),
				("channelselection-style-zzzpicon", _("ZZZ-Picons")),
				("channelselection-style-minitv", _("MiniTV left")),
				("channelselection-style-minitv4", _("MiniTV right")),
				("channelselection-style-nobile", _("Nobile")),
				("channelselection-style-nobile2", _("Nobile 2")),
				("channelselection-style-nobile-minitv", _("Nobile MiniTV")),
				("channelselection-style-minitv-picon", _("MiniTV Picon"))
				])

config.plugins.KravenFHD.ChannellistEPGList = ConfigSelection(default="channellistepglist-off", choices = [
				("channellistepglist-on", _("on")),
				("channellistepglist-off", _("off"))
				])

config.plugins.KravenFHD.ChannelSelectionMode = ConfigSelection(default="zap", choices = [
				("zap", _("Zap (1xOK)")),
				("preview", _("Preview (2xOK)"))
				])

config.plugins.KravenFHD.ChannelSelectionTrans = ConfigSelection(default="32", choices = TransList)

config.plugins.KravenFHD.ChannelSelectionServiceSize = ConfigSelection(default="size-36", choices = [
				("size-24", _("24")),
				("size-27", _("27")),
				("size-30", _("30")),
				("size-33", _("33")),
				("size-36", _("36")),
				("size-39", _("39")),
				("size-42", _("42")),
				("size-45", _("45"))
				])

config.plugins.KravenFHD.ChannelSelectionInfoSize = ConfigSelection(default="size-36", choices = [
				("size-24", _("24")),
				("size-27", _("27")),
				("size-30", _("30")),
				("size-33", _("33")),
				("size-36", _("36")),
				("size-39", _("39")),
				("size-42", _("42")),
				("size-45", _("45"))
				])

config.plugins.KravenFHD.ChannelSelectionServiceSize1 = ConfigSelection(default="size-30", choices = [
				("size-24", _("24")),
				("size-27", _("27")),
				("size-30", _("30")),
				("size-33", _("33")),
				("size-36", _("36")),
				("size-39", _("39"))
				])

config.plugins.KravenFHD.ChannelSelectionInfoSize1 = ConfigSelection(default="size-30", choices = [
				("size-24", _("24")),
				("size-27", _("27")),
				("size-30", _("30")),
				("size-33", _("33")),
				("size-36", _("36")),
				("size-39", _("39"))
				])

config.plugins.KravenFHD.ChannelSelectionEPGSize1 = ConfigSelection(default="small", choices = [
				("small", _("small")),
				("big", _("big"))
				])

config.plugins.KravenFHD.ChannelSelectionEPGSize2 = ConfigSelection(default="small", choices = [
				("small", _("small")),
				("big", _("big"))
				])

config.plugins.KravenFHD.ChannelSelectionEPGSize3 = ConfigSelection(default="small", choices = [
				("small", _("small")),
				("big", _("big"))
				])

config.plugins.KravenFHD.ChannelSelectionServiceNAList = ConfigSelection(default="FFEA04", choices = ColorSelfList)
config.plugins.KravenFHD.ChannelSelectionServiceNASelf = ConfigText(default="FFEA04")
config.plugins.KravenFHD.ChannelSelectionServiceNA = ConfigText(default="FFEA04")

config.plugins.KravenFHD.NumberZapExt = ConfigSelection(default="none", choices = [
				("none", _("off")),
				("numberzapext-xpicon", _("X-Picons")),
				("numberzapext-zpicon", _("Z-Picons")),
				("numberzapext-zzpicon", _("ZZ-Picons")),
				("numberzapext-zzzpicon", _("ZZZ-Picons"))
				])

config.plugins.KravenFHD.NZBorderList = ConfigSelection(default="ffffff", choices = ColorSelfList)
config.plugins.KravenFHD.NZBorderSelf = ConfigText(default="ffffff")
config.plugins.KravenFHD.NZBorder = ConfigText(default="ffffff")

config.plugins.KravenFHD.CoolTVGuide = ConfigSelection(default="cooltv-minitv", choices = [
				("cooltv-minitv", _("MiniTV")),
				("cooltv-picon", _("Picon"))
				])

config.plugins.KravenFHD.GraphMultiEPG = ConfigSelection(default="graphmultiepg-minitv", choices = [
				("graphmultiepg-minitv", _("MiniTV right")),
				("graphmultiepg-minitv2", _("MiniTV left")),
				("graphmultiepg", _("no MiniTV"))
				])

config.plugins.KravenFHD.GraphicalEPG = ConfigSelection(default="text-minitv", choices = [
				("text", _("Text")),
				("text-minitv", _("Text with MiniTV")),
				("graphical", _("graphical")),
				("graphical-minitv", _("graphical with MiniTV"))
				])

config.plugins.KravenFHD.GMEDescriptionSize = ConfigSelection(default="small", choices = [
				("small", _("small")),
				("big", _("big"))
				])

config.plugins.KravenFHD.GMErunningbgList = ConfigSelection(default="389416", choices = [
				("global", _("global selection background")),
				("389416", _("green")),
				("0064c7", _("blue")),
				("self", _("self"))
				])
config.plugins.KravenFHD.GMErunningbgSelf = ConfigText(default="389416")
config.plugins.KravenFHD.GMErunningbg = ConfigText(default="389416")

config.plugins.KravenFHD.GMEBorderList = ConfigSelection(default="ffffff", choices = ColorSelfList)
config.plugins.KravenFHD.GMEBorderSelf = ConfigText(default="ffffff")
config.plugins.KravenFHD.GMEBorder = ConfigText(default="ffffff")

config.plugins.KravenFHD.VerticalEPG = ConfigSelection(default="verticalepg-minitv", choices = [
				("verticalepg-minitv", _("MiniTV right")),
				("verticalepg-minitv2", _("MiniTV left")),
				("verticalepg-description", _("description")),
				("verticalepg-full", _("full"))
				])

config.plugins.KravenFHD.VerticalEPG2 = ConfigSelection(default="verticalepg-full", choices = [
				("verticalepg-minitv3", _("MiniTV")),
				("verticalepg-full", _("full"))
				])

config.plugins.KravenFHD.VEPGBorderList = ConfigSelection(default="ffffff", choices = ColorSelfList)
config.plugins.KravenFHD.VEPGBorderSelf = ConfigText(default="ffffff")
config.plugins.KravenFHD.VEPGBorder = ConfigText(default="ffffff")

config.plugins.KravenFHD.MovieSelection = ConfigSelection(default="movieselection-no-cover", choices = [
				("movieselection-no-cover", _("no Cover")),
				("movieselection-no-cover2", _("no Cover2")),
				("movieselection-small-cover", _("small Cover")),
				("movieselection-big-cover", _("big Cover")),
				("movieselection-minitv", _("MiniTV")),
				("movieselection-minitv-cover", _("MiniTV + Cover"))
				])

config.plugins.KravenFHD.MovieSelectionEPGSize = ConfigSelection(default="small", choices = [
				("small", _("small")),
				("big", _("big"))
				])

config.plugins.KravenFHD.EPGSelection = ConfigSelection(default="epgselection-standard", choices = [
				("epgselection-standard", _("standard")),
				("epgselection-minitv", _("MiniTV"))
				])

config.plugins.KravenFHD.EPGSelectionEPGSize = ConfigSelection(default="small", choices = [
				("small", _("small")),
				("big", _("big"))
				])

config.plugins.KravenFHD.EPGListSize = ConfigSelection(default="small", choices = [
				("small", _("small")),
				("big", _("big"))
				])

config.plugins.KravenFHD.EMCStyle = ConfigSelection(default="emc-minitv", choices = [
				("emc-nocover", _("no Cover")),
				("emc-nocover2", _("no Cover2")),
				("emc-smallcover", _("small Cover")),
				("emc-smallcover2", _("small Cover2")),
				("emc-bigcover", _("big Cover")),
				("emc-bigcover2", _("big Cover2")),
				("emc-verybigcover", _("very big Cover")),
				("emc-verybigcover2", _("very big Cover2")),
				("emc-minitv", _("MiniTV")),
				("emc-minitv2", _("MiniTV2")),
				("emc-full", _("full"))
				])

config.plugins.KravenFHD.EMCEPGSize = ConfigSelection(default="small", choices = [
				("small", _("small")),
				("big", _("big"))
				])

config.plugins.KravenFHD.RunningText = ConfigSelection(default="startdelay=4000", choices = [
				("none", _("off")),
				("startdelay=2000", _("2 sec")),
				("startdelay=4000", _("4 sec")),
				("startdelay=6000", _("6 sec")),
				("startdelay=8000", _("8 sec")),
				("startdelay=10000", _("10 sec")),
				("startdelay=15000", _("15 sec")),
				("startdelay=20000", _("20 sec"))
				])

config.plugins.KravenFHD.RunningTextSpeed = ConfigSelection(default="steptime=100", choices = [
				("steptime=200", _("5 px/sec")),
				("steptime=100", _("10 px/sec")),
				("steptime=50", _("20 px/sec")),
				("steptime=33", _("30 px/sec"))
				])

config.plugins.KravenFHD.ScrollBar = ConfigSelection(default="scrollbarWidth=0", choices = [
				("scrollbarWidth=0", _("off")),
				("scrollbarWidth=5", _("thin")),
				("scrollbarWidth=10", _("middle")),
				("scrollbarWidth=15", _("wide"))
				])
				
config.plugins.KravenFHD.ScrollBar2 = ConfigSelection(default="showOnDemand", choices = [
				("showOnDemand", _("on")),
				("showNever", _("off"))
				])

config.plugins.KravenFHD.IconStyle = ConfigSelection(default="icons-light", choices = [
				("icons-light", _("light")),
				("icons-dark", _("dark"))
				])

config.plugins.KravenFHD.IconStyle2 = ConfigSelection(default="icons-light2", choices = [
				("icons-light2", _("light")),
				("icons-dark2", _("dark"))
				])

config.plugins.KravenFHD.ClockStyle = ConfigSelection(default="clock-classic", choices = [
				("clock-classic", _("standard")),
				("clock-classic-big", _("standard big")),
				("clock-analog", _("analog")),
				("clock-android", _("android")),
				("clock-color", _("colored")),
				("clock-flip", _("flip")),
				("clock-weather", _("weather icon"))
				])

config.plugins.KravenFHD.ClockStyleNoInternet = ConfigSelection(default="clock-classic", choices = [
				("clock-classic", _("standard")),
				("clock-classic-big", _("standard big")),
				("clock-analog", _("analog")),
				("clock-color", _("colored")),
				("clock-flip", _("flip"))
				])

config.plugins.KravenFHD.ClockIconSize = ConfigSelection(default="size-144", choices = [
				("size-144", _("144")),
				("size-192", _("192"))
				])

config.plugins.KravenFHD.WeatherStyle = ConfigSelection(default="none", choices = [
				("none", _("off")),
				("weather-big", _("big")),
				("weather-small", _("small"))
				])

config.plugins.KravenFHD.WeatherStyle2 = ConfigSelection(default="none", choices = [
				("none", _("off")),
				("weather-left", _("on"))
				])

config.plugins.KravenFHD.WeatherStyle3 = ConfigSelection(default="none", choices = [
				("none", _("off")),
				("weather-left", _("on")),
				("netatmobar", _("NetatmoBar"))
				])

config.plugins.KravenFHD.WeatherStyleNoInternet = ConfigSelection(default="none", choices = [
				("none", _("off"))
				])

config.plugins.KravenFHD.ECMVisible = ConfigSelection(default="none", choices = [
				("none", _("off")),
				("ib", _("Infobar")),
				("sib", _("SecondInfobar")),
				("ib+sib", _("Infobar & SecondInfobar"))
				])

config.plugins.KravenFHD.ECMVisibleNA = ConfigSelection(default="na", choices = [
				("na", _("not available with selected Infobar-Style"))
				])

config.plugins.KravenFHD.ECMLine1 = ConfigSelection(default="ShortReader", choices = [
				("VeryShortCaid", _("short with CAID")),
				("VeryShortReader", _("short with source")),
				("ShortReader", _("compact"))
				])

config.plugins.KravenFHD.ECMLine2 = ConfigSelection(default="ShortReader", choices = [
				("VeryShortCaid", _("short with CAID")),
				("VeryShortReader", _("short with source")),
				("ShortReader", _("compact")),
				("Normal", _("balanced")),
				("Long", _("extensive")),
				("VeryLong", _("complete"))
				])

config.plugins.KravenFHD.ECMLine3 = ConfigSelection(default="ShortReader", choices = [
				("VeryShortCaid", _("short with CAID")),
				("VeryShortReader", _("short with source")),
				("ShortReader", _("compact")),
				("Normal", _("balanced")),
				("Long", _("extensive")),
				])

config.plugins.KravenFHD.FTA = ConfigSelection(default="FTAVisible", choices = [
				("FTAVisible", _("on")),
				("none", _("off"))
				])

config.plugins.KravenFHD.SystemInfo = ConfigSelection(default="none", choices = [
				("none", _("off")),
				("systeminfo-small", _("small")),
				("systeminfo-big", _("big")),
				("systeminfo-bigsat", _("big + Sat"))
				])

config.plugins.KravenFHD.SIB = ConfigSelection(default="sib4", choices = [
				("sib1", _("top/bottom")),
				("sib2", _("left/right")),
				("sib3", _("single")),
				("sib4", _("MiniTV")),
				("sib5", _("MiniTV2")),
				("sib6", _("Weather")),
				("sib7", _("Weather2"))
				])

config.plugins.KravenFHD.SIBFont = ConfigSelection(default="sibfont-big", choices = [
				("sibfont-big", _("big")),
				("sibfont-small", _("small"))
				])

config.plugins.KravenFHD.IBtop = ConfigSelection(default="infobar-x2-z1_top2", choices = [
				("infobar-x2-z1_top2", _("2 Tuner")),
				("infobar-x2-z1_top", _("4 Tuner")),
				("infobar-x2-z1_top3", _("8 Tuner"))
				])

config.plugins.KravenFHD.Infobox = ConfigSelection(default="sat", choices = [
				("sat", _("Tuner/Satellite + SNR")),
				("cpu", _("CPU + Load")),
				("temp", _("Temperature + Fan"))
				])
				
config.plugins.KravenFHD.Infobox2 = ConfigSelection(default="sat", choices = [
				("sat", _("Tuner/Satellite + SNR")),
				("db", _("Tuner/Satellite + dB")),
				("cpu", _("CPU + Load")),
				("temp", _("Temperature + Fan"))
				])

config.plugins.KravenFHD.tuner = ConfigSelection(default="4-tuner", choices = [
				("2-tuner", _("2 Tuner")),
				("4-tuner", _("4 Tuner")),
				("8-tuner", _("8 Tuner"))
				])

config.plugins.KravenFHD.tuner2 = ConfigSelection(default="4-tuner", choices = [
				("2-tuner", _("2 Tuner")),
				("4-tuner", _("4 Tuner")),
				("8-tuner", _("8 Tuner")),
				("10-tuner", _("10 Tuner"))
				])

config.plugins.KravenFHD.record = ConfigSelection(default="record-shine", choices = [
				("record-blink", _("record blink")),
				("record-shine", _("record shine"))
				])

config.plugins.KravenFHD.record2 = ConfigSelection(default="record-shine+no-record-tuner", choices = [
				("record-blink+tuner-shine", _("record blink, tuner shine")),
				("record-shine+tuner-blink", _("record shine, tuner blink")),
				("record+tuner-blink", _("record & tuner blink")),
				("record+tuner-shine", _("record & tuner shine")),
				("record-blink+no-record-tuner", _("record blink, no record tuner")),
				("record-shine+no-record-tuner", _("record shine, no record tuner"))
				])

config.plugins.KravenFHD.record3 = ConfigSelection(default="no-record-tuner", choices = [
				("tuner-blink", _("tuner blink")),
				("tuner-shine", _("tuner shine")),
				("no-record-tuner", _("no record tuner"))
				])

config.plugins.KravenFHD.IBColor = ConfigSelection(default="all-screens", choices = [
				("all-screens", _("in all Screens")),
				("only-infobar", _("only Infobar, SecondInfobar & Players"))
				])

config.plugins.KravenFHD.About = ConfigSelection(default="about", choices = [
				("about", _("KravenFHD"))
				])

config.plugins.KravenFHD.Logo = ConfigSelection(default="minitv", choices = [
				("logo", _("Logo")),
				("minitv", _("MiniTV")),
				("metrix-icons", _("Icons")),
				("minitv-metrix-icons", _("MiniTV + Icons"))
				])

config.plugins.KravenFHD.LogoNoInternet = ConfigSelection(default="minitv", choices = [
				("logo", _("Logo")),
				("minitv", _("MiniTV"))
				])

config.plugins.KravenFHD.MainmenuFontsize = ConfigSelection(default="mainmenu-big", choices = [
				("mainmenu-small", _("small")),
				("mainmenu-middle", _("middle")),
				("mainmenu-big", _("big"))
				])

config.plugins.KravenFHD.MenuIcons = ConfigSelection(default="stony272", choices = [
				("stony272", _("stony272")),
				("stony272-metal", _("stony272-metal")),
				("stony272-gold-round", _("stony272-gold-round")),
				("stony272-gold-square", _("stony272-gold-square")),
				("rennmaus-kleinerteufel", _("rennmaus-kleiner.teufel"))
				])

config.plugins.KravenFHD.DebugNames = ConfigSelection(default="none", choices = [
				("none", _("off")),
				("screennames-on", _("on"))
				])

config.plugins.KravenFHD.WeatherView = ConfigSelection(default="meteo", choices = [
				("icon", _("Icon")),
				("meteo", _("Meteo"))
				])

config.plugins.KravenFHD.MeteoColor = ConfigSelection(default="meteo-light", choices = [
				("meteo-light", _("light")),
				("meteo-dark", _("dark"))
				])

config.plugins.KravenFHD.Primetimeavailable = ConfigSelection(default="primetime-on", choices = [
				("none", _("off")),
				("primetime-on", _("on"))
				])

config.plugins.KravenFHD.EMCSelectionColors = ConfigSelection(default="emc-colors-on", choices = [
				("none", _("off")),
				("emc-colors-on", _("on"))
				])

config.plugins.KravenFHD.EMCSelectionBackgroundList = ConfigSelection(default="213305", choices = ColorSelfList)
config.plugins.KravenFHD.EMCSelectionBackgroundSelf = ConfigText(default="213305")
config.plugins.KravenFHD.EMCSelectionBackground = ConfigText(default="213305")

config.plugins.KravenFHD.EMCSelectionFontList = ConfigSelection(default="ffffff", choices = ColorSelfList)
config.plugins.KravenFHD.EMCSelectionFontSelf = ConfigText(default="ffffff")
config.plugins.KravenFHD.EMCSelectionFont = ConfigText(default="ffffff")

config.plugins.KravenFHD.SerienRecorder = ConfigSelection(default="none", choices = [
				("none", _("off")),
				("serienrecorder", _("on"))
				])

config.plugins.KravenFHD.MediaPortal = ConfigSelection(default="none", choices = [
				("none", _("off")),
				("mediaportal", _("on"))
				])

config.plugins.KravenFHD.PVRState = ConfigSelection(default="pvrstate-center-big", choices = [
				("pvrstate-center-big", _("center big")),
				("pvrstate-center-small", _("center small")),
				("pvrstate-left-small", _("left small")),
				("pvrstate-off", _("off"))
				])

config.plugins.KravenFHD.PigStyle = ConfigText(default="")
config.plugins.KravenFHD.PigMenuActive = ConfigYesNo(default=False)

config.plugins.KravenFHD.SplitScreen = ConfigSelection(default="splitscreen1", choices = [
				("splitscreen1", _("without description")),
				("splitscreen2", _("with description"))
				])

config.plugins.KravenFHD.FileCommander = ConfigSelection(default="filecommander-hor", choices = [
				("filecommander-hor", _("horizontal")),
				("filecommander-ver", _("vertical"))
				])

config.plugins.KravenFHD.TimerEditScreen = ConfigSelection(default="timer-standard", choices = [
				("timer-standard", _("standard layout")),
				("timer-medium", _("medium font with EPG Info")),
				("timer-big", _("big font with EPG Info"))
				])

config.plugins.KravenFHD.TimerListStyle = ConfigSelection(default="timerlist-standard", choices = [
				("timerlist-standard", _("standard")),
				("timerlist-1", _("Style 1")),
				("timerlist-2", _("Style 2")),
				("timerlist-3", _("Style 3")),
				("timerlist-4", _("Style 4")),
				("timerlist-5", _("Style 5"))
				])

config.plugins.KravenFHD.weather_cityname = ConfigText(default = "")
config.plugins.KravenFHD.weather_language = ConfigSelection(default="de", choices = LanguageList)
config.plugins.KravenFHD.weather_server = ConfigSelection(default="_owm", choices = [
				("_owm", _("OpenWeatherMap")),
				("_accu", _("Accuweather"))
				])

config.plugins.KravenFHD.weather_search_over = ConfigSelection(default="ip", choices = [
				("ip", _("Auto (IP)")),
				("name", _("Search String"))
				])

config.plugins.KravenFHD.weather_owm_latlon = ConfigText(default = "")
config.plugins.KravenFHD.weather_accu_apikey = ConfigText(default = "")
config.plugins.KravenFHD.weather_accu_id = ConfigText(default = "")
config.plugins.KravenFHD.weather_foundcity = ConfigText(default = "")

config.plugins.KravenFHD.PlayerClock = ConfigSelection(default="player-classic", choices = [
				("player-classic", _("standard")),
				("player-android", _("android")),
				("player-flip", _("flip")),
				("player-weather", _("weather icon"))
				])

config.plugins.KravenFHD.Android2List = ConfigSelection(default="000000", choices = ColorSelfList)
config.plugins.KravenFHD.Android2Self = ConfigText(default="000000")
config.plugins.KravenFHD.Android2 = ConfigText(default="000000")

config.plugins.KravenFHD.CategoryProfiles = ConfigSelection(default="category", choices = [
				("category", _(" "))
				])

config.plugins.KravenFHD.CategorySystem = ConfigSelection(default="category", choices = [
				("category", _(" "))
				])

config.plugins.KravenFHD.CategoryGlobalColors = ConfigSelection(default="category", choices = [
				("category", _(" "))
				])

config.plugins.KravenFHD.CategoryInfobarLook = ConfigSelection(default="category", choices = [
				("category", _(" "))
				])

config.plugins.KravenFHD.CategoryInfobarContents = ConfigSelection(default="category", choices = [
				("category", _(" "))
				])

config.plugins.KravenFHD.CategorySIB = ConfigSelection(default="category", choices = [
				("category", _(" "))
				])

config.plugins.KravenFHD.CategoryWeather = ConfigSelection(default="category", choices = [
				("category", _(" "))
				])

config.plugins.KravenFHD.CategoryClock = ConfigSelection(default="category", choices = [
				("category", _(" "))
				])

config.plugins.KravenFHD.CategoryECMInfos = ConfigSelection(default="category", choices = [
				("category", _(" "))
				])

config.plugins.KravenFHD.CategoryViews = ConfigSelection(default="category", choices = [
				("category", _(" "))
				])

config.plugins.KravenFHD.CategoryPermanentClock = ConfigSelection(default="category", choices = [
				("category", _(" "))
				])

config.plugins.KravenFHD.CategoryChannellist = ConfigSelection(default="category", choices = [
				("category", _(" "))
				])

config.plugins.KravenFHD.CategoryNumberZap = ConfigSelection(default="category", choices = [
				("category", _(" "))
				])

config.plugins.KravenFHD.CategoryEPGSelection = ConfigSelection(default="category", choices = [
				("category", _(" "))
				])

config.plugins.KravenFHD.CategoryGraphMultiEPG = ConfigSelection(default="category", choices = [
				("category", _(" "))
				])

config.plugins.KravenFHD.CategoryGraphicalEPG = ConfigSelection(default="category", choices = [
				("category", _(" "))
				])

config.plugins.KravenFHD.CategoryVerticalEPG = ConfigSelection(default="category", choices = [
				("category", _(" "))
				])

config.plugins.KravenFHD.CategoryTimerEdit = ConfigSelection(default="category", choices = [
				("category", _(" "))
				])

config.plugins.KravenFHD.CategoryEMC = ConfigSelection(default="category", choices = [
				("category", _(" "))
				])

config.plugins.KravenFHD.CategoryMovieSelection = ConfigSelection(default="category", choices = [
				("category", _(" "))
				])

config.plugins.KravenFHD.CategoryPlayers = ConfigSelection(default="category", choices = [
				("category", _(" "))
				])

config.plugins.KravenFHD.CategoryAntialiasing = ConfigSelection(default="category", choices = [
				("category", _(" "))
				])

config.plugins.KravenFHD.CategoryVarious = ConfigSelection(default="category", choices = [
				("category", _(" "))
				])

config.plugins.KravenFHD.Unskinned = ConfigSelection(default="none", choices = [
				("none", _("off")),
				("unskinned-colors-on", _("on"))
				])

config.plugins.KravenFHD.UnwatchedColorList = ConfigSelection(default="ffffff", choices = ColorSelfList)
config.plugins.KravenFHD.UnwatchedColorSelf = ConfigText(default="ffffff")
config.plugins.KravenFHD.UnwatchedColor = ConfigText(default="ffffff")

config.plugins.KravenFHD.WatchingColorList = ConfigSelection(default="0050EF", choices = ColorSelfList)
config.plugins.KravenFHD.WatchingColorSelf = ConfigText(default="0050EF")
config.plugins.KravenFHD.WatchingColor = ConfigText(default="0050EF")

config.plugins.KravenFHD.FinishedColorList = ConfigSelection(default="70AD11", choices = ColorSelfList)
config.plugins.KravenFHD.FinishedColorSelf = ConfigText(default="70AD11")
config.plugins.KravenFHD.FinishedColor = ConfigText(default="70AD11")

config.plugins.KravenFHD.PermanentClock = ConfigSelection(default="permanentclock-infobar-big", choices = [
				("permanentclock-infobar-big", _("infobar colors big")),
				("permanentclock-infobar-small", _("infobar colors small")),
				("permanentclock-global-big", _("global colors big")),
				("permanentclock-global-small", _("global colors small")),
				("permanentclock-transparent-big", _("transparent big")),
				("permanentclock-transparent-small", _("transparent small"))
				])

config.plugins.KravenFHD.ATVna = ConfigSelection(default="na", choices = [
				("na", _("not available for openATV"))
				])

config.plugins.KravenFHD.TBna = ConfigSelection(default="na", choices = [
				("na", _("not available for teamBlue"))
				])

config.plugins.KravenFHD.KravenIconVPosition = ConfigSelection(default="vposition0", choices = [
				("vposition-3", _("-3")),
				("vposition-2", _("-2")),
				("vposition-1", _("-1")),
				("vposition0", _("0")),
				("vposition+1", _("+1")),
				("vposition+2", _("+2")),
				("vposition+3", _("+3"))
				])

config.plugins.KravenFHD.InfobarSelfColorR = ConfigSlider(default=0, increment=15, limits=(0,255))
config.plugins.KravenFHD.InfobarSelfColorG = ConfigSlider(default=0, increment=15, limits=(0,255))
config.plugins.KravenFHD.InfobarSelfColorB = ConfigSlider(default=0, increment=15, limits=(0,255))
config.plugins.KravenFHD.BackgroundSelfColorR = ConfigSlider(default=0, increment=15, limits=(0,255))
config.plugins.KravenFHD.BackgroundSelfColorG = ConfigSlider(default=0, increment=15, limits=(0,255))
config.plugins.KravenFHD.BackgroundSelfColorB = ConfigSlider(default=75, increment=15, limits=(0,255))
config.plugins.KravenFHD.OldColorsCopied = ConfigBoolean(default = False)

#######################################################################

class KravenFHD(ConfigListScreen, Screen):

	if DESKTOP_WIDTH <= 1280:
	  skin = """
<screen name="KravenFHD-Setup" position="0,0" size="1280,720" flags="wfNoBorder" backgroundColor="#00000000">
  <widget backgroundColor="#00000000" source="Title" render="Label" font="Regular;35" foregroundColor="#00f0a30a" position="70,12" size="708,46" valign="center" transparent="1" />
  <widget backgroundColor="#00000000" source="global.CurrentTime" render="Label" font="Regular;26" foregroundColor="#00ffffff" position="1138,22" size="100,28" halign="right" valign="center" transparent="1">
    <convert type="ClockToText">Default</convert>
  </widget>
  <widget backgroundColor="#00000000" name="config" font="Regular;22" foregroundColor="#00ffffff" itemHeight="30" position="70,85" size="708,540" enableWrapAround="1" scrollbarMode="showOnDemand" transparent="1" zPosition="1" />
  <eLabel backgroundColor="#00000000" text="KravenFHD" font="Regular;36" foregroundColor="#00f0a30a" position="830,80" size="402,46" halign="center" valign="center" transparent="1" />
  <widget backgroundColor="#00000000" source="version" render="Label" font="Regular;30" foregroundColor="#00ffffff" position="845,126" size="372,40" halign="center" valign="center" transparent="1" />
  <eLabel backgroundColor="#00f0a30a" position="798,169" size="466,3" />
  <eLabel backgroundColor="#00f0a30a" position="798,431" size="466,3" />
  <eLabel backgroundColor="#00f0a30a" position="798,172" size="3,259" />
  <eLabel backgroundColor="#00f0a30a" position="1261,172" size="3,259" />
  <widget backgroundColor="#00000000" name="helperimage" position="801,172" size="460,259" zPosition="1" />
  <widget backgroundColor="#00000000" source="Canvas" render="Canvas" position="801,172" size="460,259" zPosition="-1" />
  <widget backgroundColor="#00000000" source="help" render="Label" font="Regular;20" foregroundColor="#00f0a30a" position="847,440" size="368,196" halign="center" valign="top" transparent="1" />
  <widget backgroundColor="#00000000" source="key_red" render="Label" font="Regular;20" foregroundColor="#00ffffff" position="70,665" size="220,26" valign="center" transparent="1" zPosition="1" />
  <widget backgroundColor="#00000000" source="key_green" render="Label" font="Regular;20" foregroundColor="#00ffffff" position="320,665" size="220,26" valign="center" transparent="1" zPosition="1" />
  <widget backgroundColor="#00000000" source="key_yellow" render="Label" font="Regular;20" foregroundColor="#00ffffff" position="570,665" size="220,26" valign="center" transparent="1" zPosition="1" />
  <widget backgroundColor="#00000000" source="key_blue" render="Label" font="Regular;20" foregroundColor="#00ffffff" position="820,665" size="220,26" valign="center" transparent="1" zPosition="1" />
  <eLabel backgroundColor="#00E61805" position="65,692" size="150,5" />
  <eLabel backgroundColor="#005FE500" position="315,692" size="150,5" />
  <eLabel backgroundColor="#00E5DD00" position="565,692" size="150,5" />
  <eLabel backgroundColor="#000082E5" position="815,692" size="150,5" />
  <eLabel backgroundColor="#00000000" position="0,0" size="1280,720" transparent="0" zPosition="-9" />
</screen>
"""
	else:
	  skin = """
<screen name="KravenFHD-Setup" position="0,0" size="1920,1080" flags="wfNoBorder" backgroundColor="#00000000">
  <widget backgroundColor="#00000000" source="Title" render="Label" font="Regular;51" foregroundColor="#00f0a30a" position="105,18" size="1500,69" valign="center" transparent="1" />
  <widget backgroundColor="#00000000" source="global.CurrentTime" render="Label" font="Regular;39" foregroundColor="#00ffffff" position="1707,33" size="150,42" halign="right" valign="center" transparent="1">
    <convert type="ClockToText">Default</convert>
  </widget>
  <widget backgroundColor="#00000000" name="config" font="Regular;32" foregroundColor="#00ffffff" itemHeight="45" position="105,127" size="1062,810" enableWrapAround="1" scrollbarMode="showOnDemand" transparent="1" zPosition="1" />
  <eLabel backgroundColor="#00000000" text="KravenFHD" font="Regular;54" foregroundColor="#00f0a30a" position="1245,120" size="603,69" halign="center" valign="center" transparent="1" />
  <widget backgroundColor="#00000000" source="version" render="Label" font="Regular;45" foregroundColor="#00ffffff" position="1267,208" size="558,60" halign="center" valign="center" transparent="1" />
  <eLabel backgroundColor="#00f0a30a" position="1313,337" size="466,3" />
  <eLabel backgroundColor="#00f0a30a" position="1313,599" size="466,3" />
  <eLabel backgroundColor="#00f0a30a" position="1313,340" size="3,259" />
  <eLabel backgroundColor="#00f0a30a" position="1776,340" size="3,259" />
  <widget backgroundColor="#00000000" name="helperimage" position="1316,340" size="460,259" zPosition="1" />
  <widget backgroundColor="#00000000" source="Canvas" render="Canvas" position="1316,340" size="460,259" zPosition="-1" />
  <widget backgroundColor="#00000000" source="help" render="Label" font="Regular;30" foregroundColor="#00f0a30a" position="1270,660" size="552,294" halign="center" valign="top" transparent="1" />
  <widget backgroundColor="#00000000" source="key_red" render="Label" font="Regular;30" foregroundColor="#00ffffff" position="105,997" size="330,39" valign="center" transparent="1" zPosition="1" />
  <widget backgroundColor="#00000000" source="key_green" render="Label" font="Regular;30" foregroundColor="#00ffffff" position="480,997" size="330,39" valign="center" transparent="1" zPosition="1" />
  <widget backgroundColor="#00000000" source="key_yellow" render="Label" font="Regular;30" foregroundColor="#00ffffff" position="855,997" size="330,39" valign="center" transparent="1" zPosition="1" />
  <widget backgroundColor="#00000000" source="key_blue" render="Label" font="Regular;30" foregroundColor="#00ffffff" position="1230,997" size="330,39" valign="center" transparent="1" zPosition="1" />
  <ePixmap backgroundColor="#00000000" pixmap="KravenFHD/buttons/key_red1.png" position="97,1038" size="300,7" alphatest="blend" />
  <ePixmap backgroundColor="#00000000" pixmap="KravenFHD/buttons/key_green1.png" position="472,1038" size="300,7" alphatest="blend" />
  <ePixmap backgroundColor="#00000000" pixmap="KravenFHD/buttons/key_yellow1.png" position="847,1038" size="300,7" alphatest="blend" />
  <ePixmap backgroundColor="#00000000" pixmap="KravenFHD/buttons/key_blue1.png" position="1222,1038" size="300,7" alphatest="blend" />
  <eLabel backgroundColor="#00000000" position="0,0" size="1920,1080" transparent="0" zPosition="-9" />
</screen>
"""

	def __init__(self, session, args = None, picPath = None):
		self.skin_lines = []
		Screen.__init__(self, session)
		self.session = session
		self.datei = "/usr/share/enigma2/KravenFHD/skin.xml"
		self.dateiTMP = self.datei + ".tmp"
		self.daten = "/usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/data/"
		self.komponente = "/usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/comp/"
		self.picPath = "/usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/images/"
		self.profiles = "/etc/enigma2/"
		self.Scale = AVSwitch().getFramebufferScale()
		self.PicLoad = ePicLoad()
		self["helperimage"] = Pixmap()
		self["Canvas"] = CanvasSource()
		self["help"] = StaticText()
		self["version"] = StaticText()

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
			"red": self.faq,
			"green": self.save,
			"yellow": self.categoryDown,
			"blue": self.categoryUp,
			"cancel": self.exit,
			"pageup": self.pageUp,
			"papedown": self.pageDown,
			"ok": self.OK
		}, -1)

		self["key_red"] = StaticText(_("FAQs"))
		self["key_green"] = StaticText(_("Save skin"))
		self["key_yellow"] = StaticText()
		self["key_blue"] = StaticText()
		self["Title"] = StaticText(_("Configuration tool for KravenFHD"))

		self.UpdatePicture()

		self.timer = eTimer()
		self.timer.callback.append(self.updateMylist)
		self.onLayoutFinish.append(self.updateMylist)

		self.lastProfile="0"

		self.actClockstyle=""
		self.actWeatherstyle=""
		self.actChannelselectionstyle=""
		self.actCity=""
		
		self.skincolorinfobarcolor=""
		self.skincolorbackgroundcolor=""
		
		self.actListColorSelection=None
		self.actSelfColorSelection=None

		self.BoxName=self.getBoxName()
		self.E2DistroVersion=self.getE2DistroVersion()
		self.InternetAvailable=self.getInternetAvailable()
		self.UserMenuIconsAvailable=self.getUserMenuIconsAvailable()

		if config.plugins.KravenFHD.OldColorsCopied.value==False:
			self.copyOldColors()
			config.plugins.KravenFHD.OldColorsCopied.value=True

	def mylist(self):
		self.timer.start(100, True)

	def updateMylist(self):
		
		if config.plugins.KravenFHD.customProfile.value!=self.lastProfile:
			self.loadProfile()
			self.lastProfile=config.plugins.KravenFHD.customProfile.value
		
		# page 1
		emptyLines=0
		list = []
		list.append(getConfigListEntry(_("About"), config.plugins.KravenFHD.About, _("The KravenFHD skin will be generated by this plugin according to your preferences. Make your settings and watch the changes in the preview window above. When finished, save your skin by pressing the green button and restart the GUI.")))
		list.append(getConfigListEntry(_(" "), ))
		list.append(getConfigListEntry(_("PROFILES __________________________________________________________________"), config.plugins.KravenFHD.CategoryProfiles, _("This sections offers all profile settings. Different settings can be saved, modified, shared and cloned. Read the FAQs.")))
		list.append(getConfigListEntry(_("Active Profile / Save"), config.plugins.KravenFHD.customProfile, _("Select the profile you want to work with. Profiles are saved automatically on switching them or by pressing the OK button. New profiles will be generated based on the actual one. Profiles are interchangeable between boxes.")))
		list.append(getConfigListEntry(_("Default Profile / Reset"), config.plugins.KravenFHD.defaultProfile, _("Select the default profile you want to use when resetting the active profile (OK button). You can add your own default profiles under /etc/enigma2/kravenfhd_default_n (n<=20).")))
		list.append(getConfigListEntry(_(" "), ))
		list.append(getConfigListEntry(_("SYSTEM ____________________________________________________________________"), config.plugins.KravenFHD.CategorySystem, _("This sections offers all basic settings.")))
		list.append(getConfigListEntry(_("Icons (except Infobar)"), config.plugins.KravenFHD.IconStyle2, _("Choose between light and dark icons in system screens. The icons in the infobars are not affected.")))
		list.append(getConfigListEntry(_("Running Text (Delay)"), config.plugins.KravenFHD.RunningText, _("Choose the start delay for running text.")))
		if not config.plugins.KravenFHD.RunningText.value == "none":
			list.append(getConfigListEntry(_("Running Text (Speed)"), config.plugins.KravenFHD.RunningTextSpeed, _("Choose the speed for running text.")))
		else:
			emptyLines+=1
		if self.E2DistroVersion == "VTi":
			list.append(getConfigListEntry(_("Scrollbars"), config.plugins.KravenFHD.ScrollBar, _("Choose the width of scrollbars in lists or deactivate scrollbars completely.")))
		elif self.E2DistroVersion in ("openatv","teamblue"):
			list.append(getConfigListEntry(_("Scrollbars"), config.plugins.KravenFHD.ScrollBar2, _("Choose whether scrollbars should be shown.")))
		list.append(getConfigListEntry(_("Show Infobar-Background"), config.plugins.KravenFHD.IBColor, _("Choose whether you want to see the infobar background in all screens (bicolored background).")))
		if self.InternetAvailable or self.UserMenuIconsAvailable:
			list.append(getConfigListEntry(_("Menus"), config.plugins.KravenFHD.Logo, _("Choose from different options to display the system menus. Press red button for the FAQs with details on installing menu icons.")))
			if config.plugins.KravenFHD.Logo.value in ("metrix-icons","minitv-metrix-icons") and self.InternetAvailable:
				list.append(getConfigListEntry(_("Menu-Icons"), config.plugins.KravenFHD.MenuIcons, _("Choose from different icon sets for the menu screens. Many thanks to rennmaus and kleiner.teufel for their icon set.")))
			else:
				emptyLines+=1
			if config.plugins.KravenFHD.Logo.value in ("logo","metrix-icons"):
				list.append(getConfigListEntry(_("Menu-Transparency"), config.plugins.KravenFHD.MenuColorTrans, _("Choose the degree of background transparency for system menu screens.")))
			else:
				emptyLines+=1
			list.append(getConfigListEntry(_("Mainmenu Fontsize"), config.plugins.KravenFHD.MainmenuFontsize, _("Choose the font size of mainmenus.")))
			for i in range(emptyLines+2):
				list.append(getConfigListEntry(_(" "), ))
		else:
			list.append(getConfigListEntry(_("Menus"), config.plugins.KravenFHD.LogoNoInternet, _("Choose from different options to display the system menus. Press red button for the FAQs with details on installing menu icons.")))
			if config.plugins.KravenFHD.LogoNoInternet.value == "logo":
				list.append(getConfigListEntry(_("Menu-Transparency"), config.plugins.KravenFHD.MenuColorTrans, _("Choose the degree of background transparency for system menu screens.")))
			else:
				emptyLines+=1
			list.append(getConfigListEntry(_("Mainmenu Fontsize"), config.plugins.KravenFHD.MainmenuFontsize, _("Choose the font size of mainmenus.")))
			for i in range(emptyLines+3):
				list.append(getConfigListEntry(_(" "), ))
		
		# page 2
		emptyLines=0
		list.append(getConfigListEntry(_("GLOBAL COLORS _____________________________________________________________"), config.plugins.KravenFHD.CategoryGlobalColors, _("This sections offers offers all basic color settings.")))
		list.append(getConfigListEntry(_("Background"), config.plugins.KravenFHD.BackgroundListColor, _("Choose the background for all screens. You can choose from a list of predefined colors or textures, create your own color using RGB sliders or define a color gradient.")))
		if config.plugins.KravenFHD.BackgroundListColor.value == "gradient":
			list.append(getConfigListEntry(_("          Primary Color"), config.plugins.KravenFHD.BackgroundGradientListColorPrimary, _("Choose the primary color for the background gradient. Press OK to define your own RGB color.")))
			list.append(getConfigListEntry(_("          Secondary Color"), config.plugins.KravenFHD.BackgroundGradientListColorSecondary, _("Choose the secondary color for the background gradient. Press OK to define your own RGB color.")))
			emptyLines+=1
		elif config.plugins.KravenFHD.BackgroundListColor.value == "texture":
			list.append(getConfigListEntry(_("          Texture"), config.plugins.KravenFHD.BackgroundTexture, _("Choose the texture for the background.")))
			list.append(getConfigListEntry(_("          Alternate Color"), config.plugins.KravenFHD.BackgroundAlternateListColor, _("Choose the alternate color for the background. It should match the texture at the best. Press OK to define your own RGB color.")))
			emptyLines+=1
		else:
			emptyLines+=3
		list.append(getConfigListEntry(_("Background-Transparency"), config.plugins.KravenFHD.BackgroundColorTrans, _("Choose the degree of background transparency for all screens except system menus and channellists.")))
		list.append(getConfigListEntry(_("Listselection"), config.plugins.KravenFHD.SelectionBackgroundList, _("Choose the background color of selection bars. Press OK to define your own RGB color.")))
		list.append(getConfigListEntry(_("Listselection-Border"), config.plugins.KravenFHD.SelectionBorderList, _("Choose the border color of selection bars or deactivate borders completely. Press OK to define your own RGB color.")))
		list.append(getConfigListEntry(_("Listselection-Font"), config.plugins.KravenFHD.SelectionFontList, _("Choose the color of the font in selection bars. Press OK to define your own RGB color.")))
		list.append(getConfigListEntry(_("Progress-/Volumebar"), config.plugins.KravenFHD.ProgressList, _("Choose the color of progress bars. Press OK to define your own RGB color.")))
		list.append(getConfigListEntry(_("Progress-Border"), config.plugins.KravenFHD.BorderList, _("Choose the border color of progress bars. Press OK to define your own RGB color.")))
		list.append(getConfigListEntry(_("MiniTV-Border"), config.plugins.KravenFHD.MiniTVBorderList, _("Choose the border color of MiniTV's. Press OK to define your own RGB color.")))
		list.append(getConfigListEntry(_("Lines"), config.plugins.KravenFHD.LineList, _("Choose the color of all lines. This affects dividers as well as the line in the center of some progress bars. Press OK to define your own RGB color.")))
		list.append(getConfigListEntry(_("Primary-Font"), config.plugins.KravenFHD.Font1List, _("Choose the color of the primary font. The primary font is used for list items, textboxes and other important information. Press OK to define your own RGB color.")))
		list.append(getConfigListEntry(_("Secondary-Font"), config.plugins.KravenFHD.Font2List, _("Choose the color of the secondary font. The secondary font is used for headers, labels and other additional information. Press OK to define your own RGB color.")))
		list.append(getConfigListEntry(_("Marking-Font"), config.plugins.KravenFHD.MarkedFontList, _("Choose the font color of marked list items. Press OK to define your own RGB color.")))
		list.append(getConfigListEntry(_("Colorbutton-Font"), config.plugins.KravenFHD.ButtonTextList, _("Choose the font color of the color button labels. Press OK to define your own RGB color.")))
		list.append(getConfigListEntry(_("Unskinned Colors"), config.plugins.KravenFHD.Unskinned, _("Choose whether some foreground and background colors of unskinned screens are changed or not.")))
		for i in range(emptyLines):
			list.append(getConfigListEntry(_(" "), ))
		
		# page 3
		emptyLines=0
		list.append(getConfigListEntry(_("INFOBAR-LOOK _________________________________________________________________"), config.plugins.KravenFHD.CategoryInfobarLook, _("This sections offers all settings for the infobar-look.")))
		list.append(getConfigListEntry(_("Infobar-Style"), config.plugins.KravenFHD.InfobarStyle, _("Choose from different infobar styles. Please note that not every style provides every feature. Therefore some features might be unavailable for the chosen style.")))
		list.append(getConfigListEntry(_("Infobar-Background-Style"), config.plugins.KravenFHD.IBStyle, _("Choose from different infobar background styles.")))
		if config.plugins.KravenFHD.IBStyle.value == "box":
			list.append(getConfigListEntry(_("Infobar-Box-Line"), config.plugins.KravenFHD.IBLineList, _("Choose the color of the infobar box lines. Press OK to define your own RGB color.")))
		else:
			emptyLines+=1
		if config.plugins.KravenFHD.IBStyle.value == "grad":
			list.append(getConfigListEntry(_("Infobar-Background"), config.plugins.KravenFHD.InfobarGradientListColor, _("Choose the background for the infobars. You can choose from a list of predefined colors or textures or create your own color using RGB sliders.")))
		else:
			list.append(getConfigListEntry(_("Infobar-Background"), config.plugins.KravenFHD.InfobarBoxListColor, _("Choose the background for the infobars. You can choose from a list of predefined colors or textures, create your own color using RGB sliders or define a color gradient.")))
		if config.plugins.KravenFHD.IBStyle.value == "box" and config.plugins.KravenFHD.InfobarBoxListColor.value == "gradient":
			list.append(getConfigListEntry(_("          Primary Color"), config.plugins.KravenFHD.InfobarGradientListColorPrimary, _("Choose the primary color for the infobar gradient. Press OK to define your own RGB color.")))
			list.append(getConfigListEntry(_("          Secondary Color"), config.plugins.KravenFHD.InfobarGradientListColorSecondary, _("Choose the secondary color for the infobar gradient. Press OK to define your own RGB color.")))
			list.append(getConfigListEntry(_("          Info Panels"), config.plugins.KravenFHD.InfoStyle, _("Choose gradient or color for the info panels (Sysinfos, Timeshiftbar etc.).")))
		elif config.plugins.KravenFHD.IBStyle.value == "box" and config.plugins.KravenFHD.InfobarBoxListColor.value == "texture":
			list.append(getConfigListEntry(_("          Texture"), config.plugins.KravenFHD.InfobarTexture, _("Choose the texture for the infobars.")))
			list.append(getConfigListEntry(_("          Alternate Color"), config.plugins.KravenFHD.InfobarAlternateListColor, _("Choose the alternate color for the infobars. It should match the texture at the best. Press OK to define your own RGB color.")))
			emptyLines+=1
		elif config.plugins.KravenFHD.IBStyle.value == "grad" and config.plugins.KravenFHD.InfobarGradientListColor.value == "texture":
			list.append(getConfigListEntry(_("          Texture"), config.plugins.KravenFHD.InfobarTexture, _("Choose the texture for the infobars.")))
			list.append(getConfigListEntry(_("          Alternate Color"), config.plugins.KravenFHD.InfobarAlternateListColor, _("Choose the alternate color for the infobars. It should match the texture at the best. Press OK to define your own RGB color.")))
			emptyLines+=1
		else:
			emptyLines+=3
		list.append(getConfigListEntry(_("Infobar-Transparency"), config.plugins.KravenFHD.InfobarColorTrans, _("Choose the degree of background transparency for the infobars.")))
		list.append(getConfigListEntry(_("Primary-Infobar-Font"), config.plugins.KravenFHD.IBFont1List, _("Choose the color of the primary infobar font. Press OK to define your own RGB color.")))
		list.append(getConfigListEntry(_("Secondary-Infobar-Font"), config.plugins.KravenFHD.IBFont2List, _("Choose the color of the secondary infobar font. Press OK to define your own RGB color.")))
		list.append(getConfigListEntry(_("Infobar-Icons"), config.plugins.KravenFHD.IconStyle, _("Choose between light and dark infobar icons.")))
		list.append(getConfigListEntry(_("Eventname Fontsize"), config.plugins.KravenFHD.IBFontSize, _("Choose the font size of eventname.")))
		list.append(getConfigListEntry(_("Eventname effect"), config.plugins.KravenFHD.TypeWriter, _("Choose from different effects to display eventname.")))
		for i in range(emptyLines+4):
			list.append(getConfigListEntry(_(" "), ))
		
		# page 4
		emptyLines=0
		list.append(getConfigListEntry(_("INFOBAR-CONTENTS _____________________________________________________________"), config.plugins.KravenFHD.CategoryInfobarContents, _("This sections offers all settings for infobar-contents.")))
		if config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-x2","infobar-style-z1"):
			list.append(getConfigListEntry(_("Tuner number"), config.plugins.KravenFHD.IBtop, _("Choose from different options to display tuner.")))
		elif config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-nopicon","infobar-style-x1"):
			list.append(getConfigListEntry(_("Tuner number"), config.plugins.KravenFHD.tuner2, _("Choose from different options to display tuner.")))
		elif config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-zz1","infobar-style-zz4","infobar-style-zzz1"):
			list.append(getConfigListEntry(_("Tuner number"), config.plugins.KravenFHD.tuner, _("Choose from different options to display tuner.")))
		else:
			emptyLines+=1
		if config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-nopicon","infobar-style-x1","infobar-style-zz1","infobar-style-zz4","infobar-style-zzz1","infobar-style-zzz2"):
			list.append(getConfigListEntry(_("Record-State"), config.plugins.KravenFHD.record2, _("Choose from different options to display recording state.")))
		elif config.plugins.KravenFHD.InfobarStyle.value == "infobar-style-zz2":
			list.append(getConfigListEntry(_("Record-State"), config.plugins.KravenFHD.record, _("Choose from different options to display recording state.")))
		elif config.plugins.KravenFHD.InfobarStyle.value == "infobar-style-x4":
			list.append(getConfigListEntry(_("Record-State"), config.plugins.KravenFHD.record3, _("Choose from different options to display recording state.")))
		elif config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-x2","infobar-style-z1"):
			if config.plugins.KravenFHD.IBtop.value == "infobar-x2-z1_top2":
				list.append(getConfigListEntry(_("Record-State"), config.plugins.KravenFHD.record2, _("Choose from different options to display recording state.")))
			else:
				list.append(getConfigListEntry(_("Record-State"), config.plugins.KravenFHD.record3, _("Choose from different options to display recording state.")))
		else:
			emptyLines+=1
		if config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-nopicon","infobar-style-x1","infobar-style-x2","infobar-style-z1","infobar-style-zz1","infobar-style-zz4","infobar-style-zzz1","infobar-style-zzz2"):
			if self.E2DistroVersion == "VTi":
				list.append(getConfigListEntry(_("Infobox-Contents"), config.plugins.KravenFHD.Infobox, _("Choose which informations will be shown in the info box.")))
			elif self.E2DistroVersion in ("openatv","teamblue"):
				list.append(getConfigListEntry(_("Infobox-Contents"), config.plugins.KravenFHD.Infobox2, _("Choose which informations will be shown in the info box.")))
		else:
			emptyLines+=1
		if config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-nopicon","infobar-style-x1","infobar-style-x2","infobar-style-x3","infobar-style-x4","infobar-style-z1","infobar-style-z2","infobar-style-zz1","infobar-style-zz4"):
			list.append(getConfigListEntry(_("Channelname/-number"), config.plugins.KravenFHD.InfobarChannelName, _("Choose from different options to show the channel name and number in the infobar.")))
			if not config.plugins.KravenFHD.InfobarChannelName.value == "none":
				list.append(getConfigListEntry(_("Channelname/-number-Font"), config.plugins.KravenFHD.ChannelnameFontList, _("Choose the font color of channel name and number. Press OK to define your own RGB color.")))
			else:
				emptyLines+=1
		else:
			list.append(getConfigListEntry(_("Channelname/-number"), config.plugins.KravenFHD.InfobarChannelName2, _("Choose from different options to show the channel name and number in the infobar.")))
			if not config.plugins.KravenFHD.InfobarChannelName2.value == "none":
				list.append(getConfigListEntry(_("Channelname/-number-Font"), config.plugins.KravenFHD.ChannelnameFontList, _("Choose the font color of channel name and number. Press OK to define your own RGB color.")))
			else:
				emptyLines+=1
		list.append(getConfigListEntry(_("System-Infos"), config.plugins.KravenFHD.SystemInfo, _("Choose from different additional windows with system informations or deactivate them completely.")))
		for i in range(emptyLines+1):
			list.append(getConfigListEntry(_(" "), ))
		
		# page 4 (category 2)
		emptyLines=0
		list.append(getConfigListEntry(_("SECONDINFOBAR _____________________________________________________________"), config.plugins.KravenFHD.CategorySIB, _("This sections offers all settings for SecondInfobar.")))
		list.append(getConfigListEntry(_("SecondInfobar-Style"), config.plugins.KravenFHD.SIB, _("Choose from different styles for SecondInfobar.")))
		list.append(getConfigListEntry(_("SecondInfobar Fontsize"), config.plugins.KravenFHD.SIBFont, _("Choose the font size of SecondInfobar.")))
		for i in range(emptyLines+7):
			list.append(getConfigListEntry(_(" "), ))
		
		# page 5
		emptyLines=0
		list.append(getConfigListEntry(_("WEATHER ___________________________________________________________________"), config.plugins.KravenFHD.CategoryWeather, _("This sections offers all weather settings.")))
		if self.InternetAvailable:
			if config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-nopicon","infobar-style-x1","infobar-style-x3","infobar-style-x4","infobar-style-z2","infobar-style-zz1","infobar-style-zz2","infobar-style-zz3","infobar-style-zz4","infobar-style-zzz1","infobar-style-zzz2"):
				list.append(getConfigListEntry(_("Weather"), config.plugins.KravenFHD.WeatherStyle, _("Choose from different options to show the weather in the infobar.")))
				self.actWeatherstyle=config.plugins.KravenFHD.WeatherStyle.value
			elif config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-x2","infobar-style-z1"):
				if fileExists("/usr/lib/enigma2/python/Plugins/Extensions/Netatmo/plugin.py"):
					list.append(getConfigListEntry(_("Weather"), config.plugins.KravenFHD.WeatherStyle3, _("Activate or deactivate displaying the weather in the infobar.")))
					self.actWeatherstyle=config.plugins.KravenFHD.WeatherStyle3.value
				else:
					list.append(getConfigListEntry(_("Weather"), config.plugins.KravenFHD.WeatherStyle2, _("Activate or deactivate displaying the weather in the infobar.")))
					self.actWeatherstyle=config.plugins.KravenFHD.WeatherStyle2.value
			list.append(getConfigListEntry(_("Server"), config.plugins.KravenFHD.weather_server, _("Choose from different servers for the weather data.")))
			if config.plugins.KravenFHD.weather_server.value == "_accu":
				list.append(getConfigListEntry(_("Accuweather API Key"), config.plugins.KravenFHD.weather_accu_apikey, _("Press OK to enter your API Key.\nYou will receive the key at\nhttps://developer.accuweather.com/.")))
				list.append(getConfigListEntry(_("Search by"), config.plugins.KravenFHD.weather_search_over, _("Choose from different options to specify your location.")))
				if config.plugins.KravenFHD.weather_search_over.value == 'name':
					list.append(getConfigListEntry(_("Search String"), config.plugins.KravenFHD.weather_cityname, _("Specify any search string for your location (zip/city/district/state single or combined). Press OK to use the virtual keyboard. Step up or down in the menu to start the search.")))
				else:
					emptyLines+=1
			else:
				emptyLines+=3
			list.append(getConfigListEntry(_("Language"), config.plugins.KravenFHD.weather_language, _("Specify the language for the weather output.")))
			list.append(getConfigListEntry(_("Refresh interval (in minutes)"), config.plugins.KravenFHD.refreshInterval, _("Choose the frequency of loading weather data from the internet.")))
			list.append(getConfigListEntry(_("Weather-Style"), config.plugins.KravenFHD.WeatherView, _("Choose between graphical weather symbols and Meteo symbols.")))
			if config.plugins.KravenFHD.WeatherView.value == "meteo":
				list.append(getConfigListEntry(_("Meteo-Color"), config.plugins.KravenFHD.MeteoColor, _("Choose between light and dark Meteo symbols.")))
			else:
				emptyLines+=1
		else:
			list.append(getConfigListEntry(_("Weather"), config.plugins.KravenFHD.WeatherStyleNoInternet, _("You have no internet connection. This function is disabled.")))
			self.actWeatherstyle="none"
			emptyLines+=8
		for i in range(emptyLines+1):
			list.append(getConfigListEntry(_(" "), ))
		
		# page 5 (category 2)
		emptyLines=0
		if not config.plugins.KravenFHD.InfobarStyle.value == "infobar-style-zz4":
			list.append(getConfigListEntry(_("CLOCK _____________________________________________________________________"), config.plugins.KravenFHD.CategoryClock, _("This sections offers all settings for the different clocks.")))
			if self.InternetAvailable:
				list.append(getConfigListEntry(_("Clock-Style"), config.plugins.KravenFHD.ClockStyle, _("Choose from different options to show the clock in the infobar.")))
				self.actClockstyle=config.plugins.KravenFHD.ClockStyle.value
				if self.actClockstyle == "clock-analog":
					list.append(getConfigListEntry(_("Analog-Clock-Color"), config.plugins.KravenFHD.AnalogStyle, _("Choose from different colors for the analog type clock in the infobar.")))
				elif self.actClockstyle == "clock-android":
					list.append(getConfigListEntry(_("Android-Temp-Color"), config.plugins.KravenFHD.AndroidList, _("Choose the font color of android-clock temperature. Press OK to define your own RGB color.")))
				elif self.actClockstyle == "clock-weather":
					list.append(getConfigListEntry(_("Weather-Icon-Size"), config.plugins.KravenFHD.ClockIconSize, _("Choose the size of the icon for 'weather icon' clock.")))
				else:
					emptyLines+=1
			else:
				list.append(getConfigListEntry(_("Clock-Style"), config.plugins.KravenFHD.ClockStyleNoInternet, _("Choose from different options to show the clock in the infobar.")))
		else:
			emptyLines+=3
			self.actClockstyle="none"
		for i in range(emptyLines+4):
			list.append(getConfigListEntry(_(" "), ))
		
		# page 6
		emptyLines=0
		list.append(getConfigListEntry(_("ECM INFOS _________________________________________________________________"), config.plugins.KravenFHD.CategoryECMInfos, _("This sections offers all settings for showing the decryption infos.")))
		if not config.plugins.KravenFHD.InfobarStyle.value == "infobar-style-x4":
			list.append(getConfigListEntry(_("Show ECM Infos"), config.plugins.KravenFHD.ECMVisible, _("Choose from different options where to display the ECM informations.")))
		else:
			list.append(getConfigListEntry(_("Show ECM Infos"), config.plugins.KravenFHD.ECMVisibleNA, _("  ")))
		if config.plugins.KravenFHD.InfobarStyle.value == "infobar-style-x1" and not config.plugins.KravenFHD.ECMVisible.value == "none":
			list.append(getConfigListEntry(_("ECM Infos"), config.plugins.KravenFHD.ECMLine1, _("Choose from different options to display the ECM informations.")))
			list.append(getConfigListEntry(_("Show 'free to air'"), config.plugins.KravenFHD.FTA, _("Choose whether 'free to air' is displayed or not for unencrypted channels.")))
			list.append(getConfigListEntry(_("ECM-Font"), config.plugins.KravenFHD.ECMFontList, _("Choose the font color of the ECM information. Press OK to define your own RGB color.")))
		elif config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-nopicon","infobar-style-x2","infobar-style-x3","infobar-style-z1","infobar-style-z2") and not config.plugins.KravenFHD.ECMVisible.value == "none":
			list.append(getConfigListEntry(_("ECM Infos"), config.plugins.KravenFHD.ECMLine2, _("Choose from different options to display the ECM informations.")))
			list.append(getConfigListEntry(_("Show 'free to air'"), config.plugins.KravenFHD.FTA, _("Choose whether 'free to air' is displayed or not for unencrypted channels.")))
			list.append(getConfigListEntry(_("ECM-Font"), config.plugins.KravenFHD.ECMFontList, _("Choose the font color of the ECM information. Press OK to define your own RGB color.")))
		elif config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-zz1","infobar-style-zz2","infobar-style-zz3","infobar-style-zz4","infobar-style-zzz1","infobar-style-zzz2") and not config.plugins.KravenFHD.ECMVisible.value == "none":
			list.append(getConfigListEntry(_("ECM Infos"), config.plugins.KravenFHD.ECMLine3, _("Choose from different options to display the ECM informations.")))
			list.append(getConfigListEntry(_("Show 'free to air'"), config.plugins.KravenFHD.FTA, _("Choose whether 'free to air' is displayed or not for unencrypted channels.")))
			list.append(getConfigListEntry(_("ECM-Font"), config.plugins.KravenFHD.ECMFontList, _("Choose the font color of the ECM information. Press OK to define your own RGB color.")))
		else:
			emptyLines+=3
		for i in range(emptyLines+1):
			list.append(getConfigListEntry(_(" "), ))
		
		# page 6 (category 2)
		emptyLines=0
		list.append(getConfigListEntry(_("VIEWS _____________________________________________________________________"), config.plugins.KravenFHD.CategoryViews, _("This sections offers all settings for skinned plugins.")))
		list.append(getConfigListEntry(_("Volume"), config.plugins.KravenFHD.Volume, _("Choose from different styles for the volume display.")))
		list.append(getConfigListEntry(_("CoolTVGuide"), config.plugins.KravenFHD.CoolTVGuide, _("Choose from different styles for CoolTVGuide.")))
		list.append(getConfigListEntry(_("SerienRecorder"), config.plugins.KravenFHD.SerienRecorder, _("Choose whether you want the Kraven skin to be applied to 'Serienrecorder' or not. Activation of this option prohibits the skin selection in the SR-plugin.")))
		if fileExists("/usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/plugin.py"):
			list.append(getConfigListEntry(_("MediaPortal"), config.plugins.KravenFHD.MediaPortal, _("Choose whether you want the Kraven skin to be applied to 'MediaPortal' or not. To remove it again, you must deactivate it here and activate another skin in 'MediaPortal'.")))
		else:
			emptyLines+=1
		if self.E2DistroVersion == "VTi":
			list.append(getConfigListEntry(_("SplitScreen"), config.plugins.KravenFHD.SplitScreen, _("Choose from different styles to display SplitScreen.")))
		elif self.E2DistroVersion == "openatv":
			list.append(getConfigListEntry(_("FileCommander"), config.plugins.KravenFHD.FileCommander, _("Choose from different styles to display FileCommander.")))
		elif self.E2DistroVersion == "teamblue":
			emptyLines+=1
		for i in range(emptyLines+1):
			list.append(getConfigListEntry(_(" "), ))
		
		# page 6 (category 3)
		emptyLines=0
		list.append(getConfigListEntry(_("PERMANENTCLOCK __________________________________________________________"), config.plugins.KravenFHD.CategoryPermanentClock, _("This sections offers all settings for PermanentClock.")))
		list.append(getConfigListEntry(_("PermanentClock-Color"), config.plugins.KravenFHD.PermanentClock, _("Choose the colors of PermanentClock.")))
		if config.plugins.KravenFHD.PermanentClock.value in ("permanentclock-transparent-big","permanentclock-transparent-small"):
			list.append(getConfigListEntry(_("PermanentClock-Font"), config.plugins.KravenFHD.PermanentClockFontList, _("Choose the font color of PermanentClock. Press OK to define your own RGB color.")))
		else:
			emptyLines+=1
		for i in range(emptyLines+2):
			list.append(getConfigListEntry(_(" "), ))
		
		# page 7
		emptyLines=0
		list.append(getConfigListEntry(_("CHANNELLIST _______________________________________________________________"), config.plugins.KravenFHD.CategoryChannellist, _("This sections offers all channellist settings.")))
		if self.E2DistroVersion == "VTi":
			list.append(getConfigListEntry(_("use alternative (horizontal) channellist"), config.plugins.KravenFHD.alternativeChannellist, _("Choose whether use alternative horizontal channellist or not.")))
			if config.plugins.KravenFHD.alternativeChannellist.value == "none":
				if SystemInfo.get("NumVideoDecoders",1) > 1:
					list.append(getConfigListEntry(_("Channellist-Style"), config.plugins.KravenFHD.ChannelSelectionStyle2, _("Choose from different styles for the channel selection screen.")))
					self.actChannelselectionstyle=config.plugins.KravenFHD.ChannelSelectionStyle2.value
				else:
					list.append(getConfigListEntry(_("Channellist-Style"), config.plugins.KravenFHD.ChannelSelectionStyle, _("Choose from different styles for the channel selection screen.")))
					self.actChannelselectionstyle=config.plugins.KravenFHD.ChannelSelectionStyle.value
				list.append(getConfigListEntry(_("VTi-EPGList"), config.plugins.KravenFHD.ChannellistEPGList, _("Choose whether use VTi-EPGList in channellist or not.")))
				if self.actChannelselectionstyle in ("channelselection-style-minitv","channelselection-style-minitv2","channelselection-style-minitv22","channelselection-style-minitv33","channelselection-style-minitv4","channelselection-style-nobile-minitv","channelselection-style-nobile-minitv33","channelselection-style-minitv-picon"):
					list.append(getConfigListEntry(_("Channellist-Mode"), config.plugins.KravenFHD.ChannelSelectionMode, _("Choose between direct zapping (1xOK) and zapping after preview (2xOK).")))
				else:
					emptyLines+=1
				if not self.actChannelselectionstyle in ("channelselection-style-minitv","channelselection-style-minitv2","channelselection-style-minitv3","channelselection-style-minitv4","channelselection-style-minitv22","channelselection-style-nobile-minitv","channelselection-style-nobile-minitv3","channelselection-style-minitv-picon"):
					list.append(getConfigListEntry(_("Channellist-Transparenz"), config.plugins.KravenFHD.ChannelSelectionTrans, _("Choose the degree of background transparency for the channellists.")))
				else:
					emptyLines+=1
				if self.actChannelselectionstyle in ("channelselection-style-nobile","channelselection-style-nobile2","channelselection-style-nobile-minitv","channelselection-style-nobile-minitv3","channelselection-style-nobile-minitv33"):
					list.append(getConfigListEntry(_("Servicenumber/-name Fontsize"), config.plugins.KravenFHD.ChannelSelectionServiceSize1, _("Choose the font size of channelnumber and channelname.")))
					list.append(getConfigListEntry(_("Serviceinfo Fontsize"), config.plugins.KravenFHD.ChannelSelectionInfoSize1, _("Choose the font size of serviceinformation.")))
				else:
					list.append(getConfigListEntry(_("Servicenumber/-name Fontsize"), config.plugins.KravenFHD.ChannelSelectionServiceSize, _("Choose the font size of channelnumber and channelname.")))
					list.append(getConfigListEntry(_("Serviceinfo Fontsize"), config.plugins.KravenFHD.ChannelSelectionInfoSize, _("Choose the font size of serviceinformation.")))
				if self.actChannelselectionstyle in ("channelselection-style-nobile","channelselection-style-nobile2","channelselection-style-nobile-minitv","channelselection-style-nobile-minitv3","channelselection-style-nobile-minitv33"):
					list.append(getConfigListEntry(_("EPG Fontsize"), config.plugins.KravenFHD.ChannelSelectionEPGSize1, _("Choose the font size of event description, EPG list and primetime.")))
				elif self.actChannelselectionstyle == "channelselection-style-minitv22":
					list.append(getConfigListEntry(_("EPG Fontsize"), config.plugins.KravenFHD.ChannelSelectionEPGSize2, _("Choose the font size of EPG list and primetime.")))
				else:
					list.append(getConfigListEntry(_("EPG Fontsize"), config.plugins.KravenFHD.ChannelSelectionEPGSize3, _("Choose the font size of event description, EPG list and primetime.")))
				list.append(getConfigListEntry(_("'Not available'-Font"), config.plugins.KravenFHD.ChannelSelectionServiceNAList, _("Choose the font color of channels that are unavailable at the moment. Press OK to define your own RGB color.")))
				list.append(getConfigListEntry(_("Primetime"), config.plugins.KravenFHD.Primetimeavailable, _("Choose whether primetime program information is displayed or not.")))
				if config.plugins.KravenFHD.Primetimeavailable.value == "primetime-on":
					list.append(getConfigListEntry(_("Primetime-Time"), config.plugins.KravenFHD.Primetime, _("Specify the time for your primetime.")))
					list.append(getConfigListEntry(_("Primetime-Font"), config.plugins.KravenFHD.PrimetimeFontList, _("Choose the font color of the primetime information. Press OK to define your own RGB color.")))
				else:
					emptyLines+=2
				for i in range(emptyLines+1):
					list.append(getConfigListEntry(_(" "), ))
			else:
				list.append(getConfigListEntry(_("Channellist-Style"), config.plugins.KravenFHD.ChannelSelectionHorStyle, _("Choose from different styles for the channel selection screen.")))
				list.append(getConfigListEntry(_("'Not available'-Font"), config.plugins.KravenFHD.ChannelSelectionServiceNAList, _("Choose the font color of channels that are unavailable at the moment. Press OK to define your own RGB color.")))
				if config.plugins.KravenFHD.ChannelSelectionHorStyle.value == "cshor-minitv":
					list.append(getConfigListEntry(_("Primetime"), config.plugins.KravenFHD.Primetimeavailable, _("Choose whether primetime program information is displayed or not.")))
					if config.plugins.KravenFHD.Primetimeavailable.value == "primetime-on":
						list.append(getConfigListEntry(_("Primetime-Time"), config.plugins.KravenFHD.Primetime, _("Specify the time for your primetime.")))
						list.append(getConfigListEntry(_("Primetime-Font"), config.plugins.KravenFHD.PrimetimeFontList, _("Choose the font color of the primetime information. Press OK to define your own RGB color.")))
					else:
						emptyLines+=2
				else:
					emptyLines+=3
				for i in range(emptyLines+7):
					list.append(getConfigListEntry(_(" "), ))
		elif self.E2DistroVersion == "openatv":
			if SystemInfo.get("NumVideoDecoders",1) > 1:
				list.append(getConfigListEntry(_("Channellist-Style"), config.plugins.KravenFHD.ChannelSelectionStyle2, _("Choose from different styles for the channel selection screen.")))
				self.actChannelselectionstyle=config.plugins.KravenFHD.ChannelSelectionStyle2.value
			else:
				list.append(getConfigListEntry(_("Channellist-Style"), config.plugins.KravenFHD.ChannelSelectionStyle, _("Choose from different styles for the channel selection screen.")))
				self.actChannelselectionstyle=config.plugins.KravenFHD.ChannelSelectionStyle.value
			if self.actChannelselectionstyle in ("channelselection-style-minitv","channelselection-style-minitv2","channelselection-style-minitv22","channelselection-style-minitv33","channelselection-style-minitv4","channelselection-style-nobile-minitv","channelselection-style-nobile-minitv33","channelselection-style-minitv-picon"):
				list.append(getConfigListEntry(_("Channellist-Mode"), config.plugins.KravenFHD.ChannelSelectionMode, _("Choose between direct zapping (1xOK) and zapping after preview (2xOK).")))
			else:
				emptyLines+=1
			if not self.actChannelselectionstyle in ("channelselection-style-minitv","channelselection-style-minitv2","channelselection-style-minitv3","channelselection-style-minitv4","channelselection-style-minitv22","channelselection-style-nobile-minitv","channelselection-style-nobile-minitv3","channelselection-style-minitv-picon"):
				list.append(getConfigListEntry(_("Channellist-Transparenz"), config.plugins.KravenFHD.ChannelSelectionTrans, _("Choose the degree of background transparency for the channellists.")))
			else:
				emptyLines+=1
			if self.actChannelselectionstyle in ("channelselection-style-nobile","channelselection-style-nobile2","channelselection-style-nobile-minitv","channelselection-style-nobile-minitv3","channelselection-style-nobile-minitv33"):
				list.append(getConfigListEntry(_("EPG Fontsize"), config.plugins.KravenFHD.ChannelSelectionEPGSize1, _("Choose the font size of event description, EPG list and primetime.")))
			elif self.actChannelselectionstyle == "channelselection-style-minitv22":
				list.append(getConfigListEntry(_("EPG Fontsize"), config.plugins.KravenFHD.ChannelSelectionEPGSize2, _("Choose the font size of EPG list and primetime.")))
			else:
				list.append(getConfigListEntry(_("EPG Fontsize"), config.plugins.KravenFHD.ChannelSelectionEPGSize3, _("Choose the font size of event description, EPG list and primetime.")))
			list.append(getConfigListEntry(_("'Not available'-Font"), config.plugins.KravenFHD.ChannelSelectionServiceNAList, _("Choose the font color of channels that are unavailable at the moment. Press OK to define your own RGB color.")))
			list.append(getConfigListEntry(_("Primetime"), config.plugins.KravenFHD.Primetimeavailable, _("Choose whether primetime program information is displayed or not.")))
			if config.plugins.KravenFHD.Primetimeavailable.value == "primetime-on":
				list.append(getConfigListEntry(_("Primetime-Time"), config.plugins.KravenFHD.Primetime, _("Specify the time for your primetime.")))
				list.append(getConfigListEntry(_("Primetime-Font"), config.plugins.KravenFHD.PrimetimeFontList, _("Choose the font color of the primetime information. Press OK to define your own RGB color.")))
			else:
				emptyLines+=2
			for i in range(emptyLines+5):
				list.append(getConfigListEntry(_(" "), ))
		elif self.E2DistroVersion == "teamblue":
			list.append(getConfigListEntry(_("Channellist-Style"), config.plugins.KravenFHD.ChannelSelectionStyle3, _("Choose from different styles for the channel selection screen.")))
			self.actChannelselectionstyle=config.plugins.KravenFHD.ChannelSelectionStyle3.value
			if not self.actChannelselectionstyle in ("channelselection-style-minitv","channelselection-style-minitv4","channelselection-style-nobile-minitv","channelselection-style-minitv-picon"):
				list.append(getConfigListEntry(_("Channellist-Transparenz"), config.plugins.KravenFHD.ChannelSelectionTrans, _("Choose the degree of background transparency for the channellists.")))
			else:
				emptyLines+=1
			if self.actChannelselectionstyle in ("channelselection-style-nobile","channelselection-style-nobile2","channelselection-style-nobile-minitv"):
				list.append(getConfigListEntry(_("EPG Fontsize"), config.plugins.KravenFHD.ChannelSelectionEPGSize1, _("Choose the font size of event description, EPG list and primetime.")))
			else:
				list.append(getConfigListEntry(_("EPG Fontsize"), config.plugins.KravenFHD.ChannelSelectionEPGSize3, _("Choose the font size of event description, EPG list and primetime.")))
			list.append(getConfigListEntry(_("'Not available'-Font"), config.plugins.KravenFHD.ChannelSelectionServiceNAList, _("Choose the font color of channels that are unavailable at the moment. Press OK to define your own RGB color.")))
			list.append(getConfigListEntry(_("Primetime"), config.plugins.KravenFHD.Primetimeavailable, _("Choose whether primetime program information is displayed or not.")))
			if config.plugins.KravenFHD.Primetimeavailable.value == "primetime-on":
				list.append(getConfigListEntry(_("Primetime-Time"), config.plugins.KravenFHD.Primetime, _("Specify the time for your primetime.")))
				list.append(getConfigListEntry(_("Primetime-Font"), config.plugins.KravenFHD.PrimetimeFontList, _("Choose the font color of the primetime information. Press OK to define your own RGB color.")))
			else:
				emptyLines+=2
			for i in range(emptyLines+6):
				list.append(getConfigListEntry(_(" "), ))
		
		# page 7 (category 2)
		emptyLines=0
		list.append(getConfigListEntry(_("NUMBERZAP ________________________________________________________________"), config.plugins.KravenFHD.CategoryNumberZap, _("This sections offers all settings for NumberZap.")))
		list.append(getConfigListEntry(_("NumberZap-Style"), config.plugins.KravenFHD.NumberZapExt, _("Choose from different styles for NumberZap.")))
		if not config.plugins.KravenFHD.NumberZapExt.value == "none":
			list.append(getConfigListEntry(_("Border Color"), config.plugins.KravenFHD.NZBorderList, _("Choose the border color for NumberZap. Press OK to define your own RGB color.")))
		else:
			emptyLines+=1
		for i in range(emptyLines+1):
			list.append(getConfigListEntry(_(" "), ))
		
		# page 8
		emptyLines=0
		list.append(getConfigListEntry(_("EPGSELECTION ____________________________________________________________"), config.plugins.KravenFHD.CategoryEPGSelection, _("This sections offers all settings for EPGSelection.")))
		list.append(getConfigListEntry(_("EPGSelection-Style"), config.plugins.KravenFHD.EPGSelection, _("Choose from different styles to display EPGSelection.")))
		list.append(getConfigListEntry(_("EPG-List Fontsize"), config.plugins.KravenFHD.EPGListSize, _("Choose the font size of EPG-List.")))
		list.append(getConfigListEntry(_("EPG Fontsize"), config.plugins.KravenFHD.EPGSelectionEPGSize, _("Choose the font size of event description.")))
		for i in range(emptyLines+1):
			list.append(getConfigListEntry(_(" "), ))
		
		# page 8 (category 2)
		emptyLines=0
		if self.E2DistroVersion == "VTi":
			list.append(getConfigListEntry(_("GRAPHMULTIEPG ___________________________________________________________"), config.plugins.KravenFHD.CategoryGraphMultiEPG, _("This sections offers all settings for GraphMultiEPG.")))
			list.append(getConfigListEntry(_("GraphMultiEPG-Style"), config.plugins.KravenFHD.GraphMultiEPG, _("Choose from different styles for GraphMultiEPG.")))
			list.append(getConfigListEntry(_("Event Description Fontsize"), config.plugins.KravenFHD.GMEDescriptionSize, _("Choose the font size of event description.")))
			list.append(getConfigListEntry(_("Border Color"), config.plugins.KravenFHD.GMEBorderList, _("Choose the border color for GraphMultiEPG. Press OK to define your own RGB color.")))
			list.append(getConfigListEntry(_("Selected Event Background"), config.plugins.KravenFHD.GMErunningbgList, _("Choose the background color of selected events for GraphMultiEPG. Press OK to define your own RGB color.")))
		elif self.E2DistroVersion == "openatv":
			list.append(getConfigListEntry(_("GRAPHICALEPG _____________________________________________________________"), config.plugins.KravenFHD.CategoryGraphicalEPG, _("This sections offers all settings for GraphicalEPG.")))
			list.append(getConfigListEntry(_("GraphicalEPG-Style"), config.plugins.KravenFHD.GraphicalEPG, _("Choose from different styles for GraphicalEPG.")))
			list.append(getConfigListEntry(_("Event Description Fontsize"), config.plugins.KravenFHD.GMEDescriptionSize, _("Choose the font size of event description.")))
			if config.plugins.KravenFHD.GraphicalEPG.value in ("text","text-minitv"):
				list.append(getConfigListEntry(_("Border Color"), config.plugins.KravenFHD.GMEBorderList, _("Choose the border color for GraphicalEPG. Press OK to define your own RGB color.")))
				list.append(getConfigListEntry(_("Selected Event Background"), config.plugins.KravenFHD.GMErunningbgList, _("Choose the background color of selected events for GraphicalEPG. Press OK to define your own RGB color.")))
			else:
				emptyLines+=2
		elif self.E2DistroVersion == "teamblue":
			list.append(getConfigListEntry(_("GRAPHMULTIEPG ___________________________________________________________"), config.plugins.KravenFHD.CategoryGraphMultiEPG, _("This sections offers all settings for GraphMultiEPG.")))
			list.append(getConfigListEntry(_("GraphMultiEPG-Style"), config.plugins.KravenFHD.GraphMultiEPG, _("Choose from different styles for GraphMultiEPG.")))
			list.append(getConfigListEntry(_("Event Description Fontsize"), config.plugins.KravenFHD.GMEDescriptionSize, _("Choose the font size of event description.")))
			list.append(getConfigListEntry(_("Border Color"), config.plugins.KravenFHD.TBna, _("  ")))
			list.append(getConfigListEntry(_("Selected Event Background"), config.plugins.KravenFHD.TBna, _("  ")))
		for i in range(emptyLines+1):
			list.append(getConfigListEntry(_(" "), ))
		
		# page 8 (category 3)
		emptyLines=0
		list.append(getConfigListEntry(_("VERTICALEPG ______________________________________________________________"), config.plugins.KravenFHD.CategoryVerticalEPG, _("This sections offers all settings for VerticalEPG.")))
		if self.E2DistroVersion == "VTi":
			list.append(getConfigListEntry(_("VerticalEPG-Style"), config.plugins.KravenFHD.VerticalEPG, _("Choose from different styles for VerticalEPG.")))
			list.append(getConfigListEntry(_("Border Color"), config.plugins.KravenFHD.VEPGBorderList, _("Choose the border color for VerticalEPG. Press OK to define your own RGB color.")))
		elif self.E2DistroVersion == "openatv":
			list.append(getConfigListEntry(_("VerticalEPG-Style"), config.plugins.KravenFHD.VerticalEPG2, _("Choose from different styles for VerticalEPG.")))
			list.append(getConfigListEntry(_("Border Color"), config.plugins.KravenFHD.VEPGBorderList, _("Choose the border color for VerticalEPG. Press OK to define your own RGB color.")))
		elif self.E2DistroVersion == "teamblue":
			list.append(getConfigListEntry(_("VerticalEPG-Style"), config.plugins.KravenFHD.TBna, _("  ")))
			list.append(getConfigListEntry(_("Border Color"), config.plugins.KravenFHD.TBna, _("  ")))
		for i in range(emptyLines+1):
			list.append(getConfigListEntry(_(" "), ))
		
		# page 8 (category 4)
		emptyLines=0
		list.append(getConfigListEntry(_("TIMEREDITSCREEN ___________________________________________________________"), config.plugins.KravenFHD.CategoryTimerEdit, _("This sections offers all settings for TimerEditScreen.")))
		if self.E2DistroVersion == "VTi":
			list.append(getConfigListEntry(_("TimerEdit-Style"), config.plugins.KravenFHD.TimerEditScreen, _("Choose from different styles to display TimerEditScreen.")))
			list.append(getConfigListEntry(_("TimerList-Style"), config.plugins.KravenFHD.TimerListStyle, _("Choose from different styles to display TimerList.")))
		elif self.E2DistroVersion == "openatv":
			list.append(getConfigListEntry(_("TimerEdit-Style"), config.plugins.KravenFHD.ATVna, _("  ")))
			list.append(getConfigListEntry(_("TimerList-Style"), config.plugins.KravenFHD.ATVna, _("  ")))
		elif self.E2DistroVersion == "teamblue":
			list.append(getConfigListEntry(_("TimerEdit-Style"), config.plugins.KravenFHD.TBna, _("  ")))
			list.append(getConfigListEntry(_("TimerList-Style"), config.plugins.KravenFHD.TBna, _("  ")))
		for i in range(emptyLines):
			list.append(getConfigListEntry(_(" "), ))
		
		# page 9
		emptyLines=0
		list.append(getConfigListEntry(_("ENHANCED MOVIE CENTER _____________________________________________________"), config.plugins.KravenFHD.CategoryEMC, _("This sections offers all settings for EMC ('EnhancedMovieCenter').")))
		list.append(getConfigListEntry(_("EMC-Style"), config.plugins.KravenFHD.EMCStyle, _("Choose from different styles for EnhancedMovieCenter.")))
		if not config.plugins.KravenFHD.EMCStyle.value == "emc-full":
			list.append(getConfigListEntry(_("EPG Fontsize"), config.plugins.KravenFHD.EMCEPGSize, _("Choose the font size of event description.")))
		else:
			emptyLines+=1
		list.append(getConfigListEntry(_("Unwatched Color"), config.plugins.KravenFHD.UnwatchedColorList, _("Choose the font color of unwatched movies. Press OK to define your own RGB color.")))
		list.append(getConfigListEntry(_("Watching Color"), config.plugins.KravenFHD.WatchingColorList, _("Choose the font color of watching movies. Press OK to define your own RGB color.")))
		list.append(getConfigListEntry(_("Finished Color"), config.plugins.KravenFHD.FinishedColorList, _("Choose the font color of watched movies. Press OK to define your own RGB color.")))
		list.append(getConfigListEntry(_("Custom EMC-Selection-Colors"), config.plugins.KravenFHD.EMCSelectionColors, _("Choose whether you want to customize the selection-colors for EnhancedMovieCenter.")))
		if config.plugins.KravenFHD.EMCSelectionColors.value == "emc-colors-on":
			list.append(getConfigListEntry(_("EMC-Listselection"), config.plugins.KravenFHD.EMCSelectionBackgroundList, _("Choose the background color of selection bars for EnhancedMovieCenter. Press OK to define your own RGB color.")))
			list.append(getConfigListEntry(_("EMC-Selection-Font"), config.plugins.KravenFHD.EMCSelectionFontList, _("Choose the color of the font in selection bars for EnhancedMovieCenter. Press OK to define your own RGB color.")))
		else:
			emptyLines+=2
		for i in range(emptyLines+1):
			list.append(getConfigListEntry(_(" "), ))
		
		# page 9 (category 2)
		emptyLines=0
		list.append(getConfigListEntry(_("MOVIESELECTION ____________________________________________________________"), config.plugins.KravenFHD.CategoryMovieSelection, _("This sections offers all settings for MovieSelection.")))
		list.append(getConfigListEntry(_("MovieSelection-Style"), config.plugins.KravenFHD.MovieSelection, _("Choose from different styles for MovieSelection.")))
		list.append(getConfigListEntry(_("EPG Fontsize"), config.plugins.KravenFHD.MovieSelectionEPGSize, _("Choose the font size of event description.")))
		for i in range(emptyLines+1):
			list.append(getConfigListEntry(_(" "), ))
		
		# page 9 (category 3)
		emptyLines=0
		list.append(getConfigListEntry(_("PLAYER ____________________________________________________________________"), config.plugins.KravenFHD.CategoryPlayers, _("This sections offers all settings for the movie players.")))
		list.append(getConfigListEntry(_("Clock"), config.plugins.KravenFHD.PlayerClock, _("Choose from different options to show the clock in the players.")))
		if config.plugins.KravenFHD.PlayerClock.value == "player-android":
			list.append(getConfigListEntry(_("Android-Temp-Color"), config.plugins.KravenFHD.Android2List, _("Choose the font color of android-clock temperature. Press OK to define your own RGB color.")))
		else:
			emptyLines+=1
		list.append(getConfigListEntry(_("PVRState"), config.plugins.KravenFHD.PVRState, _("Choose from different options to display the PVR state.")))
		for i in range(emptyLines):
			list.append(getConfigListEntry(_(" "), ))
		
		# page 10
		emptyLines=0
		if config.plugins.KravenFHD.IBStyle.value == "grad":
			list.append(getConfigListEntry(_("ANTIALIASING BRIGHTNESS ________________________________________________________________"), config.plugins.KravenFHD.CategoryAntialiasing, _("This sections offers all antialiasing settings. Distortions or color frames around fonts can be reduced by this settings.")))
			list.append(getConfigListEntry(_("Infobar"), config.plugins.KravenFHD.InfobarAntialias, _("Reduce distortions (faint/blurry) or color frames around fonts in the infobar and widgets by adjusting the antialiasing brightness.")))
			if not config.plugins.KravenFHD.InfobarStyle.value == "infobar-style-x4":
				list.append(getConfigListEntry(_("ECM Infos"), config.plugins.KravenFHD.ECMLineAntialias, _("Reduce distortions (faint/blurry) or color frames around the ECM information in the infobar by adjusting the antialiasing brightness.")))
			else:
				emptyLines+=1
			list.append(getConfigListEntry(_("Screens"), config.plugins.KravenFHD.ScreensAntialias, _("Reduce distortions (faint/blurry) or color frames around fonts at top and bottom of screens by adjusting the antialiasing brightness.")))
			emptyLines=1
		else:
			emptyLines+=0
		for i in range(emptyLines):
			list.append(getConfigListEntry(_(" "), ))

		# page 10 (category 2)
		list.append(getConfigListEntry(_("VARIOUS SETTINGS ________________________________________________________________"), config.plugins.KravenFHD.CategoryVarious, _("This sections offers various settings.")))
		list.append(getConfigListEntry(_("Screennames"), config.plugins.KravenFHD.DebugNames, _("Activate or deactivate small screen names for debugging purposes.")))
		list.append(getConfigListEntry(_("Icon-Font vertical position"), config.plugins.KravenFHD.KravenIconVPosition, _("Correct the vertical font position within some icons for the infobars and players.")))

		### Assign list or self color
		if config.plugins.KravenFHD.BackgroundListColor.value == "self":
			config.plugins.KravenFHD.BackgroundColor.value = config.plugins.KravenFHD.BackgroundSelfColor.value
		else:
			config.plugins.KravenFHD.BackgroundColor.value = config.plugins.KravenFHD.BackgroundListColor.value
		if config.plugins.KravenFHD.InfobarBoxListColor.value == "self":
			config.plugins.KravenFHD.InfobarBoxColor.value = config.plugins.KravenFHD.InfobarBoxSelfColor.value
		else:
			config.plugins.KravenFHD.InfobarBoxColor.value = config.plugins.KravenFHD.InfobarBoxListColor.value
		if config.plugins.KravenFHD.InfobarGradientListColor.value == "self":
			config.plugins.KravenFHD.InfobarGradientColor.value = config.plugins.KravenFHD.InfobarGradientSelfColor.value
		else:
			config.plugins.KravenFHD.InfobarGradientColor.value = config.plugins.KravenFHD.InfobarGradientListColor.value
		if config.plugins.KravenFHD.SelectionBackgroundList.value == "self":
			config.plugins.KravenFHD.SelectionBackground.value = config.plugins.KravenFHD.SelectionBackgroundSelf.value
		else:
			config.plugins.KravenFHD.SelectionBackground.value = config.plugins.KravenFHD.SelectionBackgroundList.value
		if config.plugins.KravenFHD.SelectionBorderList.value == "self":
			config.plugins.KravenFHD.SelectionBorder.value = config.plugins.KravenFHD.SelectionBorderSelf.value
		else:
			config.plugins.KravenFHD.SelectionBorder.value = config.plugins.KravenFHD.SelectionBorderList.value
		if config.plugins.KravenFHD.Font1List.value == "self":
			config.plugins.KravenFHD.Font1.value = config.plugins.KravenFHD.Font1Self.value
		else:
			config.plugins.KravenFHD.Font1.value = config.plugins.KravenFHD.Font1List.value
		if config.plugins.KravenFHD.Font2List.value == "self":
			config.plugins.KravenFHD.Font2.value = config.plugins.KravenFHD.Font2Self.value
		else:
			config.plugins.KravenFHD.Font2.value = config.plugins.KravenFHD.Font2List.value
		if config.plugins.KravenFHD.IBFont1List.value == "self":
			config.plugins.KravenFHD.IBFont1.value = config.plugins.KravenFHD.IBFont1Self.value
		else:
			config.plugins.KravenFHD.IBFont1.value = config.plugins.KravenFHD.IBFont1List.value
		if config.plugins.KravenFHD.IBFont2List.value == "self":
			config.plugins.KravenFHD.IBFont2.value = config.plugins.KravenFHD.IBFont2Self.value
		else:
			config.plugins.KravenFHD.IBFont2.value = config.plugins.KravenFHD.IBFont2List.value
		if config.plugins.KravenFHD.BackgroundGradientListColorPrimary.value == "self":
			config.plugins.KravenFHD.BackgroundGradientColorPrimary.value = config.plugins.KravenFHD.BackgroundGradientSelfColorPrimary.value
		else:
			config.plugins.KravenFHD.BackgroundGradientColorPrimary.value = config.plugins.KravenFHD.BackgroundGradientListColorPrimary.value
		if config.plugins.KravenFHD.BackgroundGradientListColorSecondary.value == "self":
			config.plugins.KravenFHD.BackgroundGradientColorSecondary.value = config.plugins.KravenFHD.BackgroundGradientSelfColorSecondary.value
		else:
			config.plugins.KravenFHD.BackgroundGradientColorSecondary.value = config.plugins.KravenFHD.BackgroundGradientListColorSecondary.value
		if config.plugins.KravenFHD.InfobarGradientListColorPrimary.value == "self":
			config.plugins.KravenFHD.InfobarGradientColorPrimary.value = config.plugins.KravenFHD.InfobarGradientSelfColorPrimary.value
		else:
			config.plugins.KravenFHD.InfobarGradientColorPrimary.value = config.plugins.KravenFHD.InfobarGradientListColorPrimary.value
		if config.plugins.KravenFHD.InfobarGradientListColorSecondary.value == "self":
			config.plugins.KravenFHD.InfobarGradientColorSecondary.value = config.plugins.KravenFHD.InfobarGradientSelfColorSecondary.value
		else:
			config.plugins.KravenFHD.InfobarGradientColorSecondary.value = config.plugins.KravenFHD.InfobarGradientListColorSecondary.value
		if config.plugins.KravenFHD.BackgroundAlternateListColor.value == "self":
			config.plugins.KravenFHD.BackgroundAlternateColor.value = config.plugins.KravenFHD.BackgroundAlternateSelfColor.value
		else:
			config.plugins.KravenFHD.BackgroundAlternateColor.value = config.plugins.KravenFHD.BackgroundAlternateListColor.value
		if config.plugins.KravenFHD.InfobarAlternateListColor.value == "self":
			config.plugins.KravenFHD.InfobarAlternateColor.value = config.plugins.KravenFHD.InfobarAlternateSelfColor.value
		else:
			config.plugins.KravenFHD.InfobarAlternateColor.value = config.plugins.KravenFHD.InfobarAlternateListColor.value
		if config.plugins.KravenFHD.MarkedFontList.value == "self":
			config.plugins.KravenFHD.MarkedFont.value = config.plugins.KravenFHD.MarkedFontSelf.value
		else:
			config.plugins.KravenFHD.MarkedFont.value = config.plugins.KravenFHD.MarkedFontList.value
		if config.plugins.KravenFHD.SelectionFontList.value == "self":
			config.plugins.KravenFHD.SelectionFont.value = config.plugins.KravenFHD.SelectionFontSelf.value
		else:
			config.plugins.KravenFHD.SelectionFont.value = config.plugins.KravenFHD.SelectionFontList.value
		if config.plugins.KravenFHD.PermanentClockFontList.value == "self":
			config.plugins.KravenFHD.PermanentClockFont.value = config.plugins.KravenFHD.PermanentClockFontSelf.value
		else:
			config.plugins.KravenFHD.PermanentClockFont.value = config.plugins.KravenFHD.PermanentClockFontList.value
		if config.plugins.KravenFHD.ECMFontList.value == "self":
			config.plugins.KravenFHD.ECMFont.value = config.plugins.KravenFHD.ECMFontSelf.value
		else:
			config.plugins.KravenFHD.ECMFont.value = config.plugins.KravenFHD.ECMFontList.value
		if config.plugins.KravenFHD.ChannelnameFontList.value == "self":
			config.plugins.KravenFHD.ChannelnameFont.value = config.plugins.KravenFHD.ChannelnameFontSelf.value
		else:
			config.plugins.KravenFHD.ChannelnameFont.value = config.plugins.KravenFHD.ChannelnameFontList.value
		if config.plugins.KravenFHD.PrimetimeFontList.value == "self":
			config.plugins.KravenFHD.PrimetimeFont.value = config.plugins.KravenFHD.PrimetimeFontSelf.value
		else:
			config.plugins.KravenFHD.PrimetimeFont.value = config.plugins.KravenFHD.PrimetimeFontList.value
		if config.plugins.KravenFHD.ButtonTextList.value == "self":
			config.plugins.KravenFHD.ButtonText.value = config.plugins.KravenFHD.ButtonTextSelf.value
		else:
			config.plugins.KravenFHD.ButtonText.value = config.plugins.KravenFHD.ButtonTextList.value
		if config.plugins.KravenFHD.AndroidList.value == "self":
			config.plugins.KravenFHD.Android.value = config.plugins.KravenFHD.AndroidSelf.value
		else:
			config.plugins.KravenFHD.Android.value = config.plugins.KravenFHD.AndroidList.value
		if config.plugins.KravenFHD.BorderList.value == "self":
			config.plugins.KravenFHD.Border.value = config.plugins.KravenFHD.BorderSelf.value
		else:
			config.plugins.KravenFHD.Border.value = config.plugins.KravenFHD.BorderList.value
		if config.plugins.KravenFHD.ProgressList.value == "self":
			config.plugins.KravenFHD.Progress.value = config.plugins.KravenFHD.ProgressSelf.value
		else:
			config.plugins.KravenFHD.Progress.value = config.plugins.KravenFHD.ProgressList.value
		if config.plugins.KravenFHD.LineList.value == "self":
			config.plugins.KravenFHD.Line.value = config.plugins.KravenFHD.LineSelf.value
		else:
			config.plugins.KravenFHD.Line.value = config.plugins.KravenFHD.LineList.value
		if config.plugins.KravenFHD.IBLineList.value == "self":
			config.plugins.KravenFHD.IBLine.value = config.plugins.KravenFHD.IBLineSelf.value
		else:
			config.plugins.KravenFHD.IBLine.value = config.plugins.KravenFHD.IBLineList.value
		if config.plugins.KravenFHD.MiniTVBorderList.value == "self":
			config.plugins.KravenFHD.MiniTVBorder.value = config.plugins.KravenFHD.MiniTVBorderSelf.value
		else:
			config.plugins.KravenFHD.MiniTVBorder.value = config.plugins.KravenFHD.MiniTVBorderList.value
		if config.plugins.KravenFHD.ChannelSelectionServiceNAList.value == "self":
			config.plugins.KravenFHD.ChannelSelectionServiceNA.value = config.plugins.KravenFHD.ChannelSelectionServiceNASelf.value
		else:
			config.plugins.KravenFHD.ChannelSelectionServiceNA.value = config.plugins.KravenFHD.ChannelSelectionServiceNAList.value
		if config.plugins.KravenFHD.NZBorderList.value == "self":
			config.plugins.KravenFHD.NZBorder.value = config.plugins.KravenFHD.NZBorderSelf.value
		else:
			config.plugins.KravenFHD.NZBorder.value = config.plugins.KravenFHD.NZBorderList.value
		if config.plugins.KravenFHD.GMErunningbgList.value == "self":
			config.plugins.KravenFHD.GMErunningbg.value = config.plugins.KravenFHD.GMErunningbgSelf.value
		else:
			config.plugins.KravenFHD.GMErunningbg.value = config.plugins.KravenFHD.GMErunningbgList.value
		if config.plugins.KravenFHD.GMEBorderList.value == "self":
			config.plugins.KravenFHD.GMEBorder.value = config.plugins.KravenFHD.GMEBorderSelf.value
		else:
			config.plugins.KravenFHD.GMEBorder.value = config.plugins.KravenFHD.GMEBorderList.value
		if config.plugins.KravenFHD.VEPGBorderList.value == "self":
			config.plugins.KravenFHD.VEPGBorder.value = config.plugins.KravenFHD.VEPGBorderSelf.value
		else:
			config.plugins.KravenFHD.VEPGBorder.value = config.plugins.KravenFHD.VEPGBorderList.value
		if config.plugins.KravenFHD.EMCSelectionBackgroundList.value == "self":
			config.plugins.KravenFHD.EMCSelectionBackground.value = config.plugins.KravenFHD.EMCSelectionBackgroundSelf.value
		else:
			config.plugins.KravenFHD.EMCSelectionBackground.value = config.plugins.KravenFHD.EMCSelectionBackgroundList.value
		if config.plugins.KravenFHD.EMCSelectionFontList.value == "self":
			config.plugins.KravenFHD.EMCSelectionFont.value = config.plugins.KravenFHD.EMCSelectionFontSelf.value
		else:
			config.plugins.KravenFHD.EMCSelectionFont.value = config.plugins.KravenFHD.EMCSelectionFontList.value
		if config.plugins.KravenFHD.Android2List.value == "self":
			config.plugins.KravenFHD.Android2.value = config.plugins.KravenFHD.Android2Self.value
		else:
			config.plugins.KravenFHD.Android2.value = config.plugins.KravenFHD.Android2List.value
		if config.plugins.KravenFHD.UnwatchedColorList.value == "self":
			config.plugins.KravenFHD.UnwatchedColor.value = config.plugins.KravenFHD.UnwatchedColorSelf.value
		else:
			config.plugins.KravenFHD.UnwatchedColor.value = config.plugins.KravenFHD.UnwatchedColorList.value
		if config.plugins.KravenFHD.WatchingColorList.value == "self":
			config.plugins.KravenFHD.WatchingColor.value = config.plugins.KravenFHD.WatchingColorSelf.value
		else:
			config.plugins.KravenFHD.WatchingColor.value = config.plugins.KravenFHD.WatchingColorList.value
		if config.plugins.KravenFHD.FinishedColorList.value == "self":
			config.plugins.KravenFHD.FinishedColor.value = config.plugins.KravenFHD.FinishedColorSelf.value
		else:
			config.plugins.KravenFHD.FinishedColor.value = config.plugins.KravenFHD.FinishedColorList.value

		### Calculate Backgrounds
		if config.plugins.KravenFHD.BackgroundColor.value == "gradient":
			self.skincolorbackgroundcolor = config.plugins.KravenFHD.BackgroundGradientColorPrimary.value
		elif config.plugins.KravenFHD.BackgroundColor.value == "texture":
			self.skincolorbackgroundcolor = config.plugins.KravenFHD.BackgroundAlternateColor.value
		else:
			self.skincolorbackgroundcolor = config.plugins.KravenFHD.BackgroundColor.value
		if config.plugins.KravenFHD.IBStyle.value == "grad":
			if config.plugins.KravenFHD.InfobarGradientColor.value == "texture":
				self.skincolorinfobarcolor = config.plugins.KravenFHD.InfobarAlternateColor.value
			else:
				self.skincolorinfobarcolor = config.plugins.KravenFHD.InfobarGradientColor.value
		else:
			if config.plugins.KravenFHD.InfobarBoxColor.value == "gradient":
				self.skincolorinfobarcolor = config.plugins.KravenFHD.InfobarGradientColorPrimary.value
			elif config.plugins.KravenFHD.InfobarBoxColor.value == "texture":
				self.skincolorinfobarcolor = config.plugins.KravenFHD.InfobarAlternateColor.value
			else:
				self.skincolorinfobarcolor = config.plugins.KravenFHD.InfobarBoxColor.value

		### Build list and define situation
		self["config"].list = list
		self["config"].l.setList(list)
		self.updateHelp()
		self["helperimage"].hide()
		self.ShowPicture()
		option = self["config"].getCurrent()[1]
		position = self["config"].instance.getCurrentIndex()

		if position == 0: # about
			self["key_yellow"].setText("<< " + _("various"))
			self["key_blue"].setText(_("profiles") + " >>")
		if (2 <= position <= 4): # profiles
			self["key_yellow"].setText("<< " + _("about"))
			self["key_blue"].setText(_("system") + " >>")
		if (6 <= position <= 17): # system
			self["key_yellow"].setText("<< " + _("profiles"))
			self["key_blue"].setText(_("global colors") + " >>")
		if (18 <= position <= 35): # global colors
			self["key_yellow"].setText("<< " + _("system"))
			self["key_blue"].setText(_("infobar-look") + " >>")
		if (36 <= position <= 53): # infobar-look
			self["key_yellow"].setText("<< " + _("global colors"))
			self["key_blue"].setText(_("infobar-contents") + " >>")
		if (54 <= position <= 60): # infobar-contents
			self["key_yellow"].setText("<< " + _("infobar-look"))
			self["key_blue"].setText(_("SecondInfobar") + " >>")
		if (62 <= position <= 71): # secondinfobar
			self["key_yellow"].setText("<< " + _("infobar-contents"))
			self["key_blue"].setText(_("weather") + " >>")
		if config.plugins.KravenFHD.InfobarStyle.value == "infobar-style-zz4":
			if (72 <= position <= 80): # weather
				self["key_yellow"].setText("<< " + _("SecondInfobar"))
				self["key_blue"].setText(_("ECM infos") + " >>")
		else:
			if (72 <= position <= 80): # weather
				self["key_yellow"].setText("<< " + _("SecondInfobar"))
				self["key_blue"].setText(_("clock") + " >>")
		if (83 <= position <= 85): # clock
			self["key_yellow"].setText("<< " + _("weather"))
			self["key_blue"].setText(_("ECM infos") + " >>")
		if (90 <= position <= 94): # ecm infos
			if config.plugins.KravenFHD.InfobarStyle.value == "infobar-style-zz4":
				self["key_yellow"].setText("<< " + _("weather"))
			else:
				self["key_yellow"].setText("<< " + _("clock"))
			self["key_blue"].setText(_("views") + " >>")
		if (96 <= position <= 101): # views
			self["key_yellow"].setText("<< " + _("ECM infos"))
			self["key_blue"].setText(_("PermanentClock") + " >>")
		if (103 <= position <= 105): # permanentclock
			self["key_yellow"].setText("<< " + _("views"))
			self["key_blue"].setText(_("channellist") + " >>")
		if (108 <= position <= 119): # channellist
			self["key_yellow"].setText("<< " + _("PermanentClock"))
			self["key_blue"].setText(_("NumberZap") + " >>")
		if (121 <= position <= 123): # numberzap
			self["key_yellow"].setText("<< " + _("channellist"))
			self["key_blue"].setText(_("EPGSelection") + " >>")
		if (126 <= position <= 129): # epgselection
			self["key_yellow"].setText("<< " + _("NumberZap"))
			self["key_blue"].setText(_("GraphEPG") + " >>")
		if (131 <= position <= 135): # graphepg
			self["key_yellow"].setText("<< " + _("EPGSelection"))
			self["key_blue"].setText(_("VerticalEPG") + " >>")
		if (137 <= position <= 139): # verticalepg
			self["key_yellow"].setText("<< " + _("GraphEPG"))
			self["key_blue"].setText(_("TimerEditScreen") + " >>")
		if (141 <= position <= 143): # timereditscreen
			self["key_yellow"].setText("<< " + _("VerticalEPG"))
			self["key_blue"].setText(_("EMC") + " >>")
		if (144 <= position <= 152): # emc
			self["key_yellow"].setText("<< " + _("TimerEditScreen"))
			self["key_blue"].setText(_("MovieSelection") + " >>")
		if (154 <= position <= 156): # movieselection
			self["key_yellow"].setText("<< " + _("EMC"))
			self["key_blue"].setText(_("player") + " >>")
		if config.plugins.KravenFHD.IBStyle.value == "box":
			if (158 <= position <= 161): # player
				self["key_yellow"].setText("<< " + _("MovieSelection"))
				self["key_blue"].setText(_("various") + " >>")
		else:
			if (158 <= position <= 161): # player
				self["key_yellow"].setText("<< " + _("MovieSelection"))
				self["key_blue"].setText(_("antialiasing") + " >>")
		if config.plugins.KravenFHD.IBStyle.value == "box":
			if (162 <= position <= 164): # various
				self["key_yellow"].setText("<< " + _("player"))
				self["key_blue"].setText(_("about") + " >>")
		else:
			if (162 <= position <= 165): # antialiasing
				self["key_yellow"].setText("<< " + _("player"))
				self["key_blue"].setText(_("various") + " >>")
			if (167 <= position <= 169): # various
				self["key_yellow"].setText("<< " + _("antialiasing"))
				self["key_blue"].setText(_("about") + " >>")

		### version
		versionpath = "/usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/version"
		versionfile = open(versionpath,"r")
		for line in versionfile:
			version = line.rstrip()
			self["version"].setText(version)
		versionfile.close()

		### preview
		option = self["config"].getCurrent()[1]
		
		if option == config.plugins.KravenFHD.customProfile:
			if config.plugins.KravenFHD.customProfile.value==self.lastProfile:
				self.saveProfile(msg=False)
				
		if option.value == "none":
			self.showText(62,_("Off"))
		elif option.value == "on":
			self.showText(62,_("On"))
		elif option == config.plugins.KravenFHD.customProfile:
			self.showText(28,"/etc/enigma2/kravenfhd_profile_"+str(config.plugins.KravenFHD.customProfile.value))
		elif option == config.plugins.KravenFHD.defaultProfile:
			if fileExists("/usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/images/"+str(config.plugins.KravenFHD.defaultProfile.value)+".jpg"):
				self["helperimage"].show()
			else:
				self.showText(28,"/etc/enigma2/kravenfhd_default_"+str(config.plugins.KravenFHD.defaultProfile.value))
		elif option == config.plugins.KravenFHD.TypeWriter:
			if option.value == "runningtext":
				self.showText(60,_("runningtext"))
			elif option.value == "typewriter":
				self.showText(60,_("typewriter"))
		elif option == config.plugins.KravenFHD.RunningTextSpeed:
			if option.value == "steptime=200":
				self.showText(62,_("5 px/sec"))
			elif option.value == "steptime=100":
				self.showText(62,_("10 px/sec"))
			elif option.value == "steptime=50":
				self.showText(62,_("20 px/sec"))
			elif option.value == "steptime=33":
				self.showText(62,_("30 px/sec"))
		elif option == config.plugins.KravenFHD.IBtop:
			if option.value == "infobar-x2-z1_top":
				self.showText(62,_("4 Tuner"))
			elif option.value == "infobar-x2-z1_top2":
				self.showText(62,_("2 Tuner"))
			elif option.value == "infobar-x2-z1_top3":
				self.showText(62,_("8 Tuner"))
		elif option == config.plugins.KravenFHD.tuner:
			if option.value == "2-tuner":
				self.showText(62,_("2 Tuner"))
			elif option.value == "4-tuner":
				self.showText(62,_("4 Tuner"))
			elif option.value == "8-tuner":
				self.showText(62,_("8 Tuner"))
		elif option == config.plugins.KravenFHD.tuner2:
			if option.value == "2-tuner":
				self.showText(62,_("2 Tuner"))
			elif option.value == "4-tuner":
				self.showText(62,_("4 Tuner"))
			elif option.value == "8-tuner":
				self.showText(62,_("8 Tuner"))
			elif option.value == "10-tuner":
				self.showText(62,_("10 Tuner"))
		elif option in (config.plugins.KravenFHD.InfobarChannelName,config.plugins.KravenFHD.InfobarChannelName2):
			if option.value == "infobar-channelname-small":
				self.showText(50,_("RTL"))
			elif option.value == "infobar-channelname-number-small":
				self.showText(50,_("5 - RTL"))
			elif option.value == "infobar-channelname":
				self.showText(95,_("RTL"))
			elif option.value == "infobar-channelname-number":
				self.showText(95,_("5 - RTL"))
		elif option in (config.plugins.KravenFHD.ECMLine1,config.plugins.KravenFHD.ECMLine2,config.plugins.KravenFHD.ECMLine3):
			if option.value == "VeryShortCaid":
				self.showText(21,"CAID - Time")
			elif option.value == "VeryShortReader":
				self.showText(21,"Reader - Time")
			elif option.value == "ShortReader":
				self.showText(21,"CAID - Reader - Time")
			elif option.value == "Normal":
				self.showText(21,"CAID - Reader - Hops - Time")
			elif option.value == "Long":
				self.showText(21,"CAID - System - Reader - Hops - Time")
			elif option.value == "VeryLong":
				self.showText(21,"CAM - CAID - System - Reader - Hops - Time")
		elif option == config.plugins.KravenFHD.FTA and option.value == "FTAVisible":
			self.showText(21,_("free to air"))
		elif option in (config.plugins.KravenFHD.weather_server,config.plugins.KravenFHD.weather_search_over):
			self.get_weather_data()
			self.showText(25,self.actCity)
		elif option == config.plugins.KravenFHD.weather_language:
			self.showText(75,option.value)
		elif option == config.plugins.KravenFHD.refreshInterval:
			if option.value == "15":
				self.showText(62,"00:15")
			elif option.value == "30":
				self.showText(62,"00:30")
			elif option.value == "60":
				self.showText(62,"01:00")
			elif option.value == "120":
				self.showText(62,"02:00")
			elif option.value == "240":
				self.showText(62,"04:00")
			elif option.value == "480":
				self.showText(62,"08:00")
		elif option == config.plugins.KravenFHD.ChannelSelectionMode:
			if option.value == "zap":
				self.showText(62,"1 x OK")
			elif option.value == "preview":
				self.showText(62,"2 x OK")
		elif option == config.plugins.KravenFHD.PVRState:
			if option.value == "pvrstate-center-big":
				self.showText(55,">> 8x")
			elif option.value == "pvrstate-center-small":
				self.showText(27,">> 8x")
			else:
				self["helperimage"].show()
		elif option == config.plugins.KravenFHD.record3:
			if option.value == "no-record-tuner":
				self.showText(50,_("Off"))
			else:
				self["helperimage"].show()
		elif option == config.plugins.KravenFHD.ChannelSelectionServiceSize:
			size=config.plugins.KravenFHD.ChannelSelectionServiceSize.value
			self.showText(int(size[-2:]),size[-2:]+" Pixel")
		elif option == config.plugins.KravenFHD.ChannelSelectionInfoSize:
			size=config.plugins.KravenFHD.ChannelSelectionInfoSize.value
			self.showText(int(size[-2:]),size[-2:]+" Pixel")
		elif option == config.plugins.KravenFHD.ChannelSelectionServiceSize1:
			size=config.plugins.KravenFHD.ChannelSelectionServiceSize1.value
			self.showText(int(size[-2:]),size[-2:]+" Pixel")
		elif option == config.plugins.KravenFHD.ChannelSelectionInfoSize1:
			size=config.plugins.KravenFHD.ChannelSelectionInfoSize1.value
			self.showText(int(size[-2:]),size[-2:]+" Pixel")
		elif option == config.plugins.KravenFHD.ChannelSelectionEPGSize1:
			if self.E2DistroVersion == "VTi":
				if config.plugins.KravenFHD.ChannellistEPGList.value == "channellistepglist-on":
					if config.plugins.KravenFHD.ChannelSelectionEPGSize1.value == "small":
						self.showText(36,_("description - 28 Pixel \nEPG list - 28 Pixel \nprimetime - 26 Pixel"))
					elif config.plugins.KravenFHD.ChannelSelectionEPGSize1.value == "big":
						self.showText(36,_("description - 32 Pixel \nEPG list - 28 Pixel \nprimetime - 29 Pixel"))
				else:
					if config.plugins.KravenFHD.ChannelSelectionEPGSize1.value == "small":
						self.showText(36,_("description - 28 Pixel \nEPG list - 26 Pixel \nprimetime - 26 Pixel"))
					elif config.plugins.KravenFHD.ChannelSelectionEPGSize1.value == "big":
						self.showText(36,_("description - 32 Pixel \nEPG list - 29 Pixel \nprimetime - 29 Pixel"))
			elif self.E2DistroVersion in ("openatv","teamblue"):
				if config.plugins.KravenFHD.ChannelSelectionEPGSize1.value == "small":
					self.showText(36,_("description - 28 Pixel \nEPG list - 26 Pixel \nprimetime - 26 Pixel"))
				elif config.plugins.KravenFHD.ChannelSelectionEPGSize1.value == "big":
					self.showText(36,_("description - 32 Pixel \nEPG list - 29 Pixel \nprimetime - 29 Pixel"))
		elif option == config.plugins.KravenFHD.ChannelSelectionEPGSize2:
			if self.E2DistroVersion == "VTi":
				if config.plugins.KravenFHD.ChannellistEPGList.value == "channellistepglist-on":
					if config.plugins.KravenFHD.ChannelSelectionEPGSize2.value == "small":
						self.showText(36,_("EPG list - 30 Pixel \nprimetime - 32 Pixel"))
					elif config.plugins.KravenFHD.ChannelSelectionEPGSize2.value == "big":
						self.showText(36,_("EPG list - 34 Pixel \nprimetime - 36 Pixel"))
				else:
					if config.plugins.KravenFHD.ChannelSelectionEPGSize2.value == "small":
						self.showText(36,_("EPG list - 32 Pixel \nprimetime - 32 Pixel"))
					elif config.plugins.KravenFHD.ChannelSelectionEPGSize2.value == "big":
						self.showText(36,_("EPG list - 36 Pixel \nprimetime - 36 Pixel"))
			elif self.E2DistroVersion in ("openatv","teamblue"):
				if config.plugins.KravenFHD.ChannelSelectionEPGSize2.value == "small":
					self.showText(36,_("EPG list - 32 Pixel \nprimetime - 32 Pixel"))
				elif config.plugins.KravenFHD.ChannelSelectionEPGSize2.value == "big":
					self.showText(36,_("EPG list - 36 Pixel \nprimetime - 36 Pixel"))
		elif option == config.plugins.KravenFHD.ChannelSelectionEPGSize3:
			if self.E2DistroVersion == "VTi":
				if config.plugins.KravenFHD.ChannellistEPGList.value == "channellistepglist-on":
					if config.plugins.KravenFHD.ChannelSelectionEPGSize3.value == "small":
						self.showText(36,_("description - 30 Pixel \nEPG list - 32 Pixel \nprimetime - 32 Pixel"))
					elif config.plugins.KravenFHD.ChannelSelectionEPGSize3.value == "big":
						self.showText(36,_("description - 34 Pixel \nEPG list - 36 Pixel \nprimetime - 36 Pixel"))
				else:
					if config.plugins.KravenFHD.ChannelSelectionEPGSize3.value == "small":
						self.showText(36,_("description - 32 Pixel \nEPG list - 32 Pixel \nprimetime - 32 Pixel"))
					elif config.plugins.KravenFHD.ChannelSelectionEPGSize3.value == "big":
						self.showText(36,_("description - 36 Pixel \nEPG list - 36 Pixel \nprimetime - 36 Pixel"))
			elif self.E2DistroVersion in ("openatv","teamblue"):
				if config.plugins.KravenFHD.ChannelSelectionEPGSize3.value == "small":
					self.showText(36,_("description - 32 Pixel \nEPG list - 32 Pixel \nprimetime - 32 Pixel"))
				elif config.plugins.KravenFHD.ChannelSelectionEPGSize3.value == "big":
					self.showText(36,_("description - 36 Pixel \nEPG list - 36 Pixel \nprimetime - 36 Pixel"))
		elif option == config.plugins.KravenFHD.MovieSelectionEPGSize:
			if config.plugins.KravenFHD.MovieSelectionEPGSize.value == "small":
				self.showText(44,_("33 Pixel"))
			elif config.plugins.KravenFHD.MovieSelectionEPGSize.value == "big":
				self.showText(48,_("36 Pixel"))
		elif option == config.plugins.KravenFHD.EPGSelectionEPGSize:
			if config.plugins.KravenFHD.EPGSelectionEPGSize.value == "small":
				self.showText(44,_("33 Pixel"))
			elif config.plugins.KravenFHD.EPGSelectionEPGSize.value == "big":
				self.showText(48,_("36 Pixel"))
		elif option == config.plugins.KravenFHD.EPGListSize:
			if self.E2DistroVersion in ("VTi","openatv"):
				if config.plugins.KravenFHD.EPGListSize.value == "small":
					self.showText(44,_("32 Pixel"))
				elif config.plugins.KravenFHD.EPGListSize.value == "big":
					self.showText(48,_("36 Pixel"))
			elif self.E2DistroVersion == "teamblue":
				if config.plugins.KravenFHD.EPGListSize.value == "small":
					self.showText(44,_("32/26 Pixel"))
				elif config.plugins.KravenFHD.EPGListSize.value == "big":
					self.showText(48,_("37/30 Pixel"))
		elif option == config.plugins.KravenFHD.GMEDescriptionSize:
			if config.plugins.KravenFHD.GMEDescriptionSize.value == "small":
				self.showText(44,_("33 Pixel"))
			elif config.plugins.KravenFHD.GMEDescriptionSize.value == "big":
				self.showText(48,_("36 Pixel"))
		elif option == config.plugins.KravenFHD.EMCEPGSize:
			if config.plugins.KravenFHD.EMCEPGSize.value == "small":
				self.showText(44,_("33 Pixel"))
			elif config.plugins.KravenFHD.EMCEPGSize.value == "big":
				self.showText(48,_("36 Pixel"))
		elif option == config.plugins.KravenFHD.IBFontSize:
			if config.plugins.KravenFHD.IBFontSize.value == "size-33":
				self.showText(33,_("33 Pixel"))
			elif config.plugins.KravenFHD.IBFontSize.value == "size-39":
				self.showText(39,_("39 Pixel"))
			elif config.plugins.KravenFHD.IBFontSize.value == "size-45":
				self.showText(45,_("45 Pixel"))
		elif option == config.plugins.KravenFHD.SIBFont:
			if config.plugins.KravenFHD.SIBFont.value == "sibfont-small":
				self.showText(33,_("small"))
			else:
				self.showText(39,_("big"))
		elif option == config.plugins.KravenFHD.ClockIconSize:
			if config.plugins.KravenFHD.ClockIconSize.value == "size-144":
				self.showText(60,_("144 Pixel"))
			elif config.plugins.KravenFHD.ClockIconSize.value == "size-192":
				self.showText(80,_("192 Pixel"))
		elif option in (config.plugins.KravenFHD.InfobarAntialias,config.plugins.KravenFHD.ECMLineAntialias,config.plugins.KravenFHD.ScreensAntialias):
			if option.value == 10:
				self.showText(62,"+/- 0%")
			elif option.value in range(0,10):
				self.showText(62,"- "+str(100-option.value*10)+"%")
			elif option.value in range(11,21):
				self.showText(62,"+ "+str(option.value*10-100)+"%")
		elif option == config.plugins.KravenFHD.DebugNames and option.value == "screennames-on":
			self.showText(62,"Debug")
		elif option in (config.plugins.KravenFHD.MenuColorTrans,config.plugins.KravenFHD.BackgroundColorTrans,config.plugins.KravenFHD.InfobarColorTrans,config.plugins.KravenFHD.ChannelSelectionTrans) and option.value == "00":
			self.showText(62,_("Off"))
		elif option == config.plugins.KravenFHD.BackgroundListColor:
			if config.plugins.KravenFHD.BackgroundListColor.value == "gradient":
				self.showGradient(config.plugins.KravenFHD.BackgroundGradientColorPrimary.value,config.plugins.KravenFHD.BackgroundGradientColorSecondary.value)
			elif config.plugins.KravenFHD.BackgroundListColor.value == "texture":
				self["helperimage"].show()
			else:
				self.showColor(self.hexRGB(config.plugins.KravenFHD.BackgroundColor.value))
		elif option == config.plugins.KravenFHD.BackgroundGradientListColorPrimary:
			self.showGradient(config.plugins.KravenFHD.BackgroundGradientColorPrimary.value,config.plugins.KravenFHD.BackgroundGradientColorSecondary.value)
		elif option == config.plugins.KravenFHD.BackgroundGradientListColorSecondary:
			self.showGradient(config.plugins.KravenFHD.BackgroundGradientColorPrimary.value,config.plugins.KravenFHD.BackgroundGradientColorSecondary.value)
		elif option == config.plugins.KravenFHD.BackgroundAlternateListColor:
			self["helperimage"].show()
		elif option == config.plugins.KravenFHD.SelectionBackgroundList:
			self.showColor(self.hexRGB(config.plugins.KravenFHD.SelectionBackground.value))
		elif option == config.plugins.KravenFHD.SelectionBorderList:
			self.showColor(self.hexRGB(config.plugins.KravenFHD.SelectionBorder.value))
		elif option == config.plugins.KravenFHD.EMCSelectionBackgroundList:
			self.showColor(self.hexRGB(config.plugins.KravenFHD.EMCSelectionBackground.value))
		elif option == config.plugins.KravenFHD.ProgressList:
			if config.plugins.KravenFHD.ProgressList.value in ("progress", "progress2"):
				self["helperimage"].show()
			else:
				self.showColor(self.hexRGB(config.plugins.KravenFHD.Progress.value))
		elif option == config.plugins.KravenFHD.BorderList:
			self.showColor(self.hexRGB(config.plugins.KravenFHD.Border.value))
		elif option == config.plugins.KravenFHD.MiniTVBorderList:
			self.showColor(self.hexRGB(config.plugins.KravenFHD.MiniTVBorder.value))
		elif option == config.plugins.KravenFHD.NZBorderList:
			self.showColor(self.hexRGB(config.plugins.KravenFHD.NZBorder.value))
		elif option == config.plugins.KravenFHD.GMEBorderList:
			self.showColor(self.hexRGB(config.plugins.KravenFHD.GMEBorder.value))
		elif option == config.plugins.KravenFHD.GMErunningbgList:
			if config.plugins.KravenFHD.GMErunningbgList.value == "global":
				self.showColor(self.hexRGB(config.plugins.KravenFHD.SelectionBackground.value))
			else:
				self.showColor(self.hexRGB(config.plugins.KravenFHD.GMErunningbg.value))
		elif option == config.plugins.KravenFHD.VEPGBorderList:
			self.showColor(self.hexRGB(config.plugins.KravenFHD.VEPGBorder.value))
		elif option == config.plugins.KravenFHD.LineList:
			self.showColor(self.hexRGB(config.plugins.KravenFHD.Line.value))
		elif option == config.plugins.KravenFHD.Font1List:
			self.showColor(self.hexRGB(config.plugins.KravenFHD.Font1.value))
		elif option == config.plugins.KravenFHD.Font2List:
			self.showColor(self.hexRGB(config.plugins.KravenFHD.Font2.value))
		elif option == config.plugins.KravenFHD.IBFont1List:
			self.showColor(self.hexRGB(config.plugins.KravenFHD.IBFont1.value))
		elif option == config.plugins.KravenFHD.IBFont2List:
			self.showColor(self.hexRGB(config.plugins.KravenFHD.IBFont2.value))
		elif option == config.plugins.KravenFHD.PermanentClockFontList:
			self.showColor(self.hexRGB(config.plugins.KravenFHD.PermanentClockFont.value))
		elif option == config.plugins.KravenFHD.SelectionFontList:
			self.showColor(self.hexRGB(config.plugins.KravenFHD.SelectionFont.value))
		elif option == config.plugins.KravenFHD.EMCSelectionFontList:
			self.showColor(self.hexRGB(config.plugins.KravenFHD.EMCSelectionFont.value))
		elif option == config.plugins.KravenFHD.UnwatchedColorList:
			self.showColor(self.hexRGB(config.plugins.KravenFHD.UnwatchedColor.value))
		elif option == config.plugins.KravenFHD.WatchingColorList:
			self.showColor(self.hexRGB(config.plugins.KravenFHD.WatchingColor.value))
		elif option == config.plugins.KravenFHD.FinishedColorList:
			self.showColor(self.hexRGB(config.plugins.KravenFHD.FinishedColor.value))
		elif option == config.plugins.KravenFHD.MarkedFontList:
			self.showColor(self.hexRGB(config.plugins.KravenFHD.MarkedFont.value))
		elif option == config.plugins.KravenFHD.ButtonTextList:
			self.showColor(self.hexRGB(config.plugins.KravenFHD.ButtonText.value))
		elif option == config.plugins.KravenFHD.AndroidList:
			self.showColor(self.hexRGB(config.plugins.KravenFHD.Android.value))
		elif option == config.plugins.KravenFHD.Android2List:
			self.showColor(self.hexRGB(config.plugins.KravenFHD.Android2.value))
		elif option == config.plugins.KravenFHD.ChannelSelectionServiceNAList:
			self.showColor(self.hexRGB(config.plugins.KravenFHD.ChannelSelectionServiceNA.value))
		elif option == config.plugins.KravenFHD.IBLine:
			self["helperimage"].show()
		elif option == config.plugins.KravenFHD.InfobarGradientListColor:
			self["helperimage"].show()
		elif option == config.plugins.KravenFHD.InfobarBoxListColor:
			self["helperimage"].show()
		elif option == config.plugins.KravenFHD.InfobarGradientListColorPrimary:
			self["helperimage"].show()
		elif option == config.plugins.KravenFHD.InfobarGradientListColorSecondary:
			self["helperimage"].show()
		elif option == config.plugins.KravenFHD.InfoStyle:
			if config.plugins.KravenFHD.InfoStyle.value == "primary":
				self.showColor(self.hexRGB(config.plugins.KravenFHD.InfobarGradientColorPrimary.value))
			elif config.plugins.KravenFHD.InfoStyle.value == "secondary":
				self.showColor(self.hexRGB(config.plugins.KravenFHD.InfobarGradientColorSecondary.value))
			else:
				self.showGradient(config.plugins.KravenFHD.InfobarGradientColorPrimary.value,config.plugins.KravenFHD.InfobarGradientColorSecondary.value)
		elif option == config.plugins.KravenFHD.InfobarAlternateListColor:
			self["helperimage"].show()
		elif option == config.plugins.KravenFHD.ChannelnameFontList:
			self.showColor(self.hexRGB(config.plugins.KravenFHD.ChannelnameFont.value))
		elif option == config.plugins.KravenFHD.ECMFontList:
			self.showColor(self.hexRGB(config.plugins.KravenFHD.ECMFont.value))
		elif option == config.plugins.KravenFHD.PrimetimeFontList:
			self.showColor(self.hexRGB(config.plugins.KravenFHD.PrimetimeFont.value))
		elif option == config.plugins.KravenFHD.ECMVisible:
			if option.value == "0":
				self.showText(45,_("Off"))
			elif option.value == "ib":
				self.showText(45,_("Infobar"))
			elif option.value == "sib":
				self.showText(45,"SecondInfobar")
			elif option.value == "ib+sib":
				self.showText(45,_("Infobar & \nSecondInfobar"))
		else:
			self["helperimage"].show()

	def updateHelp(self):
		cur = self["config"].getCurrent()
		if cur:
			self["help"].text = cur[2]

	def GetPicturePath(self):
		try:
			optionValue = self["config"].getCurrent()[1]
			returnValue = self["config"].getCurrent()[1].value
			if optionValue == config.plugins.KravenFHD.BackgroundListColor and config.plugins.KravenFHD.BackgroundListColor.value == "texture":
				self.makeTexturePreview(config.plugins.KravenFHD.BackgroundTexture.value)
				path = "/usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/images/preview.jpg"
			elif optionValue == config.plugins.KravenFHD.BackgroundTexture:
				self.makeTexturePreview(returnValue)
				path = "/usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/images/preview.jpg"
			elif optionValue == config.plugins.KravenFHD.InfobarTexture:
				self.makePreview()
				path = "/usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/images/preview.jpg"
			elif optionValue == config.plugins.KravenFHD.BackgroundAlternateListColor:
				self.makeAlternatePreview(config.plugins.KravenFHD.BackgroundTexture.value,config.plugins.KravenFHD.BackgroundAlternateColor.value)
				path = "/usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/images/preview.jpg"
			elif optionValue == config.plugins.KravenFHD.InfobarAlternateListColor:
				self.makeAlternatePreview(config.plugins.KravenFHD.InfobarTexture.value,config.plugins.KravenFHD.InfobarAlternateColor.value)
				path = "/usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/images/preview.jpg"
			elif optionValue == config.plugins.KravenFHD.IBStyle:
				self.makePreview()
				path = "/usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/images/preview.jpg"
			elif optionValue == config.plugins.KravenFHD.IBLineList:
				self.makePreview()
				path = "/usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/images/preview.jpg"
			elif optionValue == config.plugins.KravenFHD.InfobarGradientListColor:
				self.makePreview()
				path = "/usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/images/preview.jpg"
			elif optionValue == config.plugins.KravenFHD.InfobarBoxListColor:
				self.makePreview()
				path = "/usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/images/preview.jpg"
			elif optionValue in (config.plugins.KravenFHD.InfobarGradientListColorPrimary,config.plugins.KravenFHD.InfobarGradientListColorSecondary):
				self.makePreview()
				path = "/usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/images/preview.jpg"
			elif returnValue in ("startdelay=2000","startdelay=4000","startdelay=6000","startdelay=8000","startdelay=10000","startdelay=15000","startdelay=20000"):
				path = "/usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/images/running-delay.jpg"
			elif returnValue in ("about","about2"):
				path = "/usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/images/about.png"
			elif returnValue == ("meteo-light"):
				path = "/usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/images/meteo.jpg"
			elif returnValue == "progress":
				path = "/usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/images/colorfull.jpg"
			elif returnValue == "progress2":
				path = "/usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/images/colorfull2.jpg"
			elif returnValue in ("self","emc-colors-on","unskinned-colors-on",config.plugins.KravenFHD.PermanentClock.value):
				path = "/usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/images/colors.jpg"
			elif returnValue == ("channelselection-style-minitv3"):
				path = "/usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/images/channelselection-style-minitv.jpg"
			elif returnValue == "channelselection-style-nobile-minitv3":
				path = "/usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/images/channelselection-style-nobile-minitv.jpg"
			elif returnValue == "all-screens":
				path = "/usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/images/emc-smallcover.jpg"
			elif returnValue == "player-classic":
				path = "/usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/images/clock-classic.jpg"
			elif returnValue == "player-android":
				path = "/usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/images/clock-android.jpg"
			elif returnValue == "player-flip":
				path = "/usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/images/clock-flip.jpg"
			elif returnValue == "player-weather":
				path = "/usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/images/clock-weather.jpg"
			elif returnValue in ("zap","preview"):
				path = "/usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/images/modus.jpg"
			elif returnValue == "box":
				path = "/usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/images/2.jpg"
			elif returnValue == "grad":
				path = "/usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/images/infobar-style-x2.jpg"
			elif returnValue in ("record-blink","record-blink+no-record-tuner","record-shine+no-record-tuner"):
				path = "/usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/images/record-shine.jpg"
			elif returnValue == "tuner-blink":
				path = "/usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/images/tuner-shine.jpg"
			elif returnValue in ("record-blink+tuner-shine","record-shine+tuner-blink","record+tuner-blink"):
				path = "/usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/images/record+tuner-shine.jpg"
			elif returnValue == "only-infobar":
				path = "/usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/images/infobar-style-x3.jpg"
			elif returnValue in ("0C","18","32","58","7E"):
				path = "/usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/images/transparent.jpg"
			elif returnValue == "showOnDemand":
				path = "/usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/images/scrollbarWidth=15.jpg"
			elif returnValue == "showNever":
				path = "/usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/images/scrollbarWidth=0.jpg"
			elif optionValue == config.plugins.KravenFHD.KravenIconVPosition:
				path = "/usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/images/vposition.jpg"
			elif fileExists("/usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/images/" + returnValue + ".jpg"):
				path = "/usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/images/" + returnValue + ".jpg"
			if fileExists(path):
				return path
			else:
				return "/usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/images/black.jpg"
		except:
			return "/usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/images/fb.jpg"

	def UpdatePicture(self):
		self.PicLoad.PictureData.get().append(self.DecodePicture)
		self.onLayoutFinish.append(self.ShowPicture)

	def ShowPicture(self):
		self.PicLoad.setPara([self["helperimage"].instance.size().width(),self["helperimage"].instance.size().height(),self.Scale[0],self.Scale[1],0,1,"#00000000"])
		if self.picPath is not None:
			if self.E2DistroVersion == "VTi":
				self.PicLoad.startDecode(self.picPath)
				self.picPath = None
			elif self.E2DistroVersion in ("openatv","teamblue"):
				self.picPath = None
				self.PicLoad.startDecode(self.picPath)
		else:
			self.PicLoad.startDecode(self.GetPicturePath())

	def DecodePicture(self, PicInfo = ""):
		ptr = self.PicLoad.getData()
		self["helperimage"].instance.setPixmap(ptr)

	def keyLeft(self):
		ConfigListScreen.keyLeft(self)
		self.mylist()

	def keyRight(self):
		ConfigListScreen.keyRight(self)
		self.mylist()

	def keyDown(self):
		if self.E2DistroVersion in ("VTi","teamblue"):
			pass
		elif self.E2DistroVersion == "openatv":
			self["config"].instance.moveSelection(self["config"].instance.moveDown)
			self.mylist()

	def keyUp(self):
		if self.E2DistroVersion in ("VTi","teamblue"):
			pass
		elif self.E2DistroVersion == "openatv":
			self["config"].instance.moveSelection(self["config"].instance.moveUp)
			self.mylist()

	def keyUpLong(self):
		self["config"].instance.moveSelection(self["config"].instance.moveUp)
		self.mylist()

	def keyDownLong(self):
		self["config"].instance.moveSelection(self["config"].instance.moveDown)
		self.mylist()

	def pageUp(self):
		self["config"].instance.moveSelection(self["config"].instance.pageUp)
		self.mylist()

	def pageDown(self):
		self["config"].instance.moveSelection(self["config"].instance.pageDown)
		self.mylist()

	def categoryDown(self):
		position = self["config"].instance.getCurrentIndex()
		if config.plugins.KravenFHD.IBStyle.value == "box":
			if position == 0: # about
				self["config"].instance.moveSelectionTo(162)
		else:
			if position == 0: # about
				self["config"].instance.moveSelectionTo(167)
		if (2 <= position <= 4): # profiles
			self["config"].instance.moveSelectionTo(0)
		if (6 <= position <= 17): # system
			self["config"].instance.moveSelectionTo(2)
		if (18 <= position <= 35): # global colors
			self["config"].instance.moveSelectionTo(6)
		if (36 <= position <= 53): # infobar-look
			self["config"].instance.moveSelectionTo(18)
		if (54 <= position <= 60): # infobar-contents
			self["config"].instance.moveSelectionTo(36)
		if (62 <= position <= 64): # secondinfobar
			self["config"].instance.moveSelectionTo(54)
		if (72 <= position <= 80): # weather
			self["config"].instance.moveSelectionTo(62)
		if (83 <= position <= 85): # clock
			self["config"].instance.moveSelectionTo(72)
		if (90 <= position <= 94): # ecm infos
			if config.plugins.KravenFHD.InfobarStyle.value == "infobar-style-zz4":
				self["config"].instance.moveSelectionTo(72)
			else:
				self["config"].instance.moveSelectionTo(83)
		if (96 <= position <= 101): # views
			self["config"].instance.moveSelectionTo(90)
		if (103 <= position <= 105): # permanentclock
			self["config"].instance.moveSelectionTo(96)
		if (108 <= position <= 119): # channellist
			self["config"].instance.moveSelectionTo(103)
		if (121 <= position <= 123): # numberzap
			self["config"].instance.moveSelectionTo(108)
		if (126 <= position <= 129): # epgselection
			self["config"].instance.moveSelectionTo(121)
		if (131 <= position <= 135): # graphepg
			self["config"].instance.moveSelectionTo(126)
		if (137 <= position <= 139): # verticalepg
			self["config"].instance.moveSelectionTo(131)
		if (141 <= position <= 143): # timereditscreen
			self["config"].instance.moveSelectionTo(137)
		if (144 <= position <= 152): # emc
			self["config"].instance.moveSelectionTo(141)
		if (154 <= position <= 156): # movieselection
			self["config"].instance.moveSelectionTo(144)
		if (158 <= position <= 161): # player
			self["config"].instance.moveSelectionTo(154)
		if config.plugins.KravenFHD.IBStyle.value == "box":
			if (162 <= position <= 164): # various
				self["config"].instance.moveSelectionTo(158)
		else:
			if (162 <= position <= 165): # antialiasing
				self["config"].instance.moveSelectionTo(158)
			if (167 <= position <= 169): # various
				self["config"].instance.moveSelectionTo(162)
		self.mylist()

	def categoryUp(self):
		position = self["config"].instance.getCurrentIndex()
		if position == 0: # about
			self["config"].instance.moveSelectionTo(2)
		if (2 <= position <= 4): # profiles
			self["config"].instance.moveSelectionTo(6)
		if (6 <= position <= 17): # system
			self["config"].instance.moveSelectionTo(18)
		if (18 <= position <= 35): # global colors
			self["config"].instance.moveSelectionTo(36)
		if (36 <= position <= 53): # infobar-look
			self["config"].instance.moveSelectionTo(54)
		if (54 <= position <= 60): # infobar-contents
			self["config"].instance.moveSelectionTo(62)
		if (62 <= position <= 64): # secondinfobar
			self["config"].instance.moveSelectionTo(72)
		if config.plugins.KravenFHD.InfobarStyle.value == "infobar-style-zz4":
			if (72 <= position <= 81): # weather
				self["config"].instance.moveSelectionTo(90)
		else:
			if (72 <= position <= 81): # weather
				self["config"].instance.moveSelectionTo(83)
		if (83 <= position <= 85): # clock
			self["config"].instance.moveSelectionTo(90)
		if (90 <= position <= 94): # ecm infos
			self["config"].instance.moveSelectionTo(96)
		if (96 <= position <= 101): # views
			self["config"].instance.moveSelectionTo(103)
		if (103 <= position <= 105): # permanentclock
			self["config"].instance.moveSelectionTo(108)
		if (108 <= position <= 119): # channellist
			self["config"].instance.moveSelectionTo(121)
		if (121 <= position <= 123): # numberzap
			self["config"].instance.moveSelectionTo(126)
		if (126 <= position <= 129): # epgselection
			self["config"].instance.moveSelectionTo(131)
		if (131 <= position <= 135): # graphepg
			self["config"].instance.moveSelectionTo(137)
		if (137 <= position <= 139): # verticalepg
			self["config"].instance.moveSelectionTo(141)
		if (141 <= position <= 143): # timereditscreen
			self["config"].instance.moveSelectionTo(144)
		if (144 <= position <= 152): # emc
			self["config"].instance.moveSelectionTo(154)
		if (154 <= position <= 156): # movieselection
			self["config"].instance.moveSelectionTo(158)
		if (158 <= position <= 161): # player
			self["config"].instance.moveSelectionTo(162)
		if config.plugins.KravenFHD.IBStyle.value == "box":
			if (162 <= position <= 164): # various
				self["config"].instance.moveSelectionTo(0)
		else:
			if (162 <= position <= 165): # antialiasing
				self["config"].instance.moveSelectionTo(167)
			if (167 <= position <= 169): # various
				self["config"].instance.moveSelectionTo(0)
		self.mylist()

	def VirtualKeyBoardCallBack(self, callback):
		try:
			if callback:  
				self["config"].getCurrent()[1].value = callback
			else:
				pass
		except:
			pass

	def ColorSelectionCallBack(self, callback):
		try:
			if callback:
				self.actSelfColorSelection.value = callback
				self.actListColorSelection.value = "self"
				self.mylist()
			else:
				pass
		except:
			pass

	def OK(self):
		option = self["config"].getCurrent()[1]
		optionislistcolor=False
		
		if option == config.plugins.KravenFHD.BackgroundListColor:
			if not config.plugins.KravenFHD.BackgroundListColor.value in ("gradient", "texture"):
				optionislistcolor=True
				self.actSelfColorSelection = config.plugins.KravenFHD.BackgroundSelfColor
		elif option == config.plugins.KravenFHD.InfobarBoxListColor:
			if not config.plugins.KravenFHD.InfobarBoxListColor.value in ("gradient", "texture"):
				optionislistcolor=True
				self.actSelfColorSelection = config.plugins.KravenFHD.InfobarBoxSelfColor
		elif option == config.plugins.KravenFHD.InfobarGradientListColor:
			if not config.plugins.KravenFHD.InfobarGradientListColor.value == "texture":
				optionislistcolor=True
				self.actSelfColorSelection = config.plugins.KravenFHD.InfobarGradientSelfColor
		elif option == config.plugins.KravenFHD.SelectionBackgroundList:
			optionislistcolor=True
			self.actSelfColorSelection = config.plugins.KravenFHD.SelectionBackgroundSelf
		elif option == config.plugins.KravenFHD.SelectionBorderList:
			optionislistcolor=True
			self.actSelfColorSelection = config.plugins.KravenFHD.SelectionBorderSelf
		elif option == config.plugins.KravenFHD.Font1List:
			optionislistcolor=True
			self.actSelfColorSelection = config.plugins.KravenFHD.Font1Self
		elif option == config.plugins.KravenFHD.Font2List:
			optionislistcolor=True
			self.actSelfColorSelection = config.plugins.KravenFHD.Font2Self
		elif option == config.plugins.KravenFHD.IBFont1List:
			optionislistcolor=True
			self.actSelfColorSelection = config.plugins.KravenFHD.IBFont1Self
		elif option == config.plugins.KravenFHD.IBFont2List:
			optionislistcolor=True
			self.actSelfColorSelection = config.plugins.KravenFHD.IBFont2Self
		elif option == config.plugins.KravenFHD.BackgroundGradientListColorPrimary:
			optionislistcolor=True
			self.actSelfColorSelection = config.plugins.KravenFHD.BackgroundGradientSelfColorPrimary
		elif option == config.plugins.KravenFHD.BackgroundGradientListColorSecondary:
			optionislistcolor=True
			self.actSelfColorSelection = config.plugins.KravenFHD.BackgroundGradientSelfColorSecondary
		elif option == config.plugins.KravenFHD.InfobarGradientListColorPrimary:
			optionislistcolor=True
			self.actSelfColorSelection = config.plugins.KravenFHD.InfobarGradientSelfColorPrimary
		elif option == config.plugins.KravenFHD.InfobarGradientListColorSecondary:
			optionislistcolor=True
			self.actSelfColorSelection = config.plugins.KravenFHD.InfobarGradientSelfColorSecondary
		elif option == config.plugins.KravenFHD.BackgroundAlternateListColor:
			optionislistcolor=True
			self.actSelfColorSelection = config.plugins.KravenFHD.BackgroundAlternateSelfColor
		elif option == config.plugins.KravenFHD.InfobarAlternateListColor:
			optionislistcolor=True
			self.actSelfColorSelection = config.plugins.KravenFHD.InfobarAlternateSelfColor
		elif option == config.plugins.KravenFHD.MarkedFontList:
			optionislistcolor=True
			self.actSelfColorSelection = config.plugins.KravenFHD.MarkedFontSelf
		elif option == config.plugins.KravenFHD.PermanentClockFontList:
			optionislistcolor=True
			self.actSelfColorSelection = config.plugins.KravenFHD.PermanentClockFontSelf
		elif option == config.plugins.KravenFHD.SelectionFontList:
			optionislistcolor=True
			self.actSelfColorSelection = config.plugins.KravenFHD.SelectionFontSelf
		elif option == config.plugins.KravenFHD.ECMFontList:
			optionislistcolor=True
			self.actSelfColorSelection = config.plugins.KravenFHD.ECMFontSelf
		elif option == config.plugins.KravenFHD.ChannelnameFontList:
			optionislistcolor=True
			self.actSelfColorSelection = config.plugins.KravenFHD.ChannelnameFontSelf
		elif option == config.plugins.KravenFHD.PrimetimeFontList:
			optionislistcolor=True
			self.actSelfColorSelection = config.plugins.KravenFHD.PrimetimeFontSelf
		elif option == config.plugins.KravenFHD.ButtonTextList:
			optionislistcolor=True
			self.actSelfColorSelection = config.plugins.KravenFHD.ButtonTextSelf
		elif option == config.plugins.KravenFHD.AndroidList:
			optionislistcolor=True
			self.actSelfColorSelection = config.plugins.KravenFHD.AndroidSelf
		elif option == config.plugins.KravenFHD.BorderList:
			optionislistcolor=True
			self.actSelfColorSelection = config.plugins.KravenFHD.BorderSelf
		elif option == config.plugins.KravenFHD.ProgressList:
			optionislistcolor=True
			self.actSelfColorSelection = config.plugins.KravenFHD.ProgressSelf
		elif option == config.plugins.KravenFHD.LineList:
			optionislistcolor=True
			self.actSelfColorSelection = config.plugins.KravenFHD.LineSelf
		elif option == config.plugins.KravenFHD.IBLineList:
			optionislistcolor=True
			self.actSelfColorSelection = config.plugins.KravenFHD.IBLineSelf
		elif option == config.plugins.KravenFHD.MiniTVBorderList:
			optionislistcolor=True
			self.actSelfColorSelection = config.plugins.KravenFHD.MiniTVBorderSelf
		elif option == config.plugins.KravenFHD.ChannelSelectionServiceNAList:
			optionislistcolor=True
			self.actSelfColorSelection = config.plugins.KravenFHD.ChannelSelectionServiceNASelf
		elif option == config.plugins.KravenFHD.NZBorderList:
			optionislistcolor=True
			self.actSelfColorSelection = config.plugins.KravenFHD.NZBorderSelf
		elif option == config.plugins.KravenFHD.GMErunningbgList:
			optionislistcolor=True
			self.actSelfColorSelection = config.plugins.KravenFHD.GMErunningbgSelf
		elif option == config.plugins.KravenFHD.GMEBorderList:
			optionislistcolor=True
			self.actSelfColorSelection = config.plugins.KravenFHD.GMEBorderSelf
		elif option == config.plugins.KravenFHD.VEPGBorderList:
			optionislistcolor=True
			self.actSelfColorSelection = config.plugins.KravenFHD.VEPGBorderSelf
		elif option == config.plugins.KravenFHD.EMCSelectionBackgroundList:
			optionislistcolor=True
			self.actSelfColorSelection = config.plugins.KravenFHD.EMCSelectionBackgroundSelf
		elif option == config.plugins.KravenFHD.EMCSelectionFontList:
			optionislistcolor=True
			self.actSelfColorSelection = config.plugins.KravenFHD.EMCSelectionFontSelf
		elif option == config.plugins.KravenFHD.Android2List:
			optionislistcolor=True
			self.actSelfColorSelection = config.plugins.KravenFHD.Android2Self
		elif option == config.plugins.KravenFHD.UnwatchedColorList:
			optionislistcolor=True
			self.actSelfColorSelection = config.plugins.KravenFHD.UnwatchedColorSelf
		elif option == config.plugins.KravenFHD.WatchingColorList:
			optionislistcolor=True
			self.actSelfColorSelection = config.plugins.KravenFHD.WatchingColorSelf
		elif option == config.plugins.KravenFHD.FinishedColorList:
			optionislistcolor=True
			self.actSelfColorSelection = config.plugins.KravenFHD.FinishedColorSelf

		if optionislistcolor:
			self.actListColorSelection=option
			title = _("Use the sliders to define your color:")
			if self.actListColorSelection.value=="self":
				color = self.actSelfColorSelection.value
			elif self.actListColorSelection.value=="none":
				color = "000000"
			elif self.actListColorSelection.value in ("progress", "progress2"):
				color = "C3461B"
			else:
				color = self.actListColorSelection.value
			self.session.openWithCallback(self.ColorSelectionCallBack, KravenFHDColorSelection, title = title, color = color)
		elif option == config.plugins.KravenFHD.weather_cityname:
			text = self["config"].getCurrent()[1].value
			if config.plugins.KravenFHD.weather_search_over.value == 'name':
				title = _("Enter the city name of your location:")
			self.session.openWithCallback(self.VirtualKeyBoardCallBack, VirtualKeyBoard, title = title, text = text)
		elif option == config.plugins.KravenFHD.weather_accu_apikey:
			text = self["config"].getCurrent()[1].value
			title = _("Enter your API Key:")
			self.session.openWithCallback(self.VirtualKeyBoardCallBack, VirtualKeyBoard, title = title, text = text)
		elif option == config.plugins.KravenFHD.customProfile:
			self.saveProfile(msg=True)
		elif option == config.plugins.KravenFHD.defaultProfile:
			self.reset()

	def faq(self):
		from Plugins.SystemPlugins.MPHelp import PluginHelp, XMLHelpReader
		reader = XMLHelpReader(resolveFilename(SCOPE_PLUGINS, "Extensions/KravenFHD/faq.xml"))
		KravenFHDFaq = PluginHelp(*reader)
		KravenFHDFaq.open(self.session)

	def reboot(self):
		restartbox = self.session.openWithCallback(self.restartGUI,MessageBox,_("Do you really want to reboot now?"), MessageBox.TYPE_YESNO)
		restartbox.setTitle(_("Restart GUI"))

	def getDataByKey(self, list, key):
		for item in list:
			if item["key"] == key:
				return item
		return list[0]

	def getFontStyleData(self, key):
		return self.getDataByKey(channelselFontStyles, key)

	def getFontSizeData(self, key):
		return self.getDataByKey(channelInfoFontSizes, key)

	def save(self):
		
		self.saveProfile(msg=False)
		for x in self["config"].list:
			if len(x) > 1:
					x[1].save()
			else:
					pass

		self.skinSearchAndReplace = []

		### Background
		self.skinSearchAndReplace.append(['name="Kravenbg" value="#00000000', 'name="Kravenbg" value="#00' + self.skincolorbackgroundcolor])

		### Background Transparency (global)
		self.skinSearchAndReplace.append(['name="Kravenbg" value="#00', 'name="Kravenbg" value="#' + config.plugins.KravenFHD.BackgroundColorTrans.value])

		### Background2 (non-transparent)
		if config.plugins.KravenFHD.BackgroundColor.value in ("self","gradient","texture"):
			self.skinSearchAndReplace.append(['name="Kravenbg2" value="#00000000', 'name="Kravenbg2" value="#00' + self.skincolorbackgroundcolor])
			if config.plugins.KravenFHD.Unskinned.value == "unskinned-colors-on":
				self.skinSearchAndReplace.append(['name="background" value="#00000000', 'name="background" value="#00' + self.skincolorbackgroundcolor])
		else:
			self.skinSearchAndReplace.append(['name="Kravenbg2" value="#00000000', 'name="Kravenbg2" value="#00' + config.plugins.KravenFHD.BackgroundColor.value])
			if config.plugins.KravenFHD.Unskinned.value == "unskinned-colors-on":
				self.skinSearchAndReplace.append(['name="background" value="#00000000', 'name="background" value="#00' + config.plugins.KravenFHD.BackgroundColor.value])

		### Background3 (Menus Transparency)
		if self.InternetAvailable:
			if config.plugins.KravenFHD.Logo.value in ("logo","metrix-icons"):
				if config.plugins.KravenFHD.BackgroundColor.value in ("self","gradient","texture"):
					self.skinSearchAndReplace.append(['name="Kravenbg3" value="#00000000', 'name="Kravenbg3" value="#' + config.plugins.KravenFHD.MenuColorTrans.value + self.skincolorbackgroundcolor])
				else:
					self.skinSearchAndReplace.append(['name="Kravenbg3" value="#00000000', 'name="Kravenbg3" value="#' + config.plugins.KravenFHD.MenuColorTrans.value + config.plugins.KravenFHD.BackgroundColor.value])
			else:
				if config.plugins.KravenFHD.BackgroundColor.value in ("self","gradient","texture"):
					self.skinSearchAndReplace.append(['name="Kravenbg3" value="#00000000', 'name="Kravenbg3" value="#00' + self.skincolorbackgroundcolor])
				else:
					self.skinSearchAndReplace.append(['name="Kravenbg3" value="#00000000', 'name="Kravenbg3" value="#00' + config.plugins.KravenFHD.BackgroundColor.value])
		else:
			if config.plugins.KravenFHD.LogoNoInternet.value == "logo":
				if config.plugins.KravenFHD.BackgroundColor.value in ("self","gradient","texture"):
					self.skinSearchAndReplace.append(['name="Kravenbg3" value="#00000000', 'name="Kravenbg3" value="#' + config.plugins.KravenFHD.MenuColorTrans.value + self.skincolorbackgroundcolor])
				else:
					self.skinSearchAndReplace.append(['name="Kravenbg3" value="#00000000', 'name="Kravenbg3" value="#' + config.plugins.KravenFHD.MenuColorTrans.value + config.plugins.KravenFHD.BackgroundColor.value])
			else:
				if config.plugins.KravenFHD.BackgroundColor.value in ("self","gradient","texture"):
					self.skinSearchAndReplace.append(['name="Kravenbg3" value="#00000000', 'name="Kravenbg3" value="#00' + self.skincolorbackgroundcolor])
				else:
					self.skinSearchAndReplace.append(['name="Kravenbg3" value="#00000000', 'name="Kravenbg3" value="#00' + config.plugins.KravenFHD.BackgroundColor.value])
			

		### Background4 (Channellist)
		if config.plugins.KravenFHD.BackgroundColor.value in ("self","gradient","texture"):
			self.skinSearchAndReplace.append(['name="Kravenbg4" value="#00000000', 'name="Kravenbg4" value="#' + config.plugins.KravenFHD.ChannelSelectionTrans.value + self.skincolorbackgroundcolor])
		else:
			self.skinSearchAndReplace.append(['name="Kravenbg4" value="#00000000', 'name="Kravenbg4" value="#' + config.plugins.KravenFHD.ChannelSelectionTrans.value + config.plugins.KravenFHD.BackgroundColor.value])

		### Background5 (Radio Channellist)
		if config.plugins.KravenFHD.BackgroundColor.value in ("self","gradient","texture"):
			self.skinSearchAndReplace.append(['name="Kravenbg5" value="#00000000', 'name="Kravenbg5" value="#' + "60" + self.skincolorbackgroundcolor])
		else:
			self.skinSearchAndReplace.append(['name="Kravenbg5" value="#00000000', 'name="Kravenbg5" value="#' + "60" + config.plugins.KravenFHD.BackgroundColor.value])

		### SIB Background
		if config.plugins.KravenFHD.BackgroundColor.value in ("self","gradient","texture"):
			self.skinSearchAndReplace.append(['name="KravenSIBbg" value="#00000000', 'name="KravenSIBbg" value="#' + config.plugins.KravenFHD.InfobarColorTrans.value + self.skincolorbackgroundcolor])
		else:
			self.skinSearchAndReplace.append(['name="KravenSIBbg" value="#00000000', 'name="KravenSIBbg" value="#' + config.plugins.KravenFHD.InfobarColorTrans.value + config.plugins.KravenFHD.BackgroundColor.value])

		### Background Grafiks
		if config.plugins.KravenFHD.BackgroundColor.value in ("gradient","texture"):
			self.skinSearchAndReplace.append(['<!-- globalbg */-->', '<ePixmap pixmap="KravenFHD/graphics/globalbg.png" position="0,0" size="1920,1080" zPosition="-10" alphatest="blend" />'])
			self.skinSearchAndReplace.append(['<!-- nontransbg */-->', '<ePixmap pixmap="KravenFHD/graphics/nontransbg.png" position="0,0" size="1920,1080" zPosition="-10" />'])
			self.skinSearchAndReplace.append(['<!-- menubg */-->', '<ePixmap pixmap="KravenFHD/graphics/menubg.png" position="0,0" size="1920,1080" zPosition="-10" alphatest="blend" />'])
			self.skinSearchAndReplace.append(['<!-- channelbg */-->', '<ePixmap pixmap="KravenFHD/graphics/channelbg.png" position="0,0" size="1920,1080" zPosition="-10" alphatest="blend" />'])
			self.skinSearchAndReplace.append(['<!-- sibbg */-->', '<ePixmap pixmap="KravenFHD/graphics/sibbg.png" position="0,0" size="1920,1080" zPosition="-10" alphatest="blend" />'])
		else:
			self.skinSearchAndReplace.append(['<!-- globalbg */-->', '<eLabel backgroundColor="Kravenbg" position="0,0" size="1920,1080" transparent="0" zPosition="-10" />'])
			self.skinSearchAndReplace.append(['<!-- nontransbg */-->', '<eLabel backgroundColor="Kravenbg2" position="0,0" size="1920,1080" transparent="0" zPosition="-10" />'])
			self.skinSearchAndReplace.append(['<!-- menubg */-->', '<eLabel backgroundColor="Kravenbg3" position="0,0" size="1920,1080" transparent="0" zPosition="-10" />'])
			self.skinSearchAndReplace.append(['<!-- channelbg */-->', '<eLabel backgroundColor="Kravenbg4" position="0,0" size="1920,1080" transparent="0" zPosition="-10" />'])
			self.skinSearchAndReplace.append(['<!-- sibbg */-->', '<eLabel backgroundColor="KravenSIBbg" position="0,0" size="1920,1080" transparent="0" zPosition="-10" />'])

		### ECM. Transparency of infobar, color of text
		if config.plugins.KravenFHD.IBStyle.value == "grad":
			self.skinSearchAndReplace.append(['name="KravenECMbg" value="#F1325698', 'name="KravenECMbg" value="#' + config.plugins.KravenFHD.InfobarColorTrans.value + self.calcBrightness(self.skincolorinfobarcolor,config.plugins.KravenFHD.ECMLineAntialias.value)])
		else:
			self.skinSearchAndReplace.append(['name="KravenECMbg" value="#F1325698', 'name="KravenECMbg" value="#' + config.plugins.KravenFHD.InfobarColorTrans.value + self.skincolorinfobarcolor])

		### Infobar. Transparency of infobar, color of infobar
		self.skinSearchAndReplace.append(['name="KravenIBbg" value="#001B1775', 'name="KravenIBbg" value="#' + config.plugins.KravenFHD.InfobarColorTrans.value + self.skincolorinfobarcolor])

		### CoolTV. color of infobar or color of background, if ibar invisible
		if config.plugins.KravenFHD.IBColor.value == "all-screens":
			if config.plugins.KravenFHD.IBStyle.value == "grad":
				self.skinSearchAndReplace.append(['name="KravenIBCoolbg" value="#00000000', 'name="KravenIBCoolbg" value="#00' + self.calcBrightness(self.skincolorinfobarcolor,config.plugins.KravenFHD.ScreensAntialias.value)])
			else:
				self.skinSearchAndReplace.append(['name="KravenIBCoolbg" value="#00000000', 'name="KravenIBCoolbg" value="#00' + self.skincolorinfobarcolor])
		else:
			self.skinSearchAndReplace.append(['backgroundColor="KravenIBCoolbg"', 'backgroundColor="Kravenbg2"'])

		### Screens. Lower Transparency of infobar and background, color of infobar or color of background, if ibar invisible
		if config.plugins.KravenFHD.IBColor.value == "all-screens":
			if config.plugins.KravenFHD.IBStyle.value == "grad":
				self.skinSearchAndReplace.append(['name="KravenIBbg2" value="#00000000', 'name="KravenIBbg2" value="#' + self.calcTransparency(config.plugins.KravenFHD.InfobarColorTrans.value,config.plugins.KravenFHD.BackgroundColorTrans.value) + self.calcBrightness(self.skincolorinfobarcolor,config.plugins.KravenFHD.ScreensAntialias.value)])
				self.skinSearchAndReplace.append(['name="KravenIBbg3" value="#00000000', 'name="KravenIBbg3" value="#' + self.calcTransparency(config.plugins.KravenFHD.InfobarColorTrans.value,config.plugins.KravenFHD.MenuColorTrans.value) + self.calcBrightness(self.skincolorinfobarcolor,config.plugins.KravenFHD.ScreensAntialias.value)])
				self.skinSearchAndReplace.append(['name="KravenIBbg4" value="#00000000', 'name="KravenIBbg4" value="#' + self.calcTransparency(config.plugins.KravenFHD.InfobarColorTrans.value,config.plugins.KravenFHD.ChannelSelectionTrans.value) + self.calcBrightness(self.skincolorinfobarcolor,config.plugins.KravenFHD.ScreensAntialias.value)])
			else:
				self.skinSearchAndReplace.append(['name="KravenIBbg2" value="#00000000', 'name="KravenIBbg2" value="#' + config.plugins.KravenFHD.BackgroundColorTrans.value + self.skincolorinfobarcolor])
				self.skinSearchAndReplace.append(['name="KravenIBbg3" value="#00000000', 'name="KravenIBbg3" value="#' + config.plugins.KravenFHD.MenuColorTrans.value + self.skincolorinfobarcolor])
				self.skinSearchAndReplace.append(['name="KravenIBbg4" value="#00000000', 'name="KravenIBbg4" value="#' + config.plugins.KravenFHD.ChannelSelectionTrans.value + self.skincolorinfobarcolor])
		else:
			self.skinSearchAndReplace.append(['name="KravenIBbg2" value="#00000000', 'name="KravenIBbg2" value="#' + config.plugins.KravenFHD.BackgroundColorTrans.value + self.skincolorbackgroundcolor])
			self.skinSearchAndReplace.append(['name="KravenIBbg3" value="#00000000', 'name="KravenIBbg3" value="#' + config.plugins.KravenFHD.MenuColorTrans.value + self.skincolorbackgroundcolor])
			self.skinSearchAndReplace.append(['name="KravenIBbg4" value="#00000000', 'name="KravenIBbg4" value="#' + config.plugins.KravenFHD.ChannelSelectionTrans.value + self.skincolorbackgroundcolor])

		### Menu
		if self.E2DistroVersion == "VTi":
			if not self.actChannelselectionstyle in ("channelselection-style-minitv2","channelselection-style-minitv22","channelselection-style-minitv33","channelselection-style-nobile-minitv33","channelselection-style-minitv3","channelselection-style-nobile-minitv3"):
				self.skinSearchAndReplace.append(['render="KravenFHDMenuPig"', 'render="Pig"'])
			else:
				self.skinSearchAndReplace.append(['render="KravenFHDMenuPig"', 'render="KravenFHDPig3"'])
		elif self.E2DistroVersion == "openatv":
			if not self.actChannelselectionstyle in ("channelselection-style-minitv2","channelselection-style-minitv22","channelselection-style-minitv33","channelselection-style-nobile-minitv33","channelselection-style-minitv3","channelselection-style-nobile-minitv3"):
				self.skinSearchAndReplace.append(['render="KravenFHDMenuPig"', 'render="Pig"'])
		elif self.E2DistroVersion == "teamblue":
			self.skinSearchAndReplace.append(['render="KravenFHDMenuPig"', 'render="Pig"'])
		if self.InternetAvailable:
			if config.plugins.KravenFHD.Logo.value == "minitv":
				self.skinSearchAndReplace.append(['<!-- Logo -->', '<constant-widget name="Logo1"/>'])
				self.skinSearchAndReplace.append(['<!-- Metrix-Icons -->', '<constant-widget name="Icons1"/>'])
			elif config.plugins.KravenFHD.Logo.value == "logo":
				self.skinSearchAndReplace.append(['<!-- Logo -->', '<constant-widget name="Logo2"/>'])
				self.skinSearchAndReplace.append(['<!-- Metrix-Icons -->', '<constant-widget name="Icons2"/>'])
			elif config.plugins.KravenFHD.Logo.value == "metrix-icons":
				self.skinSearchAndReplace.append(['<!-- Logo -->', '<constant-widget name="Logo3"/>'])
				self.skinSearchAndReplace.append(['<!-- Metrix-Icons -->', '<constant-widget name="Icons3"/>'])
			else:
				self.skinSearchAndReplace.append(['<!-- Logo -->', '<constant-widget name="Logo4"/>'])
				self.skinSearchAndReplace.append(['<!-- Metrix-Icons -->', '<constant-widget name="Icons4"/>'])
		else:
			if config.plugins.KravenFHD.LogoNoInternet.value == "minitv":
				self.skinSearchAndReplace.append(['<!-- Logo -->', '<constant-widget name="Logo1"/>'])
				self.skinSearchAndReplace.append(['<!-- Metrix-Icons -->', '<constant-widget name="Icons1"/>'])
			else:
				self.skinSearchAndReplace.append(['<!-- Logo -->', '<constant-widget name="Logo2"/>'])
				self.skinSearchAndReplace.append(['<!-- Metrix-Icons -->', '<constant-widget name="Icons2"/>'])

		### Logo
		console1 = eConsoleAppContainer()
		if self.E2DistroVersion == "VTi":
			console1.execute("tar xf /usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/data/logo-vti.tar.gz -C /usr/share/enigma2/KravenFHD/")
		elif self.E2DistroVersion == "openatv":
			console1.execute("tar xf /usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/data/logo-openatv.tar.gz -C /usr/share/enigma2/KravenFHD/")
		elif self.E2DistroVersion == "teamblue":
			console1.execute("tar xf /usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/data/logo-teamblue.tar.gz -C /usr/share/enigma2/KravenFHD/")

		### Buttons
		console2 = eConsoleAppContainer()
		if self.E2DistroVersion == "openatv":
			console2.execute("tar xf /usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/data/buttons-openatv.tar.gz -C /usr/share/enigma2/KravenFHD/buttons/")
		elif self.E2DistroVersion in ("VTi","teamblue"):
			console2.execute("tar xf /usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/data/buttons-vti-teamblue.tar.gz -C /usr/share/enigma2/KravenFHD/buttons/")

		### Mainmenu Fontsize
		if config.plugins.KravenFHD.MainmenuFontsize.value == "mainmenu-small":
			self.skinSearchAndReplace.append(['<constant-widget name="mainmenu-big"/>', '<constant-widget name="mainmenu-small"/>'])
		elif config.plugins.KravenFHD.MainmenuFontsize.value == "mainmenu-middle":
			self.skinSearchAndReplace.append(['<constant-widget name="mainmenu-big"/>', '<constant-widget name="mainmenu-middle"/>'])

		### Infobar. Background-Style
		if config.plugins.KravenFHD.IBStyle.value == "box":

			### Infobar - Background
			self.skinSearchAndReplace.append(['<!--<eLabel position', '<eLabel position'])
			self.skinSearchAndReplace.append(['zPosition="-8" />-->', 'zPosition="-8" />'])

			### Infobar - Line
			self.skinSearchAndReplace.append(['name="KravenIBLine" value="#00ffffff', 'name="KravenIBLine" value="#00' + config.plugins.KravenFHD.IBLine.value])

			### Infobar
			if config.plugins.KravenFHD.InfobarBoxColor.value == "gradient":
				self.skinSearchAndReplace.append(['<constant-widget name="gradient-ib-top"/>', '<constant-widget name="box2-ib-top"/>'])
				if config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-nopicon","infobar-style-x1"):
					self.skinSearchAndReplace.append(['<!-- Infobar ibar -->', '<constant-widget name="box2-ib-np-x1"/>'])
				elif config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-x2","infobar-style-x3","infobar-style-x4"):
					self.skinSearchAndReplace.append(['<!-- Infobar ibar -->', '<constant-widget name="box2-ib-x2-x3"/>'])
				elif config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-z1","infobar-style-z2"):
					self.skinSearchAndReplace.append(['<!-- Infobar ibar -->', '<constant-widget name="box2-ib-z1-z2"/>'])
				elif config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-zz1","infobar-style-zz4"):
					self.skinSearchAndReplace.append(['<!-- Infobar ibar -->', '<constant-widget name="box2-ib-zz1-zz4"/>'])
				elif config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-zz2","infobar-style-zz3"):
					self.skinSearchAndReplace.append(['<!-- Infobar ibar -->', '<constant-widget name="box2-ib-zz2-zz3"/>'])
				elif config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-zzz1","infobar-style-zzz2"):
					self.skinSearchAndReplace.append(['<!-- Infobar ibar -->', '<constant-widget name="box2-ib-zzz1"/>'])
			elif config.plugins.KravenFHD.InfobarBoxColor.value == "texture":
				self.skinSearchAndReplace.append(['<constant-widget name="gradient-ib-top"/>', '<constant-widget name="texture-ib-top"/>'])
				if config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-nopicon","infobar-style-x1"):
					self.skinSearchAndReplace.append(['<!-- Infobar ibar -->', '<constant-widget name="texture-ib-np-x1"/>'])
				elif config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-x2","infobar-style-x3","infobar-style-x4"):
					self.skinSearchAndReplace.append(['<!-- Infobar ibar -->', '<constant-widget name="texture-ib-x2-x3"/>'])
				elif config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-z1","infobar-style-z2"):
					self.skinSearchAndReplace.append(['<!-- Infobar ibar -->', '<constant-widget name="texture-ib-z1-z2"/>'])
				elif config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-zz1","infobar-style-zz4"):
					self.skinSearchAndReplace.append(['<!-- Infobar ibar -->', '<constant-widget name="texture-ib-zz1-zz4"/>'])
				elif config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-zz2","infobar-style-zz3"):
					self.skinSearchAndReplace.append(['<!-- Infobar ibar -->', '<constant-widget name="texture-ib-zz2-zz3"/>'])
				elif config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-zzz1","infobar-style-zzz2"):
					self.skinSearchAndReplace.append(['<!-- Infobar ibar -->', '<constant-widget name="texture-ib-zzz1"/>'])
			else:
				self.skinSearchAndReplace.append(['<constant-widget name="gradient-ib-top"/>', '<constant-widget name="box-ib-top"/>'])
				if config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-nopicon","infobar-style-x1"):
					self.skinSearchAndReplace.append(['<!-- Infobar ibar -->', '<constant-widget name="box-ib-np-x1"/>'])
				elif config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-x2","infobar-style-x3","infobar-style-x4"):
					self.skinSearchAndReplace.append(['<!-- Infobar ibar -->', '<constant-widget name="box-ib-x2-x3"/>'])
				elif config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-z1","infobar-style-z2"):
					self.skinSearchAndReplace.append(['<!-- Infobar ibar -->', '<constant-widget name="box-ib-z1-z2"/>'])
				elif config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-zz1","infobar-style-zz4"):
					self.skinSearchAndReplace.append(['<!-- Infobar ibar -->', '<constant-widget name="box-ib-zz1-zz4"/>'])
				elif config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-zz2","infobar-style-zz3"):
					self.skinSearchAndReplace.append(['<!-- Infobar ibar -->', '<constant-widget name="box-ib-zz2-zz3"/>'])
				elif config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-zzz1","infobar-style-zzz2"):
					self.skinSearchAndReplace.append(['<!-- Infobar ibar -->', '<constant-widget name="box-ib-zzz1"/>'])

			### NetatmoBar - Background
			if config.plugins.KravenFHD.InfobarBoxColor.value == "gradient":
				self.skinSearchAndReplace.append(['<constant-widget name="gradient-netatmo"/>', '<constant-widget name="box2-netatmo"/>'])
			elif config.plugins.KravenFHD.InfobarBoxColor.value == "texture":
				self.skinSearchAndReplace.append(['<constant-widget name="gradient-netatmo"/>', '<constant-widget name="texture-netatmo"/>'])
			else:
				self.skinSearchAndReplace.append(['<constant-widget name="gradient-netatmo"/>', '<constant-widget name="box-netatmo"/>'])

			### SIB - Background
			if config.plugins.KravenFHD.InfobarBoxColor.value == "gradient":
				self.skinSearchAndReplace.append(['<constant-widget name="gradient-sib"/>', '<constant-widget name="box2-sib"/>'])
			elif config.plugins.KravenFHD.InfobarBoxColor.value == "texture":
				self.skinSearchAndReplace.append(['<constant-widget name="gradient-sib"/>', '<constant-widget name="texture-sib"/>'])
			else:
				self.skinSearchAndReplace.append(['<constant-widget name="gradient-sib"/>', '<constant-widget name="box-sib"/>'])

			### weather-big - Background
			if config.plugins.KravenFHD.InfobarBoxColor.value == "gradient":
				self.skinSearchAndReplace.append(['<constant-widget name="gradient-weather-big"/>', '<constant-widget name="box2-weather-big"/>'])
			elif config.plugins.KravenFHD.InfobarBoxColor.value == "texture":
				self.skinSearchAndReplace.append(['<constant-widget name="gradient-weather-big"/>', '<constant-widget name="texture-weather-big"/>'])
			else:
				self.skinSearchAndReplace.append(['<constant-widget name="gradient-weather-big"/>', '<constant-widget name="box-weather-big"/>'])

			### weather-small - Background
			if config.plugins.KravenFHD.InfobarBoxColor.value == "gradient":
				self.skinSearchAndReplace.append(['<constant-widget name="gradient-weather-small"/>', '<constant-widget name="box2-weather-small"/>'])
			elif config.plugins.KravenFHD.InfobarBoxColor.value == "texture":
				self.skinSearchAndReplace.append(['<constant-widget name="gradient-weather-small"/>', '<constant-widget name="texture-weather-small"/>'])
			else:
				self.skinSearchAndReplace.append(['<constant-widget name="gradient-weather-small"/>', '<constant-widget name="box-weather-small"/>'])

			### weather-small - Position
			self.skinSearchAndReplace.append(['position="1440,82" size="105,105"', 'position="1500,37" size="105,105"'])
			self.skinSearchAndReplace.append(['position="1545,82" size="172,105"', 'position="1605,37" size="172,105"'])
			self.skinSearchAndReplace.append(['position="1717,82" size="112,52"', 'position="1777,37" size="112,52"'])
			self.skinSearchAndReplace.append(['position="1717,135" size="112,52"', 'position="1777,90" size="112,52"'])

			### clock-android - ibar-Position
			if config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-x2","infobar-style-x3","infobar-style-x4","infobar-style-z1","infobar-style-z2") and self.actClockstyle == "clock-android":
				self.skinSearchAndReplace.append(['position="0,864" size="1920,216"', 'position="0,849" size="1920,231"'])
				self.skinSearchAndReplace.append(['position="0,864" size="1920,3"', 'position="0,849" size="1920,3"'])
				self.skinSearchAndReplace.append(['position="0,870" size="1920,210"', 'position="0,849" size="1920,231"'])
				self.skinSearchAndReplace.append(['position="0,870" size="1920,3"', 'position="0,849" size="1920,3"'])

			### EMCMediaCenter, MoviePlayer, DVDPlayer - Background
			if config.plugins.KravenFHD.InfobarBoxColor.value == "gradient":
				self.skinSearchAndReplace.append(['<constant-widget name="gradient-player"/>', '<constant-widget name="box2-player"/>'])
			elif config.plugins.KravenFHD.InfobarBoxColor.value == "texture":
				self.skinSearchAndReplace.append(['<constant-widget name="gradient-player"/>', '<constant-widget name="texture-player"/>'])
			else:
				self.skinSearchAndReplace.append(['<constant-widget name="gradient-player"/>', '<constant-widget name="box-player"/>'])

			### EPGSelectionEPGBar - Background
			if config.plugins.KravenFHD.InfobarBoxColor.value == "gradient":
				self.skinSearchAndReplace.append(['<constant-widget name="gradient-EPGBar"/>', '<constant-widget name="box2-EPGBar"/>'])
			elif config.plugins.KravenFHD.InfobarBoxColor.value == "texture":
				self.skinSearchAndReplace.append(['<constant-widget name="gradient-EPGBar"/>', '<constant-widget name="texture-EPGBar"/>'])
			else:
				self.skinSearchAndReplace.append(['<constant-widget name="gradient-EPGBar"/>', '<constant-widget name="box-EPGBar"/>'])

			### ChannelSelectionRadio
			if config.plugins.KravenFHD.InfobarBoxColor.value == "gradient":
				self.skinSearchAndReplace.append(['<constant-widget name="gradient-csr"/>', '<constant-widget name="box2-csr"/>'])
			elif config.plugins.KravenFHD.InfobarBoxColor.value == "texture":
				self.skinSearchAndReplace.append(['<constant-widget name="gradient-csr"/>', '<constant-widget name="texture-csr"/>'])
			else:
				self.skinSearchAndReplace.append(['<constant-widget name="gradient-csr"/>', '<constant-widget name="box-csr"/>'])

			### RadioInfoBar
			if config.plugins.KravenFHD.InfobarBoxColor.value == "gradient":
				self.skinSearchAndReplace.append(['<constant-widget name="gradient-rib"/>', '<constant-widget name="box2-rib"/>'])
			elif config.plugins.KravenFHD.InfobarBoxColor.value == "texture":
				self.skinSearchAndReplace.append(['<constant-widget name="gradient-rib"/>', '<constant-widget name="texture-rib"/>'])
			else:
				self.skinSearchAndReplace.append(['<constant-widget name="gradient-rib"/>', '<constant-widget name="box-rib"/>'])

			### GraphicalInfoBarEPG, QuickEPG
			if config.plugins.KravenFHD.InfobarBoxColor.value == "gradient":
				self.skinSearchAndReplace.append(['<constant-widget name="gradient-ibepg"/>', '<constant-widget name="box2-ibepg"/>'])
			elif config.plugins.KravenFHD.InfobarBoxColor.value == "texture":
				self.skinSearchAndReplace.append(['<constant-widget name="gradient-ibepg"/>', '<constant-widget name="texture-ibepg"/>'])
			else:
				self.skinSearchAndReplace.append(['<constant-widget name="gradient-ibepg"/>', '<constant-widget name="box-ibepg"/>'])

			### InfoBarEventView
			if config.plugins.KravenFHD.InfobarBoxColor.value == "gradient":
				self.skinSearchAndReplace.append(['<constant-widget name="gradient-ibev"/>', '<constant-widget name="box2-ibev"/>'])
			elif config.plugins.KravenFHD.InfobarBoxColor.value == "texture":
				self.skinSearchAndReplace.append(['<constant-widget name="gradient-ibev"/>', '<constant-widget name="texture-ibev"/>'])
			else:
				self.skinSearchAndReplace.append(['<constant-widget name="gradient-ibev"/>', '<constant-widget name="box-ibev"/>'])
			
			### ServiceScanMinimal
			self.skinSearchAndReplace.append(['<!-- ServiceScanMinimal IBLine -->', '<constant-widget name="ServiceScanMinimal_IBLine"/>'])

		else:
			### Infobar
			if config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-nopicon","infobar-style-x1"):
				self.skinSearchAndReplace.append(['<!-- Infobar ibar -->', '<constant-widget name="gradient-ib-np-x1"/>'])
			elif config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-x2","infobar-style-x3","infobar-style-x4"):
				self.skinSearchAndReplace.append(['<!-- Infobar ibar -->', '<constant-widget name="gradient-ib-x2-x3"/>'])
			elif config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-z1","infobar-style-z2"):
				self.skinSearchAndReplace.append(['<!-- Infobar ibar -->', '<constant-widget name="gradient-ib-z1-z2"/>'])
			elif config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-zz1","infobar-style-zz4"):
				self.skinSearchAndReplace.append(['<!-- Infobar ibar -->', '<constant-widget name="gradient-ib-zz1-zz4"/>'])
			elif config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-zz2","infobar-style-zz3"):
				self.skinSearchAndReplace.append(['<!-- Infobar ibar -->', '<constant-widget name="gradient-ib-zz2-zz3"/>'])
			elif config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-zzz1","infobar-style-zzz2"):
				self.skinSearchAndReplace.append(['<!-- Infobar ibar -->', '<constant-widget name="gradient-ib-zzz1"/>'])

		### MediaPortal (player) box-style
		if config.plugins.KravenFHD.MediaPortal.value == "mediaportal":
			if config.plugins.KravenFHD.InfobarBoxColor.value == "gradient":
				mpplayer = """<ePixmap pixmap="KravenFHD/graphics/ibar5.png" position="0,915" size="1920,165" zPosition="-9" />
	  <eLabel position="0,915" size="1920,3" backgroundColor="KravenIBLine" zPosition="-8" />"""
				self.skinSearchAndReplace.append(['<!-- MediaPortal playercolor */-->', mpplayer])
			elif config.plugins.KravenFHD.InfobarBoxColor.value == "texture":
				mpplayer1 = """<ePixmap pixmap="KravenFHD/graphics/ibtexture.png" position="0,915" size="1920,165" zPosition="-9" />
	  <eLabel position="0,915" size="1920,3" backgroundColor="KravenIBLine" zPosition="-8" />"""
				self.skinSearchAndReplace.append(['<!-- MediaPortal playercolor */-->', mpplayer1])
			else:
				mpplayer2 = """<eLabel position="0,915" size="1920,165" backgroundColor="KravenIBbg" zPosition="-9" />
	  <eLabel position="0,915" size="1920,3" backgroundColor="KravenIBLine" zPosition="-8" />"""
				self.skinSearchAndReplace.append(['<!-- MediaPortal playercolor */-->', mpplayer2])
			
		### Font Colors
		self.skinSearchAndReplace.append(['name="KravenFont1" value="#00ffffff', 'name="KravenFont1" value="#00' + config.plugins.KravenFHD.Font1.value])
		self.skinSearchAndReplace.append(['name="KravenFont2" value="#00F0A30A', 'name="KravenFont2" value="#00' + config.plugins.KravenFHD.Font2.value])
		if config.plugins.KravenFHD.Unskinned.value == "unskinned-colors-on":
			self.skinSearchAndReplace.append(['name="foreground" value="#00dddddd', 'name="foreground" value="#00' + config.plugins.KravenFHD.Font1.value])
		self.skinSearchAndReplace.append(['name="KravenIBFont1" value="#00ffffff', 'name="KravenIBFont1" value="#00' + config.plugins.KravenFHD.IBFont1.value])
		self.skinSearchAndReplace.append(['name="KravenIBFont2" value="#00F0A30A', 'name="KravenIBFont2" value="#00' + config.plugins.KravenFHD.IBFont2.value])
		self.skinSearchAndReplace.append(['name="KravenPermanentClock" value="#00ffffff', 'name="KravenPermanentClock" value="#00' + config.plugins.KravenFHD.PermanentClockFont.value])
		self.skinSearchAndReplace.append(['name="KravenSelFont" value="#00ffffff', 'name="KravenSelFont" value="#00' + config.plugins.KravenFHD.SelectionFont.value])
		self.skinSearchAndReplace.append(['name="KravenSelection" value="#000050EF', 'name="KravenSelection" value="#00' + config.plugins.KravenFHD.SelectionBackground.value])
		if config.plugins.KravenFHD.EMCSelectionColors.value == "none":
			self.skinSearchAndReplace.append(['name="KravenEMCSelFont" value="#00ffffff', 'name="KravenEMCSelFont" value="#00' + config.plugins.KravenFHD.SelectionFont.value])
			self.skinSearchAndReplace.append(['name="KravenEMCSelection" value="#000050EF', 'name="KravenEMCSelection" value="#00' + config.plugins.KravenFHD.SelectionBackground.value])
		else:
			self.skinSearchAndReplace.append(['name="KravenEMCSelFont" value="#00ffffff', 'name="KravenEMCSelFont" value="#00' + config.plugins.KravenFHD.EMCSelectionFont.value])
			self.skinSearchAndReplace.append(['name="KravenEMCSelection" value="#000050EF', 'name="KravenEMCSelection" value="#00' + config.plugins.KravenFHD.EMCSelectionBackground.value])
		self.skinSearchAndReplace.append(['name="selectedFG" value="#00ffffff', 'name="selectedFG" value="#00' + config.plugins.KravenFHD.SelectionFont.value])
		self.skinSearchAndReplace.append(['name="KravenMarked" value="#00ffffff', 'name="KravenMarked" value="#00' + config.plugins.KravenFHD.MarkedFont.value])
		self.skinSearchAndReplace.append(['name="KravenECM" value="#00ffffff', 'name="KravenECM" value="#00' + config.plugins.KravenFHD.ECMFont.value])
		self.skinSearchAndReplace.append(['name="KravenName" value="#00ffffff', 'name="KravenName" value="#00' + config.plugins.KravenFHD.ChannelnameFont.value])
		self.skinSearchAndReplace.append(['name="KravenButton" value="#00ffffff', 'name="KravenButton" value="#00' + config.plugins.KravenFHD.ButtonText.value])
		self.skinSearchAndReplace.append(['name="KravenAndroid" value="#00ffffff', 'name="KravenAndroid" value="#00' + config.plugins.KravenFHD.Android.value])
		self.skinSearchAndReplace.append(['name="KravenAndroid2" value="#00ffffff', 'name="KravenAndroid2" value="#00' + config.plugins.KravenFHD.Android2.value])
		self.skinSearchAndReplace.append(['name="KravenPrime" value="#0070AD11', 'name="KravenPrime" value="#00' + config.plugins.KravenFHD.PrimetimeFont.value])

		### Infobar (Serviceevent) Font-Size
		if config.plugins.KravenFHD.IBFontSize.value == "size-33":
			self.skinSearchAndReplace.append(['font="Regular;45" position="904,813" size="504,55"', 'font="Regular;33" position="904,822" size="504,42"']) # ZZ1, ZZZ1 now
			self.skinSearchAndReplace.append(['font="Regular;45" position="904,959" size="504,55"', 'font="Regular;33" position="904,968" size="504,42"']) # ZZ1, ZZZ1 next
			self.skinSearchAndReplace.append(['font="Regular;45" position="820,784" size="747,55"', 'font="Regular;33" position="820,793" size="747,42"']) # ZZZ2 now
			self.skinSearchAndReplace.append(['font="Regular;45" position="820,922" size="586,55"', 'font="Regular;33" position="820,931" size="586,42"']) # ZZZ2 next
			self.skinSearchAndReplace.append(['font="Regular;45" position="904,815" size="726,55"', 'font="Regular;33" position="904,824" size="726,42"']) # ZZ4 now
			self.skinSearchAndReplace.append(['font="Regular;45" position="904,965" size="726,55"', 'font="Regular;33" position="904,974" size="726,42"']) # ZZ4 next
			self.skinSearchAndReplace.append(['font="Regular;45" position="657,921" size="708,55"', 'font="Regular;33" position="657,930" size="708,42"']) # ZZ2, ZZ3 now
			self.skinSearchAndReplace.append(['font="Regular;45" position="765,999" size="655,55"', 'font="Regular;33" position="765,1008" size="655,42"']) # ZZ3 next
			self.skinSearchAndReplace.append(['font="Regular;45" position="645,882" size="721,55"', 'font="Regular;33" position="645,891" size="721,42"']) # x4 now
			self.skinSearchAndReplace.append(['font="Regular;45" position="645,960" size="721,55"', 'font="Regular;33" position="645,969" size="721,42"']) # x4 next
			self.skinSearchAndReplace.append(['font="Regular;45" position="644,921" size="722,55"', 'font="Regular;33" position="644,930" size="722,42"']) # X2, X3, Z1, Z2 now
			self.skinSearchAndReplace.append(['font="Regular;45" position="644,999" size="722,55"', 'font="Regular;33" position="644,1008" size="722,42"']) # X2, X3, Z1, Z2 next
			self.skinSearchAndReplace.append(['font="Regular;45" position="644,837" size="722,55"', 'font="Regular;33" position="644,846" size="722,42"']) # X1 now
			self.skinSearchAndReplace.append(['font="Regular;45" position="644,972" size="722,55"', 'font="Regular;33" position="644,981" size="722,42"']) # X1 next
			self.skinSearchAndReplace.append(['font="Regular;45" position="298,876" size="1061,55"', 'font="Regular;33" position="298,885" size="1061,42"']) # no picon now
			self.skinSearchAndReplace.append(['font="Regular;45" position="298,954" size="1061,55"', 'font="Regular;33" position="298,963" size="1061,42"']) # no picon next
		elif config.plugins.KravenFHD.IBFontSize.value == "size-39":
			self.skinSearchAndReplace.append(['font="Regular;45" position="904,813" size="504,55"', 'font="Regular;39" position="904,816" size="504,49"']) # ZZ1, ZZZ1 now
			self.skinSearchAndReplace.append(['font="Regular;45" position="904,959" size="504,55"', 'font="Regular;39" position="904,962" size="504,49"']) # ZZ1, ZZZ1 next
			self.skinSearchAndReplace.append(['font="Regular;45" position="820,784" size="747,55"', 'font="Regular;39" position="820,787" size="747,49"']) # ZZZ2 now
			self.skinSearchAndReplace.append(['font="Regular;45" position="820,922" size="586,55"', 'font="Regular;39" position="820,925" size="586,49"']) # ZZZ2 next
			self.skinSearchAndReplace.append(['font="Regular;45" position="904,815" size="726,55"', 'font="Regular;39" position="904,818" size="726,49"']) # ZZ4 now
			self.skinSearchAndReplace.append(['font="Regular;45" position="904,965" size="726,55"', 'font="Regular;39" position="904,968" size="726,49"']) # ZZ4 next
			self.skinSearchAndReplace.append(['font="Regular;45" position="657,921" size="708,55"', 'font="Regular;39" position="657,924" size="708,49"']) # ZZ2, ZZ3 now
			self.skinSearchAndReplace.append(['font="Regular;45" position="765,999" size="655,55"', 'font="Regular;39" position="765,1002" size="655,49"']) # ZZ3 next
			self.skinSearchAndReplace.append(['font="Regular;45" position="645,882" size="721,55"', 'font="Regular;39" position="645,885" size="721,49"']) # x4 now
			self.skinSearchAndReplace.append(['font="Regular;45" position="645,960" size="721,55"', 'font="Regular;39" position="645,963" size="721,49"']) # x4 next
			self.skinSearchAndReplace.append(['font="Regular;45" position="644,921" size="722,55"', 'font="Regular;39" position="644,924" size="722,49"']) # X2, X3, Z1, Z2 now
			self.skinSearchAndReplace.append(['font="Regular;45" position="644,999" size="722,55"', 'font="Regular;39" position="644,1002" size="722,49"']) # X2, X3, Z1, Z2 next
			self.skinSearchAndReplace.append(['font="Regular;45" position="644,837" size="722,55"', 'font="Regular;39" position="644,840" size="722,49"']) # X1 now
			self.skinSearchAndReplace.append(['font="Regular;45" position="644,972" size="722,55"', 'font="Regular;39" position="644,975" size="722,49"']) # X1 next
			self.skinSearchAndReplace.append(['font="Regular;45" position="298,876" size="1061,55"', 'font="Regular;39" position="298,879" size="1061,49"']) # no picon now
			self.skinSearchAndReplace.append(['font="Regular;45" position="298,954" size="1061,55"', 'font="Regular;39" position="298,957" size="1061,49"']) # no picon next

		### ChannelSelection (Servicename, Servicenumber, Serviceinfo) Font-Size
		if self.E2DistroVersion == "VTi":
			if not self.actChannelselectionstyle in ("channelselection-style-nobile","channelselection-style-nobile2","channelselection-style-nobile-minitv","channelselection-style-nobile-minitv3","channelselection-style-nobile-minitv33"):
				if config.plugins.KravenFHD.ChannelSelectionServiceSize.value == "size-24":
					self.skinSearchAndReplace.append(['serviceNumberFont="Regular;37"', 'serviceNumberFont="Regular;24"'])
					self.skinSearchAndReplace.append(['serviceNameFont="Regular;37"', 'serviceNameFont="Regular;24"'])
				elif config.plugins.KravenFHD.ChannelSelectionServiceSize.value == "size-27":
					self.skinSearchAndReplace.append(['serviceNumberFont="Regular;37"', 'serviceNumberFont="Regular;27"'])
					self.skinSearchAndReplace.append(['serviceNameFont="Regular;37"', 'serviceNameFont="Regular;27"'])
				elif config.plugins.KravenFHD.ChannelSelectionServiceSize.value == "size-30":
					self.skinSearchAndReplace.append(['serviceNumberFont="Regular;37"', 'serviceNumberFont="Regular;30"'])
					self.skinSearchAndReplace.append(['serviceNameFont="Regular;37"', 'serviceNameFont="Regular;30"'])
				elif config.plugins.KravenFHD.ChannelSelectionServiceSize.value == "size-33":
					self.skinSearchAndReplace.append(['serviceNumberFont="Regular;37"', 'serviceNumberFont="Regular;33"'])
					self.skinSearchAndReplace.append(['serviceNameFont="Regular;37"', 'serviceNameFont="Regular;33"'])
				elif config.plugins.KravenFHD.ChannelSelectionServiceSize.value == "size-36":
					self.skinSearchAndReplace.append(['serviceNumberFont="Regular;37"', 'serviceNumberFont="Regular;36"'])
					self.skinSearchAndReplace.append(['serviceNameFont="Regular;37"', 'serviceNameFont="Regular;36"'])
				elif config.plugins.KravenFHD.ChannelSelectionServiceSize.value == "size-39":
					self.skinSearchAndReplace.append(['serviceNumberFont="Regular;37"', 'serviceNumberFont="Regular;39"'])
					self.skinSearchAndReplace.append(['serviceNameFont="Regular;37"', 'serviceNameFont="Regular;39"'])
				elif config.plugins.KravenFHD.ChannelSelectionServiceSize.value == "size-42":
					self.skinSearchAndReplace.append(['serviceNumberFont="Regular;37"', 'serviceNumberFont="Regular;42"'])
					self.skinSearchAndReplace.append(['serviceNameFont="Regular;37"', 'serviceNameFont="Regular;42"'])
				elif config.plugins.KravenFHD.ChannelSelectionServiceSize.value == "size-45":
					self.skinSearchAndReplace.append(['serviceNumberFont="Regular;37"', 'serviceNumberFont="Regular;45"'])
					self.skinSearchAndReplace.append(['serviceNameFont="Regular;37"', 'serviceNameFont="Regular;45"'])
				if config.plugins.KravenFHD.ChannelSelectionInfoSize.value == "size-24":
					self.skinSearchAndReplace.append(['serviceInfoFont="Regular;34"', 'serviceInfoFont="Regular;24"'])
				elif config.plugins.KravenFHD.ChannelSelectionInfoSize.value == "size-27":
					self.skinSearchAndReplace.append(['serviceInfoFont="Regular;34"', 'serviceInfoFont="Regular;27"'])
				elif config.plugins.KravenFHD.ChannelSelectionInfoSize.value == "size-30":
					self.skinSearchAndReplace.append(['serviceInfoFont="Regular;34"', 'serviceInfoFont="Regular;30"'])
				elif config.plugins.KravenFHD.ChannelSelectionInfoSize.value == "size-33":
					self.skinSearchAndReplace.append(['serviceInfoFont="Regular;34"', 'serviceInfoFont="Regular;33"'])
				elif config.plugins.KravenFHD.ChannelSelectionInfoSize.value == "size-36":
					self.skinSearchAndReplace.append(['serviceInfoFont="Regular;34"', 'serviceInfoFont="Regular;36"'])
				elif config.plugins.KravenFHD.ChannelSelectionInfoSize.value == "size-39":
					self.skinSearchAndReplace.append(['serviceInfoFont="Regular;34"', 'serviceInfoFont="Regular;39"'])
				elif config.plugins.KravenFHD.ChannelSelectionInfoSize.value == "size-42":
					self.skinSearchAndReplace.append(['serviceInfoFont="Regular;34"', 'serviceInfoFont="Regular;42"'])
				elif config.plugins.KravenFHD.ChannelSelectionInfoSize.value == "size-45":
					self.skinSearchAndReplace.append(['serviceInfoFont="Regular;34"', 'serviceInfoFont="Regular;45"'])
			else:
				if config.plugins.KravenFHD.ChannelSelectionServiceSize1.value == "size-24":
					self.skinSearchAndReplace.append(['serviceNumberFont="Regular;30"', 'serviceNumberFont="Regular;24"'])
					self.skinSearchAndReplace.append(['serviceNameFont="Regular;30"', 'serviceNameFont="Regular;24"'])
				elif config.plugins.KravenFHD.ChannelSelectionServiceSize1.value == "size-27":
					self.skinSearchAndReplace.append(['serviceNumberFont="Regular;30"', 'serviceNumberFont="Regular;27"'])
					self.skinSearchAndReplace.append(['serviceNameFont="Regular;30"', 'serviceNameFont="Regular;27"'])
				elif config.plugins.KravenFHD.ChannelSelectionServiceSize1.value == "size-33":
					self.skinSearchAndReplace.append(['serviceNumberFont="Regular;30"', 'serviceNumberFont="Regular;33"'])
					self.skinSearchAndReplace.append(['serviceNameFont="Regular;30"', 'serviceNameFont="Regular;33"'])
				elif config.plugins.KravenFHD.ChannelSelectionServiceSize1.value == "size-36":
					self.skinSearchAndReplace.append(['serviceNumberFont="Regular;30"', 'serviceNumberFont="Regular;36"'])
					self.skinSearchAndReplace.append(['serviceNameFont="Regular;30"', 'serviceNameFont="Regular;36"'])
				elif config.plugins.KravenFHD.ChannelSelectionServiceSize1.value == "size-39":
					self.skinSearchAndReplace.append(['serviceNumberFont="Regular;30"', 'serviceNumberFont="Regular;39"'])
					self.skinSearchAndReplace.append(['serviceNameFont="Regular;30"', 'serviceNameFont="Regular;39"'])
				if config.plugins.KravenFHD.ChannelSelectionInfoSize1.value == "size-24":
					self.skinSearchAndReplace.append(['serviceInfoFont="Regular;30"', 'serviceInfoFont="Regular;24"'])
				elif config.plugins.KravenFHD.ChannelSelectionInfoSize1.value == "size-27":
					self.skinSearchAndReplace.append(['serviceInfoFont="Regular;30"', 'serviceInfoFont="Regular;27"'])
				elif config.plugins.KravenFHD.ChannelSelectionInfoSize1.value == "size-33":
					self.skinSearchAndReplace.append(['serviceInfoFont="Regular;30"', 'serviceInfoFont="Regular;33"'])
				elif config.plugins.KravenFHD.ChannelSelectionInfoSize1.value == "size-36":
					self.skinSearchAndReplace.append(['serviceInfoFont="Regular;30"', 'serviceInfoFont="Regular;36"'])
				elif config.plugins.KravenFHD.ChannelSelectionInfoSize1.value == "size-39":
					self.skinSearchAndReplace.append(['serviceInfoFont="Regular;30"', 'serviceInfoFont="Regular;39"'])

		### ChannelSelection (itemHeight for two lines)
		if self.actChannelselectionstyle in ("channelselection-style-nobile","channelselection-style-nobile2","channelselection-style-nobile-minitv","channelselection-style-nobile-minitv3","channelselection-style-nobile-minitv33"):
			self.skinSearchAndReplace.append(['<parameter name="ServicelistDoubleSpacedMinHeight" value="104" />', '<parameter name="ServicelistDoubleSpacedMinHeight" value="86" />'])

		### ChannelSelection (Event-Description) Font-Size and Primetime
		if self.actChannelselectionstyle in ("channelselection-style-minitv","channelselection-style-minitv3"):
			if config.plugins.KravenFHD.Primetimeavailable.value == "primetime-on" and config.plugins.KravenFHD.ChannelSelectionEPGSize3.value == "big":
				self.skinSearchAndReplace.append(['<constant-widget name="CSLEPG32"/>', '<constant-widget name="CSLEPG36Prime"/>'])
			elif config.plugins.KravenFHD.Primetimeavailable.value == "none" and config.plugins.KravenFHD.ChannelSelectionEPGSize3.value == "big":
				self.skinSearchAndReplace.append(['<constant-widget name="CSLEPG32"/>', '<constant-widget name="CSLEPG36"/>'])
			elif config.plugins.KravenFHD.Primetimeavailable.value == "primetime-on" and config.plugins.KravenFHD.ChannelSelectionEPGSize3.value == "small":
				self.skinSearchAndReplace.append(['<constant-widget name="CSLEPG32"/>', '<constant-widget name="CSLEPG32Prime"/>'])
		elif self.actChannelselectionstyle == "channelselection-style-minitv33":
			if config.plugins.KravenFHD.Primetimeavailable.value == "primetime-on" and config.plugins.KravenFHD.ChannelSelectionEPGSize3.value == "big":
				self.skinSearchAndReplace.append(['<constant-widget name="CSEPEPG32"/>', '<constant-widget name="CSEPEPG36Prime"/>'])
			elif config.plugins.KravenFHD.Primetimeavailable.value == "none" and config.plugins.KravenFHD.ChannelSelectionEPGSize3.value == "big":
				self.skinSearchAndReplace.append(['<constant-widget name="CSEPEPG32"/>', '<constant-widget name="CSEPEPG36"/>'])
			elif config.plugins.KravenFHD.Primetimeavailable.value == "primetime-on" and config.plugins.KravenFHD.ChannelSelectionEPGSize3.value == "small":
				self.skinSearchAndReplace.append(['<constant-widget name="CSEPEPG32"/>', '<constant-widget name="CSEPEPG32Prime"/>'])
		elif self.actChannelselectionstyle == "channelselection-style-minitv4":
			if config.plugins.KravenFHD.Primetimeavailable.value == "primetime-on" and config.plugins.KravenFHD.ChannelSelectionEPGSize3.value == "big":
				self.skinSearchAndReplace.append(['<constant-widget name="CSREPG32"/>', '<constant-widget name="CSREPG36Prime"/>'])
			elif config.plugins.KravenFHD.Primetimeavailable.value == "none" and config.plugins.KravenFHD.ChannelSelectionEPGSize3.value == "big":
				self.skinSearchAndReplace.append(['<constant-widget name="CSREPG32"/>', '<constant-widget name="CSREPG36"/>'])
			elif config.plugins.KravenFHD.Primetimeavailable.value == "primetime-on" and config.plugins.KravenFHD.ChannelSelectionEPGSize3.value == "small":
				self.skinSearchAndReplace.append(['<constant-widget name="CSREPG32"/>', '<constant-widget name="CSREPG32Prime"/>'])
		elif self.actChannelselectionstyle == "channelselection-style-minitv2":
			if config.plugins.KravenFHD.Primetimeavailable.value == "primetime-on" and config.plugins.KravenFHD.ChannelSelectionEPGSize3.value == "big":
				self.skinSearchAndReplace.append(['<constant-widget name="CSMT2EPG32"/>', '<constant-widget name="CSMT2EPG36Prime"/>'])
			elif config.plugins.KravenFHD.Primetimeavailable.value == "none" and config.plugins.KravenFHD.ChannelSelectionEPGSize3.value == "big":
				self.skinSearchAndReplace.append(['<constant-widget name="CSMT2EPG32"/>', '<constant-widget name="CSMT2EPG36"/>'])
			elif config.plugins.KravenFHD.Primetimeavailable.value == "primetime-on" and config.plugins.KravenFHD.ChannelSelectionEPGSize3.value == "small":
				self.skinSearchAndReplace.append(['<constant-widget name="CSMT2EPG32"/>', '<constant-widget name="CSMT2EPG32Prime"/>'])
		elif self.actChannelselectionstyle == "channelselection-style-minitv22":
			if config.plugins.KravenFHD.Primetimeavailable.value == "primetime-on" and config.plugins.KravenFHD.ChannelSelectionEPGSize2.value == "big":
				self.skinSearchAndReplace.append(['<constant-widget name="CSMT22EPG32"/>', '<constant-widget name="CSMT22EPG36Prime"/>'])
			elif config.plugins.KravenFHD.Primetimeavailable.value == "none" and config.plugins.KravenFHD.ChannelSelectionEPGSize2.value == "big":
				self.skinSearchAndReplace.append(['<constant-widget name="CSMT22EPG32"/>', '<constant-widget name="CSMT22EPG36"/>'])
			elif config.plugins.KravenFHD.Primetimeavailable.value == "primetime-on" and config.plugins.KravenFHD.ChannelSelectionEPGSize2.value == "small":
				self.skinSearchAndReplace.append(['<constant-widget name="CSMT22EPG32"/>', '<constant-widget name="CSMT22EPG32Prime"/>'])
		elif self.actChannelselectionstyle == "channelselection-style-nobile":
			if config.plugins.KravenFHD.Primetimeavailable.value == "primetime-on" and config.plugins.KravenFHD.ChannelSelectionEPGSize1.value == "big":
				self.skinSearchAndReplace.append(['<constant-widget name="CSNEPG28"/>', '<constant-widget name="CSNEPG32Prime"/>'])
			elif config.plugins.KravenFHD.Primetimeavailable.value == "none" and config.plugins.KravenFHD.ChannelSelectionEPGSize1.value == "big":
				self.skinSearchAndReplace.append(['<constant-widget name="CSNEPG28"/>', '<constant-widget name="CSNEPG32"/>'])
			elif config.plugins.KravenFHD.Primetimeavailable.value == "primetime-on" and config.plugins.KravenFHD.ChannelSelectionEPGSize1.value == "small":
				self.skinSearchAndReplace.append(['<constant-widget name="CSNEPG28"/>', '<constant-widget name="CSNEPG28Prime"/>'])
		elif self.actChannelselectionstyle == "channelselection-style-nobile2":
			if config.plugins.KravenFHD.Primetimeavailable.value == "primetime-on" and config.plugins.KravenFHD.ChannelSelectionEPGSize1.value == "big":
				self.skinSearchAndReplace.append(['<constant-widget name="CSN2EPG28"/>', '<constant-widget name="CSN2EPG32Prime"/>'])
			elif config.plugins.KravenFHD.Primetimeavailable.value == "none" and config.plugins.KravenFHD.ChannelSelectionEPGSize1.value == "big":
				self.skinSearchAndReplace.append(['<constant-widget name="CSN2EPG28"/>', '<constant-widget name="CSN2EPG32"/>'])
			elif config.plugins.KravenFHD.Primetimeavailable.value == "primetime-on" and config.plugins.KravenFHD.ChannelSelectionEPGSize1.value == "small":
				self.skinSearchAndReplace.append(['<constant-widget name="CSN2EPG28"/>', '<constant-widget name="CSN2EPG28Prime"/>'])
		elif self.actChannelselectionstyle in ("channelselection-style-nobile-minitv","channelselection-style-nobile-minitv3"):
			if config.plugins.KravenFHD.Primetimeavailable.value == "primetime-on" and config.plugins.KravenFHD.ChannelSelectionEPGSize1.value == "big":
				self.skinSearchAndReplace.append(['<constant-widget name="CSNMTEPG28"/>', '<constant-widget name="CSNMTEPG32Prime"/>'])
			elif config.plugins.KravenFHD.Primetimeavailable.value == "none" and config.plugins.KravenFHD.ChannelSelectionEPGSize1.value == "big":
				self.skinSearchAndReplace.append(['<constant-widget name="CSNMTEPG28"/>', '<constant-widget name="CSNMTEPG32"/>'])
			elif config.plugins.KravenFHD.Primetimeavailable.value == "primetime-on" and config.plugins.KravenFHD.ChannelSelectionEPGSize1.value == "small":
				self.skinSearchAndReplace.append(['<constant-widget name="CSNMTEPG28"/>', '<constant-widget name="CSNMTEPG28Prime"/>'])
		elif self.actChannelselectionstyle == "channelselection-style-nobile-minitv33":
			if config.plugins.KravenFHD.Primetimeavailable.value == "primetime-on" and config.plugins.KravenFHD.ChannelSelectionEPGSize1.value == "big":
				self.skinSearchAndReplace.append(['<constant-widget name="CSNMTEPEPG28"/>', '<constant-widget name="CSNMTEPEPG32Prime"/>'])
			elif config.plugins.KravenFHD.Primetimeavailable.value == "none" and config.plugins.KravenFHD.ChannelSelectionEPGSize1.value == "big":
				self.skinSearchAndReplace.append(['<constant-widget name="CSNMTEPEPG28"/>', '<constant-widget name="CSNMTEPEPG32"/>'])
			elif config.plugins.KravenFHD.Primetimeavailable.value == "primetime-on" and config.plugins.KravenFHD.ChannelSelectionEPGSize1.value == "small":
				self.skinSearchAndReplace.append(['<constant-widget name="CSNMTEPEPG28"/>', '<constant-widget name="CSNMTEPEPG28Prime"/>'])
		elif self.actChannelselectionstyle == "channelselection-style-nopicon":
			if config.plugins.KravenFHD.Primetimeavailable.value == "primetime-on" and config.plugins.KravenFHD.ChannelSelectionEPGSize3.value == "big":
				self.skinSearchAndReplace.append(['<constant-widget name="CSNPEPG32"/>', '<constant-widget name="CSNPEPG36Prime"/>'])
			elif config.plugins.KravenFHD.Primetimeavailable.value == "none" and config.plugins.KravenFHD.ChannelSelectionEPGSize3.value == "big":
				self.skinSearchAndReplace.append(['<constant-widget name="CSNPEPG32"/>', '<constant-widget name="CSNPEPG36"/>'])
			elif config.plugins.KravenFHD.Primetimeavailable.value == "primetime-on" and config.plugins.KravenFHD.ChannelSelectionEPGSize3.value == "small":
				self.skinSearchAndReplace.append(['<constant-widget name="CSNPEPG32"/>', '<constant-widget name="CSNPEPG32Prime"/>'])
		elif self.actChannelselectionstyle == "channelselection-style-nopicon2":
			if config.plugins.KravenFHD.Primetimeavailable.value == "primetime-on" and config.plugins.KravenFHD.ChannelSelectionEPGSize3.value == "big":
				self.skinSearchAndReplace.append(['<constant-widget name="CSNP2EPG32"/>', '<constant-widget name="CSNP2EPG36Prime"/>'])
			elif config.plugins.KravenFHD.Primetimeavailable.value == "none" and config.plugins.KravenFHD.ChannelSelectionEPGSize3.value == "big":
				self.skinSearchAndReplace.append(['<constant-widget name="CSNP2EPG32"/>', '<constant-widget name="CSNP2EPG36"/>'])
			elif config.plugins.KravenFHD.Primetimeavailable.value == "primetime-on" and config.plugins.KravenFHD.ChannelSelectionEPGSize3.value == "small":
				self.skinSearchAndReplace.append(['<constant-widget name="CSNP2EPG32"/>', '<constant-widget name="CSNP2EPG32Prime"/>'])
		elif self.actChannelselectionstyle == "channelselection-style-xpicon":
			if config.plugins.KravenFHD.Primetimeavailable.value == "primetime-on" and config.plugins.KravenFHD.ChannelSelectionEPGSize3.value == "big":
				self.skinSearchAndReplace.append(['<constant-widget name="CSXEPG32"/>', '<constant-widget name="CSXEPG36Prime"/>'])
			elif config.plugins.KravenFHD.Primetimeavailable.value == "none" and config.plugins.KravenFHD.ChannelSelectionEPGSize3.value == "big":
				self.skinSearchAndReplace.append(['<constant-widget name="CSXEPG32"/>', '<constant-widget name="CSXEPG36"/>'])
			elif config.plugins.KravenFHD.Primetimeavailable.value == "primetime-on" and config.plugins.KravenFHD.ChannelSelectionEPGSize3.value == "small":
				self.skinSearchAndReplace.append(['<constant-widget name="CSXEPG32"/>', '<constant-widget name="CSXEPG32Prime"/>'])
		elif self.actChannelselectionstyle == "channelselection-style-zpicon":
			if config.plugins.KravenFHD.Primetimeavailable.value == "primetime-on" and config.plugins.KravenFHD.ChannelSelectionEPGSize3.value == "big":
				self.skinSearchAndReplace.append(['<constant-widget name="CSZEPG32"/>', '<constant-widget name="CSZEPG36Prime"/>'])
			elif config.plugins.KravenFHD.Primetimeavailable.value == "none" and config.plugins.KravenFHD.ChannelSelectionEPGSize3.value == "big":
				self.skinSearchAndReplace.append(['<constant-widget name="CSZEPG32"/>', '<constant-widget name="CSZEPG36"/>'])
			elif config.plugins.KravenFHD.Primetimeavailable.value == "primetime-on" and config.plugins.KravenFHD.ChannelSelectionEPGSize3.value == "small":
				self.skinSearchAndReplace.append(['<constant-widget name="CSZEPG32"/>', '<constant-widget name="CSZEPG32Prime"/>'])
		elif self.actChannelselectionstyle == "channelselection-style-zzpicon":
			if config.plugins.KravenFHD.Primetimeavailable.value == "primetime-on" and config.plugins.KravenFHD.ChannelSelectionEPGSize3.value == "big":
				self.skinSearchAndReplace.append(['<constant-widget name="CSZZEPG32"/>', '<constant-widget name="CSZZEPG36Prime"/>'])
			elif config.plugins.KravenFHD.Primetimeavailable.value == "none" and config.plugins.KravenFHD.ChannelSelectionEPGSize3.value == "big":
				self.skinSearchAndReplace.append(['<constant-widget name="CSZZEPG32"/>', '<constant-widget name="CSZZEPG36"/>'])
			elif config.plugins.KravenFHD.Primetimeavailable.value == "primetime-on" and config.plugins.KravenFHD.ChannelSelectionEPGSize3.value == "small":
				self.skinSearchAndReplace.append(['<constant-widget name="CSZZEPG32"/>', '<constant-widget name="CSZZEPG32Prime"/>'])
		elif self.actChannelselectionstyle == "channelselection-style-zzzpicon":
			if config.plugins.KravenFHD.Primetimeavailable.value == "primetime-on" and config.plugins.KravenFHD.ChannelSelectionEPGSize3.value == "big":
				self.skinSearchAndReplace.append(['<constant-widget name="CSZZZEPG32"/>', '<constant-widget name="CSZZZEPG36Prime"/>'])
			elif config.plugins.KravenFHD.Primetimeavailable.value == "none" and config.plugins.KravenFHD.ChannelSelectionEPGSize3.value == "big":
				self.skinSearchAndReplace.append(['<constant-widget name="CSZZZEPG32"/>', '<constant-widget name="CSZZZEPG36"/>'])
			elif config.plugins.KravenFHD.Primetimeavailable.value == "primetime-on" and config.plugins.KravenFHD.ChannelSelectionEPGSize3.value == "small":
				self.skinSearchAndReplace.append(['<constant-widget name="CSZZZEPG32"/>', '<constant-widget name="CSZZZEPG32Prime"/>'])
		elif self.actChannelselectionstyle == "channelselection-style-minitv-picon":
			if config.plugins.KravenFHD.Primetimeavailable.value == "primetime-on" and config.plugins.KravenFHD.ChannelSelectionEPGSize3.value == "big":
				self.skinSearchAndReplace.append(['<constant-widget name="CSMTP32"/>', '<constant-widget name="CSMTP32Prime"/>'])
			elif config.plugins.KravenFHD.Primetimeavailable.value == "none" and config.plugins.KravenFHD.ChannelSelectionEPGSize3.value == "big":
				self.skinSearchAndReplace.append(['<constant-widget name="CSMTP32"/>', '<constant-widget name="CSMTP36"/>'])
			elif config.plugins.KravenFHD.Primetimeavailable.value == "primetime-on" and config.plugins.KravenFHD.ChannelSelectionEPGSize3.value == "small":
				self.skinSearchAndReplace.append(['<constant-widget name="CSMTP32"/>', '<constant-widget name="CSMTP36Prime"/>'])

		### ChannelSelection horizontal Primetime
		if self.E2DistroVersion == "VTi" and config.plugins.KravenFHD.alternativeChannellist.value == "on" and config.plugins.KravenFHD.ChannelSelectionHorStyle.value == "cshor-minitv" and config.plugins.KravenFHD.Primetimeavailable.value == "primetime-on":
			self.skinSearchAndReplace.append(['<constant-widget name="CSHORMT"/>', '<constant-widget name="CSHORMTPrime"/>'])

		### ChannelSelection 'not available' Font
		self.skinSearchAndReplace.append(['name="KravenNotAvailable" value="#00FFEA04', 'name="KravenNotAvailable" value="#00' + config.plugins.KravenFHD.ChannelSelectionServiceNA.value])

		### GraphEPG selected background color
		if config.plugins.KravenFHD.GMErunningbg.value == "global":
			self.skinSearchAndReplace.append(['name="KravenGMErunningbg" value="#00389416', 'name="KravenGMErunningbg" value="#00' + config.plugins.KravenFHD.SelectionBackground.value])
		else:
			self.skinSearchAndReplace.append(['name="KravenGMErunningbg" value="#00389416', 'name="KravenGMErunningbg" value="#00' + config.plugins.KravenFHD.GMErunningbg.value])

		### Debug-Names
		if config.plugins.KravenFHD.DebugNames.value == "screennames-on":
			self.skinSearchAndReplace.append(['<!--<text', '<eLabel backgroundColor="#00000000" font="Regular;22" foregroundColor="white" text'])

			debug = """<widget backgroundColor="#00000000" font="Regular;22" foregroundColor="white" render="Label" source="menu" position="105,0" size="750,27" halign="left" valign="center" transparent="1" zPosition="9">
	  <convert type="KravenFHDMenuEntryID"></convert>
	</widget>
	<eLabel position="0,0" size="1920,27" backgroundColor="#00000000" zPosition="8" />"""
			self.skinSearchAndReplace.append(['<!-- KravenFHDMenuEntryID-Converter -->', debug])

			debugpos1 = """ " position="105,0" size="750,27" halign="left" valign="center" transparent="1" zPosition="9" />
	<eLabel position="0,0" size="1920,27" backgroundColor="#00000000" zPosition="8" />"""
			self.skinSearchAndReplace.append(['" position="105,0" />-->', debugpos1])

			debugpos2 = """ " position="63,0" size="750,27" halign="left" valign="center" transparent="1" zPosition="9" />
	<eLabel position="0,0" size="1920,27" backgroundColor="#00000000" zPosition="8" />"""
			self.skinSearchAndReplace.append(['" position="63,0" />-->', debugpos2])

			debugpos3 = """ " position="60,0" size="750,27" halign="left" valign="center" transparent="1" zPosition="9" />
	<eLabel position="0,0" size="1920,27" backgroundColor="#00000000" zPosition="8" />"""
			self.skinSearchAndReplace.append(['" position="60,0" />-->', debugpos3])

		### Icons
		if config.plugins.KravenFHD.IBColor.value == "only-infobar":
			if config.plugins.KravenFHD.IconStyle2.value == "icons-dark2":
				self.skinSearchAndReplace.append(["/global-icons/", "/icons-dark/"])
				self.skinSearchAndReplace.append(["/infobar-global-icons/", "/icons-dark/"])
			elif config.plugins.KravenFHD.IconStyle2.value == "icons-light2":
				self.skinSearchAndReplace.append(["/global-icons/", "/icons-light/"])
				self.skinSearchAndReplace.append(["/infobar-global-icons/", "/icons-light/"])
			if config.plugins.KravenFHD.IconStyle.value == "icons-dark":
				self.skinSearchAndReplace.append(['name="KravenIcon" value="#00fff0e0"', 'name="KravenIcon" value="#00000000"'])
				self.skinSearchAndReplace.append(["/infobar-icons/", "/icons-dark/"])
			elif config.plugins.KravenFHD.IconStyle.value == "icons-light":
				self.skinSearchAndReplace.append(["/infobar-icons/", "/icons-light/"])
		elif config.plugins.KravenFHD.IBColor.value == "all-screens":
			if config.plugins.KravenFHD.IconStyle2.value == "icons-dark2":
				self.skinSearchAndReplace.append(["/global-icons/", "/icons-dark/"])
			elif config.plugins.KravenFHD.IconStyle2.value == "icons-light2":
				self.skinSearchAndReplace.append(["/global-icons/", "/icons-light/"])
			if config.plugins.KravenFHD.IconStyle.value == "icons-dark":
				self.skinSearchAndReplace.append(['name="KravenIcon" value="#00fff0e0"', 'name="KravenIcon" value="#00000000"'])
				self.skinSearchAndReplace.append(["/infobar-icons/", "/icons-dark/"])
				self.skinSearchAndReplace.append(["/infobar-global-icons/", "/icons-dark/"])
			elif config.plugins.KravenFHD.IconStyle.value == "icons-light":
				self.skinSearchAndReplace.append(["/infobar-icons/", "/icons-light/"])
				self.skinSearchAndReplace.append(["/infobar-global-icons/", "/icons-light/"])

		console3 = eConsoleAppContainer()
		if config.plugins.KravenFHD.IconStyle2.value == "icons-light2":
			console3.execute("tar xf /usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/data/icons-white.tar.gz -C /usr/share/enigma2/KravenFHD/")
		else:
			console3.execute("tar xf /usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/data/icons-black.tar.gz -C /usr/share/enigma2/KravenFHD/")

		### Weather-Server
		if config.plugins.KravenFHD.weather_server.value == "_owm":
			self.skinSearchAndReplace.append(['KravenFHDWeather', 'KravenFHDWeather_owm'])
			if config.plugins.KravenFHD.WeatherView.value == "meteo":
				self.skinSearchAndReplace.append(['size="75,75" render="KravenFHDWetterPicon" alphatest="blend" path="WetterIcons"', 'size="75,75" render="Label" font="Meteo2;60" halign="right" valign="center" foregroundColor="KravenMeteo" noWrap="1"'])
				self.skinSearchAndReplace.append(['size="75,75" path="WetterIcons" render="KravenFHDWetterPicon" alphatest="blend"', 'size="75,75" render="Label" font="Meteo2;67" halign="center" valign="center" foregroundColor="KravenMeteo" noWrap="1"'])
				self.skinSearchAndReplace.append(['size="105,105" render="KravenFHDWetterPicon" alphatest="blend" path="WetterIcons"', 'size="105,105" render="Label" font="Meteo2;90" halign="center" valign="center" foregroundColor="KravenMeteo" noWrap="1"'])
				self.skinSearchAndReplace.append(['size="150,150" render="KravenFHDWetterPicon" alphatest="blend" path="WetterIcons"', 'size="150,150" render="Label" font="Meteo2;150" halign="center" valign="center" foregroundColor="KravenMeteo" noWrap="1"'])
				self.skinSearchAndReplace.append(['MeteoIcon</convert>', 'MeteoFont</convert>'])
		elif config.plugins.KravenFHD.weather_server.value == "_accu":
			self.skinSearchAndReplace.append(['KravenFHDWeather', 'KravenFHDWeather_accu'])
			if config.plugins.KravenFHD.WeatherView.value == "meteo":
				self.skinSearchAndReplace.append(['size="75,75" render="KravenFHDWetterPicon" alphatest="blend" path="WetterIcons"', 'size="75,75" render="Label" font="Meteo;60" halign="right" valign="center" foregroundColor="KravenMeteo" noWrap="1"'])
				self.skinSearchAndReplace.append(['size="75,75" path="WetterIcons" render="KravenFHDWetterPicon" alphatest="blend"', 'size="75,75" render="Label" font="Meteo;67" halign="center" valign="center" foregroundColor="KravenMeteo" noWrap="1"'])
				self.skinSearchAndReplace.append(['size="105,105" render="KravenFHDWetterPicon" alphatest="blend" path="WetterIcons"', 'size="105,105" render="Label" font="Meteo;90" halign="center" valign="center" foregroundColor="KravenMeteo" noWrap="1"'])
				self.skinSearchAndReplace.append(['size="150,150" render="KravenFHDWetterPicon" alphatest="blend" path="WetterIcons"', 'size="150,150" render="Label" font="Meteo;1500" halign="center" valign="center" foregroundColor="KravenMeteo" noWrap="1"'])
				self.skinSearchAndReplace.append(['MeteoIcon</convert>', 'MeteoFont</convert>'])

		### Meteo-Font
		if config.plugins.KravenFHD.MeteoColor.value == "meteo-dark":
			self.skinSearchAndReplace.append(['name="KravenMeteo" value="#00fff0e0"', 'name="KravenMeteo" value="#00000000"'])

		### Progress
		if config.plugins.KravenFHD.Progress.value == "progress2":
			self.skinSearchAndReplace.append([' pixmap="KravenFHD/progress/progress18.png"',' pixmap="KravenFHD/progress/progress18_2.png"'])
			self.skinSearchAndReplace.append([' picServiceEventProgressbar="KravenFHD/progress/progress52.png"',' picServiceEventProgressbar="KravenFHD/progress/progress52_2.png"'])
			self.skinSearchAndReplace.append([' pixmap="KravenFHD/progress/progress170.png"',' pixmap="KravenFHD/progress/progress170_2.png"'])
			self.skinSearchAndReplace.append([' pixmap="KravenFHD/progress/progress200.png"',' pixmap="KravenFHD/progress/progress200_2.png"'])
			self.skinSearchAndReplace.append([' pixmap="KravenFHD/progress/progress220.png"',' pixmap="KravenFHD/progress/progress220_2.png"'])
			self.skinSearchAndReplace.append([' pixmap="KravenFHD/progress/progress248.png"',' pixmap="KravenFHD/progress/progress248_2.png"'])
			self.skinSearchAndReplace.append([' pixmap="KravenFHD/progress/progress270.png"',' pixmap="KravenFHD/progress/progress270_2.png"'])
			self.skinSearchAndReplace.append([' pixmap="KravenFHD/progress/progress300.png"',' pixmap="KravenFHD/progress/progress300_2.png"'])
			self.skinSearchAndReplace.append([' pixmap="KravenFHD/progress/progress328.png"',' pixmap="KravenFHD/progress/progress328_2.png"'])
			self.skinSearchAndReplace.append([' pixmap="KravenFHD/progress/progress370.png"',' pixmap="KravenFHD/progress/progress370_2.png"'])
			self.skinSearchAndReplace.append([' pixmap="KravenFHD/progress/progress380.png"',' pixmap="KravenFHD/progress/progress380_2.png"'])
			self.skinSearchAndReplace.append([' pixmap="KravenFHD/progress/progress410.png"',' pixmap="KravenFHD/progress/progress410_2.png"'])
			self.skinSearchAndReplace.append([' pixmap="KravenFHD/progress/progress480.png"',' pixmap="KravenFHD/progress/progress480_2.png"'])
			self.skinSearchAndReplace.append([' pixmap="KravenFHD/progress/progress581.png"',' pixmap="KravenFHD/progress/progress581_2.png"'])
			self.skinSearchAndReplace.append([' pixmap="KravenFHD/progress/progress599.png"',' pixmap="KravenFHD/progress/progress599_2.png"'])
			self.skinSearchAndReplace.append([' pixmap="KravenFHD/progress/progress655.png"',' pixmap="KravenFHD/progress/progress655_2.png"'])
			self.skinSearchAndReplace.append([' pixmap="KravenFHD/progress/progress708.png"',' pixmap="KravenFHD/progress/progress708_2.png"'])
			self.skinSearchAndReplace.append([' pixmap="KravenFHD/progress/progress749.png"',' pixmap="KravenFHD/progress/progress749_2.png"'])
			self.skinSearchAndReplace.append([' pixmap="KravenFHD/progress/progress858.png"',' pixmap="KravenFHD/progress/progress858_2.png"'])
			self.skinSearchAndReplace.append([' pixmap="KravenFHD/progress/progress888.png"',' pixmap="KravenFHD/progress/progress888_2.png"'])
			self.skinSearchAndReplace.append([' pixmap="KravenFHD/progress/progress990.png"',' pixmap="KravenFHD/progress/progress990_2.png"'])
			self.skinSearchAndReplace.append([' pixmap="KravenFHD/progress/progress1265.png"',' pixmap="KravenFHD/progress/progress1265_2.png"'])
		elif not config.plugins.KravenFHD.Progress.value == "progress":
			self.skinSearchAndReplace.append([' pixmap="KravenFHD/progress/progress18.png"'," "])
			self.skinSearchAndReplace.append([' picServiceEventProgressbar="KravenFHD/progress/progress52.png"'," "])
			self.skinSearchAndReplace.append([' pixmap="KravenFHD/progress/progress170.png"'," "])
			self.skinSearchAndReplace.append([' pixmap="KravenFHD/progress/progress200.png"'," "])
			self.skinSearchAndReplace.append([' pixmap="KravenFHD/progress/progress220.png"'," "])
			self.skinSearchAndReplace.append([' pixmap="KravenFHD/progress/progress248.png"'," "])
			self.skinSearchAndReplace.append([' pixmap="KravenFHD/progress/progress270.png"'," "])
			self.skinSearchAndReplace.append([' pixmap="KravenFHD/progress/progress300.png"'," "])
			self.skinSearchAndReplace.append([' pixmap="KravenFHD/progress/progress328.png"'," "])
			self.skinSearchAndReplace.append([' pixmap="KravenFHD/progress/progress370.png"'," "])
			self.skinSearchAndReplace.append([' pixmap="KravenFHD/progress/progress380.png"'," "])
			self.skinSearchAndReplace.append([' pixmap="KravenFHD/progress/progress410.png"'," "])
			self.skinSearchAndReplace.append([' pixmap="KravenFHD/progress/progress480.png"'," "])
			self.skinSearchAndReplace.append([' pixmap="KravenFHD/progress/progress581.png"'," "])
			self.skinSearchAndReplace.append([' pixmap="KravenFHD/progress/progress599.png"'," "])
			self.skinSearchAndReplace.append([' pixmap="KravenFHD/progress/progress655.png"'," "])
			self.skinSearchAndReplace.append([' pixmap="KravenFHD/progress/progress708.png"'," "])
			self.skinSearchAndReplace.append([' pixmap="KravenFHD/progress/progress749.png"'," "])
			self.skinSearchAndReplace.append([' pixmap="KravenFHD/progress/progress858.png"'," "])
			self.skinSearchAndReplace.append([' pixmap="KravenFHD/progress/progress888.png"'," "])
			self.skinSearchAndReplace.append([' pixmap="KravenFHD/progress/progress990.png"'," "])
			self.skinSearchAndReplace.append([' pixmap="KravenFHD/progress/progress1265.png"'," "])
			self.skinSearchAndReplace.append(['name="KravenProgress" value="#00C3461B', 'name="KravenProgress" value="#00' + config.plugins.KravenFHD.Progress.value])

		### Border
		self.skinSearchAndReplace.append(['name="KravenBorder" value="#00ffffff', 'name="KravenBorder" value="#00' + config.plugins.KravenFHD.Border.value])

		### MiniTV Border
		self.skinSearchAndReplace.append(['name="KravenBorder2" value="#003F3F3F', 'name="KravenBorder2" value="#00' + config.plugins.KravenFHD.MiniTVBorder.value])

		### NumberZap Border
		if not config.plugins.KravenFHD.NumberZapExt.value == "none":
			self.skinSearchAndReplace.append(['name="KravenNZBorder" value="#00ffffff', 'name="KravenNZBorder" value="#00' + config.plugins.KravenFHD.NZBorder.value])

		### GraphEPG Border
		self.skinSearchAndReplace.append(['name="KravenGMEBorder" value="#00ffffff', 'name="KravenGMEBorder" value="#00' + config.plugins.KravenFHD.GMEBorder.value])

		### VerticalEPG Border
		self.skinSearchAndReplace.append(['name="KravenVEPGBorder" value="#00ffffff', 'name="KravenVEPGBorder" value="#00' + config.plugins.KravenFHD.VEPGBorder.value])

		### Line
		self.skinSearchAndReplace.append(['name="KravenLine" value="#00ffffff', 'name="KravenLine" value="#00' + config.plugins.KravenFHD.Line.value])

		### Runningtext
		if config.plugins.KravenFHD.RunningText.value == "none":
			self.skinSearchAndReplace.append(["movetype=running", "movetype=none"])
		else:
			self.skinSearchAndReplace.append(["startdelay=5000", config.plugins.KravenFHD.RunningText.value])
			
			# vertical RunningText
			self.skinSearchAndReplace.append(["steptime=90", config.plugins.KravenFHD.RunningTextSpeed.value])
			
			# horizontal RunningText
			if config.plugins.KravenFHD.RunningTextSpeed.value == "steptime=200":
				self.skinSearchAndReplace.append(["steptime=80", "steptime=66"])
			elif config.plugins.KravenFHD.RunningTextSpeed.value == "steptime=100":
				self.skinSearchAndReplace.append(["steptime=80", "steptime=33"])
			elif config.plugins.KravenFHD.RunningTextSpeed.value == "steptime=50":
				self.skinSearchAndReplace.append(["steptime=80", "steptime=17"])
			elif config.plugins.KravenFHD.RunningTextSpeed.value == "steptime=33":
				self.skinSearchAndReplace.append(["steptime=80", "steptime=11"])

		### Scrollbar
		if self.E2DistroVersion == "VTi":
			if config.plugins.KravenFHD.ScrollBar.value == "scrollbarWidth=0":
				self.skinSearchAndReplace.append(['scrollbarMode="showOnDemand"', 'scrollbarMode="showNever"'])
				self.skinSearchAndReplace.append(['scrollbarWidth="5"', 'scrollbarWidth="0"'])
			elif config.plugins.KravenFHD.ScrollBar.value == "scrollbarWidth=10":
				self.skinSearchAndReplace.append(['scrollbarWidth="5"', 'scrollbarWidth="15"'])
			elif config.plugins.KravenFHD.ScrollBar.value == "scrollbarWidth=15":
				self.skinSearchAndReplace.append(['scrollbarWidth="5"', 'scrollbarWidth="22"'])
		elif self.E2DistroVersion in ("openatv","teamblue"):
			if config.plugins.KravenFHD.ScrollBar2.value == "showOnDemand":
				self.skinSearchAndReplace.append(['scrollbarMode="showNever"', 'scrollbarMode="showOnDemand"'])
				self.skinSearchAndReplace.append(['scrollbarWidth="5"', ''])
			else:
				self.skinSearchAndReplace.append(['scrollbarMode="showOnDemand"', 'scrollbarMode="showNever"'])
				self.skinSearchAndReplace.append(['scrollbarWidth="5"', ''])
					
		### Scrollbar - showNever
		self.skinSearchAndReplace.append(['scrollbarMode="never"', 'scrollbarMode="showNever"'])

		### Selectionborder
		if not config.plugins.KravenFHD.SelectionBorderList.value == "none":
			self.makeborsetpng(config.plugins.KravenFHD.SelectionBorder.value)

		### IB Color visible
		if config.plugins.KravenFHD.IBColor.value == "only-infobar":
			self.skinSearchAndReplace.append(['backgroundColor="KravenMbg"', 'backgroundColor="Kravenbg"'])
			self.skinSearchAndReplace.append(['foregroundColor="KravenMFont1"', 'foregroundColor="KravenFont1"'])
			self.skinSearchAndReplace.append(['foregroundColor="KravenMFont2"', 'foregroundColor="KravenFont2"'])
			self.skinSearchAndReplace.append(['<constant-widget name="gradient-cs"/>', " "])
			self.skinSearchAndReplace.append(['<constant-widget name="gradient-cooltv"/>', " "])
			self.skinSearchAndReplace.append(['<constant-widget name="gradient-emc"/>', " "])
			self.skinSearchAndReplace.append(['<constant-widget name="gradient-wrr"/>', " "])
			self.skinSearchAndReplace.append(['<constant-widget name="gradient-split1"/>', " "])
			self.skinSearchAndReplace.append(['<constant-widget name="gradient-split2"/>', " "])
		else:
			self.skinSearchAndReplace.append(['backgroundColor="KravenMbg"', 'backgroundColor="KravenIBbg2"'])
			self.skinSearchAndReplace.append(['foregroundColor="KravenMFont1"', 'foregroundColor="KravenIBFont1"'])
			self.skinSearchAndReplace.append(['foregroundColor="KravenMFont2"', 'foregroundColor="KravenIBFont2"'])

			if config.plugins.KravenFHD.IBStyle.value == "box":
				### Menu
				if config.plugins.KravenFHD.InfobarBoxColor.value == "gradient":
					menubox = """<ePixmap pixmap="KravenFHD/graphics/ibar4.png" position="0,960" size="1920,120" zPosition="-9" alphatest="blend" />
	<eLabel position="0,960" size="1920,3" backgroundColor="KravenIBLine" zPosition="-8" />
	<ePixmap pixmap="KravenFHD/graphics/ibaro.png" position="0,0" size="1920,88" zPosition="-9" alphatest="blend" />
	<eLabel position="0,87" size="1920,3" backgroundColor="KravenIBLine" zPosition="-8" />"""
					self.skinSearchAndReplace.append(['<!-- Menu ibar -->', menubox])

					self.skinSearchAndReplace.append(['<constant-widget name="gradient-cs"/>', '<constant-widget name="box2-cs"/>'])
					self.skinSearchAndReplace.append(['<constant-widget name="gradient-cooltv"/>', '<constant-widget name="box2-cooltv"/>'])
					self.skinSearchAndReplace.append(['<constant-widget name="gradient-emc"/>', '<constant-widget name="box2-emc"/>'])
					self.skinSearchAndReplace.append(['<constant-widget name="gradient-wrr"/>', '<constant-widget name="box2-wrr"/>'])
					self.skinSearchAndReplace.append(['<constant-widget name="gradient-split1"/>', '<constant-widget name="box2-split1"/>'])
					self.skinSearchAndReplace.append(['<constant-widget name="gradient-split2"/>', '<constant-widget name="box2-split2"/>'])
				elif config.plugins.KravenFHD.InfobarBoxColor.value == "texture":
					menubox = """<ePixmap pixmap="KravenFHD/graphics/ibtexture.png" position="0,960" size="1920,120" zPosition="-9" alphatest="blend" />
	<eLabel position="0,960" size="1920,3" backgroundColor="KravenIBLine" zPosition="-8" />
	<ePixmap pixmap="KravenFHD/graphics/ibtexture.png" position="0,0" size="1920,88" zPosition="-9" alphatest="blend" />
	<eLabel position="0,87" size="1920,3" backgroundColor="KravenIBLine" zPosition="-8" />"""
					self.skinSearchAndReplace.append(['<!-- Menu ibar -->', menubox])

					self.skinSearchAndReplace.append(['<constant-widget name="gradient-cs"/>', '<constant-widget name="texture-cs"/>'])
					self.skinSearchAndReplace.append(['<constant-widget name="gradient-cooltv"/>', '<constant-widget name="texture-cooltv"/>'])
					self.skinSearchAndReplace.append(['<constant-widget name="gradient-emc"/>', '<constant-widget name="texture-emc"/>'])
					self.skinSearchAndReplace.append(['<constant-widget name="gradient-wrr"/>', '<constant-widget name="texture-wrr"/>'])
					self.skinSearchAndReplace.append(['<constant-widget name="gradient-split1"/>', '<constant-widget name="texture-split1"/>'])
					self.skinSearchAndReplace.append(['<constant-widget name="gradient-split2"/>', '<constant-widget name="texture-split2"/>'])
				else:
					menubox = """<eLabel position="0,960" size="1920,120" backgroundColor="KravenIBbg2" zPosition="-9" />
	  <eLabel position="0,960" size="1920,3" backgroundColor="KravenIBLine" zPosition="-8" />
	  <eLabel position="0,0" size="1920,88" backgroundColor="KravenIBbg2" zPosition="-9" />
	  <eLabel position="0,87" size="1920,3" backgroundColor="KravenIBLine" zPosition="-8" />"""
					self.skinSearchAndReplace.append(['<!-- Menu ibar -->', menubox])

					self.skinSearchAndReplace.append(['<constant-widget name="gradient-cs"/>', '<constant-widget name="box-cs"/>'])
					self.skinSearchAndReplace.append(['<constant-widget name="gradient-cooltv"/>', '<constant-widget name="box-cooltv"/>'])
					self.skinSearchAndReplace.append(['<constant-widget name="gradient-emc"/>', '<constant-widget name="box-emc"/>'])
					self.skinSearchAndReplace.append(['<constant-widget name="gradient-wrr"/>', '<constant-widget name="box-wrr"/>'])
					self.skinSearchAndReplace.append(['<constant-widget name="gradient-split1"/>', '<constant-widget name="box-split1"/>'])
					self.skinSearchAndReplace.append(['<constant-widget name="gradient-split2"/>', '<constant-widget name="box-split2"/>'])

				### Title - Position
				self.skinSearchAndReplace.append(['position="105,18"','position="105,10"'])
				self.skinSearchAndReplace.append(['position="63,18"','position="63,12"'])
				self.skinSearchAndReplace.append(['position="94,18"','position="94,12"'])
				self.skinSearchAndReplace.append(['position="660,28"','position="660,22"'])

				### Clock - Position
				self.skinSearchAndReplace.append(['position="1707,33"','position="1707,25"'])

				### Clock (wbrFS_r_site) - Position
				self.skinSearchAndReplace.append(['position="366,33"','position="366,25"'])

				### Menü, OK, Exit - Position
				self.skinSearchAndReplace.append(['position="1642,1005"','position="1642,1012"'])
				self.skinSearchAndReplace.append(['position="1717,1005"','position="1717,1012"'])
				self.skinSearchAndReplace.append(['position="1792,1005"','position="1792,1012"'])

				### ColorButtons - Position
				self.skinSearchAndReplace.append(['position="97,1038"','position="97,1045"'])
				self.skinSearchAndReplace.append(['position="472,1038"','position="472,1045"'])
				self.skinSearchAndReplace.append(['position="847,1038"','position="847,1045"'])
				self.skinSearchAndReplace.append(['position="1222,1038"','position="1222,1045"'])
				self.skinSearchAndReplace.append(['position="497,1038"','position="497,1045"'])
				self.skinSearchAndReplace.append(['position="897,1038"','position="897,1045"'])
				self.skinSearchAndReplace.append(['position="1297,1038"','position="1297,1045"'])

				### ColorButtons (ChannelSelection, CoolTV, EMC) - Position
				self.skinSearchAndReplace.append(['position="56,1038"','position="56,1045"'])
				self.skinSearchAndReplace.append(['position="431,1038"','position="431,1045"'])
				self.skinSearchAndReplace.append(['position="806,1038"','position="806,1045"'])
				self.skinSearchAndReplace.append(['position="1181,1038"','position="1181,1045"'])

				### ColorButton-Text - Position
				self.skinSearchAndReplace.append(['position="105,997"','position="105,1005"'])
				self.skinSearchAndReplace.append(['position="480,997"','position="480,1005"'])
				self.skinSearchAndReplace.append(['position="855,997"','position="855,1005"'])
				self.skinSearchAndReplace.append(['position="1230,997"','position="1230,1005"'])
				self.skinSearchAndReplace.append(['position="505,997"','position="505,1005"'])
				self.skinSearchAndReplace.append(['position="905,997"','position="905,1005"'])
				self.skinSearchAndReplace.append(['position="1305,997"','position="1305,1005"'])
				self.skinSearchAndReplace.append(['position="105,958"','position="105,966"'])
				self.skinSearchAndReplace.append(['position="480,958"','position="480,966"'])
				self.skinSearchAndReplace.append(['position="855,958"','position="855,966"'])
				self.skinSearchAndReplace.append(['position="1230,958"','position="1230,966"'])

				### ColorButton-Text (ChannelSelection, CoolTV, EMC) - Position
				self.skinSearchAndReplace.append(['position="63,997"','position="63,1005"'])
				self.skinSearchAndReplace.append(['position="438,997"','position="438,1005"'])
				self.skinSearchAndReplace.append(['position="813,997"','position="813,1005"'])
				self.skinSearchAndReplace.append(['position="1188,997"','position="1188,1005"'])

				### MQB - Position
				self.skinSearchAndReplace.append(['<ePixmap alphatest="blend" pixmap="KravenFHD/buttons/key_grey1.png" position="97,963" size="300,7" />'," "])
				self.skinSearchAndReplace.append(['<ePixmap alphatest="blend" pixmap="KravenFHD/buttons/key_grey1.png" position="472,963" size="300,7" />'," "])
				self.skinSearchAndReplace.append(['<ePixmap alphatest="blend" pixmap="KravenFHD/buttons/key_grey1.png" position="847,963" size="300,7" />'," "])
				self.skinSearchAndReplace.append(['<ePixmap alphatest="blend" pixmap="KravenFHD/buttons/key_grey1.png" position="1222,963" size="300,7" />'," "])
				self.skinSearchAndReplace.append(['position="157,922"','position="157,961"'])
				self.skinSearchAndReplace.append(['position="532,922"','position="532,961"'])
				self.skinSearchAndReplace.append(['position="907,922"','position="907,961"'])
				self.skinSearchAndReplace.append(['position="1282,922"','position="1282,961"'])
				self.skinSearchAndReplace.append(['position="93,924"','position="93,963"'])
				self.skinSearchAndReplace.append(['position="468,924"','position="468,963"'])
				self.skinSearchAndReplace.append(['position="843,924"','position="843,963"'])
				self.skinSearchAndReplace.append(['position="1218,924"','position="1218,963"'])

				### MediaPlayer - Position
				self.skinSearchAndReplace.append(['position="1555,999"','position="1555,1006"'])

				### EPGSelection - Position
				self.skinSearchAndReplace.append(['position="1230,24" render="Picon"','position="1230,16" render="Picon"'])

			else:
				### Menu
				menugradient = """<ePixmap pixmap="KravenFHD/graphics/ibar.png" position="0,825" size="1920,600" alphatest="blend" zPosition="-9" />
	  <ePixmap pixmap="KravenFHD/graphics/ibaro2.png" position="0,0" size="1920,247" alphatest="blend" zPosition="-9" />"""
				self.skinSearchAndReplace.append(['<!-- Menu ibar -->', menugradient])

		self.skinSearchAndReplace.append(['backgroundColor="KravenSIBbg2"', 'backgroundColor="KravenIBbg2"'])
		self.skinSearchAndReplace.append(['foregroundColor="KravenSIBFont1"', 'foregroundColor="KravenIBFont1"'])
		self.skinSearchAndReplace.append(['foregroundColor="KravenSIBFont2"', 'foregroundColor="KravenIBFont2"'])

		### MediaPortal box-style
		if config.plugins.KravenFHD.MediaPortal.value == "mediaportal" and config.plugins.KravenFHD.IBColor.value == "all-screens" and config.plugins.KravenFHD.InfobarBoxColor.value == "gradient":
			mpbox = """<ePixmap pixmap="KravenFHD/graphics/ibar4.png" position="0,960" size="1920,120" zPosition="-9" alphatest="blend" />
	  <eLabel position="0,960" size="1920,3" backgroundColor="KravenIBLine" zPosition="-8" />
	  <ePixmap pixmap="KravenFHD/graphics/ibaro.png" position="0,0" size="1920,88" zPosition="-9" alphatest="blend" />
	  <eLabel position="0,87" size="1920,3" backgroundColor="KravenIBLine" zPosition="-8" />"""
			self.skinSearchAndReplace.append(['<!-- MediaPortal ibarcolor */-->', mpbox])
			mpboxThumbsScreen = """<ePixmap pixmap="KravenFHD/graphics/ibar4.png" position="0,1006" size="1920,120" zPosition="-9" alphatest="blend" />
	  <eLabel position="0,1006" size="1920,3" backgroundColor="KravenIBLine" zPosition="-8" />
	  <ePixmap pixmap="KravenFHD/graphics/ibaro.png" position="0,0" size="1920,88" zPosition="-9" alphatest="blend" />
	  <eLabel position="0,87" size="1920,3" backgroundColor="KravenIBLine" zPosition="-8" />"""
			self.skinSearchAndReplace.append(['<!-- MediaPortal ibarcolor ThumbsScreen */-->', mpboxThumbsScreen])
		if config.plugins.KravenFHD.MediaPortal.value == "mediaportal" and config.plugins.KravenFHD.IBColor.value == "all-screens" and config.plugins.KravenFHD.InfobarBoxColor.value == "texture":
			mpbox1 = """<ePixmap pixmap="KravenFHD/graphics/ibtexture.png" position="0,960" size="1920,120" zPosition="-9" alphatest="blend" />
	  <eLabel position="0,960" size="1920,3" backgroundColor="KravenIBLine" zPosition="-8" />
	  <ePixmap pixmap="KravenFHD/graphics/ibtexture.png" position="0,0" size="1920,88" zPosition="-9" alphatest="blend" />
	  <eLabel position="0,87" size="1920,3" backgroundColor="KravenIBLine" zPosition="-8" />"""
			self.skinSearchAndReplace.append(['<!-- MediaPortal ibarcolor */-->', mpbox1])
			mpbox1ThumbsScreen = """<ePixmap pixmap="KravenFHD/graphics/ibtexture.png" position="0,1006" size="1920,120" zPosition="-9" alphatest="blend" />
	  <eLabel position="0,1006" size="1920,3" backgroundColor="KravenIBLine" zPosition="-8" />
	  <ePixmap pixmap="KravenFHD/graphics/ibtexture.png" position="0,0" size="1920,88" zPosition="-9" alphatest="blend" />
	  <eLabel position="0,87" size="1920,3" backgroundColor="KravenIBLine" zPosition="-8" />"""
			self.skinSearchAndReplace.append(['<!-- MediaPortal ibarcolor ThumbsScreen */-->', mpbox1ThumbsScreen])
		if config.plugins.KravenFHD.MediaPortal.value == "mediaportal" and config.plugins.KravenFHD.IBColor.value == "all-screens" and not config.plugins.KravenFHD.InfobarBoxColor.value in ("gradient","texture"):
			mpbox2 = """<eLabel position="0,960" size="1920,120" backgroundColor="KravenIBbg" zPosition="-9" />
	  <eLabel position="0,960" size="1920,3" backgroundColor="KravenIBLine" zPosition="-8" />
	  <eLabel position="0,0" size="1920,88" backgroundColor="KravenIBbg" zPosition="-9" />
	  <eLabel position="0,87" size="1920,3" backgroundColor="KravenIBLine" zPosition="-8" />"""
			self.skinSearchAndReplace.append(['<!-- MediaPortal ibarcolor */-->', mpbox2])
			mpbox2ThumbsScreen = """<eLabel position="0,1006" size="1920,120" backgroundColor="KravenIBbg" zPosition="-9" />
	  <eLabel position="0,1006" size="1920,3" backgroundColor="KravenIBLine" zPosition="-8" />
	  <eLabel position="0,0" size="1920,88" backgroundColor="KravenIBbg" zPosition="-9" />
	  <eLabel position="0,87" size="1920,3" backgroundColor="KravenIBLine" zPosition="-8" />"""
			self.skinSearchAndReplace.append(['<!-- MediaPortal ibarcolor ThumbsScreen */-->', mpbox2ThumbsScreen])

		### Clock Analog Style
		self.analogstylecolor = config.plugins.KravenFHD.AnalogStyle.value
		self.analog = ("analog_" + self.analogstylecolor + ".png")
		self.skinSearchAndReplace.append(["analog.png", self.analog])

		### HelpMenu
		if self.E2DistroVersion in ("openatv","teamblue"):
			self.skinSearchAndReplace.append(['skin_default/rc_vu_1.png,skin_default/rc_vu_2.png,skin_default/rc_vu_3.png,skin_default/rc_vu_4.png,skin_default/rc_vu_5.png', 'skin_default/rc.png,skin_default/rcold.png'])

		### KravenIconVPosition
		if config.plugins.KravenFHD.KravenIconVPosition.value == "vposition-3":
			if config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-nopicon","infobar-style-x4","infobar-style-zz1","infobar-style-zzz1"):
				self.skinSearchAndReplace.append([',1030" name="KravenIconVPosition"', ',1027"'])
			elif config.plugins.KravenFHD.InfobarStyle.value == "infobar-style-x1":
				self.skinSearchAndReplace.append([',1038" name="KravenIconVPosition"', ',1035"'])
			elif config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-zz4","infobar-style-zzz2"):
				self.skinSearchAndReplace.append([',1035" name="KravenIconVPosition"', ',1032"'])
			elif config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-x2","infobar-style-z1"):
				self.skinSearchAndReplace.append([',34" name="KravenIconVPosition"', ',31"'])
			self.skinSearchAndReplace.append([',1020" name="KravenIconVPosition"', ',1017"']) # Players
		elif config.plugins.KravenFHD.KravenIconVPosition.value == "vposition-2":
			if config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-nopicon","infobar-style-x4","infobar-style-zz1","infobar-style-zzz1"):
				self.skinSearchAndReplace.append([',1030" name="KravenIconVPosition"', ',1028"'])
			elif config.plugins.KravenFHD.InfobarStyle.value == "infobar-style-x1":
				self.skinSearchAndReplace.append([',1038" name="KravenIconVPosition"', ',1036"'])
			elif config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-zz4","infobar-style-zzz2"):
				self.skinSearchAndReplace.append([',1035" name="KravenIconVPosition"', ',1033"'])
			elif config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-x2","infobar-style-z1"):
				self.skinSearchAndReplace.append([',34" name="KravenIconVPosition"', ',32"'])
			self.skinSearchAndReplace.append([',1020" name="KravenIconVPosition"', ',1018"']) # Players
		elif config.plugins.KravenFHD.KravenIconVPosition.value == "vposition-1":
			if config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-nopicon","infobar-style-x4","infobar-style-zz1","infobar-style-zzz1"):
				self.skinSearchAndReplace.append([',1030" name="KravenIconVPosition"', ',1029"'])
			elif config.plugins.KravenFHD.InfobarStyle.value == "infobar-style-x1":
				self.skinSearchAndReplace.append([',1038" name="KravenIconVPosition"', ',1037"'])
			elif config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-zz4","infobar-style-zzz2"):
				self.skinSearchAndReplace.append([',1035" name="KravenIconVPosition"', ',1034"'])
			elif config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-x2","infobar-style-z1"):
				self.skinSearchAndReplace.append([',34" name="KravenIconVPosition"', ',33"'])
			self.skinSearchAndReplace.append([',1020" name="KravenIconVPosition"', ',1019"']) # Players
		elif config.plugins.KravenFHD.KravenIconVPosition.value == "vposition0":
			if config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-nopicon","infobar-style-x4","infobar-style-zz1","infobar-style-zzz1"):
				self.skinSearchAndReplace.append([',1030" name="KravenIconVPosition"', ',1030"'])
			elif config.plugins.KravenFHD.InfobarStyle.value == "infobar-style-x1":
				self.skinSearchAndReplace.append([',1038" name="KravenIconVPosition"', ',1038"'])
			elif config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-zz4","infobar-style-zzz2"):
				self.skinSearchAndReplace.append([',1035" name="KravenIconVPosition"', ',1035"'])
			elif config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-x2","infobar-style-z1"):
				self.skinSearchAndReplace.append([',34" name="KravenIconVPosition"', ',34"'])
			self.skinSearchAndReplace.append([',1020" name="KravenIconVPosition"', ',1020"']) # Players
		elif config.plugins.KravenFHD.KravenIconVPosition.value == "vposition+1":
			if config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-nopicon","infobar-style-x4","infobar-style-zz1","infobar-style-zzz1"):
				self.skinSearchAndReplace.append([',1030" name="KravenIconVPosition"', ',1031"'])
			elif config.plugins.KravenFHD.InfobarStyle.value == "infobar-style-x1":
				self.skinSearchAndReplace.append([',1038" name="KravenIconVPosition"', ',1039"'])
			elif config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-zz4","infobar-style-zzz2"):
				self.skinSearchAndReplace.append([',1035" name="KravenIconVPosition"', ',1036"'])
			elif config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-x2","infobar-style-z1"):
				self.skinSearchAndReplace.append([',34" name="KravenIconVPosition"', ',35"'])
			self.skinSearchAndReplace.append([',1020" name="KravenIconVPosition"', ',1021"']) # Players
		elif config.plugins.KravenFHD.KravenIconVPosition.value == "vposition+2":
			if config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-nopicon","infobar-style-x4","infobar-style-zz1","infobar-style-zzz1"):
				self.skinSearchAndReplace.append([',1030" name="KravenIconVPosition"', ',1032"'])
			elif config.plugins.KravenFHD.InfobarStyle.value == "infobar-style-x1":
				self.skinSearchAndReplace.append([',1038" name="KravenIconVPosition"', ',1040"'])
			elif config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-zz4","infobar-style-zzz2"):
				self.skinSearchAndReplace.append([',1035" name="KravenIconVPosition"', ',1037"'])
			elif config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-x2","infobar-style-z1"):
				self.skinSearchAndReplace.append([',34" name="KravenIconVPosition"', ',36"'])
			self.skinSearchAndReplace.append([',1020" name="KravenIconVPosition"', ',1022"']) # Players
		elif config.plugins.KravenFHD.KravenIconVPosition.value == "vposition+3":
			if config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-nopicon","infobar-style-x4","infobar-style-zz1","infobar-style-zzz1"):
				self.skinSearchAndReplace.append([',1030" name="KravenIconVPosition"', ',1033"'])
			elif config.plugins.KravenFHD.InfobarStyle.value == "infobar-style-x1":
				self.skinSearchAndReplace.append([',1038" name="KravenIconVPosition"', ',1041"'])
			elif config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-zz4","infobar-style-zzz2"):
				self.skinSearchAndReplace.append([',1035" name="KravenIconVPosition"', ',1038"'])
			elif config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-x2","infobar-style-z1"):
				self.skinSearchAndReplace.append([',34" name="KravenIconVPosition"', ',37"'])
			self.skinSearchAndReplace.append([',1020" name="KravenIconVPosition"', ',1023"']) # Players

		### Channellist-EPGList - VTi
		if self.E2DistroVersion == "VTi" and config.plugins.KravenFHD.alternativeChannellist.value == "none":
			if config.plugins.KravenFHD.ChannellistEPGList.value == "channellistepglist-on":
				if self.actChannelselectionstyle in ("channelselection-style-nobile","channelselection-style-nobile2","channelselection-style-nobile-minitv","channelselection-style-nobile-minitv3","channelselection-style-nobile-minitv33"):
					self.skinSearchAndReplace.append(['alias name="EPGListChannelList0" font="Regular" size="34"', 'alias name="EPGListChannelList0" font="Regular" size="28"'])
					self.skinSearchAndReplace.append(['alias name="EPGListChannelList1" font="Regular" size="34"', 'alias name="EPGListChannelList1" font="Regular" size="28"'])
					self.skinSearchAndReplace.append(['parameter name="EPGServicelistText0" value="3,1,48,44"', 'parameter name="EPGServicelistText0" value="3,1,39,39"'])
					self.skinSearchAndReplace.append(['parameter name="EPGServicelistText1" value="51,1,99,44"', 'parameter name="EPGServicelistText1" value="42,1,81,39"'])
					self.skinSearchAndReplace.append(['parameter name="EPGServicelistText2" value="165,1,93,44"', 'parameter name="EPGServicelistText2" value="138,1,75,39"'])
					self.skinSearchAndReplace.append(['parameter name="EPGServicelistRecImage" value="255,13,20,20"', 'parameter name="EPGServicelistRecImage" value="219,8,20,20"'])
					self.skinSearchAndReplace.append(['parameter name="EPGServicelistRecText" value="281,1,900,44"', 'parameter name="EPGServicelistRecText" value="245,1,900,39"'])
					self.skinSearchAndReplace.append(['parameter name="EPGServicelistNonRecText" value="255,1,900,44"', 'parameter name="EPGServicelistNonRecText" value="219,1,900,39"'])
					if config.plugins.KravenFHD.Primetimeavailable.value == "primetime-on":
						self.skinSearchAndReplace.append(['<!--ChannellistEPGList-P', '<widget'])
						self.skinSearchAndReplace.append(['ChannellistEPGList-P-->', '/>'])
					else:
						self.skinSearchAndReplace.append(['<!--ChannellistEPGList-NP', '<widget'])
						self.skinSearchAndReplace.append(['ChannellistEPGList-NP-->', '/>'])
				elif self.actChannelselectionstyle == "channelselection-style-minitv22":
					if config.plugins.KravenFHD.ChannelSelectionEPGSize2.value == "small":
						self.skinSearchAndReplace.append(['alias name="EPGListChannelList0" font="Regular" size="34"', 'alias name="EPGListChannelList0" font="Regular" size="30"'])
						self.skinSearchAndReplace.append(['alias name="EPGListChannelList1" font="Regular" size="34"', 'alias name="EPGListChannelList1" font="Regular" size="30"'])
						self.skinSearchAndReplace.append(['parameter name="EPGServicelistText0" value="3,1,48,44"', 'parameter name="EPGServicelistText0" value="3,1,42,39"'])
						self.skinSearchAndReplace.append(['parameter name="EPGServicelistText1" value="51,1,99,44"', 'parameter name="EPGServicelistText1" value="45,1,87,39"'])
						self.skinSearchAndReplace.append(['parameter name="EPGServicelistText2" value="165,1,93,44"', 'parameter name="EPGServicelistText2" value="147,1,81,39"'])
						self.skinSearchAndReplace.append(['parameter name="EPGServicelistRecImage" value="255,13,20,20"', 'parameter name="EPGServicelistRecImage" value="231,10,20,20"'])
						self.skinSearchAndReplace.append(['parameter name="EPGServicelistRecText" value="281,1,900,44"', 'parameter name="EPGServicelistRecText" value="257,1,900,39"'])
						self.skinSearchAndReplace.append(['parameter name="EPGServicelistNonRecText" value="255,1,900,44"', 'parameter name="EPGServicelistNonRecText" value="231,1,900,39"'])
						if config.plugins.KravenFHD.Primetimeavailable.value == "primetime-on":
							self.skinSearchAndReplace.append(['<!--ChannellistEPGList-SP', '<widget'])
							self.skinSearchAndReplace.append(['ChannellistEPGList-SP-->', '/>'])
						else:
							self.skinSearchAndReplace.append(['<!--ChannellistEPGList-SNP', '<widget'])
							self.skinSearchAndReplace.append(['ChannellistEPGList-SNP-->', '/>'])
					else:
						if config.plugins.KravenFHD.Primetimeavailable.value == "primetime-on":
							self.skinSearchAndReplace.append(['<!--ChannellistEPGList-BP', '<widget'])
							self.skinSearchAndReplace.append(['ChannellistEPGList-BP-->', '/>'])
						else:
							self.skinSearchAndReplace.append(['<!--ChannellistEPGList-BNP', '<widget'])
							self.skinSearchAndReplace.append(['ChannellistEPGList-BNP-->', '/>'])
				else:
					if config.plugins.KravenFHD.ChannelSelectionEPGSize3.value == "small":
						self.skinSearchAndReplace.append(['alias name="EPGListChannelList0" font="Regular" size="34"', 'alias name="EPGListChannelList0" font="Regular" size="30"'])
						self.skinSearchAndReplace.append(['alias name="EPGListChannelList1" font="Regular" size="34"', 'alias name="EPGListChannelList1" font="Regular" size="30"'])
						self.skinSearchAndReplace.append(['parameter name="EPGServicelistText0" value="3,1,48,44"', 'parameter name="EPGServicelistText0" value="3,1,42,39"'])
						self.skinSearchAndReplace.append(['parameter name="EPGServicelistText1" value="51,1,99,44"', 'parameter name="EPGServicelistText1" value="45,1,87,39"'])
						self.skinSearchAndReplace.append(['parameter name="EPGServicelistText2" value="165,1,93,44"', 'parameter name="EPGServicelistText2" value="147,1,81,39"'])
						self.skinSearchAndReplace.append(['parameter name="EPGServicelistRecImage" value="255,13,20,20"', 'parameter name="EPGServicelistRecImage" value="231,10,20,20"'])
						self.skinSearchAndReplace.append(['parameter name="EPGServicelistRecText" value="281,1,900,44"', 'parameter name="EPGServicelistRecText" value="257,1,900,39"'])
						self.skinSearchAndReplace.append(['parameter name="EPGServicelistNonRecText" value="255,1,900,44"', 'parameter name="EPGServicelistNonRecText" value="231,1,900,39"'])
						if config.plugins.KravenFHD.Primetimeavailable.value == "primetime-on":
							self.skinSearchAndReplace.append(['<!--ChannellistEPGList-SP', '<widget'])
							self.skinSearchAndReplace.append(['ChannellistEPGList-SP-->', '/>'])
						else:
							self.skinSearchAndReplace.append(['<!--ChannellistEPGList-SNP', '<widget'])
							self.skinSearchAndReplace.append(['ChannellistEPGList-SNP-->', '/>'])
					else:
						if config.plugins.KravenFHD.Primetimeavailable.value == "primetime-on":
							self.skinSearchAndReplace.append(['<!--ChannellistEPGList-BP', '<widget'])
							self.skinSearchAndReplace.append(['ChannellistEPGList-BP-->', '/>'])
						else:
							self.skinSearchAndReplace.append(['<!--ChannellistEPGList-BNP', '<widget'])
							self.skinSearchAndReplace.append(['ChannellistEPGList-BNP-->', '/>'])
			else:
				self.skinSearchAndReplace.append(['<!--ChannellistSingleEpgList', '<widget'])
				self.skinSearchAndReplace.append(['ChannellistSingleEpgList-->', 'widget>'])
		elif self.E2DistroVersion in ("openatv","teamblue"):
			self.skinSearchAndReplace.append(['<!--ChannellistSingleEpgList', '<widget'])
			self.skinSearchAndReplace.append(['ChannellistSingleEpgList-->', 'widget>'])

		### NumericalTextInputHelpDialog (HelpWindow)
		if self.E2DistroVersion in ("VTi","teamblue"):
			self.skinSearchAndReplace.append(['<widget name="HelpWindow" position="1350,520" size="392,393" zPosition="98" transparent="1" alphatest="blend" />', ' '])

		### delete Font-Shadow if Channelname is inside the box
		if config.plugins.KravenFHD.IBStyle.value == "box" and config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-zz2","infobar-style-zz3","infobar-style-zzz1","infobar-style-zzz2"):
			self.skinSearchAndReplace.append(['backgroundColor="KravenNamebg"', 'backgroundColor="KravenIBbg"'])

		### Infobar - ecm-info
		if not config.plugins.KravenFHD.InfobarStyle.value == "infobar-style-x4":
			if config.plugins.KravenFHD.FTA.value == "none":
				self.skinSearchAndReplace.append(['FTAVisible</convert>', 'FTAInvisible</convert>'])
			if config.plugins.KravenFHD.InfobarStyle.value == "infobar-style-x1":
				self.skinSearchAndReplace.append(['<convert type="KravenFHDECMLine">ShortReader', '<convert type="KravenFHDECMLine">' + config.plugins.KravenFHD.ECMLine1.value])
			elif config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-nopicon","infobar-style-x2","infobar-style-x3","infobar-style-z1","infobar-style-z2"):
				self.skinSearchAndReplace.append(['<convert type="KravenFHDECMLine">ShortReader', '<convert type="KravenFHDECMLine">' + config.plugins.KravenFHD.ECMLine2.value])
			elif config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-zz1","infobar-style-zz2","infobar-style-zz3","infobar-style-zz4","infobar-style-zzz1","infobar-style-zzz2"):
				self.skinSearchAndReplace.append(['<convert type="KravenFHDECMLine">ShortReader', '<convert type="KravenFHDECMLine">' + config.plugins.KravenFHD.ECMLine3.value])

		### EPGSelection EPGList
		if self.E2DistroVersion == "VTi":
			if config.plugins.KravenFHD.EPGListSize.value == "big":
				self.skinSearchAndReplace.append(['alias name="EPGList0" font="Regular" size="32"', 'alias name="EPGList0" font="Regular" size="36"']) # EPGList (Fontsize)
				self.skinSearchAndReplace.append(['alias name="EPGList1" font="Regular" size="32"', 'alias name="EPGList1" font="Regular" size="36"'])
				
				self.skinSearchAndReplace.append(['font="Regular;32" itemHeight="EPGSelection"', 'itemHeight="54"']) # EPGSelection (itemHeight)
				self.skinSearchAndReplace.append(['parameter name="EPGlistText1" value="3,2,48,41"', 'parameter name="EPGlistText1" value="3,3,60,46"'])
				self.skinSearchAndReplace.append(['parameter name="EPGlistText2" value="57,2,243,41"', 'parameter name="EPGlistText2" value="69,3,270,46"'])
				self.skinSearchAndReplace.append(['parameter name="EPGlistRecImage" value="321,13,20,20"', 'parameter name="EPGlistRecImage" value="360,17,20,20"'])
				self.skinSearchAndReplace.append(['parameter name="EPGlistRecText" value="351,2,705,41"', 'parameter name="EPGlistRecText" value="390,3,666,46"'])
				self.skinSearchAndReplace.append(['parameter name="EPGlistNonRecText" value="321,2,735,41"', 'parameter name="EPGlistNonRecText" value="360,3,696,46"'])
				
				self.skinSearchAndReplace.append(['itemHeight="EPGSearch"', 'itemHeight="108"']) # EPGSearch (itemHeight)
				self.skinSearchAndReplace.append(['parameter name="EPGlistText3" value="321,1,735,41"', 'parameter name="EPGlistText3" value="360,2,696,46"'])
				self.skinSearchAndReplace.append(['parameter name="EPGSearchItemHeightBig" value="90"', 'parameter name="EPGSearchItemHeightBig" value="108"'])
				self.skinSearchAndReplace.append(['parameter name="EPGSearchItemHeightDefault" value="45"', 'parameter name="EPGSearchItemHeightDefault" value="54"'])
				
				self.skinSearchAndReplace.append(['itemHeight="EPGSelectionMulti"', 'itemHeight="54"']) # EPGSelectionMulti (itemHeight)
				self.skinSearchAndReplace.append(['parameter name="EPGlistMultiRecIcon" value="3,13,20,20"', 'parameter name="EPGlistMultiRecIcon" value="3,17,20,20"'])
				self.skinSearchAndReplace.append(['parameter name="EPGlistMultiRecText" value="33,2,190,41"', 'parameter name="EPGlistMultiRecText" value="33,3,222,46"'])
				self.skinSearchAndReplace.append(['parameter name="EPGlistMultiNonRecText" value="3,2,220,41"', 'parameter name="EPGlistMultiNonRecText" value="3,3,252,46"'])
				self.skinSearchAndReplace.append(['parameter name="EPGlistMultiBeginText1" value="220,2,260,41"', 'parameter name="EPGlistMultiBeginText1" value="261,3,320,46"'])
				self.skinSearchAndReplace.append(['parameter name="EPGlistMultiBeginText2" value="482,2,1285,41"', 'parameter name="EPGlistMultiBeginText2" value="542,3,1225,46"'])
				self.skinSearchAndReplace.append(['parameter name="EPGlistMultiProgress" value="300,15,50,10"', 'parameter name="EPGlistMultiProgress" value="300,19,50,16"'])
				self.skinSearchAndReplace.append(['parameter name="EPGlistMultiProgressText" value="370,2,1397,41"', 'parameter name="EPGlistMultiProgressText" value="370,3,1397,46"'])
				
				self.skinSearchAndReplace.append(['parameter name="EPGlistEPGBarText1" value="40,2,703,41"', 'parameter name="EPGlistEPGBarText1" value="40,0,703,45"']) # EPGSelectionEPGBar_HD
				self.skinSearchAndReplace.append(['parameter name="EPGlistEPGBarText2" value="3,2,741,41"', 'parameter name="EPGlistEPGBarText2" value="3,0,741,45"'])
				
			else:
				self.skinSearchAndReplace.append(['font="Regular;32" itemHeight="EPGSelection"', 'itemHeight="45"']) # EPGSelection (itemHeight)
				self.skinSearchAndReplace.append(['itemHeight="EPGSearch"', 'itemHeight="90"']) # EPGSearch (itemHeight)
				self.skinSearchAndReplace.append(['itemHeight="EPGSelectionMulti"', 'itemHeight="45"']) # EPGSelectionMulti (itemHeight)
				
		elif self.E2DistroVersion == "openatv":
			if config.plugins.KravenFHD.EPGListSize.value == "big":
				self.skinSearchAndReplace.append(['font="Regular;32" itemHeight="EPGSelection"', 'font="Regular;36" itemHeight="54"']) # EPGSelection (Fontsize and itemHeight)
				self.skinSearchAndReplace.append(['font="Regular;32" itemHeight="EPGSearch"', 'font="Regular;36" itemHeight="54"']) # EPGSearch (Fontsize and itemHeight)
				self.skinSearchAndReplace.append(['font="Regular;32" itemHeight="EPGSelectionMulti"', 'font="Regular;36" itemHeight="54"']) # EPGSelectionMulti (Fontsize and itemHeight)
			else:
				self.skinSearchAndReplace.append(['itemHeight="EPGSelection"', 'itemHeight="45"']) # EPGSelection (itemHeight)
				self.skinSearchAndReplace.append(['itemHeight="EPGSearch"', 'itemHeight="45"']) # EPGSearch (itemHeight)
				self.skinSearchAndReplace.append(['itemHeight="EPGSelectionMulti"', 'itemHeight="45"']) # EPGSelectionMulti (itemHeight)
				
		elif self.E2DistroVersion == "teamblue":
			if config.plugins.KravenFHD.EPGListSize.value == "big":
				self.skinSearchAndReplace.append(['teamBlueEPGListSkinParameter="EPGSelection_EPGSearch"', 'setEventItemFont="Regular;37" setEventTimeFont="Regular;30" setTimeWidth="155" setIconDistance="12" setIconShift="0" setColWidths="86,207" setColGap="15" itemHeight="52" position="105,120" size="1062,780"']) # EPGSelection, EPGSearch
				self.skinSearchAndReplace.append(['teamBlueEPGListSkinParameter="EPGSelectionMulti"', 'setEventItemFont="Regular;37" setEventTimeFont="Regular;30" setTimeWidth="155" setIconDistance="12" setIconShift="0" setColWidths="345,173" setColGap="15" itemHeight="52" position="75,202" size="1770,520"']) # EPGSelectionMulti
			else:
				self.skinSearchAndReplace.append(['teamBlueEPGListSkinParameter="EPGSelection_EPGSearch"', 'setEventItemFont="Regular;32" setEventTimeFont="Regular;26" setTimeWidth="135" setIconDistance="12" setIconShift="0" setColWidths="75,180" setColGap="15" itemHeight="45" position="105,120" size="1062,810"']) # EPGSelection, EPGSearch
				self.skinSearchAndReplace.append(['teamBlueEPGListSkinParameter="EPGSelectionMulti"', 'setEventItemFont="Regular;32" setEventTimeFont="Regular;26" setTimeWidth="135" setIconDistance="12" setIconShift="0" setColWidths="300,150" setColGap="15" itemHeight="45" position="75,202" size="1770,540"']) # EPGSelectionMulti

		### VTi MovieList-Picon
		if self.E2DistroVersion == "VTi" and config.usage.movielist_show_picon.value == True:
			self.skinSearchAndReplace.append(['<parameter name="MovieListMinimalVTITitle" value="40,0,1000,40" />', '<parameter name="MovieListMinimalVTITitle" value="40,0,800,40" />'])

		### change constant-widgets to panels for teamblue (part #1)
		if self.E2DistroVersion == "teamblue":
			self.skinSearchAndReplace.append(['<constant-widgets>', '<!--/* Templates -->'])
			self.skinSearchAndReplace.append(['</constant-widgets>', '<!-- Templates */-->'])
			self.skinSearchAndReplace.append(['constant-panels', 'screen'])
		elif self.E2DistroVersion in ("VTi","openatv"):
			self.skinSearchAndReplace.append(['constant-panels', 'constant-widget'])

		### Header
		self.appendSkinFile(self.daten + "header.xml")

		### Skinparameter
		self.appendSkinFile(self.daten + 'skinparameter_' + self.E2DistroVersion + '.xml')

		### Listselection-Border
		if not config.plugins.KravenFHD.SelectionBorderList.value == "none":
			self.appendSkinFile(self.daten + "selectionborder.xml")

		### Templates
		self.appendSkinFile(self.daten + "templates.xml")

		### change constant-widgets to panels for teamblue (part #2)
		if self.E2DistroVersion == "teamblue":
			self.skinSearchAndReplace.append(['constant-widget', 'panel'])

		### Volume
		self.appendSkinFile(self.daten + config.plugins.KravenFHD.Volume.value + ".xml")

		### ChannelSelection - horizontal RunningText
		if not self.BoxName == "solo2":
			if config.plugins.KravenFHD.RunningTextSpeed.value == "steptime=200":
				self.skinSearchAndReplace.append(['render="RunningTextEmptyEpg2"', 'render="KravenFHDRunningText" options="movetype=running,startpoint=0,' + config.plugins.KravenFHD.RunningText.value + ',steptime=66,wrap=0,always=0,repeat=2,oneshot=1"'])
			elif config.plugins.KravenFHD.RunningTextSpeed.value == "steptime=100":
				self.skinSearchAndReplace.append(['render="RunningTextEmptyEpg2"', 'render="KravenFHDRunningText" options="movetype=running,startpoint=0,' + config.plugins.KravenFHD.RunningText.value + ',steptime=33,wrap=0,always=0,repeat=2,oneshot=1"'])
			elif config.plugins.KravenFHD.RunningTextSpeed.value == "steptime=50":
				self.skinSearchAndReplace.append(['render="RunningTextEmptyEpg2"', 'render="KravenFHDRunningText" options="movetype=running,startpoint=0,' + config.plugins.KravenFHD.RunningText.value + ',steptime=17,wrap=0,always=0,repeat=2,oneshot=1"'])
			elif config.plugins.KravenFHD.RunningTextSpeed.value == "steptime=33":
				self.skinSearchAndReplace.append(['render="RunningTextEmptyEpg2"', 'render="KravenFHDRunningText" options="movetype=running,startpoint=0,' + config.plugins.KravenFHD.RunningText.value + ',steptime=11,wrap=0,always=0,repeat=2,oneshot=1"'])
		else:
			self.skinSearchAndReplace.append(['render="RunningTextEmptyEpg2"', 'render="KravenFHDEmptyEpg2"'])

		### ChannelSelection - VTi
		if self.E2DistroVersion == "VTi":
			self.skinSearchAndReplace.append(['name="giopet"', ' '])
			if config.plugins.KravenFHD.alternativeChannellist.value == "none":
				self.appendSkinFile(self.daten + self.actChannelselectionstyle + ".xml")
				if self.actChannelselectionstyle in ("channelselection-style-minitv33","channelselection-style-nobile-minitv33","channelselection-style-minitv2","channelselection-style-minitv22"):
					config.usage.use_pig.value = True
					config.usage.use_pig.save()
					config.usage.use_extended_pig.value = True
					config.usage.use_extended_pig.save()
					config.usage.use_extended_pig_channelselection.value = True
					config.usage.use_extended_pig_channelselection.save()
					config.usage.zap_pip.value = False
					config.usage.zap_pip.save()
					if config.plugins.KravenFHD.ChannelSelectionMode.value == "zap":
						config.usage.servicelist_preview_mode.value = False
						config.usage.servicelist_preview_mode.save()
					else:
						config.usage.servicelist_preview_mode.value = True
						config.usage.servicelist_preview_mode.save()
				elif self.actChannelselectionstyle in ("channelselection-style-minitv","channelselection-style-minitv4","channelselection-style-nobile-minitv","channelselection-style-minitv-picon"):
					config.usage.use_pig.value = True
					config.usage.use_pig.save()
					config.usage.use_extended_pig.value = False
					config.usage.use_extended_pig.save()
					config.usage.use_extended_pig_channelselection.value = False
					config.usage.use_extended_pig_channelselection.save()
					if config.plugins.KravenFHD.ChannelSelectionMode.value == "zap":
						config.usage.servicelist_preview_mode.value = False
						config.usage.servicelist_preview_mode.save()
					else:
						config.usage.servicelist_preview_mode.value = True
						config.usage.servicelist_preview_mode.save()
				elif self.actChannelselectionstyle in ("channelselection-style-minitv3","channelselection-style-nobile-minitv3"):
					config.usage.use_pig.value = True
					config.usage.use_pig.save()
					config.usage.use_extended_pig.value = False
					config.usage.use_extended_pig.save()
					config.usage.use_extended_pig_channelselection.value = False
					config.usage.use_extended_pig_channelselection.save()
					config.usage.servicelist_preview_mode.value = False
					config.usage.servicelist_preview_mode.save()
				else:
					config.usage.use_pig.value = True
					config.usage.use_pig.save()
					config.usage.use_extended_pig.value = False
					config.usage.use_extended_pig.save()
					config.usage.use_extended_pig_channelselection.value = False
					config.usage.use_extended_pig_channelselection.save()
				config.usage.servicelist_alternative_mode.value = False
				config.usage.servicelist_alternative_mode.save()
			else:
				self.appendSkinFile(self.daten + config.plugins.KravenFHD.ChannelSelectionHorStyle.value + ".xml")
				config.usage.servicelist_alternative_mode.value = True
				config.usage.servicelist_alternative_mode.save()
		
		### ChannelSelection - openatv
		elif self.E2DistroVersion == "openatv":
			config.usage.servicelist_mode.value = "standard"
			config.usage.servicelist_mode.save()
			self.skinSearchAndReplace.append(['name="giopet"', 'fieldMargins="15" nonplayableMargins="15" itemsDistances="8" progressBarWidth="78" progressPercentWidth="80" progressbarHeight="15"'])
			if self.actChannelselectionstyle in ("channelselection-style-nopicon","channelselection-style-nopicon2","channelselection-style-xpicon","channelselection-style-zpicon","channelselection-style-zzpicon","channelselection-style-zzzpicon","channelselection-style-minitv3","channelselection-style-nobile-minitv3") or config.plugins.KravenFHD.ChannelSelectionMode.value == "zap":
				config.usage.servicelistpreview_mode.value = False
			else:
				config.usage.servicelistpreview_mode.value = True
			config.usage.servicelistpreview_mode.save()
			if self.actChannelselectionstyle in ("channelselection-style-minitv2","channelselection-style-minitv22"): #DualTV
				self.appendSkinFile(self.daten + self.actChannelselectionstyle + "-openatv.xml")
				config.plugins.KravenFHD.PigStyle.value = "DualTV"
				config.plugins.KravenFHD.PigStyle.save()
			elif self.actChannelselectionstyle in ("channelselection-style-minitv33","channelselection-style-nobile-minitv33"): #ExtPreview
				self.appendSkinFile(self.daten + self.actChannelselectionstyle + "-openatv.xml")
				config.plugins.KravenFHD.PigStyle.value = "ExtPreview"
				config.plugins.KravenFHD.PigStyle.save()
			elif self.actChannelselectionstyle in ("channelselection-style-minitv3","channelselection-style-nobile-minitv3"): #Preview
				self.appendSkinFile(self.daten + self.actChannelselectionstyle + "-openatv.xml")
				config.plugins.KravenFHD.PigStyle.value = "Preview"
				config.plugins.KravenFHD.PigStyle.save()
			else:
				self.skinSearchAndReplace.append(['render="KravenFHDPig3"', 'render="Pig"'])
				self.appendSkinFile(self.daten + self.actChannelselectionstyle + ".xml")
		
		### ChannelSelection - teamblue
		elif self.E2DistroVersion == "teamblue":
			self.skinSearchAndReplace.append(['name="giopet"', ''])
			self.skinSearchAndReplace.append(['render="KravenFHDPig3"', 'render="Pig"'])
			self.appendSkinFile(self.daten + self.actChannelselectionstyle + ".xml")

		### Infobox
		if config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-nopicon","infobar-style-x1","infobar-style-x2","infobar-style-z1","infobar-style-zz1","infobar-style-zz4","infobar-style-zzz1","infobar-style-zzz2"):
			if self.E2DistroVersion == "VTi":
				if config.plugins.KravenFHD.Infobox.value == "cpu":
					self.skinSearchAndReplace.append(['<!--<eLabel text="  S:"', '<eLabel text="  L:"'])
					self.skinSearchAndReplace.append(['foregroundColor="KravenIcon" />-->', 'foregroundColor="KravenIcon" />'])
					self.skinSearchAndReplace.append(['  source="session.FrontendStatus', ' source="session.CurrentService'])
					self.skinSearchAndReplace.append(['convert  type="KravenFHDFrontendInfo">SNR', 'convert type="KravenFHDLayoutInfo">LoadAvg'])
					self.skinSearchAndReplace.append(['convert  type="KravenFHDServiceName2">OrbitalPos', 'convert  type="KravenFHDCpuUsage">$0'])
				elif config.plugins.KravenFHD.Infobox.value == "temp":
					self.skinSearchAndReplace.append(['<!--<eLabel text="  S:"', '<eLabel text="U:"'])
					self.skinSearchAndReplace.append(['foregroundColor="KravenIcon" />-->', 'foregroundColor="KravenIcon" />'])
					self.skinSearchAndReplace.append(['  source="session.FrontendStatus', ' source="session.CurrentService'])
					self.skinSearchAndReplace.append(['convert  type="KravenFHDFrontendInfo">SNR', 'convert type="KravenFHDTempFanInfo">FanInfo'])
					self.skinSearchAndReplace.append(['convert  type="KravenFHDServiceName2">OrbitalPos', 'convert  type="KravenFHDTempFanInfo">TempInfo'])
			elif self.E2DistroVersion in ("openatv","teamblue"):
				if config.plugins.KravenFHD.Infobox2.value == "cpu":
					self.skinSearchAndReplace.append(['<!--<eLabel text="  S:"', '<eLabel text="  L:"'])
					self.skinSearchAndReplace.append(['foregroundColor="KravenIcon" />-->', 'foregroundColor="KravenIcon" />'])
					self.skinSearchAndReplace.append(['  source="session.FrontendStatus', ' source="session.CurrentService'])
					self.skinSearchAndReplace.append(['convert  type="KravenFHDFrontendInfo">SNR', 'convert type="KravenFHDLayoutInfo">LoadAvg'])
					self.skinSearchAndReplace.append(['convert  type="KravenFHDServiceName2">OrbitalPos', 'convert  type="KravenFHDCpuUsage">$0'])
				elif config.plugins.KravenFHD.Infobox2.value == "temp":
					self.skinSearchAndReplace.append(['<!--<eLabel text="  S:"', '<eLabel text="U:"'])
					self.skinSearchAndReplace.append(['foregroundColor="KravenIcon" />-->', 'foregroundColor="KravenIcon" />'])
					self.skinSearchAndReplace.append(['  source="session.FrontendStatus', ' source="session.CurrentService'])
					self.skinSearchAndReplace.append(['convert  type="KravenFHDFrontendInfo">SNR', 'convert type="KravenFHDTempFanInfo">FanInfo'])
					self.skinSearchAndReplace.append(['convert  type="KravenFHDServiceName2">OrbitalPos', 'convert  type="KravenFHDTempFanInfo">TempInfo'])
				elif config.plugins.KravenFHD.Infobox2.value == "db":
					self.skinSearchAndReplace.append(['convert  type="KravenFHDFrontendInfo">SNR', 'convert  type="KravenFHDFrontendInfo">SNRdB'])

		### Record State
		if config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-nopicon","infobar-style-x1","infobar-style-zz1","infobar-style-zz4","infobar-style-zzz1","infobar-style-zzz2"):
			if config.plugins.KravenFHD.record2.value == "record-blink+tuner-shine":
				self.skinSearchAndReplace.append(['<!--  <widget', '<widget'])
				self.skinSearchAndReplace.append(['</widget>  -->', '</widget>'])
				self.skinSearchAndReplace.append(['>recordblink</convert>', '>Blink</convert>'])
				self.skinSearchAndReplace.append(['>tunerblink</convert>', ' />'])
				self.skinSearchAndReplace.append(['source="session.FrontendInfo" zPosition="3"', 'source="session.FrontendInfo" zPosition="5"'])
			elif config.plugins.KravenFHD.record2.value == "record-shine+tuner-blink":
				self.skinSearchAndReplace.append(['<!--  <widget', '<widget'])
				self.skinSearchAndReplace.append(['</widget>  -->', '</widget>'])
				self.skinSearchAndReplace.append(['>recordblink</convert>', ' />'])
				self.skinSearchAndReplace.append(['>tunerblink</convert>', '>Blink</convert>'])
			elif config.plugins.KravenFHD.record2.value == "record+tuner-blink":
				self.skinSearchAndReplace.append(['<!--  <widget', '<widget'])
				self.skinSearchAndReplace.append(['</widget>  -->', '</widget>'])
				self.skinSearchAndReplace.append(['>recordblink</convert>', '>Blink</convert>'])
				self.skinSearchAndReplace.append(['>tunerblink</convert>', '>Blink</convert>'])
			elif config.plugins.KravenFHD.record2.value == "record+tuner-shine":
				self.skinSearchAndReplace.append(['<!--  <widget', '<widget'])
				self.skinSearchAndReplace.append(['</widget>  -->', '</widget>'])
				self.skinSearchAndReplace.append(['>recordblink</convert>', ' />'])
				self.skinSearchAndReplace.append(['>tunerblink</convert>', ' />'])
				self.skinSearchAndReplace.append(['source="session.FrontendInfo" zPosition="3"', 'source="session.FrontendInfo" zPosition="5"'])
			elif config.plugins.KravenFHD.record2.value == "record-blink+no-record-tuner":
				self.skinSearchAndReplace.append(['>recordblink</convert>', '>Blink</convert>'])
			else:
				self.skinSearchAndReplace.append(['>recordblink</convert>', ' />'])
		elif config.plugins.KravenFHD.InfobarStyle.value == "infobar-style-zz2":
			if config.plugins.KravenFHD.record.value == "record-blink":
				self.skinSearchAndReplace.append(['>recordblink</convert>', '>Blink</convert>'])
			else:
				self.skinSearchAndReplace.append(['>recordblink</convert>', ' />'])
		elif config.plugins.KravenFHD.InfobarStyle.value == "infobar-style-x4":
			if config.plugins.KravenFHD.record3.value == "tuner-blink":
				self.skinSearchAndReplace.append(['<!--  <widget', '<widget'])
				self.skinSearchAndReplace.append(['</widget>  -->', '</widget>'])
				self.skinSearchAndReplace.append(['>tunerblink</convert>', '>Blink</convert>'])
			elif config.plugins.KravenFHD.record3.value == "tuner-shine":
				self.skinSearchAndReplace.append(['<!--  <widget', '<widget'])
				self.skinSearchAndReplace.append(['</widget>  -->', '</widget>'])
				self.skinSearchAndReplace.append(['>tunerblink</convert>', ' />'])
		elif config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-x2","infobar-style-z1"):
			if config.plugins.KravenFHD.IBtop.value == "infobar-x2-z1_top2":
				if config.plugins.KravenFHD.record2.value == "record-blink+tuner-shine":
					self.skinSearchAndReplace.append(['<!--  <widget', '<widget'])
					self.skinSearchAndReplace.append(['</widget>  -->', '</widget>'])
					self.skinSearchAndReplace.append(['>recordblink</convert>', '>Blink</convert>'])
					self.skinSearchAndReplace.append(['>tunerblink</convert>', ' />'])
					self.skinSearchAndReplace.append(['source="session.FrontendInfo" zPosition="3"', 'source="session.FrontendInfo" zPosition="5"'])
				elif config.plugins.KravenFHD.record2.value == "record-shine+tuner-blink":
					self.skinSearchAndReplace.append(['<!--  <widget', '<widget'])
					self.skinSearchAndReplace.append(['</widget>  -->', '</widget>'])
					self.skinSearchAndReplace.append(['>recordblink</convert>', ' />'])
					self.skinSearchAndReplace.append(['>tunerblink</convert>', '>Blink</convert>'])
				elif config.plugins.KravenFHD.record2.value == "record+tuner-blink":
					self.skinSearchAndReplace.append(['<!--  <widget', '<widget'])
					self.skinSearchAndReplace.append(['</widget>  -->', '</widget>'])
					self.skinSearchAndReplace.append(['>recordblink</convert>', '>Blink</convert>'])
					self.skinSearchAndReplace.append(['>tunerblink</convert>', '>Blink</convert>'])
				elif config.plugins.KravenFHD.record2.value == "record+tuner-shine":
					self.skinSearchAndReplace.append(['<!--  <widget', '<widget'])
					self.skinSearchAndReplace.append(['</widget>  -->', '</widget>'])
					self.skinSearchAndReplace.append(['>recordblink</convert>', ' />'])
					self.skinSearchAndReplace.append(['>tunerblink</convert>', ' />'])
					self.skinSearchAndReplace.append(['source="session.FrontendInfo" zPosition="3"', 'source="session.FrontendInfo" zPosition="5"'])
				elif config.plugins.KravenFHD.record2.value == "record-blink+no-record-tuner":
					self.skinSearchAndReplace.append(['>recordblink</convert>', '>Blink</convert>'])
				else:
					self.skinSearchAndReplace.append(['>recordblink</convert>', ' />'])
			else:
				if config.plugins.KravenFHD.record3.value == "tuner-blink":
					self.skinSearchAndReplace.append(['<!--  <widget', '<widget'])
					self.skinSearchAndReplace.append(['</widget>  -->', '</widget>'])
					self.skinSearchAndReplace.append(['>tunerblink</convert>', '>Blink</convert>'])
				elif config.plugins.KravenFHD.record3.value == "tuner-shine":
					self.skinSearchAndReplace.append(['<!--  <widget', '<widget'])
					self.skinSearchAndReplace.append(['</widget>  -->', '</widget>'])
					self.skinSearchAndReplace.append(['>tunerblink</convert>', ' />'])
					self.skinSearchAndReplace.append(['source="session.FrontendInfo" zPosition="3"', 'source="session.FrontendInfo" zPosition="5"'])

		### Infobar Clock
		if config.plugins.KravenFHD.InfobarStyle.value == "infobar-style-x1":
			self.skinSearchAndReplace.append(['<!-- Infobar clockstyle -->','<constant-widget name="' + self.actClockstyle + '"/>'])
		elif config.plugins.KravenFHD.InfobarStyle.value == "infobar-style-nopicon":
			if config.plugins.KravenFHD.ClockStyle.value == "clock-classic":
				self.skinSearchAndReplace.append(['<!-- Infobar clockstyle -->','<constant-widget name="clock-classic3"/>'])
			elif config.plugins.KravenFHD.ClockStyle.value == "clock-color":
				self.skinSearchAndReplace.append(['<!-- Infobar clockstyle -->','<constant-widget name="clock-color3"/>'])
			elif config.plugins.KravenFHD.ClockStyle.value == "clock-flip":
				self.skinSearchAndReplace.append(['<!-- Infobar clockstyle -->','<constant-widget name="clock-flip2"/>'])
			elif config.plugins.KravenFHD.ClockStyle.value == "clock-weather":
				self.skinSearchAndReplace.append(['<!-- Infobar clockstyle -->','<constant-widget name="clock-weather2"/>'])
			else:
				self.skinSearchAndReplace.append(['<!-- Infobar clockstyle -->','<constant-widget name="' + self.actClockstyle + '"/>'])
		elif config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-x2","infobar-style-x3","infobar-style-x4","infobar-style-z1","infobar-style-z2","infobar-style-zz2","infobar-style-zz3"):
			if config.plugins.KravenFHD.ClockStyle.value == "clock-classic":
				self.skinSearchAndReplace.append(['<!-- Infobar clockstyle -->','<constant-widget name="clock-classic2"/>'])
			elif config.plugins.KravenFHD.ClockStyle.value == "clock-classic-big":
				self.skinSearchAndReplace.append(['<!-- Infobar clockstyle -->','<constant-widget name="clock-classic-big2"/>'])
			elif config.plugins.KravenFHD.ClockStyle.value == "clock-color":
				self.skinSearchAndReplace.append(['<!-- Infobar clockstyle -->','<constant-widget name="clock-color2"/>'])
			elif config.plugins.KravenFHD.ClockStyle.value == "clock-analog":
				self.skinSearchAndReplace.append(['<!-- Infobar clockstyle -->','<constant-widget name="clock-analog2"/>'])
			elif config.plugins.KravenFHD.ClockStyle.value == "clock-flip":
				self.skinSearchAndReplace.append(['<!-- Infobar clockstyle -->','<constant-widget name="clock-flip2"/>'])
			elif config.plugins.KravenFHD.ClockStyle.value == "clock-weather":
				self.skinSearchAndReplace.append(['<!-- Infobar clockstyle -->','<constant-widget name="clock-weather2"/>'])
			else:
				self.skinSearchAndReplace.append(['<!-- Infobar clockstyle -->','<constant-widget name="' + self.actClockstyle + '"/>'])
		elif config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-zz1","infobar-style-zzz1"):
			if config.plugins.KravenFHD.ClockStyle.value == "clock-classic":
				self.skinSearchAndReplace.append(['<!-- Infobar clockstyle -->','<constant-widget name="clock-classic3"/>'])
			elif config.plugins.KravenFHD.ClockStyle.value == "clock-classic-big":
				self.skinSearchAndReplace.append(['<!-- Infobar clockstyle -->','<constant-widget name="clock-classic-big3"/>'])
			elif config.plugins.KravenFHD.ClockStyle.value == "clock-color":
				self.skinSearchAndReplace.append(['<!-- Infobar clockstyle -->','<constant-widget name="clock-color3"/>'])
			elif config.plugins.KravenFHD.ClockStyle.value == "clock-flip":
				self.skinSearchAndReplace.append(['<!-- Infobar clockstyle -->','<constant-widget name="clock-flip3"/>'])
			elif config.plugins.KravenFHD.ClockStyle.value == "clock-weather":
				self.skinSearchAndReplace.append(['<!-- Infobar clockstyle -->','<constant-widget name="clock-weather3"/>'])
			else:
				self.skinSearchAndReplace.append(['<!-- Infobar clockstyle -->','<constant-widget name="' + self.actClockstyle + '"/>'])
		elif config.plugins.KravenFHD.InfobarStyle.value == "infobar-style-zzz2":
			self.skinSearchAndReplace.append(['<!-- Infobar clockstyle -->','<constant-widget name="' + self.actClockstyle + '4"/>'])

		### Infobar Channelname
		if config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-nopicon","infobar-style-x1") and not config.plugins.KravenFHD.InfobarChannelName.value == "none":
			self.skinSearchAndReplace.append(['<!-- Infobar channelname -->','<constant-widget name="' + config.plugins.KravenFHD.InfobarChannelName.value + '-' + config.plugins.KravenFHD.InfobarStyle.value + '"/>'])
		elif config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-x2","infobar-style-x3","infobar-style-x4","infobar-style-z1","infobar-style-z2") and not config.plugins.KravenFHD.InfobarChannelName.value == "none":
			self.skinSearchAndReplace.append(['<!-- Infobar channelname -->','<constant-widget name="' + config.plugins.KravenFHD.InfobarChannelName.value + '-infobar-style-x2"/>'])
		elif config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-zz1","infobar-style-zz4") and not config.plugins.KravenFHD.InfobarChannelName.value == "none":
			self.skinSearchAndReplace.append(['<!-- Infobar channelname -->','<constant-widget name="' + config.plugins.KravenFHD.InfobarChannelName.value + '-infobar-style-zz1"/>'])
		elif config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-zz2","infobar-style-zz3") and not config.plugins.KravenFHD.InfobarChannelName2.value == "none":
			self.skinSearchAndReplace.append(['<!-- Infobar channelname -->','<constant-widget name="' + config.plugins.KravenFHD.InfobarChannelName2.value + '-infobar-style-zz2"/>'])
		elif config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-zzz1","infobar-style-zzz2") and not config.plugins.KravenFHD.InfobarChannelName2.value == "none":
			self.skinSearchAndReplace.append(['<!-- Infobar channelname -->','<constant-widget name="' + config.plugins.KravenFHD.InfobarChannelName2.value + '-' + config.plugins.KravenFHD.InfobarStyle.value + '"/>'])

		### Infobar/SIB - ecm-info
		if not config.plugins.KravenFHD.InfobarStyle.value == "infobar-style-x4":
			if config.plugins.KravenFHD.ECMVisible.value in ("ib","ib+sib"):
				if config.plugins.KravenFHD.InfobarStyle.value == "infobar-style-x1":
					if config.plugins.KravenFHD.tuner2.value in ("8-tuner","10-tuner"):
						self.skinSearchAndReplace.append(['<!-- Infobar ecminfo -->','<constant-widget name="ecminfo-infobar-style-x1-' + config.plugins.KravenFHD.tuner2.value + '"/>'])
					else:
						self.skinSearchAndReplace.append(['<!-- Infobar ecminfo -->','<constant-widget name="ecminfo-infobar-style-x1"/>'])
				elif config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-x2","infobar-style-x3","infobar-style-z1","infobar-style-z2"):
					self.skinSearchAndReplace.append(['<!-- Infobar ecminfo -->','<constant-widget name="ecminfo-infobar-style-x2"/>'])
				elif config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-zz1","infobar-style-zz4","infobar-style-zzz1"):
					self.skinSearchAndReplace.append(['<!-- Infobar ecminfo -->','<constant-widget name="ecminfo-infobar-style-zz1"/>'])
				elif config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-zz2","infobar-style-zz3"):
					self.skinSearchAndReplace.append(['<!-- Infobar ecminfo -->','<constant-widget name="ecminfo-infobar-style-zz2"/>'])
				else:
					self.skinSearchAndReplace.append(['<!-- Infobar ecminfo -->','<constant-widget name="ecminfo-' + config.plugins.KravenFHD.InfobarStyle.value + '"/>'])

			if config.plugins.KravenFHD.ECMVisible.value in ("sib","ib+sib"):
				if config.plugins.KravenFHD.InfobarStyle.value == "infobar-style-x1":
					if config.plugins.KravenFHD.tuner2.value in ("8-tuner","10-tuner"):
						self.skinSearchAndReplace.append(['<!-- SIB ecminfo -->','<constant-widget name="ecminfo-infobar-style-x1-' + config.plugins.KravenFHD.tuner2.value + '"/>'])
					else:
						self.skinSearchAndReplace.append(['<!-- SIB ecminfo -->','<constant-widget name="ecminfo-infobar-style-x1"/>'])
				elif config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-x2","infobar-style-x3","infobar-style-z1","infobar-style-z2"):
					self.skinSearchAndReplace.append(['<!-- SIB ecminfo -->','<constant-widget name="ecminfo-infobar-style-x2"/>'])
				elif config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-zz1","infobar-style-zz4","infobar-style-zzz1"):
					self.skinSearchAndReplace.append(['<!-- SIB ecminfo -->','<constant-widget name="ecminfo-infobar-style-zz1"/>'])
				elif config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-zz2","infobar-style-zz3"):
					self.skinSearchAndReplace.append(['<!-- SIB ecminfo -->','<constant-widget name="ecminfo-infobar-style-zz2"/>'])
				else:
					self.skinSearchAndReplace.append(['<!-- SIB ecminfo -->','<constant-widget name="ecminfo-' + config.plugins.KravenFHD.InfobarStyle.value + '"/>'])

		### Infobar_begin
		self.appendSkinFile(self.daten + "infobar-begin.xml")

		### Infobar typewriter effect
		if config.plugins.KravenFHD.TypeWriter.value == "runningtext":
			self.skinSearchAndReplace.append(['render="KravenFHDEmptyEpg"', 'render="KravenFHDRunningText" options="movetype=running,startpoint=0,' + config.plugins.KravenFHD.RunningText.value + ',' + config.plugins.KravenFHD.RunningTextSpeed.value + ',wrap=0,always=0,repeat=2,oneshot=1"'])
		elif config.plugins.KravenFHD.TypeWriter.value == "none":
			self.skinSearchAndReplace.append(['render="KravenFHDEmptyEpg"', 'render="KravenFHDEmptyEpg2"'])

		### Infobar_main
		if config.plugins.KravenFHD.InfobarStyle.value == "infobar-style-nopicon":
			if config.plugins.KravenFHD.tuner2.value == "2-tuner":
				self.appendSkinFile(self.daten + "infobar-style-nopicon_main2.xml")
			elif config.plugins.KravenFHD.tuner2.value == "4-tuner":
				self.appendSkinFile(self.daten + "infobar-style-nopicon_main4.xml")
			elif config.plugins.KravenFHD.tuner2.value == "8-tuner":
				self.appendSkinFile(self.daten + "infobar-style-nopicon_main8.xml")
			elif config.plugins.KravenFHD.tuner2.value == "10-tuner":
				self.appendSkinFile(self.daten + "infobar-style-nopicon_main10.xml")
		elif config.plugins.KravenFHD.InfobarStyle.value == "infobar-style-x1":
			if config.plugins.KravenFHD.tuner2.value == "2-tuner":
				self.appendSkinFile(self.daten + "infobar-style-x1_main2.xml")
			elif config.plugins.KravenFHD.tuner2.value == "4-tuner":
				self.appendSkinFile(self.daten + "infobar-style-x1_main4.xml")
			elif config.plugins.KravenFHD.tuner2.value == "8-tuner":
				self.appendSkinFile(self.daten + "infobar-style-x1_main8.xml")
			elif config.plugins.KravenFHD.tuner2.value == "10-tuner":
				self.appendSkinFile(self.daten + "infobar-style-x1_main10.xml")
		elif config.plugins.KravenFHD.InfobarStyle.value == "infobar-style-zz1":
			if config.plugins.KravenFHD.tuner.value == "2-tuner":
				self.appendSkinFile(self.daten + "infobar-style-zz1_main2.xml")
			elif config.plugins.KravenFHD.tuner.value == "4-tuner":
				self.appendSkinFile(self.daten + "infobar-style-zz1_main4.xml")
			elif config.plugins.KravenFHD.tuner.value == "8-tuner":
				self.appendSkinFile(self.daten + "infobar-style-zz1_main8.xml")
		elif config.plugins.KravenFHD.InfobarStyle.value == "infobar-style-zz4":
			if config.plugins.KravenFHD.tuner.value == "2-tuner":
				self.appendSkinFile(self.daten + "infobar-style-zz4_main2.xml")
			elif config.plugins.KravenFHD.tuner.value == "4-tuner":
				self.appendSkinFile(self.daten + "infobar-style-zz4_main4.xml")
			elif config.plugins.KravenFHD.tuner.value == "8-tuner":
				self.appendSkinFile(self.daten + "infobar-style-zz4_main8.xml")
		elif config.plugins.KravenFHD.InfobarStyle.value == "infobar-style-zzz1":
			if config.plugins.KravenFHD.tuner.value == "2-tuner":
				self.appendSkinFile(self.daten + "infobar-style-zzz1_main2.xml")
			elif config.plugins.KravenFHD.tuner.value == "4-tuner":
				self.appendSkinFile(self.daten + "infobar-style-zzz1_main4.xml")
			elif config.plugins.KravenFHD.tuner.value == "8-tuner":
				self.appendSkinFile(self.daten + "infobar-style-zzz1_main8.xml")
		else:
			self.appendSkinFile(self.daten + config.plugins.KravenFHD.InfobarStyle.value + "_main.xml")

		### Infobar_top
		if config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-x2","infobar-style-z1"):
			if config.plugins.KravenFHD.IBtop.value == "infobar-x2-z1_top":
				self.appendSkinFile(self.daten + "infobar-x2-z1_top.xml")
			elif config.plugins.KravenFHD.IBtop.value == "infobar-x2-z1_top2":
				self.appendSkinFile(self.daten + "infobar-x2-z1_top2.xml")
			elif config.plugins.KravenFHD.IBtop.value == "infobar-x2-z1_top3":
				self.appendSkinFile(self.daten + "infobar-x2-z1_top3.xml")

		### clock-weather (icon size)
		if not config.plugins.KravenFHD.InfobarStyle.value == "infobar-style-zz4" and self.actClockstyle == "clock-weather":
			if config.plugins.KravenFHD.ClockIconSize.value == "size-192":
				self.skinSearchAndReplace.append(['position="1599,897" size="144,144"','position="1575,873" size="192,192"'])
				self.skinSearchAndReplace.append(['position="1599,912" size="144,144"','position="1575,888" size="192,192"'])
				self.skinSearchAndReplace.append(['position="1614,897" size="144,144"','position="1590,873" size="192,192"'])

		### system-info
		if config.plugins.KravenFHD.IBStyle.value == "box":
			if config.plugins.KravenFHD.SystemInfo.value == "systeminfo-small":
				if config.plugins.KravenFHD.InfobarBoxColor.value == "gradient":
					self.skinSearchAndReplace.append(['<constant-widget name="systeminfo-small-bg"/>','<constant-widget name="systeminfo-small-bg-box2"/>'])
				elif config.plugins.KravenFHD.InfobarBoxColor.value == "texture":
					self.skinSearchAndReplace.append(['<constant-widget name="systeminfo-small-bg"/>','<constant-widget name="systeminfo-small-bg-texture"/>'])
				self.appendSkinFile(self.daten + "systeminfo-small2.xml")
			elif config.plugins.KravenFHD.SystemInfo.value == "systeminfo-big":
				if config.plugins.KravenFHD.InfobarBoxColor.value == "gradient":
					self.skinSearchAndReplace.append(['<constant-widget name="systeminfo-big-bg"/>','<constant-widget name="systeminfo-big-bg-box2"/>'])
				elif config.plugins.KravenFHD.InfobarBoxColor.value == "texture":
					self.skinSearchAndReplace.append(['<constant-widget name="systeminfo-big-bg"/>','<constant-widget name="systeminfo-big-bg-texture"/>'])
				self.appendSkinFile(self.daten + "systeminfo-big2.xml")
			elif config.plugins.KravenFHD.SystemInfo.value == "systeminfo-bigsat":
				if config.plugins.KravenFHD.InfobarBoxColor.value == "gradient":
					self.skinSearchAndReplace.append(['<constant-widget name="systeminfo-bigsat-bg"/>','<constant-widget name="systeminfo-bigsat-bg-box2"/>'])
				elif config.plugins.KravenFHD.InfobarBoxColor.value == "texture":
					self.skinSearchAndReplace.append(['<constant-widget name="systeminfo-bigsat-bg"/>','<constant-widget name="systeminfo-bigsat-bg-texture"/>'])
				self.appendSkinFile(self.daten + "systeminfo-bigsat2.xml")
		else:
			self.appendSkinFile(self.daten + config.plugins.KravenFHD.SystemInfo.value + ".xml")

		### weather-style
		if config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-nopicon","infobar-style-x1","infobar-style-x3","infobar-style-x4","infobar-style-z2","infobar-style-zz1","infobar-style-zz2","infobar-style-zz3","infobar-style-zz4","infobar-style-zzz1","infobar-style-zzz2"):
			self.actWeatherstyle=config.plugins.KravenFHD.WeatherStyle.value
		elif config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-x2","infobar-style-z1"):
			if fileExists("/usr/lib/enigma2/python/Plugins/Extensions/Netatmo/plugin.py"):
				self.actWeatherstyle=config.plugins.KravenFHD.WeatherStyle3.value
			else:
				self.actWeatherstyle=config.plugins.KravenFHD.WeatherStyle2.value
		if self.actWeatherstyle != "netatmobar":
			self.appendSkinFile(self.daten + self.actWeatherstyle + ".xml")
		if config.plugins.KravenFHD.refreshInterval.value == "0":
			config.plugins.KravenFHD.refreshInterval.value = config.plugins.KravenFHD.refreshInterval.default
			config.plugins.KravenFHD.refreshInterval.save()

		### Infobar_end - SIB_begin
		self.appendSkinFile(self.daten + "infobar-style_middle.xml")

		### SIB_main + SIB-Fontsize
		if config.plugins.KravenFHD.InfobarStyle.value == "infobar-style-nopicon":
			if config.plugins.KravenFHD.tuner2.value == "2-tuner":
				self.appendSkinFile(self.daten + "infobar-style-nopicon_main2.xml")
			elif config.plugins.KravenFHD.tuner2.value == "4-tuner":
				self.appendSkinFile(self.daten + "infobar-style-nopicon_main4.xml")
			elif config.plugins.KravenFHD.tuner2.value == "8-tuner":
				self.appendSkinFile(self.daten + "infobar-style-nopicon_main8.xml")
			elif config.plugins.KravenFHD.tuner2.value == "10-tuner":
				self.appendSkinFile(self.daten + "infobar-style-nopicon_main10.xml")

		elif config.plugins.KravenFHD.InfobarStyle.value == "infobar-style-x1":
			if config.plugins.KravenFHD.tuner2.value == "2-tuner":
				self.appendSkinFile(self.daten + "infobar-style-x1_main2.xml")
			elif config.plugins.KravenFHD.tuner2.value == "4-tuner":
				self.appendSkinFile(self.daten + "infobar-style-x1_main4.xml")
			elif config.plugins.KravenFHD.tuner2.value == "8-tuner":
				self.appendSkinFile(self.daten + "infobar-style-x1_main8.xml")
			elif config.plugins.KravenFHD.tuner2.value == "10-tuner":
				self.appendSkinFile(self.daten + "infobar-style-x1_main10.xml")

		elif config.plugins.KravenFHD.InfobarStyle.value == "infobar-style-x2":
			self.appendSkinFile(self.daten + "infobar-style-x2_main.xml")

		elif config.plugins.KravenFHD.InfobarStyle.value == "infobar-style-x3":
			self.appendSkinFile(self.daten + "infobar-style-x3_main.xml")

		elif config.plugins.KravenFHD.InfobarStyle.value == "infobar-style-x4":
			self.appendSkinFile(self.daten + "infobar-style-x4_main.xml")

		elif config.plugins.KravenFHD.InfobarStyle.value == "infobar-style-z1":
			self.appendSkinFile(self.daten + "infobar-style-z1_main.xml")

		elif config.plugins.KravenFHD.InfobarStyle.value == "infobar-style-z2":
			self.appendSkinFile(self.daten + "infobar-style-z2_main.xml")

		elif config.plugins.KravenFHD.InfobarStyle.value == "infobar-style-zz1":
			if config.plugins.KravenFHD.SIBFont.value == "sibfont-small":
				self.skinSearchAndReplace.append(['font="Regular2; 33" size="1798,252">', 'font="Regular2; 33" size="1798,252">']) # sib1-small
				self.skinSearchAndReplace.append(['font="Regular2; 33" size="1800,420">', 'font="Regular2; 33" size="1800,378">']) # sib4+sib6-small
				self.skinSearchAndReplace.append(['font="Regular2; 33" size="1050,420">', 'font="Regular2; 33" size="1050,378">']) # sib5+sib7-small
				self.skinSearchAndReplace.append(['font="Regular2; 33" size="705,420">', 'font="Regular2; 33" size="705,378">']) # sib5+sib7-small
			else:
				self.skinSearchAndReplace.append(['font="Regular2; 36" size="1798,276">', 'font="Regular2; 36" size="1798,230">']) # sib1
				self.skinSearchAndReplace.append(['font="Regular2; 38" size="1800,441">', 'font="Regular2; 38" size="1800,392">']) # sib4+sib6
				self.skinSearchAndReplace.append(['font="Regular2; 38" size="1050,441">', 'font="Regular2; 38" size="1050,392">']) # sib5+sib7
				self.skinSearchAndReplace.append(['font="Regular2; 38" size="705,441">', 'font="Regular2; 38" size="705,392">']) # sib5+sib7
			if config.plugins.KravenFHD.tuner.value == "2-tuner":
				self.appendSkinFile(self.daten + "infobar-style-zz1_main2.xml")
			elif config.plugins.KravenFHD.tuner.value == "4-tuner":
				self.appendSkinFile(self.daten + "infobar-style-zz1_main4.xml")
			elif config.plugins.KravenFHD.tuner.value == "8-tuner":
				self.appendSkinFile(self.daten + "infobar-style-zz1_main8.xml")

		elif config.plugins.KravenFHD.InfobarStyle.value == "infobar-style-zz2":
			if config.plugins.KravenFHD.SIBFont.value == "sibfont-small":
				self.skinSearchAndReplace.append(['font="Regular2; 33" size="1798,252">', 'font="Regular2; 33" size="1798,252">']) # sib1-small
				self.skinSearchAndReplace.append(['font="Regular2; 33" size="1800,420">', 'font="Regular2; 33" size="1800,378">']) # sib4+sib6-small
				self.skinSearchAndReplace.append(['font="Regular2; 33" size="1050,420">', 'font="Regular2; 33" size="1050,378">']) # sib5+sib7-small
				self.skinSearchAndReplace.append(['font="Regular2; 33" size="705,420">', 'font="Regular2; 33" size="705,378">']) # sib5+sib7-small
			else:
				self.skinSearchAndReplace.append(['font="Regular2; 36" size="1798,276">', 'font="Regular2; 36" size="1798,230">']) # sib1
				self.skinSearchAndReplace.append(['font="Regular2; 38" size="1800,441">', 'font="Regular2; 38" size="1800,392">']) # sib4+sib6
				self.skinSearchAndReplace.append(['font="Regular2; 38" size="1050,441">', 'font="Regular2; 38" size="1050,392">']) # sib5+sib7
				self.skinSearchAndReplace.append(['font="Regular2; 38" size="705,441">', 'font="Regular2; 38" size="705,392">']) # sib5+sib7
			self.appendSkinFile(self.daten + "infobar-style-zz2_main.xml")

		elif config.plugins.KravenFHD.InfobarStyle.value == "infobar-style-zz3":
			if config.plugins.KravenFHD.SIBFont.value == "sibfont-small":
				self.skinSearchAndReplace.append(['font="Regular2; 33" size="1798,252">', 'font="Regular2; 33" size="1798,252">']) # sib1-small
				self.skinSearchAndReplace.append(['font="Regular2; 33" size="1800,420">', 'font="Regular2; 33" size="1800,378">']) # sib4+sib6-small
				self.skinSearchAndReplace.append(['font="Regular2; 33" size="1050,420">', 'font="Regular2; 33" size="1050,378">']) # sib5+sib7-small
				self.skinSearchAndReplace.append(['font="Regular2; 33" size="705,420">', 'font="Regular2; 33" size="705,378">']) # sib5+sib7-small
			else:
				self.skinSearchAndReplace.append(['font="Regular2; 36" size="1798,276">', 'font="Regular2; 36" size="1798,230">']) # sib1
				self.skinSearchAndReplace.append(['font="Regular2; 38" size="1800,441">', 'font="Regular2; 38" size="1800,392">']) # sib4+sib6
				self.skinSearchAndReplace.append(['font="Regular2; 38" size="1050,441">', 'font="Regular2; 38" size="1050,392">']) # sib5+sib7
				self.skinSearchAndReplace.append(['font="Regular2; 38" size="705,441">', 'font="Regular2; 38" size="705,392">']) # sib5+sib7
			self.appendSkinFile(self.daten + "infobar-style-zz3_main.xml")

		elif config.plugins.KravenFHD.InfobarStyle.value == "infobar-style-zz4":
			if config.plugins.KravenFHD.SIBFont.value == "sibfont-small":
				self.skinSearchAndReplace.append(['font="Regular2; 33" size="1798,252">', 'font="Regular2; 33" size="1798,252">']) # sib1-small
				self.skinSearchAndReplace.append(['font="Regular2; 33" size="1800,420">', 'font="Regular2; 33" size="1800,378">']) # sib4+sib6-small
				self.skinSearchAndReplace.append(['font="Regular2; 33" size="1050,420">', 'font="Regular2; 33" size="1050,378">']) # sib5+sib7-small
				self.skinSearchAndReplace.append(['font="Regular2; 33" size="705,420">', 'font="Regular2; 33" size="705,378">']) # sib5+sib7-small
			else:
				self.skinSearchAndReplace.append(['font="Regular2; 36" size="1798,276">', 'font="Regular2; 36" size="1798,230">']) # sib1
				self.skinSearchAndReplace.append(['font="Regular2; 38" size="1800,441">', 'font="Regular2; 38" size="1800,392">']) # sib4+sib6
				self.skinSearchAndReplace.append(['font="Regular2; 38" size="1050,441">', 'font="Regular2; 38" size="1050,392">']) # sib5+sib7
				self.skinSearchAndReplace.append(['font="Regular2; 38" size="705,441">', 'font="Regular2; 38" size="705,392">']) # sib5+sib7
			if config.plugins.KravenFHD.tuner.value == "2-tuner":
				self.appendSkinFile(self.daten + "infobar-style-zz4_main2.xml")
			elif config.plugins.KravenFHD.tuner.value == "4-tuner":
				self.appendSkinFile(self.daten + "infobar-style-zz4_main4.xml")
			elif config.plugins.KravenFHD.tuner.value == "8-tuner":
				self.appendSkinFile(self.daten + "infobar-style-zz4_main8.xml")

		elif config.plugins.KravenFHD.InfobarStyle.value == "infobar-style-zzz1":
			if config.plugins.KravenFHD.SIBFont.value == "sibfont-small":
				self.skinSearchAndReplace.append(['font="Regular2; 33" size="1798,252">', 'font="Regular2; 33" size="1798,168">']) # sib1-small
				self.skinSearchAndReplace.append(['font="Regular2; 33" size="855,588">', 'font="Regular2; 33" size="855,504">']) # sib2-small
				self.skinSearchAndReplace.append(['font="Regular2; 33" size="1800,588">', 'font="Regular2; 33" size="1800,504">']) # sib3-small
				self.skinSearchAndReplace.append(['font="Regular2; 33" size="1800,420">', 'font="Regular2; 33" size="1800,304">']) # sib4+sib6-small
				self.skinSearchAndReplace.append(['font="Regular2; 33" size="1050,420">', 'font="Regular2; 33" size="1050,336">']) # sib5+sib7-small
				self.skinSearchAndReplace.append(['font="Regular2; 33" size="705,420">', 'font="Regular2; 33" size="705,336">']) # sib5+sib7-small
			else:
				self.skinSearchAndReplace.append(['font="Regular2; 36" size="1798,276">', 'font="Regular2; 36" size="1798,184">']) # sib1
				self.skinSearchAndReplace.append(['font="Regular2; 38" size="855,588">', 'font="Regular2; 38" size="855,490">']) # sib2
				self.skinSearchAndReplace.append(['font="Regular2; 38" size="1800,588">', 'font="Regular2; 38" size="1800,490">']) # sib3
				self.skinSearchAndReplace.append(['font="Regular2; 38" size="1800,441">', 'font="Regular2; 38" size="1800,343">']) # sib4+sib6
				self.skinSearchAndReplace.append(['font="Regular2; 38" size="1050,441">', 'font="Regular2; 38" size="1050,343">']) # sib5+sib7
				self.skinSearchAndReplace.append(['font="Regular2; 38" size="705,441">', 'font="Regular2; 38" size="705,343">']) # sib5+sib7
			if config.plugins.KravenFHD.tuner.value == "2-tuner":
				self.appendSkinFile(self.daten + "infobar-style-zzz1_main2.xml")
			elif config.plugins.KravenFHD.tuner.value == "4-tuner":
				self.appendSkinFile(self.daten + "infobar-style-zzz1_main4.xml")
			elif config.plugins.KravenFHD.tuner.value == "8-tuner":
				self.appendSkinFile(self.daten + "infobar-style-zzz1_main8.xml")

		elif config.plugins.KravenFHD.InfobarStyle.value == "infobar-style-zzz2":
			if config.plugins.KravenFHD.SIBFont.value == "sibfont-small":
				self.skinSearchAndReplace.append(['font="Regular2; 33" size="1798,252">', 'font="Regular2; 33" size="1798,168">']) # sib1-small
				self.skinSearchAndReplace.append(['font="Regular2; 33" size="855,588">', 'font="Regular2; 33" size="855,504">']) # sib2-small
				self.skinSearchAndReplace.append(['font="Regular2; 33" size="1800,588">', 'font="Regular2; 33" size="1800,504">']) # sib3-small
				self.skinSearchAndReplace.append(['font="Regular2; 33" size="1800,420">', 'font="Regular2; 33" size="1800,304">']) # sib4+sib6-small
				self.skinSearchAndReplace.append(['font="Regular2; 33" size="1050,420">', 'font="Regular2; 33" size="1050,336">']) # sib5+sib7-small
				self.skinSearchAndReplace.append(['font="Regular2; 33" size="705,420">', 'font="Regular2; 33" size="705,336">']) # sib5+sib7-small
			else:
				self.skinSearchAndReplace.append(['font="Regular2; 36" size="1798,276">', 'font="Regular2; 36" size="1798,184">']) # sib1
				self.skinSearchAndReplace.append(['font="Regular2; 38" size="855,588">', 'font="Regular2; 38" size="855,490">']) # sib2
				self.skinSearchAndReplace.append(['font="Regular2; 38" size="1800,588">', 'font="Regular2; 38" size="1800,490">']) # sib3
				self.skinSearchAndReplace.append(['font="Regular2; 38" size="1800,441">', 'font="Regular2; 38" size="1800,343">']) # sib4+sib6
				self.skinSearchAndReplace.append(['font="Regular2; 38" size="1050,441">', 'font="Regular2; 38" size="1050,343">']) # sib5+sib7
				self.skinSearchAndReplace.append(['font="Regular2; 38" size="705,441">', 'font="Regular2; 38" size="705,343">']) # sib5+sib7
			self.appendSkinFile(self.daten + "infobar-style-zzz2_main.xml")

		if config.plugins.KravenFHD.SIBFont.value == "sibfont-small":
			self.appendSkinFile(self.daten + config.plugins.KravenFHD.SIB.value + "-small.xml")
		else:
			self.appendSkinFile(self.daten + config.plugins.KravenFHD.SIB.value + ".xml")
		if self.E2DistroVersion in ("VTi","openatv") and fileExists("/usr/lib/enigma2/python/Plugins/Extensions/SecondInfoBar/plugin.py"):
			config.plugins.SecondInfoBar.HideNormalIB.value = True
			config.plugins.SecondInfoBar.HideNormalIB.save()

		### Main XML
		self.appendSkinFile(self.daten + "main.xml")

		if config.plugins.KravenFHD.IBStyle.value == "grad":
			### Timeshift_begin
			self.appendSkinFile(self.daten + "timeshift-begin.xml")

			if self.actWeatherstyle in ("weather-big","weather-left"):
				if config.plugins.KravenFHD.SystemInfo.value == "systeminfo-bigsat":
					self.appendSkinFile(self.daten + "timeshift-begin-leftlow.xml")
				else:
					self.appendSkinFile(self.daten + "timeshift-begin-low.xml")
			elif self.actWeatherstyle == "weather-small":
				self.appendSkinFile(self.daten + "timeshift-begin-left.xml")
			else:
				self.appendSkinFile(self.daten + "timeshift-begin-high.xml")

			### Timeshift_Infobar_main
			if config.plugins.KravenFHD.InfobarStyle.value == "infobar-style-nopicon":
				if config.plugins.KravenFHD.tuner.value == "2-tuner":
					self.appendSkinFile(self.daten + "infobar-style-nopicon_main2.xml")
				elif config.plugins.KravenFHD.tuner2.value == "4-tuner":
					self.appendSkinFile(self.daten + "infobar-style-nopicon_main4.xml")
				elif config.plugins.KravenFHD.tuner2.value == "8-tuner":
					self.appendSkinFile(self.daten + "infobar-style-nopicon_main8.xml")
				elif config.plugins.KravenFHD.tuner2.value == "10-tuner":
					self.appendSkinFile(self.daten + "infobar-style-nopicon_main10.xml")
			elif config.plugins.KravenFHD.InfobarStyle.value == "infobar-style-x1":
				if config.plugins.KravenFHD.tuner2.value == "2-tuner":
					self.appendSkinFile(self.daten + "infobar-style-x1_main2.xml")
				elif config.plugins.KravenFHD.tuner2.value == "4-tuner":
					self.appendSkinFile(self.daten + "infobar-style-x1_main4.xml")
				elif config.plugins.KravenFHD.tuner2.value == "8-tuner":
					self.appendSkinFile(self.daten + "infobar-style-x1_main8.xml")
				elif config.plugins.KravenFHD.tuner2.value == "10-tuner":
					self.appendSkinFile(self.daten + "infobar-style-x1_main10.xml")
			elif config.plugins.KravenFHD.InfobarStyle.value == "infobar-style-zz1":
				if config.plugins.KravenFHD.tuner.value == "2-tuner":
					self.appendSkinFile(self.daten + "infobar-style-zz1_main2.xml")
				elif config.plugins.KravenFHD.tuner.value == "4-tuner":
					self.appendSkinFile(self.daten + "infobar-style-zz1_main4.xml")
				elif config.plugins.KravenFHD.tuner.value == "8-tuner":
					self.appendSkinFile(self.daten + "infobar-style-zz1_main8.xml")
			elif config.plugins.KravenFHD.InfobarStyle.value == "infobar-style-zz4":
				if config.plugins.KravenFHD.tuner.value == "2-tuner":
					self.appendSkinFile(self.daten + "infobar-style-zz4_main2.xml")
				elif config.plugins.KravenFHD.tuner.value == "4-tuner":
					self.appendSkinFile(self.daten + "infobar-style-zz4_main4.xml")
				elif config.plugins.KravenFHD.tuner.value == "8-tuner":
					self.appendSkinFile(self.daten + "infobar-style-zz4_main8.xml")
			elif config.plugins.KravenFHD.InfobarStyle.value == "infobar-style-zzz1":
				if config.plugins.KravenFHD.tuner.value == "2-tuner":
					self.appendSkinFile(self.daten + "infobar-style-zzz1_main2.xml")
				elif config.plugins.KravenFHD.tuner.value == "4-tuner":
					self.appendSkinFile(self.daten + "infobar-style-zzz1_main4.xml")
				elif config.plugins.KravenFHD.tuner.value == "8-tuner":
					self.appendSkinFile(self.daten + "infobar-style-zzz1_main8.xml")
			else:
				self.appendSkinFile(self.daten + config.plugins.KravenFHD.InfobarStyle.value + "_main.xml")

			### Timeshift_Infobar_top
			if config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-x2","infobar-style-z1"):
				if config.plugins.KravenFHD.IBtop.value == "infobar-x2-z1_top":
					self.appendSkinFile(self.daten + "infobar-x2-z1_top.xml")
				elif config.plugins.KravenFHD.IBtop.value == "infobar-x2-z1_top2":
					self.appendSkinFile(self.daten + "infobar-x2-z1_top2.xml")
				elif config.plugins.KravenFHD.IBtop.value == "infobar-x2-z1_top3":
					self.appendSkinFile(self.daten + "infobar-x2-z1_top3.xml")

			### Timeshift_system-info
			self.appendSkinFile(self.daten + config.plugins.KravenFHD.SystemInfo.value + ".xml")

			### Timeshift_weather-style
			if self.actWeatherstyle != "netatmobar":
				self.appendSkinFile(self.daten + self.actWeatherstyle + ".xml")

			### Timeshift_end
			self.appendSkinFile(self.daten + "timeshift-end.xml")

			### InfobarTunerState
			if self.actWeatherstyle in ("weather-big","weather-left","netatmobar"):
				if config.plugins.KravenFHD.SystemInfo.value == "systeminfo-bigsat":
					self.appendSkinFile(self.daten + "infobartunerstate-low.xml")
				else:
					self.appendSkinFile(self.daten + "infobartunerstate-mid.xml")
			else:
				self.appendSkinFile(self.daten + "infobartunerstate-high.xml")

		elif config.plugins.KravenFHD.IBStyle.value == "box":
			if config.plugins.KravenFHD.InfobarBoxColor.value == "gradient":
				self.skinSearchAndReplace.append(['<constant-widget name="timeshift-bg"/>', '<constant-widget name="timeshift-bg-box2"/>'])
				self.skinSearchAndReplace.append(['<constant-widget name="ibts-bg"/>', '<constant-widget name="ibts-bg-box2"/>'])
				self.skinSearchAndReplace.append(['<constant-widget name="autoresolution-bg"/>', '<constant-widget name="autoresolution-bg-box2"/>'])
			elif config.plugins.KravenFHD.InfobarBoxColor.value == "texture":
				self.skinSearchAndReplace.append(['<constant-widget name="timeshift-bg"/>', '<constant-widget name="timeshift-bg-texture"/>'])
				self.skinSearchAndReplace.append(['<constant-widget name="ibts-bg"/>', '<constant-widget name="ibts-bg-texture"/>'])
				self.skinSearchAndReplace.append(['<constant-widget name="autoresolution-bg"/>', '<constant-widget name="autoresolution-bg-texture"/>'])
			self.appendSkinFile(self.daten + "timeshift-ibts-ar.xml")

		### Players
		self.appendSkinFile(self.daten + "player-movie.xml")
		self.appendSkinFile(self.daten + config.plugins.KravenFHD.PlayerClock.value + ".xml")
		self.appendSkinFile(self.daten + "screen_end.xml")
		self.appendSkinFile(self.daten + "player-emc.xml")
		self.appendSkinFile(self.daten + config.plugins.KravenFHD.PlayerClock.value + ".xml")
		self.appendSkinFile(self.daten + "screen_end.xml")

		### PermanentClock
		if config.plugins.KravenFHD.PermanentClock.value == "permanentclock-infobar-small":
			self.skinSearchAndReplace.append(['backgroundColor="KravenIBbg" name="PermanentClockScreen" size="180,45"', 'backgroundColor="KravenIBbg" name="PermanentClockScreen" size="120,30"'])
			self.skinSearchAndReplace.append(['<constant-widget name="permanentclock-infobar-big"/>', '<constant-widget name="permanentclock-infobar-small"/>'])
		elif config.plugins.KravenFHD.PermanentClock.value == "permanentclock-global-big":
			self.skinSearchAndReplace.append(['backgroundColor="KravenIBbg" name="PermanentClockScreen" size="180,45"', 'backgroundColor="Kravenbg" name="PermanentClockScreen" size="180,45"'])
			self.skinSearchAndReplace.append(['<constant-widget name="permanentclock-infobar-big"/>', '<constant-widget name="permanentclock-global-big"/>'])
		elif config.plugins.KravenFHD.PermanentClock.value == "permanentclock-global-small":
			self.skinSearchAndReplace.append(['backgroundColor="KravenIBbg" name="PermanentClockScreen" size="180,45"', 'backgroundColor="Kravenbg" name="PermanentClockScreen" size="120,30"'])
			self.skinSearchAndReplace.append(['<constant-widget name="permanentclock-infobar-big"/>', '<constant-widget name="permanentclock-global-small"/>'])
		elif config.plugins.KravenFHD.PermanentClock.value == "permanentclock-transparent-big":
			self.skinSearchAndReplace.append(['backgroundColor="KravenIBbg" name="PermanentClockScreen" size="180,45"', 'backgroundColor="transparent" name="PermanentClockScreen" size="180,45"'])
			self.skinSearchAndReplace.append(['<constant-widget name="permanentclock-infobar-big"/>', '<constant-widget name="permanentclock-transparent-big"/>'])
		elif config.plugins.KravenFHD.PermanentClock.value == "permanentclock-transparent-small":
			self.skinSearchAndReplace.append(['backgroundColor="KravenIBbg" name="PermanentClockScreen" size="180,45"', 'backgroundColor="transparent" name="PermanentClockScreen" size="120,30"'])
			self.skinSearchAndReplace.append(['<constant-widget name="permanentclock-infobar-big"/>', '<constant-widget name="permanentclock-transparent-small"/>'])

		### Plugins
		self.appendSkinFile(self.daten + "plugins.xml")

		### MSNWeatherPlugin XML
		if self.E2DistroVersion in ("openatv","teamblue"):
			if fileExists("/usr/lib/enigma2/python/Components/Converter/MSNWeather.pyo"):
				self.appendSkinFile(self.daten + "MSNWeatherPlugin.xml")
				if self.InternetAvailable and not fileExists("/usr/share/enigma2/KravenFHD/msn_weather_icons/1.png"):
					console4 = eConsoleAppContainer()
					console4.execute("wget -q http://picons.mynonpublic.com/msn-icon.tar.gz -O /tmp/msn-icon.tar.gz; tar xf /tmp/msn-icon.tar.gz -C /usr/share/enigma2/KravenFHD/")
			else:
				self.appendSkinFile(self.daten + "MSNWeatherPlugin2.xml")

		### NetatmoBar
		if self.InternetAvailable:
			if config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-x2","infobar-style-z1"):
				if fileExists("/usr/lib/enigma2/python/Plugins/Extensions/Netatmo/plugin.py"):
					if config.plugins.KravenFHD.WeatherStyle3.value == "netatmobar":
						self.appendSkinFile(self.daten + "netatmobar.xml")

		### EMC (Event-Description) Font-Size
		if config.plugins.KravenFHD.EMCStyle.value in ("emc-bigcover","emc-minitv"):
			if config.plugins.KravenFHD.EMCEPGSize.value == "big":
				self.skinSearchAndReplace.append(['<constant-widget name="emcmbc33"/>', '<constant-widget name="emcmbc36"/>'])
		elif config.plugins.KravenFHD.EMCStyle.value in ("emc-bigcover2","emc-minitv2"):
			if config.plugins.KravenFHD.EMCEPGSize.value == "big":
				self.skinSearchAndReplace.append(['<constant-widget name="emcm2bc233"/>', '<constant-widget name="emcm2bc236"/>'])
		elif config.plugins.KravenFHD.EMCStyle.value == "emc-nocover":
			if config.plugins.KravenFHD.EMCEPGSize.value == "big":
				self.skinSearchAndReplace.append(['<constant-widget name="emcnc33"/>', '<constant-widget name="emcnc36"/>'])
		elif config.plugins.KravenFHD.EMCStyle.value == "emc-nocover2":
			if config.plugins.KravenFHD.EMCEPGSize.value == "big":
				self.skinSearchAndReplace.append(['<constant-widget name="emcnc233"/>', '<constant-widget name="emcnc236"/>'])
		elif config.plugins.KravenFHD.EMCStyle.value == "emc-smallcover":
			if config.plugins.KravenFHD.EMCEPGSize.value == "big":
				self.skinSearchAndReplace.append(['<constant-widget name="emcsc33"/>', '<constant-widget name="emcsc36"/>'])
		elif config.plugins.KravenFHD.EMCStyle.value == "emc-smallcover2":
			if config.plugins.KravenFHD.EMCEPGSize.value == "big":
				self.skinSearchAndReplace.append(['<constant-widget name="emcsc233"/>', '<constant-widget name="emcsc236"/>'])
		elif config.plugins.KravenFHD.EMCStyle.value == "emc-verybigcover":
			if config.plugins.KravenFHD.EMCEPGSize.value == "big":
				self.skinSearchAndReplace.append(['<constant-widget name="emcvbc33"/>', '<constant-widget name="emcvbc36"/>'])
		elif config.plugins.KravenFHD.EMCStyle.value == "emc-verybigcover2":
			if config.plugins.KravenFHD.EMCEPGSize.value == "big":
				self.skinSearchAndReplace.append(['<constant-widget name="emcvbc233"/>', '<constant-widget name="emcvbc236"/>'])

		### EMC (MovieList) Font-Colors
		self.skinSearchAndReplace.append(['UnwatchedColor="unwatched"', 'UnwatchedColor="#00' + config.plugins.KravenFHD.UnwatchedColor.value + '"'])
		self.skinSearchAndReplace.append(['WatchingColor="watching"', 'WatchingColor="#00' + config.plugins.KravenFHD.WatchingColor.value + '"'])
		self.skinSearchAndReplace.append(['FinishedColor="finished"', 'FinishedColor="#00' + config.plugins.KravenFHD.FinishedColor.value + '"'])

		### EMC
		self.appendSkinFile(self.daten + config.plugins.KravenFHD.EMCStyle.value + ".xml")

		### NumberZapExt
		self.appendSkinFile(self.daten + config.plugins.KravenFHD.NumberZapExt.value + ".xml")
		if self.E2DistroVersion in ("VTi","openatv") and not config.plugins.KravenFHD.NumberZapExt.value == "none":
			config.usage.numberzap_show_picon.value = True
			config.usage.numberzap_show_picon.save()
			config.usage.numberzap_show_servicename.value = True
			config.usage.numberzap_show_servicename.save()

		### PVRState
		if config.plugins.KravenFHD.IBStyle.value == "box":
			if config.plugins.KravenFHD.InfobarBoxColor.value == "gradient":
				if config.plugins.KravenFHD.PVRState.value == "pvrstate-center-big":
					self.skinSearchAndReplace.append(['<constant-widget name="pvrstate-bg"/>', '<constant-widget name="pvrstate-bg-box2"/>'])
				else:
					self.skinSearchAndReplace.append(['<constant-widget name="pvrstate2-bg"/>', '<constant-widget name="pvrstate2-bg-box2"/>'])
			elif config.plugins.KravenFHD.InfobarBoxColor.value == "texture":
				if config.plugins.KravenFHD.PVRState.value == "pvrstate-center-big":
					self.skinSearchAndReplace.append(['<constant-widget name="pvrstate-bg"/>', '<constant-widget name="pvrstate-bg-texture"/>'])
				else:
					self.skinSearchAndReplace.append(['<constant-widget name="pvrstate2-bg"/>', '<constant-widget name="pvrstate2-bg-texture"/>'])
		self.appendSkinFile(self.daten + config.plugins.KravenFHD.PVRState.value + ".xml")

		### SplitScreen
		if self.E2DistroVersion == "VTi":
			self.appendSkinFile(self.daten + config.plugins.KravenFHD.SplitScreen.value + ".xml")

		### FileCommander
		if self.E2DistroVersion == "openatv":
			self.appendSkinFile(self.daten + config.plugins.KravenFHD.FileCommander.value + ".xml")

		### TimerEditScreen
		if self.E2DistroVersion == "VTi":
			self.appendSkinFile(self.daten + config.plugins.KravenFHD.TimerEditScreen.value + ".xml")
		elif self.E2DistroVersion in ("openatv","teamblue"):
			self.appendSkinFile(self.daten + "timer-openatv.xml")

		### TimerListStyle
		if self.E2DistroVersion == "VTi":
			if config.plugins.KravenFHD.TimerListStyle.value == "timerlist-standard":
				config.usage.timerlist_style.value = False
				config.usage.timerlist_style.save()
			elif config.plugins.KravenFHD.TimerListStyle.value == "timerlist-1":
				config.usage.timerlist_style.value = "1"
				config.usage.timerlist_style.save()
			elif config.plugins.KravenFHD.TimerListStyle.value == "timerlist-2":
				config.usage.timerlist_style.value = "2"
				config.usage.timerlist_style.save()
			elif config.plugins.KravenFHD.TimerListStyle.value == "timerlist-3":
				config.usage.timerlist_style.value = "3"
				config.usage.timerlist_style.save()
			elif config.plugins.KravenFHD.TimerListStyle.value == "timerlist-4":
				config.usage.timerlist_style.value = "4"
				config.usage.timerlist_style.save()
			elif config.plugins.KravenFHD.TimerListStyle.value == "timerlist-5":
				config.usage.timerlist_style.value = "5"
				config.usage.timerlist_style.save()

		### EPGSelection EPGSize
		if config.plugins.KravenFHD.EPGSelectionEPGSize.value == "big":
			self.skinSearchAndReplace.append(['font="Regular;33" foregroundColor="EPGSelection" position="1230,493" size="627,420"', 'font="Regular;36" foregroundColor="KravenFont1" position="1230,493" size="627,414"'])
			self.skinSearchAndReplace.append(['font="Regular;33" foregroundColor="EPGSelection" position="1230,440" size="627,462"', 'font="Regular;36" foregroundColor="KravenFont1" position="1230,440" size="627,460"'])
			self.skinSearchAndReplace.append(['font="Regular;33" foregroundColor="EPGSelection" position="1230,173" size="627,756"', 'font="Regular;36" foregroundColor="KravenFont1" position="1230,173" size="627,736"'])
			self.skinSearchAndReplace.append(['font="Regular;33" foregroundColor="EPGSelection" position="1230,120" size="627,798"', 'font="Regular;36" foregroundColor="KravenFont1" position="1230,120" size="627,782"'])
		else:
			self.skinSearchAndReplace.append(['font="Regular;33" foregroundColor="EPGSelection" position="1230,493" size="627,420"', 'font="Regular;33" foregroundColor="KravenFont1" position="1230,493" size="627,420"'])
			self.skinSearchAndReplace.append(['font="Regular;33" foregroundColor="EPGSelection" position="1230,440" size="627,462"', 'font="Regular;33" foregroundColor="KravenFont1" position="1230,440" size="627,462"'])
			self.skinSearchAndReplace.append(['font="Regular;33" foregroundColor="EPGSelection" position="1230,173" size="627,756"', 'font="Regular;33" foregroundColor="KravenFont1" position="1230,173" size="627,756"'])
			self.skinSearchAndReplace.append(['font="Regular;33" foregroundColor="EPGSelection" position="1230,120" size="627,798"', 'font="Regular;33" foregroundColor="KravenFont1" position="1230,120" size="627,798"'])

		### EPGSelection xml
		if self.E2DistroVersion in ("VTi","openatv"):
			self.appendSkinFile(self.daten + config.plugins.KravenFHD.EPGSelection.value + ".xml")
		elif self.E2DistroVersion == "teamblue":
			self.appendSkinFile(self.daten + config.plugins.KravenFHD.EPGSelection.value + "_teamblue.xml")

		### CoolTVGuide
		self.appendSkinFile(self.daten + config.plugins.KravenFHD.CoolTVGuide.value + ".xml")

		### GraphEPG (Event-Description) Font-Size
		if config.plugins.KravenFHD.GMEDescriptionSize.value == "big":
			self.skinSearchAndReplace.append(['<constant-widget name="GE33"/>', '<constant-widget name="GE36"/>'])
			self.skinSearchAndReplace.append(['<constant-widget name="GEMTR33"/>', '<constant-widget name="GEMTR36"/>'])
			self.skinSearchAndReplace.append(['<constant-widget name="GEMTL33"/>', '<constant-widget name="GEMTL36"/>'])

		### GraphEPG
		if self.E2DistroVersion == "VTi":
			self.appendSkinFile(self.daten + config.plugins.KravenFHD.GraphMultiEPG.value + ".xml")
		elif self.E2DistroVersion == "openatv":
			self.appendSkinFile(self.daten + "graphmultiepg-minitv.xml")
			if config.plugins.KravenFHD.GraphicalEPG.value == "text":
				config.epgselection.graph_type_mode.value = False
				config.epgselection.graph_type_mode.save()
				config.epgselection.graph_pig.value = False
				config.epgselection.graph_pig.save()
			elif config.plugins.KravenFHD.GraphicalEPG.value == "text-minitv":
				config.epgselection.graph_type_mode.value = False
				config.epgselection.graph_type_mode.save()
				config.epgselection.graph_pig.value = True
				config.epgselection.graph_pig.save()
			elif config.plugins.KravenFHD.GraphicalEPG.value == "graphical":
				config.epgselection.graph_type_mode.value = "graphics"
				config.epgselection.graph_type_mode.save()
				config.epgselection.graph_pig.value = False
				config.epgselection.graph_pig.save()
			elif config.plugins.KravenFHD.GraphicalEPG.value == "graphical-minitv":
				config.epgselection.graph_type_mode.value = "graphics"
				config.epgselection.graph_type_mode.save()
				config.epgselection.graph_pig.value = True
				config.epgselection.graph_pig.save()
		elif self.E2DistroVersion == "teamblue":
			self.appendSkinFile(self.daten + config.plugins.KravenFHD.GraphMultiEPG.value + "_teamblue.xml")

		### VerticalEPG
		if self.E2DistroVersion == "VTi":
			self.appendSkinFile(self.daten + config.plugins.KravenFHD.VerticalEPG.value + ".xml")
		elif self.E2DistroVersion == "openatv":
			if config.plugins.KravenFHD.VerticalEPG2.value == "verticalepg-full":
				config.epgselection.vertical_pig.value = False
				config.epgselection.vertical_pig.save()
			elif config.plugins.KravenFHD.VerticalEPG2.value == "verticalepg-minitv3":
				config.epgselection.graph_pig.value = True
				config.epgselection.graph_pig.save()

		### MovieSelection (MovieList) Font-Size - teamblue
		if self.E2DistroVersion == "teamblue":
			self.skinSearchAndReplace.append(['name="MovieList-teamblue"', 'fontName="Regular" fontSizesOriginal="32,30,30" fontSizesCompact="32,30" fontSizesMinimal="32,30" itemHeights="135,81,45" pbarShift="10" pbarHeight="24" pbarLargeWidth="72" partIconeShiftMinimal="10" partIconeShiftCompact="10" partIconeShiftOriginal="10" spaceIconeText="6" iconsWidth="30" trashShift="8" dirShift="8" spaceRight="3" columnsOriginal="300,320" columnsCompactDescription="210,240,270" compactColumn="320" treeDescription="270"'])
		elif self.E2DistroVersion in ("VTi","openatv"):
			self.skinSearchAndReplace.append([' name="MovieList-teamblue" ', ' '])

		### MovieSelection (Event-Description) Font-Size
		if config.plugins.KravenFHD.MovieSelection.value == "movieselection-no-cover":
			if config.plugins.KravenFHD.MovieSelectionEPGSize.value == "big":
				self.skinSearchAndReplace.append(['<constant-widget name="msnc33"/>', '<constant-widget name="msnc36"/>'])
		elif config.plugins.KravenFHD.MovieSelection.value == "movieselection-no-cover2":
			if config.plugins.KravenFHD.MovieSelectionEPGSize.value == "big":
				self.skinSearchAndReplace.append(['<constant-widget name="msnc233"/>', '<constant-widget name="msnc236"/>'])
		elif config.plugins.KravenFHD.MovieSelection.value == "movieselection-small-cover":
			if config.plugins.KravenFHD.MovieSelectionEPGSize.value == "big":
				self.skinSearchAndReplace.append(['<constant-widget name="mssc33"/>', '<constant-widget name="mssc36"/>'])
		elif config.plugins.KravenFHD.MovieSelection.value == "movieselection-big-cover":
			if config.plugins.KravenFHD.MovieSelectionEPGSize.value == "big":
				self.skinSearchAndReplace.append(['<constant-widget name="msbc33"/>', '<constant-widget name="msbc36"/>'])
		elif config.plugins.KravenFHD.MovieSelection.value == "movieselection-minitv":
			if config.plugins.KravenFHD.MovieSelectionEPGSize.value == "big":
				self.skinSearchAndReplace.append(['<constant-widget name="msm33"/>', '<constant-widget name="msm36"/>'])
		elif config.plugins.KravenFHD.MovieSelection.value == "movieselection-minitv-cover":
			if config.plugins.KravenFHD.MovieSelectionEPGSize.value == "big":
				self.skinSearchAndReplace.append(['<constant-widget name="msmc33"/>', '<constant-widget name="msmc36"/>'])

		### MovieSelection
		self.appendSkinFile(self.daten + config.plugins.KravenFHD.MovieSelection.value + ".xml")

		### SerienRecorder
		if config.plugins.KravenFHD.SerienRecorder.value == "serienrecorder":
			self.appendSkinFile(self.daten + config.plugins.KravenFHD.SerienRecorder.value + ".xml")

		### MediaPortal
		if fileExists("/usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins_1080/KravenFHD/skin.xml"):
			console5 = eConsoleAppContainer()
			console5.execute("rm -rf /usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins_1080/KravenFHD/skin.xml")

		if self.E2DistroVersion in ("VTi","openatv"):
			if fileExists("/usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/plugin.py") and config.plugins.KravenFHD.MediaPortal.value == "mediaportal":
				console6 = eConsoleAppContainer()
				if config.plugins.KravenFHD.IBColor.value == "all-screens" and config.plugins.KravenFHD.IconStyle.value == "icons-light" and config.plugins.KravenFHD.IBStyle.value == "grad":
					console6.execute("tar xf /usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/data/MediaPortal.tar.gz -C /usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins_1080/; tar xf /usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/data/MediaPortal_IB_icons-light.tar.gz -C /usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins_1080/KravenFHD/; tar xf /usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/data/Player_IB_icons-light.tar.gz -C /usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins_1080/KravenFHD/simpleplayer/")
				elif config.plugins.KravenFHD.IBColor.value == "all-screens" and config.plugins.KravenFHD.IconStyle.value == "icons-light" and config.plugins.KravenFHD.IBStyle.value == "box":
					console6.execute("tar xf /usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/data/MediaPortal.tar.gz -C /usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins_1080/; tar xf /usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/data/MediaPortal_box_icons-light.tar.gz -C /usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins_1080/KravenFHD/; tar xf /usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/data/Player_box_icons-light.tar.gz -C /usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins_1080/KravenFHD/simpleplayer/")
				elif config.plugins.KravenFHD.IBColor.value == "all-screens" and config.plugins.KravenFHD.IconStyle.value == "icons-dark" and config.plugins.KravenFHD.IBStyle.value == "grad":
					console6.execute("tar xf /usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/data/MediaPortal.tar.gz -C /usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins_1080/; tar xf /usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/data/MediaPortal_IB_icons-dark.tar.gz -C /usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins_1080/KravenFHD/; tar xf /usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/data/Player_IB_icons-dark.tar.gz -C /usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins_1080/KravenFHD/simpleplayer/")
				elif config.plugins.KravenFHD.IBColor.value == "all-screens" and config.plugins.KravenFHD.IconStyle.value == "icons-dark" and config.plugins.KravenFHD.IBStyle.value == "box":
					console6.execute("tar xf /usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/data/MediaPortal.tar.gz -C /usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins_1080/; tar xf /usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/data/MediaPortal_box_icons-dark.tar.gz -C /usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins_1080/KravenFHD/; tar xf /usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/data/Player_box_icons-dark.tar.gz -C /usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins_1080/KravenFHD/simpleplayer/")
				elif config.plugins.KravenFHD.IBColor.value == "only-infobar" and config.plugins.KravenFHD.IconStyle.value == "icons-light" and config.plugins.KravenFHD.IBStyle.value == "grad":
					console6.execute("tar xf /usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/data/MediaPortal.tar.gz -C /usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins_1080/; tar xf /usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/data/Player_IB_icons-light.tar.gz -C /usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins_1080/KravenFHD/simpleplayer/")
				elif config.plugins.KravenFHD.IBColor.value == "only-infobar" and config.plugins.KravenFHD.IconStyle.value == "icons-light" and config.plugins.KravenFHD.IBStyle.value == "box":
					console6.execute("tar xf /usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/data/MediaPortal.tar.gz -C /usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins_1080/; tar xf /usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/data/Player_box_icons-light.tar.gz -C /usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins_1080/KravenFHD/simpleplayer/")
				elif config.plugins.KravenFHD.IBColor.value == "only-infobar" and config.plugins.KravenFHD.IconStyle.value == "icons-dark" and config.plugins.KravenFHD.IBStyle.value == "grad":
					console6.execute("tar xf /usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/data/MediaPortal.tar.gz -C /usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins_1080/; tar xf /usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/data/MediaPortal_icons-dark.tar.gz -C /usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins_1080/KravenFHD/; tar xf /usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/data/Player_IB_icons-dark.tar.gz -C /usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins_1080/KravenFHD/simpleplayer/")
				elif config.plugins.KravenFHD.IBColor.value == "only-infobar" and config.plugins.KravenFHD.IconStyle.value == "icons-dark" and config.plugins.KravenFHD.IBStyle.value == "box":
					console6.execute("tar xf /usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/data/MediaPortal.tar.gz -C /usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins_1080/; tar xf /usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/data/MediaPortal_icons-dark.tar.gz -C /usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins_1080/KravenFHD/; tar xf /usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/data/Player_box_icons-dark.tar.gz -C /usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins_1080/KravenFHD/simpleplayer/")

		elif self.E2DistroVersion == "teamblue":
			if fileExists("/usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/plugin.py") and config.plugins.KravenFHD.MediaPortal.value == "mediaportal":
				console6 = eConsoleAppContainer()
				if config.plugins.KravenFHD.IBColor.value == "all-screens" and config.plugins.KravenFHD.IconStyle.value == "icons-light" and config.plugins.KravenFHD.IBStyle.value == "grad":
					console6.execute("tar xf /usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/data/MediaPortal_teamblue.tar.gz -C /usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins_1080/; tar xf /usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/data/MediaPortal_IB_icons-light_teamblue.tar.gz -C /usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins_1080/KravenFHD/; tar xf /usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/data/Player_IB_icons-light_teamblue.tar.gz -C /usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins_1080/KravenFHD/simpleplayer/")
				elif config.plugins.KravenFHD.IBColor.value == "all-screens" and config.plugins.KravenFHD.IconStyle.value == "icons-light" and config.plugins.KravenFHD.IBStyle.value == "box":
					console6.execute("tar xf /usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/data/MediaPortal_teamblue.tar.gz -C /usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins_1080/; tar xf /usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/data/MediaPortal_box_icons-light_teamblue.tar.gz -C /usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins_1080/KravenFHD/; tar xf /usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/data/Player_box_icons-light_teamblue.tar.gz -C /usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins_1080/KravenFHD/simpleplayer/")
				elif config.plugins.KravenFHD.IBColor.value == "all-screens" and config.plugins.KravenFHD.IconStyle.value == "icons-dark" and config.plugins.KravenFHD.IBStyle.value == "grad":
					console6.execute("tar xf /usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/data/MediaPortal_teamblue.tar.gz -C /usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins_1080/; tar xf /usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/data/MediaPortal_IB_icons-dark_teamblue.tar.gz -C /usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins_1080/KravenFHD/; tar xf /usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/data/Player_IB_icons-dark_teamblue.tar.gz -C /usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins_1080/KravenFHD/simpleplayer/")
				elif config.plugins.KravenFHD.IBColor.value == "all-screens" and config.plugins.KravenFHD.IconStyle.value == "icons-dark" and config.plugins.KravenFHD.IBStyle.value == "box":
					console6.execute("tar xf /usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/data/MediaPortal_teamblue.tar.gz -C /usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins_1080/; tar xf /usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/data/MediaPortal_box_icons-dark_teamblue.tar.gz -C /usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins_1080/KravenFHD/; tar xf /usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/data/Player_box_icons-dark_teamblue.tar.gz -C /usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins_1080/KravenFHD/simpleplayer/")
				elif config.plugins.KravenFHD.IBColor.value == "only-infobar" and config.plugins.KravenFHD.IconStyle.value == "icons-light" and config.plugins.KravenFHD.IBStyle.value == "grad":
					console6.execute("tar xf /usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/data/MediaPortal_teamblue.tar.gz -C /usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins_1080/; tar xf /usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/data/Player_IB_icons-light_teamblue.tar.gz -C /usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins_1080/KravenFHD/simpleplayer/")
				elif config.plugins.KravenFHD.IBColor.value == "only-infobar" and config.plugins.KravenFHD.IconStyle.value == "icons-light" and config.plugins.KravenFHD.IBStyle.value == "box":
					console6.execute("tar xf /usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/data/MediaPortal_teamblue.tar.gz -C /usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins_1080/; tar xf /usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/data/Player_box_icons-light_teamblue.tar.gz -C /usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins_1080/KravenFHD/simpleplayer/")
				elif config.plugins.KravenFHD.IBColor.value == "only-infobar" and config.plugins.KravenFHD.IconStyle.value == "icons-dark" and config.plugins.KravenFHD.IBStyle.value == "grad":
					console6.execute("tar xf /usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/data/MediaPortal_teamblue.tar.gz -C /usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins_1080/; tar xf /usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/data/MediaPortal_icons-dark_teamblue.tar.gz -C /usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins_1080/KravenFHD/; tar xf /usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/data/Player_IB_icons-dark_teamblue.tar.gz -C /usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins_1080/KravenFHD/simpleplayer/")
				elif config.plugins.KravenFHD.IBColor.value == "only-infobar" and config.plugins.KravenFHD.IconStyle.value == "icons-dark" and config.plugins.KravenFHD.IBStyle.value == "box":
					console6.execute("tar xf /usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/data/MediaPortal_teamblue.tar.gz -C /usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins_1080/; tar xf /usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/data/MediaPortal_icons-dark_teamblue.tar.gz -C /usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins_1080/KravenFHD/; tar xf /usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/data/Player_box_icons-dark_teamblue.tar.gz -C /usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins_1080/KravenFHD/simpleplayer/")

		if fileExists("/usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins_1080/KravenFHD/MP_skin.xml") and not config.plugins.KravenFHD.MediaPortal.value == "mediaportal":
			console7 = eConsoleAppContainer()
			console7.execute("rm -rf /usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins_1080/KravenFHD")

		### vti - openatv - teamblue
		if self.E2DistroVersion == "VTi":
			self.appendSkinFile(self.daten + "vti.xml")
		elif self.E2DistroVersion == "openatv":
			self.appendSkinFile(self.daten + "openatv.xml")
		elif self.E2DistroVersion == "teamblue":
			self.appendSkinFile(self.daten + "teamblue.xml")

		### skin-user
		try:
			self.appendSkinFile(self.daten + "skin-user.xml")
		except:
			pass
		### skin-end
		self.appendSkinFile(self.daten + "skin-end.xml")

		xFile = open(self.dateiTMP, "w")
		for xx in self.skin_lines:
			xFile.writelines(xx)
		xFile.close()

		move(self.dateiTMP, self.datei)

		### Menu icons download - we do it here to give it some time
		if self.InternetAvailable:
			if config.plugins.KravenFHD.Logo.value in ("metrix-icons","minitv-metrix-icons"):
				self.installIcons(config.plugins.KravenFHD.MenuIcons.value)

		### Get weather data to make sure the helper config values are not empty
		self.get_weather_data()

		# Make ibar graphics
		if config.plugins.KravenFHD.BackgroundColor.value == "gradient":
			self.makeBGGradientpng()
		elif config.plugins.KravenFHD.BackgroundColor.value == "texture":
			self.makeBGTexturepng()

		if config.plugins.KravenFHD.IBStyle.value == "grad":
			if config.plugins.KravenFHD.InfobarGradientColor.value == "texture":
				self.makeIbarTextureGradientpng(config.plugins.KravenFHD.InfobarTexture.value,config.plugins.KravenFHD.InfobarColorTrans.value) # ibars
				self.makeRectTexturepng(config.plugins.KravenFHD.InfobarTexture.value, config.plugins.KravenFHD.InfobarColorTrans.value, 1358, 255, "shift") # timeshift bar
				self.makeRectTexturepng(config.plugins.KravenFHD.InfobarTexture.value, config.plugins.KravenFHD.InfobarColorTrans.value, 600, 300, "wsmall") # weather small
				if config.plugins.KravenFHD.SystemInfo.value == "systeminfo-small":
					self.makeRectTexturepng(config.plugins.KravenFHD.InfobarTexture.value, config.plugins.KravenFHD.InfobarColorTrans.value, 600, 277, "info") # sysinfo small
				elif config.plugins.KravenFHD.SystemInfo.value == "systeminfo-big":
					self.makeRectTexturepng(config.plugins.KravenFHD.InfobarTexture.value, config.plugins.KravenFHD.InfobarColorTrans.value, 600, 412, "info") # sysinfo big
				else:
					self.makeRectTexturepng(config.plugins.KravenFHD.InfobarTexture.value, config.plugins.KravenFHD.InfobarColorTrans.value, 600, 562, "info") # sysinfo bigsat
			else:
				self.makeIbarColorGradientpng(self.skincolorinfobarcolor, config.plugins.KravenFHD.InfobarColorTrans.value) # ibars
				self.makeRectColorpng(self.skincolorinfobarcolor, config.plugins.KravenFHD.InfobarColorTrans.value, 1358, 255, "shift") # timeshift bar
				self.makeRectColorpng(self.skincolorinfobarcolor, config.plugins.KravenFHD.InfobarColorTrans.value, 600, 300, "wsmall") # weather small
				if config.plugins.KravenFHD.SystemInfo.value == "systeminfo-small":
					self.makeRectColorpng(self.skincolorinfobarcolor, config.plugins.KravenFHD.InfobarColorTrans.value, 600, 277, "info") # sysinfo small
				elif config.plugins.KravenFHD.SystemInfo.value == "systeminfo-big":
					self.makeRectColorpng(self.skincolorinfobarcolor, config.plugins.KravenFHD.InfobarColorTrans.value, 600, 412, "info") # sysinfo big
				else:
					self.makeRectColorpng(self.skincolorinfobarcolor, config.plugins.KravenFHD.InfobarColorTrans.value, 600, 562, "info") # sysinfo bigsat
		elif config.plugins.KravenFHD.IBStyle.value == "box":
			if config.plugins.KravenFHD.InfobarBoxColor.value == "gradient":
				self.makeIBGradientpng()
			elif config.plugins.KravenFHD.InfobarBoxColor.value == "texture":
				self.makeIBTexturepng()

		if config.plugins.KravenFHD.SerienRecorder.value == "serienrecorder":
			self.makeSRpng(self.skincolorbackgroundcolor) # serienrecorder

		# Thats it
		self.restart()

	def restart(self):
		configfile.save()
		restartbox = self.session.openWithCallback(self.restartGUI,MessageBox,_("GUI needs a restart to apply a new skin.\nDo you want to Restart the GUI now?"), MessageBox.TYPE_YESNO)
		restartbox.setTitle(_("Restart GUI"))

	def appendSkinFile(self, appendFileName, skinPartSearchAndReplace=None):
		"""
		add skin file to main skin content

		appendFileName:
		 xml skin-part to add

		skinPartSearchAndReplace:
		 (optional) a list of search and replace arrays. first element, search, second for replace
		"""
		skFile = open(appendFileName, "r")
		file_lines = skFile.readlines()
		skFile.close()

		tmpSearchAndReplace = []

		if skinPartSearchAndReplace is not None:
			tmpSearchAndReplace = self.skinSearchAndReplace + skinPartSearchAndReplace
		else:
			tmpSearchAndReplace = self.skinSearchAndReplace

		for skinLine in file_lines:
			for item in tmpSearchAndReplace:
				skinLine = skinLine.replace(item[0], item[1])
			self.skin_lines.append(skinLine)

	def restartGUI(self, answer):
		if answer is True:
			config.skin.primary_skin.setValue("KravenFHD/skin.xml")
			config.skin.save()
			configfile.save()
			self.session.open(TryQuitMainloop, 3)
		else:
			self.close()

	def exit(self):
		askExit = self.session.openWithCallback(self.doExit,MessageBox,_("Do you really want to exit without saving?"), MessageBox.TYPE_YESNO)
		askExit.setTitle(_("Exit"))

	def doExit(self,answer):
		if answer is True:
			for x in self["config"].list:
				if len(x) > 1:
						x[1].cancel()
				else:
						pass
			self.close()
		else:
			self.mylist()

	def getBoxName(self):
		if fileExists("/proc/stb/info/vumodel"):
			file = open('/proc/stb/info/vumodel', 'r')
			boxname = file.readline().strip()
			file.close()
			return boxname
		else:
			try:
				from boxbranding import getMachineName
				return getMachineName()
			except ImportError:
				return "unknown"

	def getE2DistroVersion(self):
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

	def getInternetAvailable(self):
		import ping
		r = ping.doOne("8.8.8.8",1.5)
		if r != None and r <= 1.5:
			return True
		else:
			return False

	def getUserMenuIconsAvailable(self):
		userpath="/usr/share/enigma2/Kraven-user-icons"
		if path.exists(userpath) and any(File.endswith(".png") for File in listdir(userpath)):
			return True
		else:
			return False

	def reset(self):
		askReset = self.session.openWithCallback(self.doReset,MessageBox,_("Do you really want to reset all values to the selected default profile?"), MessageBox.TYPE_YESNO)
		askReset.setTitle(_("Reset profile"))

	def doReset(self,answer):
		if answer is True:
			if config.plugins.KravenFHD.defaultProfile.value == "default":
				for name in config.plugins.KravenFHD.dict():
					if not name in ("customProfile","DebugNames"):
						item=(getattr(config.plugins.KravenFHD,name))
						item.value=item.default
			else:
				self.loadProfile(loadDefault=True)
		self.mylist()

	def showColor(self,actcolor):
		c = self["Canvas"]
		c.fill(0,0,460,259,actcolor)
		c.flush()

	def showGradient(self,color1,color2):
		width=460
		height=259
		color1=color1[-6:]
		r1=int(color1[0:2],16)
		g1=int(color1[2:4],16)
		b1=int(color1[4:6],16)
		color2=color2[-6:]
		r2=int(color2[0:2],16)
		g2=int(color2[2:4],16)
		b2=int(color2[4:6],16)
		c = self["Canvas"]
		if color1!=color2:
			for pos in range(0,height):
				p=pos/float(height)
				r=r2*p+r1*(1-p)
				g=g2*p+g1*(1-p)
				b=b2*p+b1*(1-p)
				c.fill(0,pos,width,1,self.RGB(int(r),int(g),int(b)))
		else:
			c.fill(0,0,width,height,self.RGB(int(r1),int(g1),int(b1)))
		c.flush()

	def showText(self,fontsize,text):
		from enigma import gFont,RT_HALIGN_CENTER,RT_VALIGN_CENTER
		c = self["Canvas"]
		c.fill(0,0,460,259,self.RGB(0,0,0))
		c.writeText(0,0,460,259,self.RGB(255,255,255),self.RGB(0,0,0),gFont("Regular",fontsize),text,RT_HALIGN_CENTER+RT_VALIGN_CENTER)
		c.flush()

	def loadProfile(self,loadDefault=False):
		if loadDefault:
			profile=config.plugins.KravenFHD.defaultProfile.value
			fname=self.profiles+"kravenfhd_default_"+profile
		else:
			profile=config.plugins.KravenFHD.customProfile.value
			fname=self.profiles+"kravenfhd_profile_"+profile
		if profile and fileExists(fname):
			print ("KravenPlugin: Load profile "+fname)
			
			# assume colors are not copied yet
			config.plugins.KravenFHD.OldColorsCopied.value=False
			
			pFile=open(fname,"r")
			for line in pFile:
				try:
					line=line.split("|")
					name=line[0]
					value=line[1]
					type=line[2].strip('\n')
					if not (name in ("customProfile","DebugNames","weather_search_over","weather_owm_latlon","weather_accu_latlon","weather_accu_id","weather_accu_apikey","weather_foundcity","weather_cityname","weather_language","weather_server") or (loadDefault and name == "defaultProfile")):
						# fix for changed value "gradient"/"grad"
						if name=="IBStyle" and value=="gradient":
							value="grad"
						# fix for changed name "InfobarColor"/"InfobarGradientColor"
						if name=="InfobarColor":
							config.plugins.KravenFHD.InfobarGradientColor.value=value
						if type == "<type 'int'>":
							getattr(config.plugins.KravenFHD,name).value=int(value)
						elif type == "<type 'hex'>":
							getattr(config.plugins.KravenFHD,name).value=hex(value)
						elif type == "<type 'list'>":
							getattr(config.plugins.KravenFHD,name).value=eval(value)
						else:
							getattr(config.plugins.KravenFHD,name).value=str(value)
				except:
					pass
			pFile.close()

			# copy old colors
			if config.plugins.KravenFHD.OldColorsCopied.value==False:
				self.copyOldColors()
				config.plugins.KravenFHD.OldColorsCopied.value=True

			# fix possible inconsistencies between boxes
			if self.E2DistroVersion == "VTi":
				if SystemInfo.get("NumVideoDecoders",1)>1:
					if config.plugins.KravenFHD.ChannelSelectionStyle.value!=config.plugins.KravenFHD.ChannelSelectionStyle.default:
						config.plugins.KravenFHD.ChannelSelectionStyle2.value=config.plugins.KravenFHD.ChannelSelectionStyle.value
						config.plugins.KravenFHD.ChannelSelectionStyle.value=config.plugins.KravenFHD.ChannelSelectionStyle.default
				else:
					if config.plugins.KravenFHD.ChannelSelectionStyle2.value!=config.plugins.KravenFHD.ChannelSelectionStyle2.default:
						if config.plugins.KravenFHD.ChannelSelectionStyle2.value in ("channelselection-style-minitv33","channelselection-style-minitv2","channelselection-style-minitv22"):
							config.plugins.KravenFHD.ChannelSelectionStyle.value="channelselection-style-minitv3"
						elif config.plugins.KravenFHD.ChannelSelectionStyle2.value == "channelselection-style-nobile-minitv33":
							config.plugins.KravenFHD.ChannelSelectionStyle.value="channelselection-style-nobile-minitv3"
						else:
							config.plugins.KravenFHD.ChannelSelectionStyle.value=config.plugins.KravenFHD.ChannelSelectionStyle2.value
						config.plugins.KravenFHD.ChannelSelectionStyle2.value=config.plugins.KravenFHD.ChannelSelectionStyle2.default
				if not fileExists("/usr/lib/enigma2/python/Plugins/Extensions/Netatmo/plugin.py") and config.plugins.KravenFHD.WeatherStyle3.value=="netatmobar":
					config.plugins.KravenFHD.WeatherStyle3.value=config.plugins.KravenFHD.WeatherStyle3.default
		elif not loadDefault:
			print ("KravenPlugin: Create profile "+fname)
			self.saveProfile(msg=False)

	def saveProfile(self,msg=True):
		profile=config.plugins.KravenFHD.customProfile.value
		if profile:
			try:
				fname=self.profiles+"kravenfhd_profile_"+profile
				print ("KravenPlugin: Save profile "+fname)
				pFile=open(fname,"w")
				for name in config.plugins.KravenFHD.dict():
					if not name in ("customProfile","DebugNames","weather_owm_latlon","weather_accu_latlon","weather_accu_id","weather_accu_apikey","weather_foundcity","weather_cityname","weather_language","weather_server"):
						value=getattr(config.plugins.KravenFHD,name).value
						pFile.writelines(name+"|"+str(value)+"|"+str(type(value))+"\n")
				pFile.close()
				if msg:
					self.session.open(MessageBox,_("Profile ")+str(profile)+_(" saved successfully."), MessageBox.TYPE_INFO, timeout=5)
			except:
				self.session.open(MessageBox,_("Profile ")+str(profile)+_(" could not be saved!"), MessageBox.TYPE_INFO, timeout=15)

	def installIcons(self,author):

		if self.InternetAvailable==False: 
			return

		if self.E2DistroVersion == "VTi":
			print "VTI Image found. Use VTI Server"
			pathname="http://coolskins.de/downloads/kraven/"
		elif self.E2DistroVersion == "openatv":
			print "ATV Image found. Use ATV Server"
			pathname="http://picons.mynonpublic.com/"
		elif self.E2DistroVersion == "teamblue":
			print "teamBlue Image found. Use ATV Server"
			pathname="http://picons.mynonpublic.com/"
		else:
			print "No Icons found. Aborted"
			return

		instname="/usr/share/enigma2/Kraven-menu-icons/iconpackname"
		versname="Kraven-Menu-Icons-by-"+author+".packname"
		
		# Read iconpack version on box
		packinstalled = "not installed"
		if fileExists(instname):
			pFile=open(instname,"r")
			for line in pFile:
				packinstalled=line.strip('\n')
			pFile.close()
		print ("KravenPlugin: Iconpack on box is "+packinstalled)
		
		# Read iconpack version on server
		packonserver = "unknown"
		fullversname=pathname+versname
		sub=subprocess.Popen("wget -q "+fullversname+" -O /tmp/"+versname,shell=True)
		sub.wait()
		if fileExists("/tmp/"+versname):
			pFile=open("/tmp/"+versname,"r")
			for line in pFile:
				packonserver=line.strip('\n')
			pFile.close()
			popen("rm /tmp/"+versname)
			print ("KravenPlugin: Iconpack on server is "+packonserver)

			# Download an install icon pack, if needed
			if packinstalled != packonserver:
				packname=packonserver
				fullpackname=pathname+packname
				sub=subprocess.Popen("rm -rf /usr/share/enigma2/Kraven-menu-icons/*.*; rm -rf /usr/share/enigma2/Kraven-menu-icons; wget -q "+fullpackname+" -O /tmp/"+packname+"; tar xf /tmp/"+packname+" -C /usr/share/enigma2/",shell=True)
				sub.wait()
				popen("rm /tmp/"+packname)
				print ("KravenPlugin: Installed iconpack "+fullpackname)
			else:
				print ("KravenPlugin: No need to install other iconpack")

	def copyOldColors(self):
		# list colors with possible "gradient","texture"
		if config.plugins.KravenFHD.BackgroundColor.value in ("gradient","texture"):
			config.plugins.KravenFHD.BackgroundListColor.value = config.plugins.KravenFHD.BackgroundColor.value
		else:
			config.plugins.KravenFHD.BackgroundListColor.value = config.plugins.KravenFHD.BackgroundColor.value[-6:]
		if config.plugins.KravenFHD.InfobarBoxColor.value in ("gradient","texture"):
			config.plugins.KravenFHD.InfobarBoxListColor.value = config.plugins.KravenFHD.InfobarBoxColor.value
		else:
			config.plugins.KravenFHD.InfobarBoxListColor.value = config.plugins.KravenFHD.InfobarBoxColor.value[-6:]
		if config.plugins.KravenFHD.InfobarGradientColor.value in ("gradient","texture"):
			config.plugins.KravenFHD.InfobarGradientListColor.value = config.plugins.KravenFHD.InfobarGradientColor.value
		else:
			config.plugins.KravenFHD.InfobarGradientListColor.value = config.plugins.KravenFHD.InfobarGradientColor.value[-6:]
		# list colors
		config.plugins.KravenFHD.SelectionBackgroundList.value = config.plugins.KravenFHD.SelectionBackground.value[-6:]
		config.plugins.KravenFHD.SelectionBorderList.value = config.plugins.KravenFHD.SelectionBorder.value[-6:]
		config.plugins.KravenFHD.Font1List.value = config.plugins.KravenFHD.Font1.value[-6:]
		config.plugins.KravenFHD.Font2List.value = config.plugins.KravenFHD.Font2.value[-6:]
		config.plugins.KravenFHD.IBFont1List.value = config.plugins.KravenFHD.IBFont1.value[-6:]
		config.plugins.KravenFHD.IBFont2List.value = config.plugins.KravenFHD.IBFont2.value[-6:]
		config.plugins.KravenFHD.BackgroundGradientListColorPrimary.value = config.plugins.KravenFHD.BackgroundGradientColorPrimary.value[-6:]
		config.plugins.KravenFHD.BackgroundGradientListColorSecondary.value = config.plugins.KravenFHD.BackgroundGradientColorSecondary.value[-6:]
		config.plugins.KravenFHD.InfobarGradientListColorPrimary.value = config.plugins.KravenFHD.InfobarGradientColorPrimary.value[-6:]
		config.plugins.KravenFHD.InfobarGradientListColorSecondary.value = config.plugins.KravenFHD.InfobarGradientColorSecondary.value[-6:]
		config.plugins.KravenFHD.BackgroundAlternateListColor.value = config.plugins.KravenFHD.BackgroundAlternateColor.value[-6:]
		config.plugins.KravenFHD.InfobarAlternateListColor.value = config.plugins.KravenFHD.InfobarAlternateColor.value[-6:]
		config.plugins.KravenFHD.MarkedFontList.value = config.plugins.KravenFHD.MarkedFont.value[-6:]
		config.plugins.KravenFHD.PermanentClockFontList.value = config.plugins.KravenFHD.PermanentClockFont.value[-6:]
		config.plugins.KravenFHD.SelectionFontList.value = config.plugins.KravenFHD.SelectionFont.value[-6:]
		config.plugins.KravenFHD.ECMFontList.value = config.plugins.KravenFHD.ECMFont.value[-6:]
		config.plugins.KravenFHD.ChannelnameFontList.value = config.plugins.KravenFHD.ChannelnameFont.value[-6:]
		config.plugins.KravenFHD.PrimetimeFontList.value = config.plugins.KravenFHD.PrimetimeFont.value[-6:]
		config.plugins.KravenFHD.ButtonTextList.value = config.plugins.KravenFHD.ButtonText.value[-6:]
		config.plugins.KravenFHD.AndroidList.value = config.plugins.KravenFHD.Android.value[-6:]
		config.plugins.KravenFHD.BorderList.value = config.plugins.KravenFHD.Border.value[-6:]
		config.plugins.KravenFHD.ProgressList.value = config.plugins.KravenFHD.Progress.value[-6:]
		config.plugins.KravenFHD.LineList.value = config.plugins.KravenFHD.Line.value[-6:]
		config.plugins.KravenFHD.IBLineList.value = config.plugins.KravenFHD.IBLine.value[-6:]
		config.plugins.KravenFHD.MiniTVBorderList.value = config.plugins.KravenFHD.MiniTVBorder.value[-6:]
		config.plugins.KravenFHD.ChannelSelectionServiceNAList.value = config.plugins.KravenFHD.ChannelSelectionServiceNA.value[-6:]
		config.plugins.KravenFHD.NZBorderList.value = config.plugins.KravenFHD.NZBorder.value[-6:]
		config.plugins.KravenFHD.GMErunningbgList.value = config.plugins.KravenFHD.GMErunningbg.value[-6:]
		config.plugins.KravenFHD.GMEBorderList.value = config.plugins.KravenFHD.GMEBorder.value[-6:]
		config.plugins.KravenFHD.VEPGBorderList.value = config.plugins.KravenFHD.VEPGBorder.value[-6:]
		config.plugins.KravenFHD.EMCSelectionBackgroundList.value = config.plugins.KravenFHD.EMCSelectionBackground.value[-6:]
		config.plugins.KravenFHD.EMCSelectionFontList.value = config.plugins.KravenFHD.EMCSelectionFont.value[-6:]
		config.plugins.KravenFHD.Android2List.value = config.plugins.KravenFHD.Android2.value[-6:]
		config.plugins.KravenFHD.UnwatchedColorList.value = config.plugins.KravenFHD.UnwatchedColor.value[-6:]
		config.plugins.KravenFHD.WatchingColorList.value = config.plugins.KravenFHD.WatchingColor.value[-6:]
		config.plugins.KravenFHD.FinishedColorList.value = config.plugins.KravenFHD.FinishedColor.value[-6:]
		# self colors
		config.plugins.KravenFHD.BackgroundSelfColor.value = str(hex(config.plugins.KravenFHD.BackgroundSelfColorR.value)[2:4]).zfill(2) + str(hex(config.plugins.KravenFHD.BackgroundSelfColorG.value)[2:4]).zfill(2) + str(hex(config.plugins.KravenFHD.BackgroundSelfColorB.value)[2:4]).zfill(2)
		config.plugins.KravenFHD.InfobarBoxSelfColor.value = str(hex(config.plugins.KravenFHD.InfobarSelfColorR.value)[2:4]).zfill(2) + str(hex(config.plugins.KravenFHD.InfobarSelfColorG.value)[2:4]).zfill(2) + str(hex(config.plugins.KravenFHD.InfobarSelfColorB.value)[2:4]).zfill(2)
		config.plugins.KravenFHD.InfobarGradientSelfColor.value = str(hex(config.plugins.KravenFHD.InfobarSelfColorR.value)[2:4]).zfill(2) + str(hex(config.plugins.KravenFHD.InfobarSelfColorG.value)[2:4]).zfill(2) + str(hex(config.plugins.KravenFHD.InfobarSelfColorB.value)[2:4]).zfill(2)

	def makeTexturePreview(self,style):
		width=460
		height=259
		inpath="/usr/share/enigma2/KravenFHD/textures/"
		usrpath="/usr/share/enigma2/Kraven-user-icons/"
		outpath="/usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/images/"
		if fileExists(usrpath+style+".png"):
			bg=Image.open(usrpath+style+".png")
		elif fileExists(usrpath+style+".jpg"):
			bg=Image.open(usrpath+style+".jpg")
		elif fileExists(inpath+style+".png"):
			bg=Image.open(inpath+style+".png")
		elif fileExists(inpath+style+".jpg"):
			bg=Image.open(inpath+style+".jpg")
		bg_w,bg_h=bg.size
		image=Image.new("RGBA",(width,height),(0,0,0,0))
		for i in xrange(0,width,bg_w):
			for j in xrange(0,height,bg_h):
				image.paste(bg,(i,j))
		image.save(outpath+"preview.jpg")
		
	def makeAlternatePreview(self,style,color):
		width=460
		height=259
		inpath="/usr/share/enigma2/KravenFHD/textures/"
		usrpath="/usr/share/enigma2/Kraven-user-icons/"
		outpath="/usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/images/"
		if fileExists(usrpath+style+".png"):
			bg=Image.open(usrpath+style+".png")
		elif fileExists(usrpath+style+".jpg"):
			bg=Image.open(usrpath+style+".jpg")
		elif fileExists(inpath+style+".png"):
			bg=Image.open(inpath+style+".png")
		elif fileExists(inpath+style+".jpg"):
			bg=Image.open(inpath+style+".jpg")
		bg_w,bg_h=bg.size
		image=Image.new("RGBA",(width,height),(0,0,0,0))
		for i in xrange(0,width,bg_w):
			for j in xrange(0,height,bg_h):
				image.paste(bg,(i,j))
		color=color[-6:]
		r=int(color[0:2],16)
		g=int(color[2:4],16)
		b=int(color[4:6],16)
		image.paste((int(r),int(g),int(b),255),(0,int(height/2),width,height))
		image.save(outpath+"preview.jpg")
		
	def makePreview(self):
		width=460
		height=259
		lineheight=3
		boxbarheight=50
		gradbarheight=100
		
		inpath="/usr/share/enigma2/KravenFHD/textures/"
		usrpath="/usr/share/enigma2/Kraven-user-icons/"
			
		# background
		if config.plugins.KravenFHD.BackgroundColor.value == "texture":
			style=config.plugins.KravenFHD.BackgroundTexture.value
			if fileExists(usrpath+style+".png"):
				bg=Image.open(usrpath+style+".png")
			elif fileExists(usrpath+style+".jpg"):
				bg=Image.open(usrpath+style+".jpg")
			elif fileExists(inpath+style+".png"):
				bg=Image.open(inpath+style+".png")
			elif fileExists(inpath+style+".jpg"):
				bg=Image.open(inpath+style+".jpg")
			bg_w,bg_h=bg.size
			img=Image.new("RGBA",(width,height),(0,0,0,0))
			for i in xrange(0,width,bg_w):
				for j in xrange(0,height,bg_h):
					img.paste(bg,(i,j))
		elif config.plugins.KravenFHD.BackgroundColor.value == "gradient":
			c1=config.plugins.KravenFHD.BackgroundGradientColorPrimary.value
			c2=config.plugins.KravenFHD.BackgroundGradientColorSecondary.value
			c1=c1[-6:]
			r1=int(c1[0:2],16)
			g1=int(c1[2:4],16)
			b1=int(c1[4:6],16)
			c2=c2[-6:]
			r2=int(c2[0:2],16)
			g2=int(c2[2:4],16)
			b2=int(c2[4:6],16)
			if c1!=c2:
				img=Image.new("RGBA",(1,height))
				for pos in range(0,height):
					p=pos/float(height)
					r=r2*p+r1*(1-p)
					g=g2*p+g1*(1-p)
					b=b2*p+b1*(1-p)
					img.putpixel((0,pos),(int(r),int(g),int(b),255))
				img=img.resize((width,height))
			else:
				img=Image.new("RGBA",(width,height),(int(r1),int(g1),int(b1),255))
		else:
			c=self.skincolorbackgroundcolor
			c=c[-6:]
			r=int(c[0:2],16)
			g=int(c[2:4],16)
			b=int(c[4:6],16)
			img=Image.new("RGBA",(width,height),(int(r),int(g),int(b),255))
		
		# infobars
		if config.plugins.KravenFHD.IBStyle.value=="grad":
			if config.plugins.KravenFHD.InfobarGradientColor.value == "texture":
				style=config.plugins.KravenFHD.InfobarTexture.value
				if fileExists(usrpath+style+".png"):
					bg=Image.open(usrpath+style+".png")
				elif fileExists(usrpath+style+".jpg"):
					bg=Image.open(usrpath+style+".jpg")
				elif fileExists(inpath+style+".png"):
					bg=Image.open(inpath+style+".png")
				elif fileExists(inpath+style+".jpg"):
					bg=Image.open(inpath+style+".jpg")
				bg_w,bg_h=bg.size
				ib=Image.new("RGBA",(width,gradbarheight),(0,0,0,0))
				for i in xrange(0,width,bg_w):
					for j in xrange(0,gradbarheight,bg_h):
						ib.paste(bg,(i,j))
			else:
				c=self.skincolorinfobarcolor
				c=c[-6:]
				r=int(c[0:2],16)
				g=int(c[2:4],16)
				b=int(c[4:6],16)
				ib=Image.new("RGBA",(width,gradbarheight),(int(r),int(g),int(b),255))
			trans=(255-int(config.plugins.KravenFHD.InfobarColorTrans.value,16))/255.0
			gr=Image.new("L",(1,gradbarheight),int(255*trans))
			for pos in range(0,gradbarheight):
				gr.putpixel((0,pos),int(self.dexpGradient(gradbarheight,2.0,pos)*trans))
			gr=gr.resize(ib.size)
			img.paste(ib,(0,height-gradbarheight),gr)
			ib=ib.transpose(Image.ROTATE_180)
			gr=gr.transpose(Image.ROTATE_180)
			img.paste(ib,(0,0),gr)
		else: # config.plugins.KravenFHD.IBStyle.value=="box":
			if config.plugins.KravenFHD.InfobarBoxColor.value == "texture":
				style=config.plugins.KravenFHD.InfobarTexture.value
				if fileExists(usrpath+style+".png"):
					bg=Image.open(usrpath+style+".png")
				elif fileExists(usrpath+style+".jpg"):
					bg=Image.open(usrpath+style+".jpg")
				elif fileExists(inpath+style+".png"):
					bg=Image.open(inpath+style+".png")
				elif fileExists(inpath+style+".jpg"):
					bg=Image.open(inpath+style+".jpg")
				bg_w,bg_h=bg.size
				ib=Image.new("RGBA",(width,boxbarheight),(0,0,0,0))
				for i in xrange(0,width,bg_w):
					for j in xrange(0,boxbarheight,bg_h):
						ib.paste(bg,(i,j))
				img.paste(ib,(0,0))
				img.paste(ib,(0,height-boxbarheight))
			elif config.plugins.KravenFHD.InfobarBoxColor.value == "gradient":
				c1=config.plugins.KravenFHD.InfobarGradientColorPrimary.value
				c2=config.plugins.KravenFHD.InfobarGradientColorSecondary.value
				c1=c1[-6:]
				r1=int(c1[0:2],16)
				g1=int(c1[2:4],16)
				b1=int(c1[4:6],16)
				c2=c2[-6:]
				r2=int(c2[0:2],16)
				g2=int(c2[2:4],16)
				b2=int(c2[4:6],16)
				if c1!=c2:
					ib=Image.new("RGBA",(1,boxbarheight))
					for pos in range(0,boxbarheight):
						p=pos/float(boxbarheight)
						r=r2*p+r1*(1-p)
						g=g2*p+g1*(1-p)
						b=b2*p+b1*(1-p)
						ib.putpixel((0,pos),(int(r),int(g),int(b),255))
					ib=ib.resize((width,boxbarheight))
					img.paste(ib,(0,height-boxbarheight))
					ib=ib.transpose(Image.ROTATE_180)
					img.paste(ib,(0,0))
				else:
					ib=Image.new("RGBA",(width,boxbarheight),(int(r1),int(g1),int(b1),255))
					img.paste(ib,(0,0))
					img.paste(ib,(0,height-boxbarheight))
			else:
				c=self.skincolorinfobarcolor
				c=c[-6:]
				r=int(c[0:2],16)
				g=int(c[2:4],16)
				b=int(c[4:6],16)
				ib=Image.new("RGBA",(width,boxbarheight),(int(r),int(g),int(b),255))
				img.paste(ib,(0,0))
				img.paste(ib,(0,height-boxbarheight))
			c=config.plugins.KravenFHD.IBLine.value
			c=c[-6:]
			r=int(c[0:2],16)
			g=int(c[2:4],16)
			b=int(c[4:6],16)
			img.paste((int(r),int(g),int(b),255),(0,boxbarheight,width,boxbarheight+lineheight))
			img.paste((int(r),int(g),int(b),255),(0,height-boxbarheight-lineheight,width,height-boxbarheight))
				
		img.save("/usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/images/preview.jpg")
		
	def makeIbarColorGradientpng(self, newcolor, newtrans):

		width = 1920 # width of the png file
		gradientspeed = 2.0 # look of the gradient. 1 is flat (linear), higher means rounder

		ibarheight = 465 # height of ibar
		ibargradientstart = 75 # start of ibar gradient (from top)
		ibargradientsize = 150 # size of ibar gradient

		ibaroheight = 247 # height of ibaro
		ibarogradientstart = 97 # start of ibaro gradient (from top)
		ibarogradientsize = 150 # size of ibaro gradient

		ibaro2height = 187 # height of ibaro2
		ibaro2gradientstart = 37 # start of ibaro2 gradient (from top)
		ibaro2gradientsize = 150 # size of ibaro2 gradient

		ibaro3height = 217 # height of ibaro3
		ibaro3gradientstart = 67 # start of ibaro3 gradient (from top)
		ibaro3gradientsize = 150 # size of ibaro3 gradient

		newcolor = newcolor[-6:]
		r = int(newcolor[0:2], 16)
		g = int(newcolor[2:4], 16)
		b = int(newcolor[4:6], 16)

		trans = (255-int(newtrans,16))/255.0

		img = Image.new("RGBA",(width,ibarheight),(r,g,b,0))
		gradient = Image.new("L",(1,ibarheight),int(255*trans))
		for pos in range(0,ibargradientstart):
			gradient.putpixel((0,pos),0)
		for pos in range(0,ibargradientsize):
			gradient.putpixel((0,ibargradientstart+pos),int(self.dexpGradient(ibargradientsize,gradientspeed,pos)*trans))
		alpha = gradient.resize(img.size)
		img.putalpha(alpha)
		img.save("/usr/share/enigma2/KravenFHD/graphics/ibar.png")

		img = Image.new("RGBA",(width,ibaroheight),(r,g,b,0))
		gradient = Image.new("L",(1,ibaroheight),0)
		for pos in range(0,ibarogradientstart):
			gradient.putpixel((0,pos),int(255*trans))
		for pos in range(0,ibarogradientsize):
			gradient.putpixel((0,ibarogradientstart+ibarogradientsize-pos-1),int(self.dexpGradient(ibarogradientsize,gradientspeed,pos)*trans))
		alpha = gradient.resize(img.size)
		img.putalpha(alpha)
		img.save("/usr/share/enigma2/KravenFHD/graphics/ibaro.png")

		img = Image.new("RGBA",(width,ibaro2height),(r,g,b,0))
		gradient = Image.new("L",(1,ibaro2height),0)
		for pos in range(0,ibaro2gradientstart):
			gradient.putpixel((0,pos),int(255*trans))
		for pos in range(0,ibaro2gradientsize):
			gradient.putpixel((0,ibaro2gradientstart+ibaro2gradientsize-pos-1),int(self.dexpGradient(ibaro2gradientsize,gradientspeed,pos)*trans))
		alpha = gradient.resize(img.size)
		img.putalpha(alpha)
		img.save("/usr/share/enigma2/KravenFHD/graphics/ibaro2.png")

		img = Image.new("RGBA",(width,ibaro3height),(r,g,b,0))
		gradient = Image.new("L",(1,ibaro3height),0)
		for pos in range(0,ibaro3gradientstart):
			gradient.putpixel((0,pos),int(255*trans))
		for pos in range(0,ibaro3gradientsize):
			gradient.putpixel((0,ibaro3gradientstart+ibaro3gradientsize-pos-1),int(self.dexpGradient(ibaro3gradientsize,gradientspeed,pos)*trans))
		alpha = gradient.resize(img.size)
		img.putalpha(alpha)
		img.save("/usr/share/enigma2/KravenFHD/graphics/ibaro3.png")

	def makeIbarTextureGradientpng(self, style, trans):

		width = 1920 # width of the png file
		gradientspeed = 2.0 # look of the gradient. 1 is flat (linear), higher means rounder

		ibarheight = 465 # height of ibar
		ibargradientstart = 75 # start of ibar gradient (from top)
		ibargradientsize = 150 # size of ibar gradient

		ibaroheight = 247 # height of ibaro
		ibarogradientstart = 97 # start of ibaro gradient (from top)
		ibarogradientsize = 150 # size of ibaro gradient

		ibaro2height = 187 # height of ibaro2
		ibaro2gradientstart = 37 # start of ibaro2 gradient (from top)
		ibaro2gradientsize = 150 # size of ibaro2 gradient

		ibaro3height = 217 # height of ibaro3
		ibaro3gradientstart = 67 # start of ibaro3 gradient (from top)
		ibaro3gradientsize = 150 # size of ibaro3 gradient

		trans = (255-int(trans,16))/255.0

		inpath="/usr/share/enigma2/KravenFHD/textures/"
		usrpath="/usr/share/enigma2/Kraven-user-icons/"
		if fileExists(usrpath+style+".png"):
			bg=Image.open(usrpath+style+".png")
		elif fileExists(usrpath+style+".jpg"):
			bg=Image.open(usrpath+style+".jpg")
		elif fileExists(inpath+style+".png"):
			bg=Image.open(inpath+style+".png")
		elif fileExists(inpath+style+".jpg"):
			bg=Image.open(inpath+style+".jpg")
		bg_w,bg_h=bg.size

		img = Image.new("RGBA",(width,ibarheight),(0,0,0,0))
		for i in xrange(0,width,bg_w):
			for j in xrange(0,ibarheight,bg_h):
				img.paste(bg,(i,j))
		gradient = Image.new("L",(1,ibarheight),int(255*trans))
		for pos in range(0,ibargradientstart):
			gradient.putpixel((0,pos),0)
		for pos in range(0,ibargradientsize):
			gradient.putpixel((0,ibargradientstart+pos),int(self.dexpGradient(ibargradientsize,gradientspeed,pos)*trans))
		alpha = gradient.resize(img.size)
		img.putalpha(alpha)
		img.save("/usr/share/enigma2/KravenFHD/graphics/ibar.png")

		img = Image.new("RGBA",(width,ibaroheight),(0,0,0,0))
		for i in xrange(0,width,bg_w):
			for j in xrange(0,ibaroheight,bg_h):
				img.paste(bg,(i,j))
		gradient = Image.new("L",(1,ibaroheight),0)
		for pos in range(0,ibarogradientstart):
			gradient.putpixel((0,pos),int(255*trans))
		for pos in range(0,ibarogradientsize):
			gradient.putpixel((0,ibarogradientstart+ibarogradientsize-pos-1),int(self.dexpGradient(ibarogradientsize,gradientspeed,pos)*trans))
		alpha = gradient.resize(img.size)
		img.putalpha(alpha)
		img.save("/usr/share/enigma2/KravenFHD/graphics/ibaro.png")

		img = Image.new("RGBA",(width,ibaro2height),(0,0,0,0))
		for i in xrange(0,width,bg_w):
			for j in xrange(0,ibaroheight,bg_h):
				img.paste(bg,(i,j))
		gradient = Image.new("L",(1,ibaro2height),0)
		for pos in range(0,ibaro2gradientstart):
			gradient.putpixel((0,pos),int(255*trans))
		for pos in range(0,ibaro2gradientsize):
			gradient.putpixel((0,ibaro2gradientstart+ibaro2gradientsize-pos-1),int(self.dexpGradient(ibaro2gradientsize,gradientspeed,pos)*trans))
		alpha = gradient.resize(img.size)
		img.putalpha(alpha)
		img.save("/usr/share/enigma2/KravenFHD/graphics/ibaro2.png")

		img = Image.new("RGBA",(width,ibaro3height),(0,0,0,0))
		for i in xrange(0,width,bg_w):
			for j in xrange(0,ibaroheight,bg_h):
				img.paste(bg,(i,j))
		gradient = Image.new("L",(1,ibaro3height),0)
		for pos in range(0,ibaro3gradientstart):
			gradient.putpixel((0,pos),int(255*trans))
		for pos in range(0,ibaro3gradientsize):
			gradient.putpixel((0,ibaro3gradientstart+ibaro3gradientsize-pos-1),int(self.dexpGradient(ibaro3gradientsize,gradientspeed,pos)*trans))
		alpha = gradient.resize(img.size)
		img.putalpha(alpha)
		img.save("/usr/share/enigma2/KravenFHD/graphics/ibaro3.png")

	def makeRectColorpng(self, newcolor, newtrans, width, height, pngname):

		gradientspeed = 2.0 # look of the gradient. 1 is flat (linear), higher means rounder
		gradientsize = 120 # size of gradient

		newcolor = newcolor[-6:]
		r = int(newcolor[0:2], 16)
		g = int(newcolor[2:4], 16)
		b = int(newcolor[4:6], 16)

		trans = (255-int(newtrans,16))/255.0

		img = Image.new("RGBA",(width,height),(r,g,b,int(255*trans)))

		gradient = Image.new("RGBA",(1,gradientsize),(r,g,b,0))
		for pos in range(0,gradientsize):
			gradient.putpixel((0,pos),(r,g,b,int((self.dexpGradient(gradientsize,gradientspeed,pos))*trans)))

		hgradient = gradient.resize((width-2*gradientsize, gradientsize))
		img.paste(hgradient, (gradientsize,0,width-gradientsize,gradientsize))
		hgradient = hgradient.transpose(Image.ROTATE_180)
		img.paste(hgradient, (gradientsize,height-gradientsize,width-gradientsize,height))

		vgradient = gradient.transpose(Image.ROTATE_90)
		vgradient = vgradient.resize((gradientsize,height-2*gradientsize))
		img.paste(vgradient, (0,gradientsize,gradientsize,height-gradientsize))
		vgradient = vgradient.transpose(Image.ROTATE_180)
		img.paste(vgradient, (width-gradientsize,gradientsize,width,height-gradientsize))

		corner = Image.new("RGBA",(gradientsize,gradientsize),(r,g,b,0))
		for xpos in range(0,gradientsize):
			for ypos in range(0,gradientsize):
				dist = int(round((xpos**2+ypos**2)**0.503))
				corner.putpixel((xpos,ypos),(r,g,b,int((self.dexpGradient(gradientsize,gradientspeed,gradientsize-dist-1))*trans)))
		corner = corner.filter(ImageFilter.BLUR)
		img.paste(corner, (width-gradientsize,height-gradientsize,width,height))
		corner = corner.transpose(Image.ROTATE_90)
		img.paste(corner, (width-gradientsize,0,width,gradientsize))
		corner = corner.transpose(Image.ROTATE_90)
		img.paste(corner, (0,0,gradientsize,gradientsize))
		corner = corner.transpose(Image.ROTATE_90)
		img.paste(corner, (0,height-gradientsize,gradientsize,height))

		img.save("/usr/share/enigma2/KravenFHD/graphics/"+pngname+".png")

	def makeRectTexturepng(self, style, trans, width, height, pngname):

		gradientspeed = 2.0 # look of the gradient. 1 is flat (linear), higher means rounder
		gradientsize = 120 # size of gradient

		trans = (255-int(trans,16))/255.0

		inpath="/usr/share/enigma2/KravenFHD/textures/"
		usrpath="/usr/share/enigma2/Kraven-user-icons/"
		if fileExists(usrpath+style+".png"):
			bg=Image.open(usrpath+style+".png")
		elif fileExists(usrpath+style+".jpg"):
			bg=Image.open(usrpath+style+".jpg")
		elif fileExists(inpath+style+".png"):
			bg=Image.open(inpath+style+".png")
		elif fileExists(inpath+style+".jpg"):
			bg=Image.open(inpath+style+".jpg")
		bg_w,bg_h=bg.size
		
		img=Image.new("RGBA",(width,height),(0,0,0,0))
		for i in xrange(0,width,bg_w):
			for j in xrange(0,height,bg_h):
				img.paste(bg,(i,j))

		mask=Image.new("L",(width,height),255*trans)
		
		gradient = Image.new("L",(1,gradientsize),0)
		for pos in range(0,gradientsize):
			gradient.putpixel((0,pos),int((self.dexpGradient(gradientsize,gradientspeed,pos))*trans))

		hgradient = gradient.resize((width-2*gradientsize, gradientsize))
		mask.paste(hgradient, (gradientsize,0,width-gradientsize,gradientsize))
		hgradient = hgradient.transpose(Image.ROTATE_180)
		mask.paste(hgradient, (gradientsize,height-gradientsize,width-gradientsize,height))

		vgradient = gradient.transpose(Image.ROTATE_90)
		vgradient = vgradient.resize((gradientsize,height-2*gradientsize))
		mask.paste(vgradient, (0,gradientsize,gradientsize,height-gradientsize))
		vgradient = vgradient.transpose(Image.ROTATE_180)
		mask.paste(vgradient, (width-gradientsize,gradientsize,width,height-gradientsize))

		corner = Image.new("L",(gradientsize,gradientsize),0)
		for xpos in range(0,gradientsize):
			for ypos in range(0,gradientsize):
				dist = int(round((xpos**2+ypos**2)**0.503))
				corner.putpixel((xpos,ypos),int((self.dexpGradient(gradientsize,gradientspeed,gradientsize-dist-1))*trans))
		corner = corner.filter(ImageFilter.BLUR)
		mask.paste(corner, (width-gradientsize,height-gradientsize,width,height))
		corner = corner.transpose(Image.ROTATE_90)
		mask.paste(corner, (width-gradientsize,0,width,gradientsize))
		corner = corner.transpose(Image.ROTATE_90)
		mask.paste(corner, (0,0,gradientsize,gradientsize))
		corner = corner.transpose(Image.ROTATE_90)
		mask.paste(corner, (0,height-gradientsize,gradientsize,height))
		
		img.putalpha(mask)

		img.save("/usr/share/enigma2/KravenFHD/graphics/"+pngname+".png")

	def makeBGGradientpng(self):
		self.makeGradientpng("globalbg",1920,1080,config.plugins.KravenFHD.BackgroundGradientColorPrimary.value,config.plugins.KravenFHD.BackgroundGradientColorSecondary.value,config.plugins.KravenFHD.BackgroundColorTrans.value)
		self.makeGradientpng("nontransbg",1920,1080,config.plugins.KravenFHD.BackgroundGradientColorPrimary.value,config.plugins.KravenFHD.BackgroundGradientColorSecondary.value,"00")
		self.makeGradientpng("menubg",1920,1080,config.plugins.KravenFHD.BackgroundGradientColorPrimary.value,config.plugins.KravenFHD.BackgroundGradientColorSecondary.value,config.plugins.KravenFHD.MenuColorTrans.value)
		self.makeGradientpng("channelbg",1920,1080,config.plugins.KravenFHD.BackgroundGradientColorPrimary.value,config.plugins.KravenFHD.BackgroundGradientColorSecondary.value,config.plugins.KravenFHD.ChannelSelectionTrans.value)
		self.makeGradientpng("sibbg",1920,1080,config.plugins.KravenFHD.BackgroundGradientColorPrimary.value,config.plugins.KravenFHD.BackgroundGradientColorSecondary.value,config.plugins.KravenFHD.InfobarColorTrans.value)
			
	def makeIBGradientpng(self):
		width=1920
		#Ibar
		ibarheights=[
			("infobar-style-nopicon",248),
			("infobar-style-x1",248),
			("infobar-style-zz1",297),
			("infobar-style-zz2",278),
			("infobar-style-zz3",278),
			("infobar-style-zz4",297),
			("infobar-style-zzz1",371),
			("infobar-style-zzz2",371)
			]
		for pair in ibarheights:
			if config.plugins.KravenFHD.InfobarStyle.value == pair[0]:
				self.makeGradientpng("ibar",width,pair[1],config.plugins.KravenFHD.InfobarGradientColorPrimary.value,config.plugins.KravenFHD.InfobarGradientColorSecondary.value,config.plugins.KravenFHD.InfobarColorTrans.value)
		if config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-x2","infobar-style-x3","infobar-style-x4"):
			if config.plugins.KravenFHD.ClockStyle.value == "clock-android":
				self.makeGradientpng("ibar",width,231,config.plugins.KravenFHD.InfobarGradientColorPrimary.value,config.plugins.KravenFHD.InfobarGradientColorSecondary.value,config.plugins.KravenFHD.InfobarColorTrans.value)
			else:
				self.makeGradientpng("ibar",width,216,config.plugins.KravenFHD.InfobarGradientColorPrimary.value,config.plugins.KravenFHD.InfobarGradientColorSecondary.value,config.plugins.KravenFHD.InfobarColorTrans.value)
		if config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-z1","infobar-style-z2"):
			if config.plugins.KravenFHD.ClockStyle.value == "clock-android":
				self.makeGradientpng("ibar",width,231,config.plugins.KravenFHD.InfobarGradientColorPrimary.value,config.plugins.KravenFHD.InfobarGradientColorSecondary.value,config.plugins.KravenFHD.InfobarColorTrans.value)
			else:
				self.makeGradientpng("ibar",width,216,config.plugins.KravenFHD.InfobarGradientColorPrimary.value,config.plugins.KravenFHD.InfobarGradientColorSecondary.value,config.plugins.KravenFHD.InfobarColorTrans.value)
		self.makeGradientpng("ibar2",width,90,config.plugins.KravenFHD.InfobarGradientColorPrimary.value,config.plugins.KravenFHD.InfobarGradientColorSecondary.value,config.plugins.KravenFHD.InfobarColorTrans.value)
		self.makeGradientpng("ibar3",width,105,config.plugins.KravenFHD.InfobarGradientColorPrimary.value,config.plugins.KravenFHD.InfobarGradientColorSecondary.value,config.plugins.KravenFHD.InfobarColorTrans.value)
		self.makeGradientpng("ibar4",width,120,config.plugins.KravenFHD.InfobarGradientColorPrimary.value,config.plugins.KravenFHD.InfobarGradientColorSecondary.value,config.plugins.KravenFHD.InfobarColorTrans.value)
		self.makeGradientpng("ibar5",width,165,config.plugins.KravenFHD.InfobarGradientColorPrimary.value,config.plugins.KravenFHD.InfobarGradientColorSecondary.value,config.plugins.KravenFHD.InfobarColorTrans.value)
		self.makeGradientpng("ibar6",width,309,config.plugins.KravenFHD.InfobarGradientColorPrimary.value,config.plugins.KravenFHD.InfobarGradientColorSecondary.value,config.plugins.KravenFHD.InfobarColorTrans.value)
		self.makeGradientpng("ibar7",width,427,config.plugins.KravenFHD.InfobarGradientColorPrimary.value,config.plugins.KravenFHD.InfobarGradientColorSecondary.value,config.plugins.KravenFHD.InfobarColorTrans.value)
		#Ibaro
		ibaroheights=[
			("ibaro",88),
			("ibaro2",105),
			("ibaro3",173),
			("ibaro4",225)
			]
		for pair in ibaroheights:
			self.makeGradientpng(pair[0],width,pair[1],config.plugins.KravenFHD.InfobarGradientColorSecondary.value,config.plugins.KravenFHD.InfobarGradientColorPrimary.value,config.plugins.KravenFHD.InfobarColorTrans.value)

		#Sysinfo
		if config.plugins.KravenFHD.InfoStyle.value == "primary":
			FirstColor=config.plugins.KravenFHD.InfobarGradientColorPrimary.value
			SecondColor=config.plugins.KravenFHD.InfobarGradientColorPrimary.value
		elif config.plugins.KravenFHD.InfoStyle.value == "secondary":
			FirstColor=config.plugins.KravenFHD.InfobarGradientColorSecondary.value
			SecondColor=config.plugins.KravenFHD.InfobarGradientColorSecondary.value
		else:
			FirstColor=config.plugins.KravenFHD.InfobarGradientColorPrimary.value
			SecondColor=config.plugins.KravenFHD.InfobarGradientColorSecondary.value
		if config.plugins.KravenFHD.SystemInfo.value == "systeminfo-small":
			self.makeGradientpng("info",450,120,FirstColor,SecondColor,config.plugins.KravenFHD.InfobarColorTrans.value)
		elif config.plugins.KravenFHD.SystemInfo.value == "systeminfo-big":
			self.makeGradientpng("info",450,255,FirstColor,SecondColor,config.plugins.KravenFHD.InfobarColorTrans.value)
		elif config.plugins.KravenFHD.SystemInfo.value == "systeminfo-bigsat":
			self.makeGradientpng("info",450,390,FirstColor,SecondColor,config.plugins.KravenFHD.InfobarColorTrans.value)
		
		#Timeshift
		self.makeGradientpng("shift",1177,93,FirstColor,SecondColor,config.plugins.KravenFHD.InfobarColorTrans.value)

		#InfobarTunerState
		self.makeGradientpng("ibts",1920,48,FirstColor,SecondColor,config.plugins.KravenFHD.InfobarColorTrans.value)

		#AutoResolution
		self.makeGradientpng("autoresolution",378,93,FirstColor,SecondColor,config.plugins.KravenFHD.InfobarColorTrans.value)

		#PVRState
		if config.plugins.KravenFHD.PVRState.value == "pvrstate-center-big":
			self.makeGradientpng("pvrstate",330,135,FirstColor,SecondColor,config.plugins.KravenFHD.InfobarColorTrans.value)
		elif config.plugins.KravenFHD.PVRState.value in ("pvrstate-center-small","pvrstate-left-small"):
			self.makeGradientpng("pvrstate",165,67,FirstColor,SecondColor,config.plugins.KravenFHD.InfobarColorTrans.value)

		#Weather-small
		if config.plugins.KravenFHD.WeatherStyle.value == "weather-small":
			self.makeGradientpng("wsmall",450,180,config.plugins.KravenFHD.InfobarGradientColorSecondary.value,config.plugins.KravenFHD.InfobarGradientColorPrimary.value,config.plugins.KravenFHD.InfobarColorTrans.value)

	def makeGradientpng(self,name,width,height,color1,color2,trans):
		path="/usr/share/enigma2/KravenFHD/graphics/"
		width=int(width)
		height=int(height)
		color1=color1[-6:]
		r1=int(color1[0:2],16)
		g1=int(color1[2:4],16)
		b1=int(color1[4:6],16)
		color2=color2[-6:]
		r2=int(color2[0:2],16)
		g2=int(color2[2:4],16)
		b2=int(color2[4:6],16)
		trans=255-int(trans,16)
		gradient=Image.new("RGBA",(1,height))
		for pos in range(0,height):
			p=pos/float(height)
			r=r2*p+r1*(1-p)
			g=g2*p+g1*(1-p)
			b=b2*p+b1*(1-p)
			gradient.putpixel((0,pos),(int(r),int(g),int(b),int(trans)))
		gradient=gradient.resize((width,height))
		gradient.save(path+name+".png")

	def makeBGTexturepng(self):
		self.makeTexturepng("globalbg",1920,1080,config.plugins.KravenFHD.BackgroundTexture.value,config.plugins.KravenFHD.BackgroundColorTrans.value)
		self.makeTexturepng("nontransbg",1920,1080,config.plugins.KravenFHD.BackgroundTexture.value,"00")
		self.makeTexturepng("menubg",1920,1080,config.plugins.KravenFHD.BackgroundTexture.value,config.plugins.KravenFHD.MenuColorTrans.value)
		self.makeTexturepng("channelbg",1920,1080,config.plugins.KravenFHD.BackgroundTexture.value,config.plugins.KravenFHD.ChannelSelectionTrans.value)
		self.makeTexturepng("sibbg",1920,1080,config.plugins.KravenFHD.BackgroundTexture.value,config.plugins.KravenFHD.InfobarColorTrans.value)
			
	def makeIBTexturepng(self):
		self.makeTexturepng("ibtexture",1920,1080,config.plugins.KravenFHD.InfobarTexture.value,config.plugins.KravenFHD.InfobarColorTrans.value)
			
	def makeTexturepng(self,name,width,height,style,trans):
		width=int(width)
		height=int(height)
		trans=255-int(trans,16)
		path="/usr/share/enigma2/KravenFHD/textures/"
		usrpath="/usr/share/enigma2/Kraven-user-icons/"
		outpath="/usr/share/enigma2/KravenFHD/graphics/"
		if fileExists(usrpath+style+".png"):
			bg=Image.open(usrpath+style+".png")
		elif fileExists(usrpath+style+".jpg"):
			bg=Image.open(usrpath+style+".jpg")
		elif fileExists(path+style+".png"):
			bg=Image.open(path+style+".png")
		elif fileExists(path+style+".jpg"):
			bg=Image.open(path+style+".jpg")
		bg_w,bg_h=bg.size
		image=Image.new("RGBA",(width,height),(0,0,0,0))
		for i in xrange(0,width,bg_w):
			for j in xrange(0,height,bg_h):
				image.paste(bg,(i,j))
		alpha=Image.new("L",(width,height),trans)
		image.putalpha(alpha)
		image.save(outpath+name+".png")

	def makeBackpng(self):
		# this makes a transparent png
		# not needed above, use it manually
		width = 1920 # width of the png file
		height = 1080 # height of the png file
		img = Image.new("RGBA",(width,height),(0,0,0,0))
		img.save("/usr/share/enigma2/KravenFHD/graphics/backg.png")

	def makeSRpng(self,newcolor):
		if config.plugins.KravenFHD.SerienRecorder.value == "serienrecorder":
			width = 900 # width of the png file
			height = 585 # height of the png file

			newcolor = newcolor[-6:]
			r = int(newcolor[0:2], 16)
			g = int(newcolor[2:4], 16)
			b = int(newcolor[4:6], 16)
		
			img = Image.new("RGBA",(width,height),(r,g,b,255))
			img.save("/usr/share/enigma2/KravenFHD/graphics/popup_bg.png")
		else:
			pass

	def makeborsetpng(self,newcolor):
		width = 2
		height = 2
		newcolor = newcolor[-6:]
		r = int(newcolor[0:2], 16)
		g = int(newcolor[2:4], 16)
		b = int(newcolor[4:6], 16)
		img = Image.new("RGBA",(width,height),(r,g,b,255))
		img.save("/usr/share/enigma2/KravenFHD/graphics/borset.png")

	def dexpGradient(self,len,spd,pos):
		if pos < 0:
			pos = 0
		if pos > len-1:
			pos = len-1
		a = ((len/2)**spd)*2.0
		if pos <= len/2:
			f = (pos**spd)
		else:
			f = a-((len-pos)**spd)
		e = int((f/a)*255)
		return e

	def calcBrightness(self,color,factor):
		f = int(int(factor)*25.5-255)
		color = color[-6:]
		r = int(color[0:2],16)+f
		g = int(color[2:4],16)+f
		b = int(color[4:6],16)+f
		if r<0:
			r=0
		if g<0:
			g=0
		if b<0:
			b=0
		if r>255:
			r=255
		if g>255:
			g=255
		if b>255:
			b=255
		return str(hex(r)[2:4]).zfill(2)+str(hex(g)[2:4]).zfill(2)+str(hex(b)[2:4]).zfill(2)

	def calcTransparency(self,trans1,trans2):
		t1 = int(trans1,16)
		t2 = int(trans2,16)
		return str(hex(min(t1,t2))[2:4]).zfill(2)

	def hexRGB(self,color):
		color = color[-6:]
		r = int(color[0:2],16)
		g = int(color[2:4],16)
		b = int(color[4:6],16)
		return (r<<16)|(g<<8)|b

	def RGB(self,r,g,b):
		return (r<<16)|(g<<8)|b

	def get_weather_data(self):

			self.city = ''
			self.lat = ''
			self.lon = ''
			self.accu_id = ''
			self.preview_text = ''
			self.preview_warning = ''

			if config.plugins.KravenFHD.weather_server.value == '_accu':
				if config.plugins.KravenFHD.weather_search_over.value == 'ip':
					self.get_accu_id_by_ip()
				elif config.plugins.KravenFHD.weather_search_over.value == 'name':
					self.get_accu_id_by_name()
			elif config.plugins.KravenFHD.weather_server.value == '_owm':
				self.get_owm_by_ip()

			self.actCity=self.preview_text+self.preview_warning

	def get_owm_by_ip(self):

		if self.InternetAvailable==False: 
			return
		
		try:
			res = requests.get('http://ip-api.com/json/?lang=de&fields=status,city,lat,lon', timeout=1)
			data = res.json()

			if data['status']=='success':
				self.city = data['city']
				self.lat = data['lat']
				self.lon = data['lon']
				self.preview_text = str(self.city) + '\nLat: ' + str(self.lat) + '\nLong: ' + str(self.lon)
				config.plugins.KravenFHD.weather_owm_latlon.value = 'lat=%s&lon=%s&units=metric&lang=%s' % (str(self.lat),str(self.lon),str(config.plugins.KravenFHD.weather_language.value))
				config.plugins.KravenFHD.weather_owm_latlon.save()
				config.plugins.KravenFHD.weather_foundcity.value = self.city
				config.plugins.KravenFHD.weather_foundcity.save()
			else:
				self.preview_text = _('No data for IP')
		except:
			self.preview_text = _('No data for IP')

	def get_accu_id_by_ip(self):

		if self.InternetAvailable==False: 
			return
		
		try:
			res = requests.get('http://ip-api.com/json/?lang=de&fields=status,city', timeout=1)
			data = res.json()

			if data['status'] == 'success':
				city = data['city']
				apikey = config.plugins.KravenFHD.weather_accu_apikey.value
				language = config.plugins.KravenFHD.weather_language.value
				res1 = requests.get('http://dataservice.accuweather.com/locations/v1/cities/search?q=%s&apikey=%s&language=%s' % (str(city),str(apikey),str(language)), timeout=1)
				data1 = res1.json()
			
				if 'Code' in data1:
					if data1['Code'] == 'ServiceUnavailable':
						self.preview_warning = _('API requests exceeded')
					elif data1['Code'] == 'Unauthorized':
						self.preview_warning = _('API authorization failed')
				else:
					self.accu_id = data1[0]['Key']
					self.city = data1[0]['LocalizedName']
					self.lat = data1[0]['GeoPosition']['Latitude']
					self.lon = data1[0]['GeoPosition']['Longitude']
					self.preview_text = str(self.city) + '\nLat: ' + str(self.lat) + '\nLong: ' + str(self.lon)
					config.plugins.KravenFHD.weather_accu_id.value = str(self.accu_id)
					config.plugins.KravenFHD.weather_accu_id.save()
					config.plugins.KravenFHD.weather_foundcity.value = str(self.city)
					config.plugins.KravenFHD.weather_foundcity.save()
			else:
				self.preview_text = _('No data for IP')
		except:
			self.preview_warning = _('No Accu ID found')

	def get_accu_id_by_name(self):

		if self.InternetAvailable==False: 
			return
		
		try:
			city = config.plugins.KravenFHD.weather_cityname.getValue()
			apikey = config.plugins.KravenFHD.weather_accu_apikey.value
			language = config.plugins.KravenFHD.weather_language.value
			
			res = requests.get('http://dataservice.accuweather.com/locations/v1/cities/search?q=%s&apikey=%s&language=%s' % (str(city),str(apikey),str(language)), timeout=1)
			data = res.json()
			
			if 'Code' in data:
				if data['Code'] == 'ServiceUnavailable':
					self.preview_warning = _('API requests exceeded')
				elif data['Code'] == 'Unauthorized':
					self.preview_warning = _('API authorization failed')
			else:
				self.accu_id = data[0]['Key']
				self.city = data[0]['LocalizedName']
				self.lat = data[0]['GeoPosition']['Latitude']
				self.lon = data[0]['GeoPosition']['Longitude']
				self.preview_text = str(self.city) + '\nLat: ' + str(self.lat) + '\nLong: ' + str(self.lon)
				config.plugins.KravenFHD.weather_accu_id.value = str(self.accu_id)
				config.plugins.KravenFHD.weather_accu_id.save()
				config.plugins.KravenFHD.weather_foundcity.value = str(self.city)
				config.plugins.KravenFHD.weather_foundcity.save()
		except:
			self.preview_warning = _('No Accu ID found')
