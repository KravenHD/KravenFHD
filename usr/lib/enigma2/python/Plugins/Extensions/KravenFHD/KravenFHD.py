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
from Components.ActionMap import ActionMap
from Components.AVSwitch import AVSwitch
from Components.config import config, configfile, ConfigYesNo, ConfigSubsection, getConfigListEntry, ConfigSelection, ConfigNumber, ConfigText, ConfigInteger, ConfigClock, ConfigSlider
from Components.ConfigList import ConfigListScreen
from Components.Sources.StaticText import StaticText
from Components.Label import Label
from Components.Language import language
from os import environ, listdir, remove, rename, system, popen
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
from xml import etree
from xml.etree.cElementTree import fromstring

#############################################################

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

ColorList = [
	("00F0A30A", _("amber")),
	("00B27708", _("amber dark")),
	("001B1775", _("blue")),
	("000E0C3F", _("blue dark")),
	("007D5929", _("brown")),
	("003F2D15", _("brown dark")),
	("000050EF", _("cobalt")),
	("00001F59", _("cobalt dark")),
	("001BA1E2", _("cyan")),
	("000F5B7F", _("cyan dark")),
	("00FFEA04", _("yellow")),
	("00999999", _("grey")),
	("003F3F3F", _("grey dark")),
	("0070AD11", _("green")),
	("00213305", _("green dark")),
	("00A19181", _("Kraven")),
	("0028150B", _("Kraven dark")),
	("006D8764", _("olive")),
	("00313D2D", _("olive dark")),
	("00C3461B", _("orange")),
	("00892E13", _("orange dark")),
	("00F472D0", _("pink")),
	("00723562", _("pink dark")),
	("00E51400", _("red")),
	("00330400", _("red dark")),
	("00000000", _("black")),
	("00647687", _("steel")),
	("00262C33", _("steel dark")),
	("006C0AAB", _("violet")),
	("001F0333", _("violet dark")),
	("00ffffff", _("white"))
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
	("647687", _("steel")),
	("262C33", _("steel dark")),
	("131619", _("steel very dark")),
	("6C0AAB", _("violet")),
	("1F0333", _("violet dark")),
	("11001E", _("violet very dark")),
	("ffffff", _("white")),
	("self", _("self"))
	]

LanguageList = [
	("de", _("Deutsch")),
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
config.plugins.KravenFHD.InfobarSelfColorR = ConfigSlider(default=0, increment=15, limits=(0,255))
config.plugins.KravenFHD.InfobarSelfColorG = ConfigSlider(default=0, increment=15, limits=(0,255))
config.plugins.KravenFHD.InfobarSelfColorB = ConfigSlider(default=0, increment=15, limits=(0,255))
config.plugins.KravenFHD.BackgroundSelfColorR = ConfigSlider(default=0, increment=15, limits=(0,255))
config.plugins.KravenFHD.BackgroundSelfColorG = ConfigSlider(default=0, increment=15, limits=(0,255))
config.plugins.KravenFHD.BackgroundSelfColorB = ConfigSlider(default=75, increment=15, limits=(0,255))
config.plugins.KravenFHD.InfobarAntialias = ConfigSlider(default=10, increment=1, limits=(0,20))
config.plugins.KravenFHD.ECMLineAntialias = ConfigSlider(default=10, increment=1, limits=(0,20))
config.plugins.KravenFHD.ScreensAntialias = ConfigSlider(default=10, increment=1, limits=(0,20))

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
				
config.plugins.KravenFHD.refreshInterval = ConfigSelection(default="15", choices = [
				("0", _("0")),
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
				("volume-top", _("top"))
				])

config.plugins.KravenFHD.MenuColorTrans = ConfigSelection(default="32", choices = TransList)

config.plugins.KravenFHD.BackgroundColorTrans = ConfigSelection(default="32", choices = TransList)

config.plugins.KravenFHD.InfobarColorTrans = ConfigSelection(default="00", choices = TransList)

config.plugins.KravenFHD.BackgroundColor = ConfigSelection(default="self", choices = BackgroundList)

config.plugins.KravenFHD.InfobarColor = ConfigSelection(default="self", choices = BackgroundList)

config.plugins.KravenFHD.SelectionBackground = ConfigSelection(default="000050EF", choices = ColorList)

config.plugins.KravenFHD.Font1 = ConfigSelection(default="00ffffff", choices = ColorList)

config.plugins.KravenFHD.Font2 = ConfigSelection(default="00F0A30A", choices = ColorList)

config.plugins.KravenFHD.IBFont1 = ConfigSelection(default="00ffffff", choices = ColorList)

config.plugins.KravenFHD.IBFont2 = ConfigSelection(default="00F0A30A", choices = ColorList)

config.plugins.KravenFHD.SelectionFont = ConfigSelection(default="00ffffff", choices = ColorList)

config.plugins.KravenFHD.MarkedFont = ConfigSelection(default="00ffffff", choices = ColorList)

config.plugins.KravenFHD.ECMFont = ConfigSelection(default="00ffffff", choices = ColorList)

config.plugins.KravenFHD.ChannelnameFont = ConfigSelection(default="00ffffff", choices = ColorList)

config.plugins.KravenFHD.PrimetimeFont = ConfigSelection(default="0070AD11", choices = ColorList)

config.plugins.KravenFHD.ButtonText = ConfigSelection(default="00ffffff", choices = ColorList)

config.plugins.KravenFHD.Android = ConfigSelection(default="00000000", choices = ColorList)

config.plugins.KravenFHD.Border = ConfigSelection(default="00ffffff", choices = ColorList)

config.plugins.KravenFHD.Progress = ConfigSelection(default="progress", choices = [
				("00F0A30A", _("amber")),
				("00B27708", _("amber dark")),
				("001B1775", _("blue")),
				("000E0C3F", _("blue dark")),
				("007D5929", _("brown")),
				("003F2D15", _("brown dark")),
				("progress", _("colorfull")),
				("000050EF", _("cobalt")),
				("00001F59", _("cobalt dark")),
				("001BA1E2", _("cyan")),
				("000F5B7F", _("cyan dark")),
				("00FFEA04", _("yellow")),
				("00999999", _("grey")),
				("003F3F3F", _("grey dark")),
				("0070AD11", _("green")),
				("00213305", _("green dark")),
				("00A19181", _("Kraven")),
				("0028150B", _("Kraven dark")),
				("006D8764", _("olive")),
				("00313D2D", _("olive dark")),
				("00C3461B", _("orange")),
				("00892E13", _("orange dark")),
				("00F472D0", _("pink")),
				("00723562", _("pink dark")),
				("00E51400", _("red")),
				("00330400", _("red dark")),
				("00000000", _("black")),
				("00647687", _("steel")),
				("00262C33", _("steel dark")),
				("006C0AAB", _("violet")),
				("001F0333", _("violet dark")),
				("00ffffff", _("white"))
				])

config.plugins.KravenFHD.Line = ConfigSelection(default="00ffffff", choices = ColorList)

config.plugins.KravenFHD.IBLine = ConfigSelection(default="00ffffff", choices = ColorList)

config.plugins.KravenFHD.IBStyle = ConfigSelection(default="gradient", choices = [
				("gradient", _("gradient")),
				("box", _("box"))
				])

BorderList = [("none", _("off"))]
BorderList = BorderList + ColorList
config.plugins.KravenFHD.SelectionBorder = ConfigSelection(default="none", choices = BorderList)

config.plugins.KravenFHD.MiniTVBorder = ConfigSelection(default="003F3F3F", choices = ColorList)

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
				("infobar-style-z1", _("Z1")),
				("infobar-style-z2", _("Z2")),
				("infobar-style-zz1", _("ZZ1")),
				("infobar-style-zz2", _("ZZ2")),
				("infobar-style-zz3", _("ZZ3")),
				("infobar-style-zz4", _("ZZ4")),
				("infobar-style-zzz1", _("ZZZ1"))
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

config.plugins.KravenFHD.ChannelSelectionStyle = ConfigSelection(default="channelselection-style-minitv", choices = [
				("channelselection-style-nopicon", _("no Picon")),
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
				("channelselection-style-nobile-minitv3", _("Nobile Preview"))
				])

config.plugins.KravenFHD.ChannelSelectionStyle2 = ConfigSelection(default="channelselection-style-minitv", choices = [
				("channelselection-style-nopicon", _("no Picon")),
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
				("channelselection-style-nobile-minitv33", _("Nobile Extended Preview"))
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
				("size-55", _("45"))
				])

config.plugins.KravenFHD.ChannelSelectionInfoSize = ConfigSelection(default="size-36", choices = [
				("size-24", _("24")),
				("size-27", _("27")),
				("size-30", _("30")),
				("size-33", _("33")),
				("size-36", _("36")),
				("size-39", _("39")),
				("size-42", _("42")),
				("size-55", _("45"))
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

config.plugins.KravenFHD.ChannelSelectionServiceNA = ConfigSelection(default="00FFEA04", choices = ColorList)

config.plugins.KravenFHD.NumberZapExt = ConfigSelection(default="none", choices = [
				("none", _("off")),
				("numberzapext-xpicon", _("X-Picons")),
				("numberzapext-zpicon", _("Z-Picons")),
				("numberzapext-zzpicon", _("ZZ-Picons")),
				("numberzapext-zzzpicon", _("ZZZ-Picons"))
				])

config.plugins.KravenFHD.CoolTVGuide = ConfigSelection(default="cooltv-minitv", choices = [
				("cooltv-minitv", _("MiniTV")),
				("cooltv-picon", _("Picon"))
				])

config.plugins.KravenFHD.MovieSelection = ConfigSelection(default="movieselection-no-cover", choices = [
				("movieselection-no-cover", _("no Cover")),
				("movieselection-small-cover", _("small Cover")),
				("movieselection-big-cover", _("big Cover")),
				("movieselection-minitv", _("MiniTV")),
				("movieselection-minitv-cover", _("MiniTV + Cover"))
				])

config.plugins.KravenFHD.MovieSelectionEPGSize = ConfigSelection(default="small", choices = [
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
				("emc-minitv2", _("MiniTV2"))
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
				("steptime=66", _("15 px/sec")),
				("steptime=50", _("20 px/sec"))
				])

config.plugins.KravenFHD.ScrollBar = ConfigSelection(default="scrollbarWidth=0", choices = [
				("scrollbarWidth=0", _("off")),
				("scrollbarWidth=5", _("thin")),
				("scrollbarWidth=10", _("middle")),
				("scrollbarWidth=15", _("wide"))
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

config.plugins.KravenFHD.ECMVisible = ConfigSelection(default="none", choices = [
				("none", _("off")),
				("ib", _("Infobar")),
				("sib", _("SecondInfobar")),
				("ib+sib", _("Infobar & SecondInfobar"))
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

config.plugins.KravenFHD.record2 = ConfigSelection(default="record+tuner-shine", choices = [
				("record-blink", _("record blink")),
				("tuner-blink", _("tuner blink")),
				("record+tuner-blink", _("record & tuner blink")),
				("record+tuner-shine", _("record & tuner shine"))
				])

config.plugins.KravenFHD.record3 = ConfigSelection(default="tuner-shine", choices = [
				("tuner-blink", _("tuner blink")),
				("tuner-shine", _("tuner shine"))
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

config.plugins.KravenFHD.MenuIcons = ConfigSelection(default="stony272", choices = [
				("stony272", _("stony272")),
				("stony272-metal", _("stony272-metal")),
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

config.plugins.KravenFHD.EMCSelectionBackground = ConfigSelection(default="00213305", choices = ColorList)

config.plugins.KravenFHD.EMCSelectionFont = ConfigSelection(default="00ffffff", choices = ColorList)

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

config.plugins.KravenFHD.SplitScreen = ConfigSelection(default="splitscreen1", choices = [
				("splitscreen1", _("without description")),
				("splitscreen2", _("with description"))
				])

config.plugins.KravenFHD.weather_gmcode = ConfigText(default="GM")
config.plugins.KravenFHD.weather_cityname = ConfigText(default = "")
config.plugins.KravenFHD.weather_language = ConfigSelection(default="de", choices = LanguageList)
config.plugins.KravenFHD.weather_server = ConfigSelection(default="_owm", choices = [
				("_owm", _("OpenWeatherMap")),
				("_accu", _("Accuweather")),
				("_realtek", _("RealTek"))
				])

config.plugins.KravenFHD.weather_search_over = ConfigSelection(default="ip", choices = [
				("ip", _("Auto (IP)")),
				("name", _("Search String")),
				("gmcode", _("GM Code"))
				])

config.plugins.KravenFHD.weather_owm_latlon = ConfigText(default = "")
config.plugins.KravenFHD.weather_accu_latlon = ConfigText(default = "")
config.plugins.KravenFHD.weather_realtek_latlon = ConfigText(default = "")
config.plugins.KravenFHD.weather_accu_id = ConfigText(default = "")
config.plugins.KravenFHD.weather_foundcity = ConfigText(default = "")

config.plugins.KravenFHD.PlayerClock = ConfigSelection(default="player-classic", choices = [
				("player-classic", _("standard")),
				("player-android", _("android")),
				("player-flip", _("flip")),
				("player-weather", _("weather icon"))
				])

config.plugins.KravenFHD.Android2 = ConfigSelection(default="00000000", choices = ColorList)

config.plugins.KravenFHD.CategoryProfiles = ConfigSelection(default="category", choices = [
				("category", _(" "))
				])

config.plugins.KravenFHD.CategorySystem = ConfigSelection(default="category", choices = [
				("category", _(" "))
				])

config.plugins.KravenFHD.CategoryGlobalColors = ConfigSelection(default="category", choices = [
				("category", _(" "))
				])

config.plugins.KravenFHD.CategoryInfobar = ConfigSelection(default="category", choices = [
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

config.plugins.KravenFHD.CategoryMovieSelection = ConfigSelection(default="category", choices = [
				("category", _(" "))
				])

config.plugins.KravenFHD.CategoryChannellist = ConfigSelection(default="category", choices = [
				("category", _(" "))
				])

config.plugins.KravenFHD.CategoryEMC = ConfigSelection(default="category", choices = [
				("category", _(" "))
				])

config.plugins.KravenFHD.CategoryPlayers = ConfigSelection(default="category", choices = [
				("category", _(" "))
				])

config.plugins.KravenFHD.CategoryAntialiasing = ConfigSelection(default="category", choices = [
				("category", _(" "))
				])

config.plugins.KravenFHD.CategoryDebug = ConfigSelection(default="category", choices = [
				("category", _(" "))
				])

#######################################################################

class KravenFHD(ConfigListScreen, Screen):
	skin = """
<screen name="KravenFHD-Setup" position="0,0" size="1280,720" flags="wfNoBorder" backgroundColor="#00000000">
  <widget font="Regular; 20" halign="left" valign="center" source="key_red" position="70,665" size="220,26" render="Label" backgroundColor="#00000000" foregroundColor="#00ffffff" transparent="1" zPosition="1" />
  <widget font="Regular; 20" halign="left" valign="center" source="key_green" position="320,665" size="220,26" render="Label" backgroundColor="#00000000" foregroundColor="#00ffffff" transparent="1" zPosition="1" />
  <widget font="Regular; 20" halign="left" valign="center" source="key_yellow" position="570,665" size="220,26" render="Label" backgroundColor="#00000000" foregroundColor="#00ffffff" transparent="1" zPosition="1" />
  <widget font="Regular; 20" halign="left" valign="center" source="key_blue" position="820,665" size="220,26" render="Label" backgroundColor="#00000000" foregroundColor="#00ffffff" transparent="1" zPosition="1" />
  <widget name="config" position="70,85" size="708,540" itemHeight="30" font="Regular;24" transparent="1" enableWrapAround="1" scrollbarMode="showOnDemand" zPosition="1" backgroundColor="#00000000" />
  <eLabel position="70,12" size="708,46" text="KravenFHD - Konfigurationstool" font="Regular; 35" valign="center" halign="left" transparent="1" backgroundColor="#00000000" foregroundColor="#00f0a30a" />
  <eLabel position="798,169" size="466,3" backgroundColor="#00f0a30a" />
  <eLabel position="798,431" size="466,3" backgroundColor="#00f0a30a" />
  <eLabel position="798,172" size="3,259" backgroundColor="#00f0a30a" />
  <eLabel position="1261,172" size="3,259" backgroundColor="#00f0a30a" />
  <eLabel backgroundColor="#00000000" position="0,0" size="1280,720" transparent="0" zPosition="-9" />
  <ePixmap pixmap="KravenFHD/buttons/key_red1.png" position="65,692" size="200,5" backgroundColor="#00000000" alphatest="blend" />
  <ePixmap pixmap="KravenFHD/buttons/key_green1.png" position="315,692" size="200,5" backgroundColor="#00000000" alphatest="blend" />
  <ePixmap pixmap="KravenFHD/buttons/key_yellow1.png" position="565,692" size="200,5" backgroundColor="#00000000" alphatest="blend" />
  <ePixmap pixmap="KravenFHD/buttons/key_blue1.png" position="815,692" size="200,5" backgroundColor="#00000000" alphatest="blend" />
  <widget source="global.CurrentTime" render="Label" position="1138,22" size="100,28" font="Regular;26" halign="right" backgroundColor="#00000000" transparent="1" valign="center" foregroundColor="#00ffffff">
    <convert type="ClockToText">Default</convert>
  </widget>
  <eLabel position="830,80" size="402,46" text="KravenFHD" font="Regular; 36" valign="center" halign="center" transparent="1" backgroundColor="#00000000" foregroundColor="#00f0a30a" />
  <eLabel position="845,126" size="372,40" text="Version: 1.1.0" font="Regular; 30" valign="center" halign="center" transparent="1" backgroundColor="#00000000" foregroundColor="#00ffffff" />
  <widget name="helperimage" position="801,172" size="460,259" zPosition="1" backgroundColor="#00000000" />
  <widget source="Canvas" render="Canvas" position="801,172" size="460,259" zPosition="-1" backgroundColor="#00000000" />
  <widget source="help" render="Label" position="847,440" size="368,196" font="Regular;20" backgroundColor="#00000000" foregroundColor="#00f0a30a" halign="center" valign="top" transparent="1" />
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

		self.UpdatePicture()

		self.timer = eTimer()
		self.timer.callback.append(self.updateMylist)
		self.onLayoutFinish.append(self.updateMylist)

		self.lastProfile="0"

		self.actClockstyle=""
		self.actWeatherstyle=""
		self.actChannelselectionstyle=""
		self.actCity=""

	def mylist(self):
		self.timer.start(100, True)

	def updateMylist(self):
		
		# page 1
		emptyLines=0
		list = []
		list.append(getConfigListEntry(_("About"), config.plugins.KravenFHD.About, _("The KravenFHD skin will be generated by this plugin according to your preferences. Make your settings and watch the changes in the preview window above. When finished, save your skin by pressing the green button and restart the GUI.")))
		list.append(getConfigListEntry(_(" "), ))
		list.append(getConfigListEntry(_("PROFILES __________________________________________________________________"), config.plugins.KravenFHD.CategoryProfiles, _("This sections offers all profile settings. Different settings can be saved, modified, shared and cloned. Read the FAQs.")))
		list.append(getConfigListEntry(_("Active Profile / Save"), config.plugins.KravenFHD.customProfile, _("Select the profile you want to work with. Profiles are saved automatically on switching them or by pressing the OK button. New profiles will be generated based on the actual one. Profiles are interchangeable between boxes.")))
		list.append(getConfigListEntry(_("Default Profile / Reset"), config.plugins.KravenFHD.defaultProfile, _("Select the default profile you want to use when resetting the active profile (OK button). You can add your own default profiles under /etc/enigma2/kraven_default_n (n<=20).")))
		list.append(getConfigListEntry(_(" "), ))
		list.append(getConfigListEntry(_("SYSTEM ____________________________________________________________________"), config.plugins.KravenFHD.CategorySystem, _("This sections offers all basic settings.")))
		list.append(getConfigListEntry(_("Icons (except Infobar)"), config.plugins.KravenFHD.IconStyle2, _("Choose between light and dark icons in system screens. The icons in the infobars are not affected.")))
		list.append(getConfigListEntry(_("Running Text (Delay)"), config.plugins.KravenFHD.RunningText, _("Choose the start delay for running text.")))
		if config.plugins.KravenFHD.RunningText.value in ("startdelay=2000","startdelay=4000","startdelay=6000","startdelay=8000","startdelay=10000","startdelay=15000","startdelay=20000"):
			list.append(getConfigListEntry(_("Running Text (Speed)"), config.plugins.KravenFHD.RunningTextSpeed, _("Choose the speed for running text.")))
		else:
			emptyLines+=1
		list.append(getConfigListEntry(_("Scrollbars"), config.plugins.KravenFHD.ScrollBar, _("Choose the width of scrollbars in lists or deactivate scrollbars completely.")))
		list.append(getConfigListEntry(_("Show Infobar-Background"), config.plugins.KravenFHD.IBColor, _("Choose whether you want to see the infobar background in all screens (bicolored background).")))
		list.append(getConfigListEntry(_("Menus"), config.plugins.KravenFHD.Logo, _("Choose from different options to display the system menus. Press red button for the FAQs with details on installing menu icons.")))
		if config.plugins.KravenFHD.Logo.value in ("metrix-icons","minitv-metrix-icons"):
			list.append(getConfigListEntry(_("Menu-Icons"), config.plugins.KravenFHD.MenuIcons, _("Choose from different icon sets for the menu screens. Many thanks to rennmaus and kleiner.teufel for their icon set.")))
		else:
			emptyLines+=1
		if config.plugins.KravenFHD.Logo.value in ("logo","metrix-icons"):
			list.append(getConfigListEntry(_("Menu-Transparency"), config.plugins.KravenFHD.MenuColorTrans, _("Choose the degree of background transparency for system menu screens.")))
		else:
			emptyLines+=1
		for i in range(emptyLines+3):
			list.append(getConfigListEntry(_(" "), ))
		
		# page 2
		emptyLines=0
		list.append(getConfigListEntry(_("GLOBAL COLORS _____________________________________________________________"), config.plugins.KravenFHD.CategoryGlobalColors, _("This sections offers offers all basic color settings.")))
		list.append(getConfigListEntry(_("Background"), config.plugins.KravenFHD.BackgroundColor, _("Choose the background color for all screens. You can choose from a list of predefined colors or create your own color using RGB sliders.")))
		if config.plugins.KravenFHD.BackgroundColor.value == "self":
			list.append(getConfigListEntry(_("          red"), config.plugins.KravenFHD.BackgroundSelfColorR, _("Set the intensity of this basic color with the slider.")))
			list.append(getConfigListEntry(_("          green"), config.plugins.KravenFHD.BackgroundSelfColorG, _("Set the intensity of this basic color with the slider.")))
			list.append(getConfigListEntry(_("          blue"), config.plugins.KravenFHD.BackgroundSelfColorB, _("Set the intensity of this basic color with the slider.")))
		else:
			emptyLines+=3
		list.append(getConfigListEntry(_("Background-Transparency"), config.plugins.KravenFHD.BackgroundColorTrans, _("Choose the degree of background transparency for all screens except system menus and channellists.")))
		list.append(getConfigListEntry(_("Listselection"), config.plugins.KravenFHD.SelectionBackground, _("Choose the background color of selection bars.")))
		list.append(getConfigListEntry(_("Listselection-Border"), config.plugins.KravenFHD.SelectionBorder, _("Choose the border color of selection bars or deactivate borders completely.")))
		list.append(getConfigListEntry(_("Listselection-Font"), config.plugins.KravenFHD.SelectionFont, _("Choose the color of the font in selection bars.")))
		list.append(getConfigListEntry(_("Progress-/Volumebar"), config.plugins.KravenFHD.Progress, _("Choose the color of progress bars.")))
		list.append(getConfigListEntry(_("Progress-Border"), config.plugins.KravenFHD.Border, _("Choose the border color of progress bars.")))
		list.append(getConfigListEntry(_("MiniTV-Border"), config.plugins.KravenFHD.MiniTVBorder, _("Choose the border color of MiniTV's.")))
		list.append(getConfigListEntry(_("Lines"), config.plugins.KravenFHD.Line, _("Choose the color of all lines. This affects dividers as well as the line in the center of some progress bars.")))
		list.append(getConfigListEntry(_("Primary-Font"), config.plugins.KravenFHD.Font1, _("Choose the color of the primary font. The primary font is used for list items, textboxes and other important information.")))
		list.append(getConfigListEntry(_("Secondary-Font"), config.plugins.KravenFHD.Font2, _("Choose the color of the secondary font. The secondary font is used for headers, labels and other additional information.")))
		list.append(getConfigListEntry(_("Marking-Font"), config.plugins.KravenFHD.MarkedFont, _("Choose the font color of marked list items.")))
		list.append(getConfigListEntry(_("Colorbutton-Font"), config.plugins.KravenFHD.ButtonText, _("Choose the font color of the color button labels.")))
		for i in range(emptyLines+1):
			list.append(getConfigListEntry(_(" "), ))
		
		# page 3
		emptyLines=0
		list.append(getConfigListEntry(_("INFOBAR ___________________________________________________________________"), config.plugins.KravenFHD.CategoryInfobar, _("This sections offers all settings for the infobar.")))
		list.append(getConfigListEntry(_("Infobar-Style"), config.plugins.KravenFHD.InfobarStyle, _("Choose from different infobar styles. Please note that not every style provides every feature. Therefore some features might be unavailable for the chosen style.")))
		list.append(getConfigListEntry(_("Infobar-Background-Style"), config.plugins.KravenFHD.IBStyle, _("Choose from different infobar background styles.")))
		if config.plugins.KravenFHD.IBStyle.value == "box":
			list.append(getConfigListEntry(_("Infobar-Box-Line"), config.plugins.KravenFHD.IBLine, _("Choose the color of the infobar box lines.")))
		else:
			emptyLines+=1
		list.append(getConfigListEntry(_("Infobar-Background"), config.plugins.KravenFHD.InfobarColor, _("Choose the background color of the infobars. You can choose from a list of predefined colors or create your own color using RGB sliders.")))
		if config.plugins.KravenFHD.InfobarColor.value == "self":
			list.append(getConfigListEntry(_("          red"), config.plugins.KravenFHD.InfobarSelfColorR, _("Set the intensity of this basic color with the slider.")))
			list.append(getConfigListEntry(_("          green"), config.plugins.KravenFHD.InfobarSelfColorG, _("Set the intensity of this basic color with the slider.")))
			list.append(getConfigListEntry(_("          blue"), config.plugins.KravenFHD.InfobarSelfColorB, _("Set the intensity of this basic color with the slider.")))
		else:
			emptyLines+=3
		list.append(getConfigListEntry(_("Infobar-Transparency"), config.plugins.KravenFHD.InfobarColorTrans, _("Choose the degree of background transparency for the infobars.")))
		list.append(getConfigListEntry(_("Primary-Infobar-Font"), config.plugins.KravenFHD.IBFont1, _("Choose the color of the primary infobar font.")))
		list.append(getConfigListEntry(_("Secondary-Infobar-Font"), config.plugins.KravenFHD.IBFont2, _("Choose the color of the secondary infobar font.")))
		list.append(getConfigListEntry(_("Infobar-Icons"), config.plugins.KravenFHD.IconStyle, _("Choose between light and dark infobar icons.")))
		if config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-x2","infobar-style-z1"):
			list.append(getConfigListEntry(_("Tuner number"), config.plugins.KravenFHD.IBtop, _("Choose from different options to display tuner.")))
		elif config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-nopicon","infobar-style-x1"):
			list.append(getConfigListEntry(_("Tuner number"), config.plugins.KravenFHD.tuner2, _("Choose from different options to display tuner.")))
		elif config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-zz1","infobar-style-zz4","infobar-style-zzz1"):
			list.append(getConfigListEntry(_("Tuner number"), config.plugins.KravenFHD.tuner, _("Choose from different options to display tuner.")))
		else:
			emptyLines+=1
		if config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-nopicon","infobar-style-x1","infobar-style-zz1","infobar-style-zz4","infobar-style-zzz1"):
			list.append(getConfigListEntry(_("Record-State"), config.plugins.KravenFHD.record2, _("Choose from different options to display recording state.")))
		elif config.plugins.KravenFHD.InfobarStyle.value == "infobar-style-zz2":
			list.append(getConfigListEntry(_("Record-State"), config.plugins.KravenFHD.record, _("Choose from different options to display recording state.")))
		elif config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-x2","infobar-style-z1"):
			if config.plugins.KravenFHD.IBtop.value == "infobar-x2-z1_top2":
				list.append(getConfigListEntry(_("Record-State"), config.plugins.KravenFHD.record2, _("Choose from different options to display record state.")))
			else:
				list.append(getConfigListEntry(_("Record-State"), config.plugins.KravenFHD.record3, _("Choose from different options to display record state.")))
		else:
			emptyLines+=1
		if config.plugins.KravenFHD.InfobarStyle.value == "infobar-style-x1":
			if not config.plugins.KravenFHD.tuner2.value == "10-tuner":
				list.append(getConfigListEntry(_("Infobox-Contents"), config.plugins.KravenFHD.Infobox, _("Choose which informations will be shown in the info box.")))
			else:
				emptyLines+=1
		elif config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-nopicon","infobar-style-x2","infobar-style-z1","infobar-style-zz1","infobar-style-zz4","infobar-style-zzz1"):
			list.append(getConfigListEntry(_("Infobox-Contents"), config.plugins.KravenFHD.Infobox, _("Choose which informations will be shown in the info box.")))
		else:
			emptyLines+=1
		if config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-nopicon","infobar-style-x1","infobar-style-x2","infobar-style-x3","infobar-style-z1","infobar-style-z2","infobar-style-zz1","infobar-style-zz4"):
			list.append(getConfigListEntry(_("Channelname/-number"), config.plugins.KravenFHD.InfobarChannelName, _("Choose from different options to show the channel name and number in the infobar.")))
			if not config.plugins.KravenFHD.InfobarChannelName.value == "none":
				list.append(getConfigListEntry(_("Channelname/-number-Font"), config.plugins.KravenFHD.ChannelnameFont, _("Choose the font color of channel name and number")))
			else:
				emptyLines+=1
		else:
			list.append(getConfigListEntry(_("Channelname/-number"), config.plugins.KravenFHD.InfobarChannelName2, _("Choose from different options to show the channel name and number in the infobar.")))
			if not config.plugins.KravenFHD.InfobarChannelName2.value == "none":
				list.append(getConfigListEntry(_("Channelname/-number-Font"), config.plugins.KravenFHD.ChannelnameFont, _("Choose the font color of channel name and number")))
			else:
				emptyLines+=1
		list.append(getConfigListEntry(_("System-Infos"), config.plugins.KravenFHD.SystemInfo, _("Choose from different additional windows with system informations or deactivate them completely.")))
		for i in range(emptyLines):
			list.append(getConfigListEntry(_(" "), ))
		
		# page 4
		emptyLines=0
		list.append(getConfigListEntry(_("WEATHER ___________________________________________________________________"), config.plugins.KravenFHD.CategoryWeather, _("This sections offers all weather settings.")))
		if config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-nopicon","infobar-style-x1","infobar-style-x3","infobar-style-z2","infobar-style-zz1","infobar-style-zz2","infobar-style-zz3","infobar-style-zz4","infobar-style-zzz1"):
			list.append(getConfigListEntry(_("Weather"), config.plugins.KravenFHD.WeatherStyle, _("Choose from different options to show the weather in the infobar.")))
			self.actWeatherstyle=config.plugins.KravenFHD.WeatherStyle.value
		elif config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-x2","infobar-style-z1"):
			list.append(getConfigListEntry(_("Weather"), config.plugins.KravenFHD.WeatherStyle2, _("Activate or deactivate displaying the weather in the infobar.")))
			self.actWeatherstyle=config.plugins.KravenFHD.WeatherStyle2.value
		list.append(getConfigListEntry(_("Search by"), config.plugins.KravenFHD.weather_search_over, _("Choose from different options to specify your location.")))
		if config.plugins.KravenFHD.weather_search_over.value == 'name':
			list.append(getConfigListEntry(_("Search String"), config.plugins.KravenFHD.weather_cityname, _("Specify any search string for your location (zip/city/district/state single or combined). Press OK to use the virtual keyboard. Step up or down in the menu to start the search.")))
		elif config.plugins.KravenFHD.weather_search_over.value == 'gmcode':
			list.append(getConfigListEntry(_("GM Code"), config.plugins.KravenFHD.weather_gmcode, _("Specify the GM code for your location. You can find it at https://weather.codes. Press OK to use the virtual keyboard. Step up or down in the menu to start the search.")))
		else:
			emptyLines+=1
		list.append(getConfigListEntry(_("Server"), config.plugins.KravenFHD.weather_server, _("Choose from different servers for the weather data.")))
		list.append(getConfigListEntry(_("Language"), config.plugins.KravenFHD.weather_language, _("Specify the language for the weather output.")))
		list.append(getConfigListEntry(_("Refresh interval (in minutes)"), config.plugins.KravenFHD.refreshInterval, _("Choose the frequency of loading weather data from the internet.")))
		list.append(getConfigListEntry(_("Weather-Style"), config.plugins.KravenFHD.WeatherView, _("Choose between graphical weather symbols and Meteo symbols.")))
		if config.plugins.KravenFHD.WeatherView.value == "meteo":
			list.append(getConfigListEntry(_("Meteo-Color"), config.plugins.KravenFHD.MeteoColor, _("Choose between light and dark Meteo symbols.")))
		else:
			emptyLines+=1
		for i in range(emptyLines+1):
			list.append(getConfigListEntry(_(" "), ))
		
		# page 4 (category 2)
		emptyLines=0
		if not config.plugins.KravenFHD.InfobarStyle.value == "infobar-style-zz4":
			list.append(getConfigListEntry(_("CLOCK _____________________________________________________________________"), config.plugins.KravenFHD.CategoryClock, _("This sections offers all settings for the different clocks.")))
			list.append(getConfigListEntry(_("Clock-Style"), config.plugins.KravenFHD.ClockStyle, _("Choose from different options to show the clock in the infobar.")))
			self.actClockstyle=config.plugins.KravenFHD.ClockStyle.value
			if self.actClockstyle == "clock-analog":
				list.append(getConfigListEntry(_("Analog-Clock-Color"), config.plugins.KravenFHD.AnalogStyle, _("Choose from different colors for the analog type clock in the infobar.")))
			elif self.actClockstyle == "clock-android":
				list.append(getConfigListEntry(_("Android-Temp-Color"), config.plugins.KravenFHD.Android, _("Choose the font color of android-clock temperature.")))
			elif self.actClockstyle == "clock-weather":
				list.append(getConfigListEntry(_("Weather-Icon-Size"), config.plugins.KravenFHD.ClockIconSize, _("Choose the size of the icon for 'weather icon' clock.")))
			else:
				emptyLines+=1
		else:
			emptyLines+=3
			self.actClockstyle="none"
		for i in range(emptyLines+5):
			list.append(getConfigListEntry(_(" "), ))
		
		# page 5
		emptyLines=0
		list.append(getConfigListEntry(_("ECM INFOS _________________________________________________________________"), config.plugins.KravenFHD.CategoryECMInfos, _("This sections offers all settings for showing the decryption infos.")))
		list.append(getConfigListEntry(_("Show ECM Infos"), config.plugins.KravenFHD.ECMVisible, _("Choose from different options where to display the ECM informations.")))
		if config.plugins.KravenFHD.InfobarStyle.value == "infobar-style-x1" and not config.plugins.KravenFHD.ECMVisible.value == "none":
			list.append(getConfigListEntry(_("ECM Infos"), config.plugins.KravenFHD.ECMLine1, _("Choose from different options to display the ECM informations.")))
			list.append(getConfigListEntry(_("Show 'free to air'"), config.plugins.KravenFHD.FTA, _("Choose whether 'free to air' is displayed or not for unencrypted channels.")))
			list.append(getConfigListEntry(_("ECM-Font"), config.plugins.KravenFHD.ECMFont, _("Choose the font color of the ECM information.")))
		elif config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-nopicon","infobar-style-x2","infobar-style-x3","infobar-style-z1","infobar-style-z2") and not config.plugins.KravenFHD.ECMVisible.value == "none":
			list.append(getConfigListEntry(_("ECM Infos"), config.plugins.KravenFHD.ECMLine2, _("Choose from different options to display the ECM informations.")))
			list.append(getConfigListEntry(_("Show 'free to air'"), config.plugins.KravenFHD.FTA, _("Choose whether 'free to air' is displayed or not for unencrypted channels.")))
			list.append(getConfigListEntry(_("ECM-Font"), config.plugins.KravenFHD.ECMFont, _("Choose the font color of the ECM information.")))
		elif config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-zz1","infobar-style-zz2","infobar-style-zz3","infobar-style-zz4","infobar-style-zzz1") and not config.plugins.KravenFHD.ECMVisible.value == "none":
			list.append(getConfigListEntry(_("ECM Infos"), config.plugins.KravenFHD.ECMLine3, _("Choose from different options to display the ECM informations.")))
			list.append(getConfigListEntry(_("Show 'free to air'"), config.plugins.KravenFHD.FTA, _("Choose whether 'free to air' is displayed or not for unencrypted channels.")))
			list.append(getConfigListEntry(_("ECM-Font"), config.plugins.KravenFHD.ECMFont, _("Choose the font color of the ECM information.")))
		else:
			emptyLines+=3
		for i in range(emptyLines+1):
			list.append(getConfigListEntry(_(" "), ))
		
		# page 5 (category 2)
		emptyLines=0
		list.append(getConfigListEntry(_("VIEWS _____________________________________________________________________"), config.plugins.KravenFHD.CategoryViews, _("This sections offers all settings for skinned plugins.")))
		list.append(getConfigListEntry(_("Volume"), config.plugins.KravenFHD.Volume, _("Choose from different styles for the volume display.")))
		list.append(getConfigListEntry(_("CoolTVGuide"), config.plugins.KravenFHD.CoolTVGuide, _("Choose from different styles for CoolTVGuide.")))
		list.append(getConfigListEntry(_("SecondInfobar"), config.plugins.KravenFHD.SIB, _("Choose from different styles for SecondInfobar.")))
		list.append(getConfigListEntry(_("SerienRecorder"), config.plugins.KravenFHD.SerienRecorder, _("Choose whether you want the Kraven skin to be applied to 'Serienrecorder' or not. Activation of this option prohibits the skin selection in the SR-plugin.")))
		if fileExists("/usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/plugin.py"):
			list.append(getConfigListEntry(_("MediaPortal"), config.plugins.KravenFHD.MediaPortal, _("Choose whether you want the Kraven skin to be applied to 'MediaPortal' or not. To remove it again, you must deactivate it here and activate another skin in 'MediaPortal'.")))
		else:
			emptyLines+=1
		list.append(getConfigListEntry(_("NumberZap"), config.plugins.KravenFHD.NumberZapExt, _("Choose from different styles for NumberZap.")))
		list.append(getConfigListEntry(_("SplitScreen"), config.plugins.KravenFHD.SplitScreen, _("Choose from different styles to display SplitScreen.")))
		for i in range(emptyLines+1):
			list.append(getConfigListEntry(_(" "), ))
		
		# page 5 (category 3)
		emptyLines=0
		list.append(getConfigListEntry(_("MOVIESELECTION ____________________________________________________________"), config.plugins.KravenFHD.CategoryMovieSelection, _("This sections offers all settings for MovieSelection.")))
		list.append(getConfigListEntry(_("MovieSelection-Style"), config.plugins.KravenFHD.MovieSelection, _("Choose from different styles for MovieSelection.")))
		list.append(getConfigListEntry(_("EPG Fontsize"), config.plugins.KravenFHD.MovieSelectionEPGSize, _("Choose the font size of event description.")))
		
		# page 6
		emptyLines=0
		list.append(getConfigListEntry(_("CHANNELLIST _______________________________________________________________"), config.plugins.KravenFHD.CategoryChannellist, _("This sections offers all channellist settings.")))
		if SystemInfo.get("NumVideoDecoders",1) > 1:
			list.append(getConfigListEntry(_("Channellist-Style"), config.plugins.KravenFHD.ChannelSelectionStyle2, _("Choose from different styles for the channel selection screen.")))
			self.actChannelselectionstyle=config.plugins.KravenFHD.ChannelSelectionStyle2.value
		else:
			list.append(getConfigListEntry(_("Channellist-Style"), config.plugins.KravenFHD.ChannelSelectionStyle, _("Choose from different styles for the channel selection screen.")))
			self.actChannelselectionstyle=config.plugins.KravenFHD.ChannelSelectionStyle.value
		if self.actChannelselectionstyle in ("channelselection-style-minitv","channelselection-style-minitv2","channelselection-style-minitv22","channelselection-style-minitv33","channelselection-style-minitv4","channelselection-style-nobile-minitv","channelselection-style-nobile-minitv33"):
			list.append(getConfigListEntry(_("Channellist-Mode"), config.plugins.KravenFHD.ChannelSelectionMode, _("Choose between direct zapping (1xOK) and zapping after preview (2xOK).")))
		else:
			emptyLines+=1
		if not self.actChannelselectionstyle in ("channelselection-style-minitv","channelselection-style-minitv2","channelselection-style-minitv3","channelselection-style-minitv4","channelselection-style-minitv22","channelselection-style-nobile-minitv","channelselection-style-nobile-minitv3"):
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
		list.append(getConfigListEntry(_("'not available'-Font"), config.plugins.KravenFHD.ChannelSelectionServiceNA, _("Choose the font color of channels that are unavailable at the moment.")))
		list.append(getConfigListEntry(_("Primetime"), config.plugins.KravenFHD.Primetimeavailable, _("Choose whether primetime program information is displayed or not.")))
		if config.plugins.KravenFHD.Primetimeavailable.value == "primetime-on":
			list.append(getConfigListEntry(_("Primetime-Time"), config.plugins.KravenFHD.Primetime, _("Specify the time for your primetime.")))
			list.append(getConfigListEntry(_("Primetime-Font"), config.plugins.KravenFHD.PrimetimeFont, _("Choose the font color of the primetime information.")))
		else:
			emptyLines+=2
		for i in range(emptyLines+7):
			list.append(getConfigListEntry(_(" "), ))
		
		# page 7
		emptyLines=0
		list.append(getConfigListEntry(_("ENHANCED MOVIE CENTER _____________________________________________________"), config.plugins.KravenFHD.CategoryEMC, _("This sections offers all settings for EMC ('EnhancedMovieCenter').")))
		list.append(getConfigListEntry(_("EMC-Style"), config.plugins.KravenFHD.EMCStyle, _("Choose from different styles for EnhancedMovieCenter.")))
		list.append(getConfigListEntry(_("EPG Fontsize"), config.plugins.KravenFHD.EMCEPGSize, _("Choose the font size of event description.")))
		list.append(getConfigListEntry(_("Custom EMC-Selection-Colors"), config.plugins.KravenFHD.EMCSelectionColors, _("Choose whether you want to customize the selection-colors for EnhancedMovieCenter.")))
		if config.plugins.KravenFHD.EMCSelectionColors.value == "emc-colors-on":
			list.append(getConfigListEntry(_("EMC-Listselection"), config.plugins.KravenFHD.EMCSelectionBackground, _("Choose the background color of selection bars for EnhancedMovieCenter.")))
			list.append(getConfigListEntry(_("EMC-Selection-Font"), config.plugins.KravenFHD.EMCSelectionFont, _("Choose the color of the font in selection bars for EnhancedMovieCenter.")))
		else:
			emptyLines+=2
		for i in range(emptyLines+1):
			list.append(getConfigListEntry(_(" "), ))
		
		# page 7 (category 2)
		emptyLines=0
		list.append(getConfigListEntry(_("PLAYER ____________________________________________________________________"), config.plugins.KravenFHD.CategoryPlayers, _("This sections offers all settings for the movie players.")))
		list.append(getConfigListEntry(_("Clock"), config.plugins.KravenFHD.PlayerClock, _("Choose from different options to show the clock in the players.")))
		if config.plugins.KravenFHD.PlayerClock.value == "player-android":
			list.append(getConfigListEntry(_("Android-Temp-Color"), config.plugins.KravenFHD.Android2, _("Choose the font color of android-clock temperature.")))
		else:
			emptyLines+=1
		list.append(getConfigListEntry(_("PVRState"), config.plugins.KravenFHD.PVRState, _("Choose from different options to display the PVR state.")))
		for i in range(emptyLines+1):
			list.append(getConfigListEntry(_(" "), ))
		
		# page 7 (category 3)
		emptyLines=0
		if config.plugins.KravenFHD.IBStyle.value == "gradient":
			list.append(getConfigListEntry(_("ANTIALIASING BRIGHTNESS ________________________________________________________________"), config.plugins.KravenFHD.CategoryAntialiasing, _("This sections offers all antialiasing settings. Distortions or color frames around fonts can be reduced by this settings.")))
			list.append(getConfigListEntry(_("Infobar"), config.plugins.KravenFHD.InfobarAntialias, _("Reduce distortions (faint/blurry) or color frames around fonts in the infobar and widgets by adjusting the antialiasing brightness.")))
			list.append(getConfigListEntry(_("ECM Infos"), config.plugins.KravenFHD.ECMLineAntialias, _("Reduce distortions (faint/blurry) or color frames around the ECM information in the infobar by adjusting the antialiasing brightness.")))
			list.append(getConfigListEntry(_("Screens"), config.plugins.KravenFHD.ScreensAntialias, _("Reduce distortions (faint/blurry) or color frames around fonts at top and bottom of screens by adjusting the antialiasing brightness.")))
		else:
			emptyLines+=4
		for i in range(emptyLines+2):
			list.append(getConfigListEntry(_(" "), ))

		# page 8
		list.append(getConfigListEntry(_("DEBUG _____________________________________________________________________"), config.plugins.KravenFHD.CategoryDebug, _("This sections offers all debug settings.")))
		list.append(getConfigListEntry(_("Screennames"), config.plugins.KravenFHD.DebugNames, _("Activate or deactivate small screen names for debugging purposes.")))

		self["config"].list = list
		self["config"].l.setList(list)
		self.updateHelp()
		self["helperimage"].hide()
		self.ShowPicture()

		position = self["config"].instance.getCurrentIndex()
		if position == 0:
			self["key_yellow"].setText("<< " + _("debug"))
			self["key_blue"].setText(_("profiles") + " >>")
		if (2 <= position <= 4):
			self["key_yellow"].setText("<< " + _("about"))
			self["key_blue"].setText(_("system") + " >>")
		if (6 <= position <= 17):
			self["key_yellow"].setText("<< " + _("profiles"))
			self["key_blue"].setText(_("global colors") + " >>")
		if (18 <= position <= 35):
			self["key_yellow"].setText("<< " + _("system"))
			self["key_blue"].setText(_("infobar") + " >>")
		if (36 <= position <= 53):
			self["key_yellow"].setText("<< " + _("global colors"))
			self["key_blue"].setText(_("weather") + " >>")
		if config.plugins.KravenFHD.InfobarStyle.value == "infobar-style-zz4":
			if (54 <= position <= 62):
				self["key_yellow"].setText("<< " + _("infobar"))
				self["key_blue"].setText(_("ECM infos") + " >>")
		else:
			if (54 <= position <= 62):
				self["key_yellow"].setText("<< " + _("infobar"))
				self["key_blue"].setText(_("clock") + " >>")
		if (64 <= position <= 66):
			self["key_yellow"].setText("<< " + _("weather"))
			self["key_blue"].setText(_("ECM infos") + " >>")
		if (72 <= position <= 76):
			if config.plugins.KravenFHD.InfobarStyle.value == "infobar-style-zz4":
				self["key_yellow"].setText("<< " + _("weather"))
			else:
				self["key_yellow"].setText("<< " + _("clock"))
			self["key_blue"].setText(_("views") + " >>")
		if (78 <= position <= 85):
			self["key_yellow"].setText("<< " + _("ECM infos"))
			self["key_blue"].setText(_("MovieSelection") + " >>")
			
		if (87 <= position <= 89):
			self["key_yellow"].setText("<< " + _("views"))
			self["key_blue"].setText(_("channellist") + " >>")
			
		if (90 <= position <= 107):
			self["key_yellow"].setText("<< " + _("MovieSelection"))
			self["key_blue"].setText(_("EMC") + " >>")
		if (108 <= position <= 113):
			self["key_yellow"].setText("<< " + _("channellist"))
			self["key_blue"].setText(_("player") + " >>")
		if config.plugins.KravenFHD.IBStyle.value == "box":
			if (115 <= position <= 118):
				self["key_yellow"].setText("<< " + _("EMC"))
				self["key_blue"].setText(_("debug") + " >>")
		else:
			if (115 <= position <= 118):
				self["key_yellow"].setText("<< " + _("EMC"))
				self["key_blue"].setText(_("antialiasing") + " >>")
		if (120 <= position <= 123):
			self["key_yellow"].setText("<< " + _("player"))
			self["key_blue"].setText(_("debug") + " >>")
		if (126 <= position <= 127):
			if config.plugins.KravenFHD.IBStyle.value == "box":
				self["key_yellow"].setText("<< " + _("player"))
			else:
				self["key_yellow"].setText("<< " + _("antialiasing"))
			self["key_blue"].setText(_("about") + " >>")

		option = self["config"].getCurrent()[1]
		if option == config.plugins.KravenFHD.customProfile:
			if config.plugins.KravenFHD.customProfile.value==self.lastProfile:
				self.saveProfile(msg=False)
			else:
				self.loadProfile()
				self.lastProfile=config.plugins.KravenFHD.customProfile.value
		if option.value == "none":
			self.showText(62,_("Off"))
		elif option == config.plugins.KravenFHD.customProfile:
			self.showText(31,"/etc/enigma2/kravenfhd_profile_"+str(config.plugins.KravenFHD.customProfile.value))
		elif option == config.plugins.KravenFHD.defaultProfile:
			if fileExists("/usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/images/"+str(config.plugins.KravenFHD.defaultProfile.value)+".jpg"):
				self["helperimage"].show()
			else:
				self.showText(31,"/etc/enigma2/kravenfhd_default_"+str(config.plugins.KravenFHD.defaultProfile.value))
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
			if option.value == "4-tuner":
				self.showText(62,_("4 Tuner"))
			elif option.value == "8-tuner":
				self.showText(62,_("8 Tuner"))
		elif option == config.plugins.KravenFHD.tuner2:
			if option.value == "2-tuner":
				self.showText(62,_("2 Tuner"))
			if option.value == "4-tuner":
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
		elif option in (config.plugins.KravenFHD.weather_gmcode,config.plugins.KravenFHD.weather_cityname,config.plugins.KravenFHD.weather_server,config.plugins.KravenFHD.weather_search_over):
			self.get_weather_data()
			self.showText(25,self.actCity)
		elif option == config.plugins.KravenFHD.weather_language:
			self.showText(75,option.value)
		elif option == config.plugins.KravenFHD.refreshInterval:
			if option.value == "0":
				self.showText(62,_("Off"))
			elif option.value == "15":
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
			if config.plugins.KravenFHD.ChannelSelectionEPGSize1.value == "small":
				self.showText(36,_("description - 28 Pixel \nEPG list - 26 Pixel \nprimetime - 26 Pixel"))
			elif config.plugins.KravenFHD.ChannelSelectionEPGSize1.value == "big":
				self.showText(36,_("description - 32 Pixel \nEPG list - 29 Pixel \nprimetime - 29 Pixel"))
		elif option == config.plugins.KravenFHD.ChannelSelectionEPGSize2:
			if config.plugins.KravenFHD.ChannelSelectionEPGSize2.value == "small":
				self.showText(36,_("EPG list - 32 Pixel \nprimetime - 32 Pixel"))
			elif config.plugins.KravenFHD.ChannelSelectionEPGSize2.value == "big":
				self.showText(36,_("EPG list - 36 Pixel \nprimetime - 36 Pixel"))
		elif option == config.plugins.KravenFHD.ChannelSelectionEPGSize3:
			if config.plugins.KravenFHD.ChannelSelectionEPGSize3.value == "small":
				self.showText(36,_("description - 32 Pixel \nEPG list - 32 Pixel \nprimetime - 32 Pixel"))
			elif config.plugins.KravenFHD.ChannelSelectionEPGSize3.value == "big":
				self.showText(36,_("description - 36 Pixel \nEPG list - 36 Pixel \nprimetime - 36 Pixel"))
		elif option == config.plugins.KravenFHD.MovieSelectionEPGSize:
			if config.plugins.KravenFHD.MovieSelectionEPGSize.value == "small":
				self.showText(44,_("33 Pixel"))
			elif config.plugins.KravenFHD.MovieSelectionEPGSize.value == "big":
				self.showText(48,_("36 Pixel"))
		elif option == config.plugins.KravenFHD.EMCEPGSize:
			if config.plugins.KravenFHD.EMCEPGSize.value == "small":
				self.showText(44,_("33 Pixel"))
			elif config.plugins.KravenFHD.EMCEPGSize.value == "big":
				self.showText(48,_("36 Pixel"))
		elif option == config.plugins.KravenFHD.ClockIconSize:
			if config.plugins.KravenFHD.ClockIconSize.value == "size-144":
				self.showText(60,"144 Pixel")
			elif config.plugins.KravenFHD.ClockIconSize.value == "size-192":
				self.showText(80,"192 Pixel")
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
		elif option == config.plugins.KravenFHD.BackgroundColor:
			if config.plugins.KravenFHD.BackgroundColor.value == "self":
				self["helperimage"].show()
			else:
				self.showColor(self.hexRGB(config.plugins.KravenFHD.BackgroundColor.value))
		elif option in (config.plugins.KravenFHD.BackgroundSelfColorR,config.plugins.KravenFHD.BackgroundSelfColorG,config.plugins.KravenFHD.BackgroundSelfColorB):
			self.showColor(self.RGB(int(config.plugins.KravenFHD.BackgroundSelfColorR.value), int(config.plugins.KravenFHD.BackgroundSelfColorG.value), int(config.plugins.KravenFHD.BackgroundSelfColorB.value)))
		elif option == config.plugins.KravenFHD.SelectionBackground:
			self.showColor(self.hexRGB(config.plugins.KravenFHD.SelectionBackground.value))
		elif option == config.plugins.KravenFHD.SelectionBorder:
			self.showColor(self.hexRGB(config.plugins.KravenFHD.SelectionBorder.value))
		elif option == config.plugins.KravenFHD.EMCSelectionBackground:
			self.showColor(self.hexRGB(config.plugins.KravenFHD.EMCSelectionBackground.value))
		elif option == config.plugins.KravenFHD.Progress:
			if config.plugins.KravenFHD.Progress.value == "progress":
				self["helperimage"].show()
			else:
				self.showColor(self.hexRGB(config.plugins.KravenFHD.Progress.value))
		elif option == config.plugins.KravenFHD.Border:
			self.showColor(self.hexRGB(config.plugins.KravenFHD.Border.value))
		elif option == config.plugins.KravenFHD.MiniTVBorder:
			self.showColor(self.hexRGB(config.plugins.KravenFHD.MiniTVBorder.value))
		elif option == config.plugins.KravenFHD.IBLine:
			self.showColor(self.hexRGB(config.plugins.KravenFHD.IBLine.value))
		elif option == config.plugins.KravenFHD.Line:
			self.showColor(self.hexRGB(config.plugins.KravenFHD.Line.value))
		elif option == config.plugins.KravenFHD.Font1:
			self.showColor(self.hexRGB(config.plugins.KravenFHD.Font1.value))
		elif option == config.plugins.KravenFHD.Font2:
			self.showColor(self.hexRGB(config.plugins.KravenFHD.Font2.value))
		elif option == config.plugins.KravenFHD.IBFont1:
			self.showColor(self.hexRGB(config.plugins.KravenFHD.IBFont1.value))
		elif option == config.plugins.KravenFHD.IBFont2:
			self.showColor(self.hexRGB(config.plugins.KravenFHD.IBFont2.value))
		elif option == config.plugins.KravenFHD.SelectionFont:
			self.showColor(self.hexRGB(config.plugins.KravenFHD.SelectionFont.value))
		elif option == config.plugins.KravenFHD.EMCSelectionFont:
			self.showColor(self.hexRGB(config.plugins.KravenFHD.EMCSelectionFont.value))
		elif option == config.plugins.KravenFHD.MarkedFont:
			self.showColor(self.hexRGB(config.plugins.KravenFHD.MarkedFont.value))
		elif option == config.plugins.KravenFHD.ButtonText:
			self.showColor(self.hexRGB(config.plugins.KravenFHD.ButtonText.value))
		elif option == config.plugins.KravenFHD.Android:
			self.showColor(self.hexRGB(config.plugins.KravenFHD.Android.value))
		elif option == config.plugins.KravenFHD.Android2:
			self.showColor(self.hexRGB(config.plugins.KravenFHD.Android2.value))
		elif option == config.plugins.KravenFHD.ChannelSelectionServiceNA:
			self.showColor(self.hexRGB(config.plugins.KravenFHD.ChannelSelectionServiceNA.value))
		elif option == config.plugins.KravenFHD.InfobarColor:
			if config.plugins.KravenFHD.InfobarColor.value == "self":
				self["helperimage"].show()
			else:
				self.showColor(self.hexRGB(config.plugins.KravenFHD.InfobarColor.value))
		elif option in (config.plugins.KravenFHD.InfobarSelfColorR,config.plugins.KravenFHD.InfobarSelfColorG,config.plugins.KravenFHD.InfobarSelfColorB):
			self.showColor(self.RGB(int(config.plugins.KravenFHD.InfobarSelfColorR.value), int(config.plugins.KravenFHD.InfobarSelfColorG.value), int(config.plugins.KravenFHD.InfobarSelfColorB.value)))
		elif option == config.plugins.KravenFHD.ChannelnameFont:
			self.showColor(self.hexRGB(config.plugins.KravenFHD.ChannelnameFont.value))
		elif option == config.plugins.KravenFHD.ECMFont:
			self.showColor(self.hexRGB(config.plugins.KravenFHD.ECMFont.value))
		elif option == config.plugins.KravenFHD.PrimetimeFont:
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
			returnValue = self["config"].getCurrent()[1].value
			if returnValue in ("startdelay=2000","startdelay=4000","startdelay=6000","startdelay=8000","startdelay=10000","startdelay=15000","startdelay=20000"):
				path = "/usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/images/running-delay.jpg"
			elif returnValue in ("steptime=200","steptime=100","steptime=66","steptime=50"):
				path = "/usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/images/running-speed.jpg"
			elif returnValue in ("about","about2"):
				path = "/usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/images/about.png"
			elif returnValue == ("meteo-light"):
				path = "/usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/images/meteo.jpg"
			elif returnValue == "progress":
				path = "/usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/images/colorfull.jpg"
			elif returnValue in ("self","emc-colors-on"):
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
			elif returnValue == "record-blink":
				path = "/usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/images/record-shine.jpg"
			elif returnValue == "tuner-blink":
				path = "/usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/images/tuner-shine.jpg"
			elif returnValue == "record+tuner-blink":
				path = "/usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/images/record+tuner-shine.jpg"
			elif returnValue in ("only-infobar","gradient"):
				path = "/usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/images/infobar-style-x3.jpg"
			elif returnValue in ("0C","18","32","58","7E"):
				path = "/usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/images/transparent.jpg"
			else:
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
			self.PicLoad.startDecode(self.picPath)
			self.picPath = None
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
		pass

	def keyUp(self):
		pass

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
		if position == 0:
			self["config"].instance.moveSelectionTo(126)
		if (2 <= position <= 4):
			self["config"].instance.moveSelectionTo(0)
		if (6 <= position <= 17):
			self["config"].instance.moveSelectionTo(2)
		if (18 <= position <= 35):
			self["config"].instance.moveSelectionTo(6)
		if (36 <= position <= 53):
			self["config"].instance.moveSelectionTo(18)
		if (54 <= position <= 62):
			self["config"].instance.moveSelectionTo(36)
		if (64 <= position <= 66):
			self["config"].instance.moveSelectionTo(54)
		if (72 <= position <= 76):
			if config.plugins.KravenFHD.InfobarStyle.value == "infobar-style-zz4":
				self["config"].instance.moveSelectionTo(54)
			else:
				self["config"].instance.moveSelectionTo(64)
		if (78 <= position <= 85):
			self["config"].instance.moveSelectionTo(72)
		if (87 <= position <= 89):
			self["config"].instance.moveSelectionTo(78)
		if (90 <= position <= 107):
			self["config"].instance.moveSelectionTo(87)
		if (108 <= position <= 113):
			self["config"].instance.moveSelectionTo(90)
		if (115 <= position <= 118):
			self["config"].instance.moveSelectionTo(108)
		if (120 <= position <= 123):
			self["config"].instance.moveSelectionTo(115)
		if (126 <= position <= 127):
			if config.plugins.KravenFHD.IBStyle.value == "box":
				self["config"].instance.moveSelectionTo(115)
			else:
				self["config"].instance.moveSelectionTo(120)
		self.mylist()

	def categoryUp(self):
		position = self["config"].instance.getCurrentIndex()
		if position == 0:
			self["config"].instance.moveSelectionTo(2)
		if (2 <= position <= 4):
			self["config"].instance.moveSelectionTo(6)
		if (6 <= position <= 17):
			self["config"].instance.moveSelectionTo(18)
		if (18 <= position <= 35):
			self["config"].instance.moveSelectionTo(36)
		if (36 <= position <= 53):
			self["config"].instance.moveSelectionTo(54)
		if config.plugins.KravenFHD.InfobarStyle.value == "infobar-style-zz4":
			if (54 <= position <= 63):
				self["config"].instance.moveSelectionTo(72)
		else:
			if (54 <= position <= 63):
				self["config"].instance.moveSelectionTo(64)
		if (64 <= position <= 66):
			self["config"].instance.moveSelectionTo(72)
		if (72 <= position <= 76):
			self["config"].instance.moveSelectionTo(78)
		if (78 <= position <= 85):
			self["config"].instance.moveSelectionTo(87)
		if (87 <= position <= 89):
			self["config"].instance.moveSelectionTo(90)
		if (90 <= position <= 107):
			self["config"].instance.moveSelectionTo(108)
		if (108 <= position <= 113):
			self["config"].instance.moveSelectionTo(115)
		if config.plugins.KravenFHD.IBStyle.value == "box":
			if (115 <= position <= 118):
					self["config"].instance.moveSelectionTo(126)
		else:
			if (115 <= position <= 118):
				self["config"].instance.moveSelectionTo(120)
		if (120 <= position <= 123):
			self["config"].instance.moveSelectionTo(126)
		if (126 <= position <= 127):
			self["config"].instance.moveSelectionTo(0)
		self.mylist()

	def keyVirtualKeyBoardCallBack(self, callback):
		try:
			if callback:  
				self["config"].getCurrent()[1].value = callback
			else:
				pass
		except:
			pass

	def OK(self):
		option = self["config"].getCurrent()[1]
		if option in (config.plugins.KravenFHD.weather_cityname,config.plugins.KravenFHD.weather_gmcode):
			from Screens.VirtualKeyBoard import VirtualKeyBoard
			text = self["config"].getCurrent()[1].value
			if config.plugins.KravenFHD.weather_search_over.value == 'name':
				title = _("Enter the city name of your location:")
			elif config.plugins.KravenFHD.weather_search_over.value == 'gmcode':
				title = _("Enter the GM code for your location:")
			self.session.openWithCallback(self.keyVirtualKeyBoardCallBack, VirtualKeyBoard, title = title, text = text)
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
		if config.plugins.KravenFHD.BackgroundColor.value == "self":
			self.skincolorbackgroundcolor = str(hex(config.plugins.KravenFHD.BackgroundSelfColorR.value)[2:4]).zfill(2) + str(hex(config.plugins.KravenFHD.BackgroundSelfColorG.value)[2:4]).zfill(2) + str(hex(config.plugins.KravenFHD.BackgroundSelfColorB.value)[2:4]).zfill(2)
		else:
			self.skincolorbackgroundcolor = config.plugins.KravenFHD.BackgroundColor.value
		self.skinSearchAndReplace.append(['name="Kravenbg" value="#00000000', 'name="Kravenbg" value="#00' + self.skincolorbackgroundcolor])

		### Background Transparency (global)
		self.skinSearchAndReplace.append(['name="Kravenbg" value="#00', 'name="Kravenbg" value="#' + config.plugins.KravenFHD.BackgroundColorTrans.value])

		### Background2 (non-transparent)
		if config.plugins.KravenFHD.BackgroundColor.value == "self":
			self.skinSearchAndReplace.append(['name="Kravenbg2" value="#00000000', 'name="Kravenbg2" value="#00' + self.skincolorbackgroundcolor])
		else:
			self.skinSearchAndReplace.append(['name="Kravenbg2" value="#00000000', 'name="Kravenbg2" value="#00' + config.plugins.KravenFHD.BackgroundColor.value])

		### Background3 (Menus Transparency)
		if config.plugins.KravenFHD.Logo.value in ("logo","metrix-icons"):
			if config.plugins.KravenFHD.BackgroundColor.value == "self":
				self.skinSearchAndReplace.append(['name="Kravenbg3" value="#00000000', 'name="Kravenbg3" value="#' + config.plugins.KravenFHD.MenuColorTrans.value + self.skincolorbackgroundcolor])
			else:
				self.skinSearchAndReplace.append(['name="Kravenbg3" value="#00000000', 'name="Kravenbg3" value="#' + config.plugins.KravenFHD.MenuColorTrans.value + config.plugins.KravenFHD.BackgroundColor.value])
		else:
			if config.plugins.KravenFHD.BackgroundColor.value == "self":
				self.skinSearchAndReplace.append(['name="Kravenbg3" value="#00000000', 'name="Kravenbg3" value="#00' + self.skincolorbackgroundcolor])
			else:
				self.skinSearchAndReplace.append(['name="Kravenbg3" value="#00000000', 'name="Kravenbg3" value="#00' + config.plugins.KravenFHD.BackgroundColor.value])

		### Background4 (Channellist)
		if config.plugins.KravenFHD.BackgroundColor.value == "self":
			self.skinSearchAndReplace.append(['name="Kravenbg4" value="#00000000', 'name="Kravenbg4" value="#' + config.plugins.KravenFHD.ChannelSelectionTrans.value + self.skincolorbackgroundcolor])
		else:
			self.skinSearchAndReplace.append(['name="Kravenbg4" value="#00000000', 'name="Kravenbg4" value="#' + config.plugins.KravenFHD.ChannelSelectionTrans.value + config.plugins.KravenFHD.BackgroundColor.value])

		### Background5 (Radio Channellist)
		if config.plugins.KravenFHD.BackgroundColor.value == "self":
			self.skinSearchAndReplace.append(['name="Kravenbg5" value="#00000000', 'name="Kravenbg5" value="#' + "60" + self.skincolorbackgroundcolor])
		else:
			self.skinSearchAndReplace.append(['name="Kravenbg5" value="#00000000', 'name="Kravenbg5" value="#' + "60" + config.plugins.KravenFHD.BackgroundColor.value])

		### Infobar Backgrounds
		if config.plugins.KravenFHD.InfobarColor.value == "self":
			self.skincolorinfobarcolor = str(hex(config.plugins.KravenFHD.InfobarSelfColorR.value)[2:4]).zfill(2) + str(hex(config.plugins.KravenFHD.InfobarSelfColorG.value)[2:4]).zfill(2) + str(hex(config.plugins.KravenFHD.InfobarSelfColorB.value)[2:4]).zfill(2)
		else:
			self.skincolorinfobarcolor = config.plugins.KravenFHD.InfobarColor.value

		### SIB Background
		if config.plugins.KravenFHD.BackgroundColor.value == "self":
			self.skinSearchAndReplace.append(['name="KravenSIBbg" value="#00000000', 'name="KravenSIBbg" value="#' + config.plugins.KravenFHD.InfobarColorTrans.value + self.skincolorbackgroundcolor])
		else:
			self.skinSearchAndReplace.append(['name="KravenSIBbg" value="#00000000', 'name="KravenSIBbg" value="#' + config.plugins.KravenFHD.InfobarColorTrans.value + config.plugins.KravenFHD.BackgroundColor.value])

		### Channelname. Transparency 50%, color always grey
		self.skinSearchAndReplace.append(['name="KravenNamebg" value="#A01B1775', 'name="KravenNamebg" value="#7F7F7F7F'])

		### ECM. Transparency of infobar, color of text
		if config.plugins.KravenFHD.IBStyle.value == "gradient":
			self.skinSearchAndReplace.append(['name="KravenECMbg" value="#F1325698', 'name="KravenECMbg" value="#' + config.plugins.KravenFHD.InfobarColorTrans.value + self.calcBrightness(self.skincolorinfobarcolor,config.plugins.KravenFHD.ECMLineAntialias.value)])
		else:
			self.skinSearchAndReplace.append(['name="KravenECMbg" value="#F1325698', 'name="KravenECMbg" value="#' + config.plugins.KravenFHD.InfobarColorTrans.value + self.skincolorinfobarcolor])

		### Infobar. Transparency of infobar, color of infobar
		self.skinSearchAndReplace.append(['name="KravenIBbg" value="#001B1775', 'name="KravenIBbg" value="#' + config.plugins.KravenFHD.InfobarColorTrans.value + self.skincolorinfobarcolor])

		### CoolTV. color of infobar or color of background, if ibar invisible
		if config.plugins.KravenFHD.IBColor.value == "all-screens":
			if config.plugins.KravenFHD.IBStyle.value == "gradient":
				self.skinSearchAndReplace.append(['name="KravenIBCoolbg" value="#00000000', 'name="KravenIBCoolbg" value="#00' + self.calcBrightness(self.skincolorinfobarcolor,config.plugins.KravenFHD.ScreensAntialias.value)])
			else:
				self.skinSearchAndReplace.append(['name="KravenIBCoolbg" value="#00000000', 'name="KravenIBCoolbg" value="#00' + self.skincolorinfobarcolor])
		else:
			self.skinSearchAndReplace.append(['backgroundColor="KravenIBCoolbg"', 'backgroundColor="Kravenbg2"'])

		### Screens. Lower Transparency of infobar and background, color of infobar or color of background, if ibar invisible
		if config.plugins.KravenFHD.IBColor.value == "all-screens":
			if config.plugins.KravenFHD.IBStyle.value == "gradient":
				self.skinSearchAndReplace.append(['name="KravenIBbg2" value="#00000000', 'name="KravenIBbg2" value="#' + self.calcTransparency(config.plugins.KravenFHD.InfobarColorTrans.value,config.plugins.KravenFHD.BackgroundColorTrans.value) + self.calcBrightness(self.skincolorinfobarcolor,config.plugins.KravenFHD.ScreensAntialias.value)])
				self.skinSearchAndReplace.append(['name="KravenIBbg3" value="#00000000', 'name="KravenIBbg3" value="#' + self.calcTransparency(config.plugins.KravenFHD.InfobarColorTrans.value,config.plugins.KravenFHD.MenuColorTrans.value) + self.calcBrightness(self.skincolorinfobarcolor,config.plugins.KravenFHD.ScreensAntialias.value)])
				self.skinSearchAndReplace.append(['name="KravenIBbg4" value="#00000000', 'name="KravenIBbg4" value="#' + self.calcTransparency(config.plugins.KravenFHD.InfobarColorTrans.value,config.plugins.KravenFHD.ChannelSelectionTrans.value) + self.calcBrightness(self.skincolorinfobarcolor,config.plugins.KravenFHD.ScreensAntialias.value)])
			else:
				self.skinSearchAndReplace.append(['name="KravenIBbg2" value="#00000000', 'name="KravenIBbg2" value="#' + config.plugins.KravenFHD.BackgroundColorTrans.value + self.skincolorinfobarcolor])
				self.skinSearchAndReplace.append(['name="KravenIBbg3" value="#00000000', 'name="KravenIBbg3" value="#' + config.plugins.KravenFHD.MenuColorTrans.value + self.skincolorinfobarcolor])
				self.skinSearchAndReplace.append(['name="KravenIBbg4" value="#00000000', 'name="KravenIBbg4" value="#' + config.plugins.KravenFHD.ChannelSelectionTrans.value + self.skincolorinfobarcolor])
		else:
			self.skinSearchAndReplace.append(['name="KravenIBbg2" value="#00000000', 'name="KravenIBbg2" value="#00' + config.plugins.KravenFHD.BackgroundColorTrans.value + self.skincolorbackgroundcolor])
			self.skinSearchAndReplace.append(['name="KravenIBbg3" value="#00000000', 'name="KravenIBbg3" value="#00' + config.plugins.KravenFHD.MenuColorTrans.value + self.skincolorbackgroundcolor])
			self.skinSearchAndReplace.append(['name="KravenIBbg4" value="#00000000', 'name="KravenIBbg4" value="#00' + config.plugins.KravenFHD.ChannelSelectionTrans.value + self.skincolorbackgroundcolor])

		### Menu
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

		### Infobar. Background-Style
		if config.plugins.KravenFHD.IBStyle.value == "box":

			### Infobar - Background
			self.skinSearchAndReplace.append(['<!--<eLabel position', '<eLabel position'])
			self.skinSearchAndReplace.append(['zPosition="-8" />-->', 'zPosition="-8" />'])

			### Infobar - Line
			self.skinSearchAndReplace.append(['name="KravenIBLine" value="#00ffffff', 'name="KravenIBLine" value="#' + config.plugins.KravenFHD.IBLine.value])

			### Infobar
			self.skinSearchAndReplace.append(['<constant-widget name="gradient-ib-top"/>', '<constant-widget name="box-ib-top"/>'])
			if config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-nopicon","infobar-style-x1"):
				self.skinSearchAndReplace.append(['<!-- Infobar ibar -->', '<constant-widget name="box-ib-np-x1"/>'])
			elif config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-x2","infobar-style-x3"):
				self.skinSearchAndReplace.append(['<!-- Infobar ibar -->', '<constant-widget name="box-ib-x2-x3"/>'])
			elif config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-z1","infobar-style-z2"):
				self.skinSearchAndReplace.append(['<!-- Infobar ibar -->', '<constant-widget name="box-ib-z1-z2"/>'])
			elif config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-zz1","infobar-style-zz4"):
				self.skinSearchAndReplace.append(['<!-- Infobar ibar -->', '<constant-widget name="box-ib-zz1-zz4"/>'])
			elif config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-zz2","infobar-style-zz3"):
				self.skinSearchAndReplace.append(['<!-- Infobar ibar -->', '<constant-widget name="box-ib-zz2-zz3"/>'])
			elif config.plugins.KravenFHD.InfobarStyle.value == "infobar-style-zzz1":
				self.skinSearchAndReplace.append(['<!-- Infobar ibar -->', '<constant-widget name="box-ib-zzz1"/>'])

			### SIB - Background
			self.skinSearchAndReplace.append(['<constant-widget name="gradient-sib"/>', '<constant-widget name="box-sib"/>'])

			### weather-big - Background
			self.skinSearchAndReplace.append(['<constant-widget name="gradient-weather-small"/>', '<constant-widget name="box-weather-small"/>'])

			### weather-small - Background
			self.skinSearchAndReplace.append(['<constant-widget name="gradient-weather-big"/>', '<constant-widget name="box-weather-big"/>'])

			### weather-small - Position
			self.skinSearchAndReplace.append(['position="1440,82" size="105,105"', 'position="1500,37" size="105,105"'])
			self.skinSearchAndReplace.append(['position="1545,82" size="172,105"', 'position="1605,37" size="172,105"'])
			self.skinSearchAndReplace.append(['position="1717,82" size="112,52"', 'position="1777,37" size="112,52"'])
			self.skinSearchAndReplace.append(['position="1717,135" size="112,52"', 'position="1777,90" size="112,52"'])

			### clock-android - Position
			if config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-x2","infobar-style-x3","infobar-style-z1","infobar-style-z2") and self.actClockstyle == "clock-android":
				self.skinSearchAndReplace.append(['position="0,864" size="1920,216"', 'position="0,849" size="1920,231"'])
				self.skinSearchAndReplace.append(['position="0,864" size="1920,3"', 'position="0,849" size="1920,3"'])
				self.skinSearchAndReplace.append(['position="0,870" size="1920,210"', 'position="0,849" size="1920,231"'])
				self.skinSearchAndReplace.append(['position="0,870" size="1920,3"', 'position="0,849" size="1920,3"'])

			### EMCMediaCenter, MoviePlayer, DVDPlayer - Background
			self.skinSearchAndReplace.append(['<constant-widget name="gradient-player"/>', '<constant-widget name="box-player"/>'])

			### EPGSelectionEPGBar - Background
			self.skinSearchAndReplace.append(['<constant-widget name="gradient-EPGBar"/>', '<constant-widget name="box-EPGBar"/>'])

			### ChannelSelectionRadio
			self.skinSearchAndReplace.append(['<constant-widget name="gradient-csr"/>', '<constant-widget name="box-csr"/>'])

			### RadioInfoBar
			self.skinSearchAndReplace.append(['<constant-widget name="gradient-rib"/>', '<constant-widget name="box-rib"/>'])

		else:
			### Infobar
			if config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-nopicon","infobar-style-x1"):
				self.skinSearchAndReplace.append(['<!-- Infobar ibar -->', '<constant-widget name="gradient-ib-np-x1"/>'])
			elif config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-x2","infobar-style-x3"):
				self.skinSearchAndReplace.append(['<!-- Infobar ibar -->', '<constant-widget name="gradient-ib-x2-x3"/>'])
			elif config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-z1","infobar-style-z2"):
				self.skinSearchAndReplace.append(['<!-- Infobar ibar -->', '<constant-widget name="gradient-ib-z1-z2"/>'])
			elif config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-zz1","infobar-style-zz4"):
				self.skinSearchAndReplace.append(['<!-- Infobar ibar -->', '<constant-widget name="gradient-ib-zz1-zz4"/>'])
			elif config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-zz2","infobar-style-zz3"):
				self.skinSearchAndReplace.append(['<!-- Infobar ibar -->', '<constant-widget name="gradient-ib-zz2-zz3"/>'])
			elif config.plugins.KravenFHD.InfobarStyle.value == "infobar-style-zzz1":
				self.skinSearchAndReplace.append(['<!-- Infobar ibar -->', '<constant-widget name="gradient-ib-zzz1"/>'])
			
		### Font Colors
		self.skinSearchAndReplace.append(['name="KravenFont1" value="#00ffffff', 'name="KravenFont1" value="#' + config.plugins.KravenFHD.Font1.value])
		self.skinSearchAndReplace.append(['name="KravenFont2" value="#00F0A30A', 'name="KravenFont2" value="#' + config.plugins.KravenFHD.Font2.value])
		self.skinSearchAndReplace.append(['name="KravenIBFont1" value="#00ffffff', 'name="KravenIBFont1" value="#' + config.plugins.KravenFHD.IBFont1.value])
		self.skinSearchAndReplace.append(['name="KravenIBFont2" value="#00F0A30A', 'name="KravenIBFont2" value="#' + config.plugins.KravenFHD.IBFont2.value])
		self.skinSearchAndReplace.append(['name="KravenSelFont" value="#00ffffff', 'name="KravenSelFont" value="#' + config.plugins.KravenFHD.SelectionFont.value])
		self.skinSearchAndReplace.append(['name="KravenSelection" value="#000050EF', 'name="KravenSelection" value="#' + config.plugins.KravenFHD.SelectionBackground.value])
		if config.plugins.KravenFHD.EMCSelectionColors.value == "none":
			self.skinSearchAndReplace.append(['name="KravenEMCSelFont" value="#00ffffff', 'name="KravenEMCSelFont" value="#' + config.plugins.KravenFHD.SelectionFont.value])
			self.skinSearchAndReplace.append(['name="KravenEMCSelection" value="#000050EF', 'name="KravenEMCSelection" value="#' + config.plugins.KravenFHD.SelectionBackground.value])
		else:
			self.skinSearchAndReplace.append(['name="KravenEMCSelFont" value="#00ffffff', 'name="KravenEMCSelFont" value="#' + config.plugins.KravenFHD.EMCSelectionFont.value])
			self.skinSearchAndReplace.append(['name="KravenEMCSelection" value="#000050EF', 'name="KravenEMCSelection" value="#' + config.plugins.KravenFHD.EMCSelectionBackground.value])
		self.skinSearchAndReplace.append(['name="selectedFG" value="#00ffffff', 'name="selectedFG" value="#' + config.plugins.KravenFHD.SelectionFont.value])
		self.skinSearchAndReplace.append(['name="KravenMarked" value="#00ffffff', 'name="KravenMarked" value="#' + config.plugins.KravenFHD.MarkedFont.value])
		self.skinSearchAndReplace.append(['name="KravenECM" value="#00ffffff', 'name="KravenECM" value="#' + config.plugins.KravenFHD.ECMFont.value])
		self.skinSearchAndReplace.append(['name="KravenName" value="#00ffffff', 'name="KravenName" value="#' + config.plugins.KravenFHD.ChannelnameFont.value])
		self.skinSearchAndReplace.append(['name="KravenButton" value="#00ffffff', 'name="KravenButton" value="#' + config.plugins.KravenFHD.ButtonText.value])
		self.skinSearchAndReplace.append(['name="KravenAndroid" value="#00ffffff', 'name="KravenAndroid" value="#' + config.plugins.KravenFHD.Android.value])
		self.skinSearchAndReplace.append(['name="KravenAndroid2" value="#00ffffff', 'name="KravenAndroid2" value="#' + config.plugins.KravenFHD.Android2.value])
		self.skinSearchAndReplace.append(['name="KravenPrime" value="#0070AD11', 'name="KravenPrime" value="#' + config.plugins.KravenFHD.PrimetimeFont.value])

		### ChannelSelection (Servicename, Servicenumber, Serviceinfo) Font-Size
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

		### ChannelSelection 'not available' Font
		self.skinSearchAndReplace.append(['name="KravenNotAvailable" value="#00FFEA04', 'name="KravenNotAvailable" value="#' + config.plugins.KravenFHD.ChannelSelectionServiceNA.value])

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
		elif config.plugins.KravenFHD.weather_server.value == "_realtek":
			self.skinSearchAndReplace.append(['KravenFHDWeather', 'KravenFHDWeather_realtek'])
			if config.plugins.KravenFHD.WeatherView.value == "meteo":
				self.skinSearchAndReplace.append(['size="75,75" render="KravenFHDWetterPicon" alphatest="blend" path="WetterIcons"', 'size="75,75" render="Label" font="Meteo;60" halign="right" valign="center" foregroundColor="KravenMeteo" noWrap="1"'])
				self.skinSearchAndReplace.append(['size="75,75" path="WetterIcons" render="KravenFHDWetterPicon" alphatest="blend"', 'size="75,75" render="Label" font="Meteo;67" halign="center" valign="center" foregroundColor="KravenMeteo" noWrap="1"'])
				self.skinSearchAndReplace.append(['size="105,105" render="KravenFHDWetterPicon" alphatest="blend" path="WetterIcons"', 'size="105,105" render="Label" font="Meteo;90" halign="center" valign="center" foregroundColor="KravenMeteo" noWrap="1"'])
				self.skinSearchAndReplace.append(['size="150,150" render="KravenFHDWetterPicon" alphatest="blend" path="WetterIcons"', 'size="150,150" render="Label" font="Meteo;150" halign="center" valign="center" foregroundColor="KravenMeteo" noWrap="1"'])
				self.skinSearchAndReplace.append(['MeteoIcon</convert>', 'MeteoFont</convert>'])

		### Meteo-Font
		if config.plugins.KravenFHD.MeteoColor.value == "meteo-dark":
			self.skinSearchAndReplace.append(['name="KravenMeteo" value="#00fff0e0"', 'name="KravenMeteo" value="#00000000"'])

		### Progress
		if not config.plugins.KravenFHD.Progress.value == "progress":
			self.skinSearchAndReplace.append([' pixmap="KravenFHD/progress/progress18.png"'," "])
			self.skinSearchAndReplace.append([' picServiceEventProgressbar="KravenFHD/progress/progress52.png"'," "])
			self.skinSearchAndReplace.append([' pixmap="KravenFHD/progress/progress170.png"'," "])
			self.skinSearchAndReplace.append([' pixmap="KravenFHD/progress/progress220.png"'," "])
			self.skinSearchAndReplace.append([' pixmap="KravenFHD/progress/progress248.png"'," "])
			self.skinSearchAndReplace.append([' pixmap="KravenFHD/progress/progress300.png"'," "])
			self.skinSearchAndReplace.append([' pixmap="KravenFHD/progress/progress328.png"'," "])
			self.skinSearchAndReplace.append([' pixmap="KravenFHD/progress/progress370.png"'," "])
			self.skinSearchAndReplace.append([' pixmap="KravenFHD/progress/progress380.png"'," "])
			self.skinSearchAndReplace.append([' pixmap="KravenFHD/progress/progress410.png"'," "])
			self.skinSearchAndReplace.append([' pixmap="KravenFHD/progress/progress581.png"'," "])
			self.skinSearchAndReplace.append([' pixmap="KravenFHD/progress/progress599.png"'," "])
			self.skinSearchAndReplace.append([' pixmap="KravenFHD/progress/progress708.png"'," "])
			self.skinSearchAndReplace.append([' pixmap="KravenFHD/progress/progress749.png"'," "])
			self.skinSearchAndReplace.append([' pixmap="KravenFHD/progress/progress858.png"'," "])
			self.skinSearchAndReplace.append([' pixmap="KravenFHD/progress/progress990.png"'," "])
			self.skinSearchAndReplace.append(['name="KravenProgress" value="#00C3461B', 'name="KravenProgress" value="#' + config.plugins.KravenFHD.Progress.value])

		### Border
		self.skinSearchAndReplace.append(['name="KravenBorder" value="#00ffffff', 'name="KravenBorder" value="#' + config.plugins.KravenFHD.Border.value])

		### MiniTV Border
		self.skinSearchAndReplace.append(['name="KravenBorder2" value="#003F3F3F', 'name="KravenBorder2" value="#' + config.plugins.KravenFHD.MiniTVBorder.value])

		### Line
		self.skinSearchAndReplace.append(['name="KravenLine" value="#00ffffff', 'name="KravenLine" value="#' + config.plugins.KravenFHD.Line.value])

		### Runningtext
		if config.plugins.KravenFHD.RunningText.value == "none":
			self.skinSearchAndReplace.append(["movetype=running", "movetype=none"])
		if not config.plugins.KravenFHD.RunningText.value == "none":
			self.skinSearchAndReplace.append(["startdelay=5000", config.plugins.KravenFHD.RunningText.value])
			self.skinSearchAndReplace.append(["steptime=90", config.plugins.KravenFHD.RunningTextSpeed.value])
			if config.plugins.KravenFHD.RunningTextSpeed.value == "steptime=200":
				self.skinSearchAndReplace.append(["steptime=80", "steptime=66"])
			elif config.plugins.KravenFHD.RunningTextSpeed.value == "steptime=100":
				self.skinSearchAndReplace.append(["steptime=80", "steptime=33"])
			elif config.plugins.KravenFHD.RunningTextSpeed.value == "steptime=66":
				self.skinSearchAndReplace.append(["steptime=80", "steptime=22"])
			elif config.plugins.KravenFHD.RunningTextSpeed.value == "steptime=50":
				self.skinSearchAndReplace.append(["steptime=80", "steptime=17"])

		### Scrollbar
		if config.plugins.KravenFHD.ScrollBar.value == "scrollbarWidth=0":
			self.skinSearchAndReplace.append(['scrollbarMode="showOnDemand"', 'scrollbarMode="showNever"'])
			self.skinSearchAndReplace.append(['scrollbarWidth="5"', 'scrollbarWidth="0"'])
		elif config.plugins.KravenFHD.ScrollBar.value == "scrollbarWidth=10":
			self.skinSearchAndReplace.append(['scrollbarWidth="5"', 'scrollbarWidth="15"'])
		elif config.plugins.KravenFHD.ScrollBar.value == "scrollbarWidth=15":
			self.skinSearchAndReplace.append(['scrollbarWidth="5"', 'scrollbarWidth="22"'])

		### Selectionborder
		if not config.plugins.KravenFHD.SelectionBorder.value == "none":
			self.selectionbordercolor = config.plugins.KravenFHD.SelectionBorder.value
			self.borset = ("borset_" + self.selectionbordercolor + ".png")
			self.skinSearchAndReplace.append(["borset.png", self.borset])

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

				### Title (ChannelSelection, EMC) - Position
				self.skinSearchAndReplace.append(['position="63,18"','position="63,12"'])

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
				self.skinSearchAndReplace.append(['<ePixmap backgroundColor="Kravenbg3" alphatest="blend" pixmap="KravenFHD/buttons/key_grey1.png" position="97,963" size="300,7" />'," "])
				self.skinSearchAndReplace.append(['<ePixmap backgroundColor="Kravenbg3" alphatest="blend" pixmap="KravenFHD/buttons/key_grey1.png" position="472,963" size="300,7" />'," "])
				self.skinSearchAndReplace.append(['<ePixmap backgroundColor="Kravenbg3" alphatest="blend" pixmap="KravenFHD/buttons/key_grey1.png" position="847,963" size="300,7" />'," "])
				self.skinSearchAndReplace.append(['<ePixmap backgroundColor="Kravenbg3" alphatest="blend" pixmap="KravenFHD/buttons/key_grey1.png" position="1222,963" size="300,7" />'," "])
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
				self.skinSearchAndReplace.append(['position="1230,24" render="KravenFHDXPicon"','position="1230,16" render="KravenFHDXPicon"'])

			else:
				### Menu
				menugradient = """<ePixmap pixmap="KravenFHD/ibar.png" position="0,825" size="1920,600" alphatest="blend" zPosition="-9" />
	  <ePixmap pixmap="KravenFHD/ibaro.png" position="0,-90" size="1920,664" alphatest="blend" zPosition="-9" />"""
				self.skinSearchAndReplace.append(['<!-- Menu ibar -->', menugradient])

		self.skinSearchAndReplace.append(['backgroundColor="KravenSIBbg2"', 'backgroundColor="KravenIBbg2"'])
		self.skinSearchAndReplace.append(['foregroundColor="KravenSIBFont1"', 'foregroundColor="KravenIBFont1"'])
		self.skinSearchAndReplace.append(['foregroundColor="KravenSIBFont2"', 'foregroundColor="KravenIBFont2"'])

		### Clock Analog Style
		self.analogstylecolor = config.plugins.KravenFHD.AnalogStyle.value
		self.analog = ("analog_" + self.analogstylecolor + ".png")
		self.skinSearchAndReplace.append(["analog.png", self.analog])

		### Header
		if config.usage.movielist_show_picon.value == True:
			self.skinSearchAndReplace.append(['<parameter name="MovieListMinimalVTITitle" value="40,0,1000,40" />', '<parameter name="MovieListMinimalVTITitle" value="40,0,800,40" />'])
		self.appendSkinFile(self.daten + "header_begin.xml")
		if not config.plugins.KravenFHD.SelectionBorder.value == "none":
			self.appendSkinFile(self.daten + "header_middle.xml")
		self.appendSkinFile(self.daten + "header_end.xml")

		### Volume
		self.appendSkinFile(self.daten + config.plugins.KravenFHD.Volume.value + ".xml")

		### ChannelSelection
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
		elif self.actChannelselectionstyle in ("channelselection-style-minitv","channelselection-style-minitv4","channelselection-style-nobile-minitv"):
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

		### Infobox
		if config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-nopicon","infobar-style-x1","infobar-style-x2","infobar-style-z1","infobar-style-zz1","infobar-style-zz4","infobar-style-zzz1"):
			if config.plugins.KravenFHD.Infobox.value == "cpu":
				self.skinSearchAndReplace.append(['<!--<eLabel text="  S:"', '<eLabel text="  L:"'])
				self.skinSearchAndReplace.append(['foregroundColor="KravenIcon" />-->', 'foregroundColor="KravenIcon" />'])
				self.skinSearchAndReplace.append(['  source="session.FrontendStatus', ' source="session.CurrentService'])
				self.skinSearchAndReplace.append(['convert  type="KravenFHDFrontendInfo">SNR', 'convert type="KravenFHDLayoutInfo">LoadAvg'])
				self.skinSearchAndReplace.append(['convert  type="KravenFHDExtServiceInfo">OrbitalPosition', 'convert  type="KravenFHDCpuUsage">$0'])
			elif config.plugins.KravenFHD.Infobox.value == "temp":
				self.skinSearchAndReplace.append(['<!--<eLabel text="  S:"', '<eLabel text="U:"'])
				self.skinSearchAndReplace.append(['foregroundColor="KravenIcon" />-->', 'foregroundColor="KravenIcon" />'])
				self.skinSearchAndReplace.append(['  source="session.FrontendStatus', ' source="session.CurrentService'])
				self.skinSearchAndReplace.append(['convert  type="KravenFHDFrontendInfo">SNR', 'convert type="KravenFHDTempFanInfo">FanInfo'])
				self.skinSearchAndReplace.append(['convert  type="KravenFHDExtServiceInfo">OrbitalPosition', 'convert  type="KravenFHDTempFanInfo">TempInfo'])

		### Record State
		if config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-nopicon","infobar-style-x1","infobar-style-zz1","infobar-style-zz4","infobar-style-zzz1"):
			if config.plugins.KravenFHD.record2.value == "record-blink":
				self.skinSearchAndReplace.append(['>recordblink</convert>', '>Blink</convert>'])
				self.skinSearchAndReplace.append(['>tunerblink</convert>', ' />'])
				self.skinSearchAndReplace.append(['source="session.FrontendInfo" zPosition="3"', 'source="session.FrontendInfo" zPosition="5"'])
			elif config.plugins.KravenFHD.record2.value == "tuner-blink":
				self.skinSearchAndReplace.append(['>recordblink</convert>', ' />'])
				self.skinSearchAndReplace.append(['>tunerblink</convert>', '>Blink</convert>'])
			elif config.plugins.KravenFHD.record2.value == "record+tuner-blink":
				self.skinSearchAndReplace.append(['>recordblink</convert>', '>Blink</convert>'])
				self.skinSearchAndReplace.append(['>tunerblink</convert>', '>Blink</convert>'])
			else:
				self.skinSearchAndReplace.append(['>recordblink</convert>', ' />'])
				self.skinSearchAndReplace.append(['>tunerblink</convert>', ' />'])
				self.skinSearchAndReplace.append(['source="session.FrontendInfo" zPosition="3"', 'source="session.FrontendInfo" zPosition="5"'])
		elif config.plugins.KravenFHD.InfobarStyle.value == "infobar-style-zz2":
			if config.plugins.KravenFHD.record.value == "record-blink":
				self.skinSearchAndReplace.append(['>recordblink</convert>', '>Blink</convert>'])
			else:
				self.skinSearchAndReplace.append(['>recordblink</convert>', ' />'])
		elif config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-x2","infobar-style-z1"):
			if config.plugins.KravenFHD.IBtop.value == "infobar-x2-z1_top2":
				if config.plugins.KravenFHD.record2.value == "record-blink":
					self.skinSearchAndReplace.append(['>recordblink</convert>', '>Blink</convert>'])
					self.skinSearchAndReplace.append(['>tunerblink</convert>', ' />'])
					self.skinSearchAndReplace.append(['source="session.FrontendInfo" zPosition="3"', 'source="session.FrontendInfo" zPosition="5"'])
				elif config.plugins.KravenFHD.record2.value == "tuner-blink":
					self.skinSearchAndReplace.append(['>recordblink</convert>', ' />'])
					self.skinSearchAndReplace.append(['>tunerblink</convert>', '>Blink</convert>'])
				elif config.plugins.KravenFHD.record2.value == "record+tuner-blink":
					self.skinSearchAndReplace.append(['>recordblink</convert>', '>Blink</convert>'])
					self.skinSearchAndReplace.append(['>tunerblink</convert>', '>Blink</convert>'])
				else:
					self.skinSearchAndReplace.append(['>recordblink</convert>', ' />'])
					self.skinSearchAndReplace.append(['>tunerblink</convert>', ' />'])
					self.skinSearchAndReplace.append(['source="session.FrontendInfo" zPosition="3"', 'source="session.FrontendInfo" zPosition="5"'])
			else:
				if config.plugins.KravenFHD.record3.value == "tuner-blink":
					self.skinSearchAndReplace.append(['>tunerblink</convert>', '>Blink</convert>'])
				else:
					self.skinSearchAndReplace.append(['>tunerblink</convert>', ' />'])
					self.skinSearchAndReplace.append(['source="session.FrontendInfo" zPosition="3"', 'source="session.FrontendInfo" zPosition="5"'])

		### Infobar_begin
		self.appendSkinFile(self.daten + "infobar-begin.xml")

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

		### Channelname
		if config.plugins.KravenFHD.InfobarStyle.value == "infobar-style-nopicon":
			self.skinSearchAndReplace.append(['"KravenName" position="30,765"', '"KravenName" position="63,750"'])
			self.skinSearchAndReplace.append(['"KravenName" position="30,675"', '"KravenName" position="63,675"'])
			self.appendSkinFile(self.daten + config.plugins.KravenFHD.InfobarChannelName.value + ".xml")
		elif config.plugins.KravenFHD.InfobarStyle.value == "infobar-style-x1":
			self.skinSearchAndReplace.append(['"KravenName" position="30,765"', '"KravenName" position="30,750"'])
			self.appendSkinFile(self.daten + config.plugins.KravenFHD.InfobarChannelName.value + ".xml")
		elif config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-x2","infobar-style-x3","infobar-style-z1","infobar-style-z2"):
			self.appendSkinFile(self.daten + config.plugins.KravenFHD.InfobarChannelName.value + ".xml")
		elif config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-zz1","infobar-style-zz4"):
			self.skinSearchAndReplace.append(['"KravenName" position="30,765"', '"KravenName" position="30,711"'])
			self.skinSearchAndReplace.append(['"KravenName" position="30,675"', '"KravenName" position="30,621"'])
			self.appendSkinFile(self.daten + config.plugins.KravenFHD.InfobarChannelName.value + ".xml")
		elif config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-zz2","infobar-style-zz3"):
			self.skinSearchAndReplace.append(['"KravenName" position="30,765" size="1860,90"', '"KravenName" position="652,801" size="847,75"'])
			self.appendSkinFile(self.daten + config.plugins.KravenFHD.InfobarChannelName2.value + ".xml")
		elif config.plugins.KravenFHD.InfobarStyle.value == "infobar-style-zzz1":
			self.skinSearchAndReplace.append(['"KravenName" position="30,765" size="1860,90"', '"KravenName" position="669,711" size="1131,75"'])
			self.appendSkinFile(self.daten + config.plugins.KravenFHD.InfobarChannelName2.value + ".xml")

		### clock-weather (icon size)
		if not config.plugins.KravenFHD.InfobarStyle.value == "infobar-style-zz4" and self.actClockstyle == "clock-weather":
			if config.plugins.KravenFHD.ClockIconSize.value == "size-192":
				self.skinSearchAndReplace.append(['position="1599,897" size="144,144"','position="1575,873" size="192,192"'])
				self.skinSearchAndReplace.append(['position="1599,912" size="144,144"','position="1575,888" size="192,192"'])
				self.skinSearchAndReplace.append(['position="1614,897" size="144,144"','position="1590,873" size="192,192"'])

		### clock-style_ib
		if config.plugins.KravenFHD.InfobarStyle.value == "infobar-style-x1":
			self.appendSkinFile(self.daten + config.plugins.KravenFHD.ClockStyle.value + ".xml")
		elif config.plugins.KravenFHD.InfobarStyle.value == "infobar-style-nopicon":
			if config.plugins.KravenFHD.ClockStyle.value == "clock-classic":
				self.appendSkinFile(self.daten + "clock-classic3.xml")
			elif config.plugins.KravenFHD.ClockStyle.value == "clock-color":
				self.appendSkinFile(self.daten + "clock-color3.xml")
			elif config.plugins.KravenFHD.ClockStyle.value == "clock-flip":
				self.appendSkinFile(self.daten + "clock-flip2.xml")
			elif config.plugins.KravenFHD.ClockStyle.value == "clock-weather":
				self.appendSkinFile(self.daten + "clock-weather2.xml")
			else:
				self.appendSkinFile(self.daten + config.plugins.KravenFHD.ClockStyle.value + ".xml")
		elif config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-x2","infobar-style-x3","infobar-style-z1","infobar-style-z2","infobar-style-zz2","infobar-style-zz3"):
			if config.plugins.KravenFHD.ClockStyle.value == "clock-classic":
				self.appendSkinFile(self.daten + "clock-classic2.xml")
			elif config.plugins.KravenFHD.ClockStyle.value == "clock-classic-big":
				self.appendSkinFile(self.daten + "clock-classic-big2.xml")
			elif config.plugins.KravenFHD.ClockStyle.value == "clock-color":
				self.appendSkinFile(self.daten + "clock-color2.xml")
			elif config.plugins.KravenFHD.ClockStyle.value == "clock-analog":
				self.appendSkinFile(self.daten + "clock-analog2.xml")
			elif config.plugins.KravenFHD.ClockStyle.value == "clock-flip":
				self.appendSkinFile(self.daten + "clock-flip2.xml")
			elif config.plugins.KravenFHD.ClockStyle.value == "clock-weather":
				self.appendSkinFile(self.daten + "clock-weather2.xml")
			else:
				self.appendSkinFile(self.daten + config.plugins.KravenFHD.ClockStyle.value + ".xml")
		elif config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-zz1","infobar-style-zzz1"):
			if config.plugins.KravenFHD.ClockStyle.value == "clock-classic":
				self.appendSkinFile(self.daten + "clock-classic3.xml")
			elif config.plugins.KravenFHD.ClockStyle.value == "clock-classic-big":
				self.appendSkinFile(self.daten + "clock-classic-big3.xml")
			elif config.plugins.KravenFHD.ClockStyle.value == "clock-color":
				self.appendSkinFile(self.daten + "clock-color3.xml")
			elif config.plugins.KravenFHD.ClockStyle.value == "clock-flip":
				self.appendSkinFile(self.daten + "clock-flip3.xml")
			elif config.plugins.KravenFHD.ClockStyle.value == "clock-weather":
				self.appendSkinFile(self.daten + "clock-weather3.xml")
			else:
				self.appendSkinFile(self.daten + config.plugins.KravenFHD.ClockStyle.value + ".xml")

		### infobar - ecm-info
		if config.plugins.KravenFHD.ECMVisible.value in ("ib","ib+sib"):

			if config.plugins.KravenFHD.FTA.value == "none":
				self.skinSearchAndReplace.append(['FTAVisible</convert>', 'FTAInvisible</convert>'])

			if config.plugins.KravenFHD.InfobarStyle.value == "infobar-style-x1":
				self.skinSearchAndReplace.append(['<convert type="KravenFHDECMLine">ShortReader', '<convert type="KravenFHDECMLine">' + config.plugins.KravenFHD.ECMLine1.value])
			elif config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-nopicon","infobar-style-x2","infobar-style-x3","infobar-style-z1","infobar-style-z2"):
				self.skinSearchAndReplace.append(['<convert type="KravenFHDECMLine">ShortReader', '<convert type="KravenFHDECMLine">' + config.plugins.KravenFHD.ECMLine2.value])
			elif config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-zz1","infobar-style-zz2","infobar-style-zz3","infobar-style-zz4","infobar-style-zzz1"):
				self.skinSearchAndReplace.append(['<convert type="KravenFHDECMLine">ShortReader', '<convert type="KravenFHDECMLine">' + config.plugins.KravenFHD.ECMLine3.value])

			if config.plugins.KravenFHD.InfobarStyle.value == "infobar-style-x1":
				if config.plugins.KravenFHD.tuner2.value == "8-tuner":
					self.skinSearchAndReplace.append(['position="409,1039" size="604,33"', 'position="409,1039" size="525,33"'])
				elif config.plugins.KravenFHD.tuner2.value == "10-tuner":
					self.skinSearchAndReplace.append(['position="409,1039" size="604,33"', 'position="409,1039" size="742,33"'])
				self.appendSkinFile(self.daten + "infobar-ecminfo-x1.xml")
			elif config.plugins.KravenFHD.InfobarStyle.value == "infobar-style-nopicon":
				self.appendSkinFile(self.daten + "infobar-ecminfo-nopicon.xml")
			elif config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-x2","infobar-style-z1"):
				self.appendSkinFile(self.daten + "infobar-ecminfo-x2.xml")
			elif config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-x3","infobar-style-z2"):
				self.appendSkinFile(self.daten + "infobar-ecminfo-x3.xml")
			elif config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-zz1","infobar-style-zz4","infobar-style-zzz1"):
				self.appendSkinFile(self.daten + "infobar-ecminfo-zz1.xml")
			elif config.plugins.KravenFHD.InfobarStyle.value == "infobar-style-zz2":
				self.appendSkinFile(self.daten + "infobar-ecminfo-zz2.xml")
			elif config.plugins.KravenFHD.InfobarStyle.value == "infobar-style-zz3":
				self.appendSkinFile(self.daten + "infobar-ecminfo-zz3.xml")

		### system-info
		if config.plugins.KravenFHD.IBStyle.value == "box":
			if config.plugins.KravenFHD.SystemInfo.value == "systeminfo-small":
				self.appendSkinFile(self.daten + "systeminfo-small2.xml")
			elif config.plugins.KravenFHD.SystemInfo.value == "systeminfo-big":
				self.appendSkinFile(self.daten + "systeminfo-big2.xml")
			elif config.plugins.KravenFHD.SystemInfo.value == "systeminfo-bigsat":
				self.appendSkinFile(self.daten + "systeminfo-bigsat2.xml")
		else:
			self.appendSkinFile(self.daten + config.plugins.KravenFHD.SystemInfo.value + ".xml")

		### weather-style
		if config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-nopicon","infobar-style-x1","infobar-style-x3","infobar-style-z2","infobar-style-zz1","infobar-style-zz2","infobar-style-zz3","infobar-style-zz4","infobar-style-zzz1"):
			self.actWeatherstyle=config.plugins.KravenFHD.WeatherStyle.value
		elif config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-x2","infobar-style-z1"):
			self.actWeatherstyle=config.plugins.KravenFHD.WeatherStyle2.value

		self.appendSkinFile(self.daten + self.actWeatherstyle + ".xml")
		if self.actWeatherstyle == "none" and self.actClockstyle != "clock-android" and self.actClockstyle != "clock-weather" and config.plugins.KravenFHD.SIB.value != "sib6" and config.plugins.KravenFHD.SIB.value != "sib7" and config.plugins.KravenFHD.PlayerClock.value != "player-android" and config.plugins.KravenFHD.PlayerClock.value != "player-weather":
			config.plugins.KravenFHD.refreshInterval.value = "0"
			config.plugins.KravenFHD.refreshInterval.save()
		elif config.plugins.KravenFHD.refreshInterval.value == "0":
			config.plugins.KravenFHD.refreshInterval.value = config.plugins.KravenFHD.refreshInterval.default
			config.plugins.KravenFHD.refreshInterval.save()

		### Infobar_end - SIB_begin
		self.appendSkinFile(self.daten + "infobar-style_middle.xml")

		### clock-style - SIB
		if config.plugins.KravenFHD.InfobarStyle.value == "infobar-style-x1":
			self.appendSkinFile(self.daten + config.plugins.KravenFHD.ClockStyle.value + ".xml")
		elif config.plugins.KravenFHD.InfobarStyle.value == "infobar-style-nopicon":
			if config.plugins.KravenFHD.ClockStyle.value == "clock-classic":
				self.appendSkinFile(self.daten + "clock-classic3.xml")
			elif config.plugins.KravenFHD.ClockStyle.value == "clock-color":
				self.appendSkinFile(self.daten + "clock-color3.xml")
			elif config.plugins.KravenFHD.ClockStyle.value == "clock-flip":
				self.appendSkinFile(self.daten + "clock-flip2.xml")
			elif config.plugins.KravenFHD.ClockStyle.value == "clock-weather":
				self.appendSkinFile(self.daten + "clock-weather2.xml")
			else:
				self.appendSkinFile(self.daten + config.plugins.KravenFHD.ClockStyle.value + ".xml")
		elif config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-x2","infobar-style-x3","infobar-style-z1","infobar-style-z2","infobar-style-zz2","infobar-style-zz3"):
			if config.plugins.KravenFHD.ClockStyle.value == "clock-classic":
				self.appendSkinFile(self.daten + "clock-classic2.xml")
			elif config.plugins.KravenFHD.ClockStyle.value == "clock-classic-big":
				self.appendSkinFile(self.daten + "clock-classic-big2.xml")
			elif config.plugins.KravenFHD.ClockStyle.value == "clock-color":
				self.appendSkinFile(self.daten + "clock-color2.xml")
			elif config.plugins.KravenFHD.ClockStyle.value == "clock-analog":
				self.appendSkinFile(self.daten + "clock-analog2.xml")
			elif config.plugins.KravenFHD.ClockStyle.value == "clock-flip":
				self.appendSkinFile(self.daten + "clock-flip2.xml")
			elif config.plugins.KravenFHD.ClockStyle.value == "clock-weather":
				self.appendSkinFile(self.daten + "clock-weather2.xml")
			else:
				self.appendSkinFile(self.daten + config.plugins.KravenFHD.ClockStyle.value + ".xml")
		elif config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-zz1","infobar-style-zzz1"):
			if config.plugins.KravenFHD.ClockStyle.value == "clock-classic":
				self.appendSkinFile(self.daten + "clock-classic3.xml")
			elif config.plugins.KravenFHD.ClockStyle.value == "clock-classic-big":
				self.appendSkinFile(self.daten + "clock-classic-big3.xml")
			elif config.plugins.KravenFHD.ClockStyle.value == "clock-color":
				self.appendSkinFile(self.daten + "clock-color3.xml")
			elif config.plugins.KravenFHD.ClockStyle.value == "clock-flip":
				self.appendSkinFile(self.daten + "clock-flip3.xml")
			elif config.plugins.KravenFHD.ClockStyle.value == "clock-weather":
				self.appendSkinFile(self.daten + "clock-weather3.xml")
			else:
				self.appendSkinFile(self.daten + config.plugins.KravenFHD.ClockStyle.value + ".xml")

		### secondinfobar - ecm-info
		if config.plugins.KravenFHD.ECMVisible.value in ("sib","ib+sib"):
			if config.plugins.KravenFHD.FTA.value == "none":
				self.skinSearchAndReplace.append(['FTAVisible</convert>', 'FTAInvisible</convert>'])

			if config.plugins.KravenFHD.InfobarStyle.value == "infobar-style-x1":
				self.skinSearchAndReplace.append(['<convert type="KravenFHDECMLine">ShortReader', '<convert type="KravenFHDECMLine">' + config.plugins.KravenFHD.ECMLine1.value])
			elif config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-nopicon","infobar-style-x2","infobar-style-x3","infobar-style-z1","infobar-style-z2"):
				self.skinSearchAndReplace.append(['<convert type="KravenFHDECMLine">ShortReader', '<convert type="KravenFHDECMLine">' + config.plugins.KravenFHD.ECMLine2.value])
			elif config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-zz1","infobar-style-zz2","infobar-style-zz3","infobar-style-zz4","infobar-style-zzz1"):
				self.skinSearchAndReplace.append(['<convert type="KravenFHDECMLine">ShortReader', '<convert type="KravenFHDECMLine">' + config.plugins.KravenFHD.ECMLine3.value])

			if config.plugins.KravenFHD.InfobarStyle.value == "infobar-style-x1":
				if config.plugins.KravenFHD.tuner2.value == "8-tuner":
					self.skinSearchAndReplace.append(['position="409,1039" size="604,33"', 'position="409,1039" size="525,33"'])
				elif config.plugins.KravenFHD.tuner2.value == "10-tuner":
					self.skinSearchAndReplace.append(['position="409,1039" size="604,33"', 'position="409,1039" size="742,33"'])
				self.appendSkinFile(self.daten + "infobar-ecminfo-x1.xml")
			elif config.plugins.KravenFHD.InfobarStyle.value == "infobar-style-nopicon":
				self.appendSkinFile(self.daten + "infobar-ecminfo-nopicon.xml")
			elif config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-x2","infobar-style-z1"):
				self.appendSkinFile(self.daten + "infobar-ecminfo-x2.xml")
			elif config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-x3","infobar-style-z2"):
				self.appendSkinFile(self.daten + "infobar-ecminfo-x3.xml")
			elif config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-zz1","infobar-style-zz4","infobar-style-zzz1"):
				self.appendSkinFile(self.daten + "infobar-ecminfo-zz1.xml")
			elif config.plugins.KravenFHD.InfobarStyle.value == "infobar-style-zz2":
				self.appendSkinFile(self.daten + "infobar-ecminfo-zz2.xml")
			elif config.plugins.KravenFHD.InfobarStyle.value == "infobar-style-zz3":
				self.appendSkinFile(self.daten + "infobar-ecminfo-zz3.xml")

		### SIB_main
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
		elif config.plugins.KravenFHD.InfobarStyle.value == "infobar-style-z1":
			self.appendSkinFile(self.daten + "infobar-style-z1_main.xml")
		elif config.plugins.KravenFHD.InfobarStyle.value == "infobar-style-z2":
			self.appendSkinFile(self.daten + "infobar-style-z2_main.xml")
		elif config.plugins.KravenFHD.InfobarStyle.value == "infobar-style-zz1":
			self.skinSearchAndReplace.append(['size="1798,276">', 'size="1798,230">'])
			self.skinSearchAndReplace.append([',441">', ',392">'])
			if config.plugins.KravenFHD.tuner.value == "2-tuner":
				self.appendSkinFile(self.daten + "infobar-style-zz1_main2.xml")
			elif config.plugins.KravenFHD.tuner.value == "4-tuner":
				self.appendSkinFile(self.daten + "infobar-style-zz1_main4.xml")
			elif config.plugins.KravenFHD.tuner.value == "8-tuner":
				self.appendSkinFile(self.daten + "infobar-style-zz1_main8.xml")
		elif config.plugins.KravenFHD.InfobarStyle.value == "infobar-style-zz2":
			self.skinSearchAndReplace.append(['size="1798,276">', 'size="1798,230">'])
			self.skinSearchAndReplace.append([',441">', ',392">'])
			self.appendSkinFile(self.daten + "infobar-style-zz2_main.xml")
		elif config.plugins.KravenFHD.InfobarStyle.value == "infobar-style-zz3":
			self.skinSearchAndReplace.append(['size="1798,276">', 'size="1798,230">'])
			self.skinSearchAndReplace.append([',441">', ',392">'])
			self.appendSkinFile(self.daten + "infobar-style-zz3_main.xml")
		elif config.plugins.KravenFHD.InfobarStyle.value == "infobar-style-zz4":
			self.skinSearchAndReplace.append(['size="1798,276">', 'size="1798,230">'])
			self.skinSearchAndReplace.append([',441">', ',392">'])
			if config.plugins.KravenFHD.tuner.value == "2-tuner":
				self.appendSkinFile(self.daten + "infobar-style-zz4_main2.xml")
			elif config.plugins.KravenFHD.tuner.value == "4-tuner":
				self.appendSkinFile(self.daten + "infobar-style-zz4_main4.xml")
			elif config.plugins.KravenFHD.tuner.value == "8-tuner":
				self.appendSkinFile(self.daten + "infobar-style-zz4_main8.xml")
		elif config.plugins.KravenFHD.InfobarStyle.value == "infobar-style-zzz1":
			self.skinSearchAndReplace.append(['size="855,588">', 'size="855,490">'])
			self.skinSearchAndReplace.append(['size="1798,276">', 'size="1798,184">'])
			self.skinSearchAndReplace.append([',441">', ',343">'])
			if config.plugins.KravenFHD.tuner.value == "2-tuner":
				self.appendSkinFile(self.daten + "infobar-style-zzz1_main2.xml")
			elif config.plugins.KravenFHD.tuner.value == "4-tuner":
				self.appendSkinFile(self.daten + "infobar-style-zzz1_main4.xml")
			elif config.plugins.KravenFHD.tuner.value == "8-tuner":
				self.appendSkinFile(self.daten + "infobar-style-zzz1_main8.xml")
		self.appendSkinFile(self.daten + config.plugins.KravenFHD.SIB.value + ".xml")
		if fileExists("/usr/lib/enigma2/python/Plugins/Extensions/SecondInfoBar/plugin.py"):
			config.plugins.SecondInfoBar.HideNormalIB.value = True
			config.plugins.SecondInfoBar.HideNormalIB.save()

		### Main XML
		self.appendSkinFile(self.daten + "main.xml")

		if config.plugins.KravenFHD.IBStyle.value == "gradient":
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

			### Timeshift_Channelname
			if config.plugins.KravenFHD.InfobarStyle.value == "infobar-style-nopicon":
				self.skinSearchAndReplace.append(['"KravenName" position="30,765"', '"KravenName" position="63,750"'])
				self.skinSearchAndReplace.append(['"KravenName" position="30,675"', '"KravenName" position="63,675"'])
				self.appendSkinFile(self.daten + config.plugins.KravenFHD.InfobarChannelName.value + ".xml")
			elif config.plugins.KravenFHD.InfobarStyle.value == "infobar-style-x1":
				self.skinSearchAndReplace.append(['"KravenName" position="30,765"', '"KravenName" position="30,750"'])
				self.appendSkinFile(self.daten + config.plugins.KravenFHD.InfobarChannelName.value + ".xml")
			elif config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-x2","infobar-style-x3","infobar-style-z1","infobar-style-z2"):
				self.appendSkinFile(self.daten + config.plugins.KravenFHD.InfobarChannelName.value + ".xml")
			elif config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-zz1","infobar-style-zz4"):
				self.skinSearchAndReplace.append(['"KravenName" position="30,765"', '"KravenName" position="30,711"'])
				self.skinSearchAndReplace.append(['"KravenName" position="30,675"', '"KravenName" position="30,621"'])
				self.appendSkinFile(self.daten + config.plugins.KravenFHD.InfobarChannelName.value + ".xml")
			elif config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-zz2","infobar-style-zz3"):
				self.skinSearchAndReplace.append(['"KravenName" position="30,765" size="1860,90"', '"KravenName" position="652,801" size="847,75"'])
				self.appendSkinFile(self.daten + config.plugins.KravenFHD.InfobarChannelName2.value + ".xml")
			elif config.plugins.KravenFHD.InfobarStyle.value == "infobar-style-zzz1":
				self.skinSearchAndReplace.append(['"KravenName" position="30,765" size="1860,90"', '"KravenName" position="669,711" size="1131,75"'])
				self.appendSkinFile(self.daten + config.plugins.KravenFHD.InfobarChannelName2.value + ".xml")

			### Timeshift_clock-style_ib
			if config.plugins.KravenFHD.InfobarStyle.value == "infobar-style-x1":
				self.appendSkinFile(self.daten + config.plugins.KravenFHD.ClockStyle.value + ".xml")
			elif config.plugins.KravenFHD.InfobarStyle.value == "infobar-style-nopicon":
				if config.plugins.KravenFHD.ClockStyle.value == "clock-classic":
					self.appendSkinFile(self.daten + "clock-classic3.xml")
				elif config.plugins.KravenFHD.ClockStyle.value == "clock-color":
					self.appendSkinFile(self.daten + "clock-color3.xml")
				elif config.plugins.KravenFHD.ClockStyle.value == "clock-flip":
					self.appendSkinFile(self.daten + "clock-flip2.xml")
				elif config.plugins.KravenFHD.ClockStyle.value == "clock-weather":
					self.appendSkinFile(self.daten + "clock-weather2.xml")
				else:
					self.appendSkinFile(self.daten + config.plugins.KravenFHD.ClockStyle.value + ".xml")
			elif config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-x2","infobar-style-x3","infobar-style-z1","infobar-style-z2","infobar-style-zz2","infobar-style-zz3"):
				if config.plugins.KravenFHD.ClockStyle.value == "clock-classic":
					self.appendSkinFile(self.daten + "clock-classic2.xml")
				elif config.plugins.KravenFHD.ClockStyle.value == "clock-classic-big":
					self.appendSkinFile(self.daten + "clock-classic-big2.xml")
				elif config.plugins.KravenFHD.ClockStyle.value == "clock-color":
					self.appendSkinFile(self.daten + "clock-color2.xml")
				elif config.plugins.KravenFHD.ClockStyle.value == "clock-analog":
					self.appendSkinFile(self.daten + "clock-analog2.xml")
				elif config.plugins.KravenFHD.ClockStyle.value == "clock-flip":
					self.appendSkinFile(self.daten + "clock-flip2.xml")
				elif config.plugins.KravenFHD.ClockStyle.value == "clock-weather":
					self.appendSkinFile(self.daten + "clock-weather2.xml")
				else:
					self.appendSkinFile(self.daten + config.plugins.KravenFHD.ClockStyle.value + ".xml")
			elif config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-zz1","infobar-style-zzz1"):
				if config.plugins.KravenFHD.ClockStyle.value == "clock-classic":
					self.appendSkinFile(self.daten + "clock-classic3.xml")
				elif config.plugins.KravenFHD.ClockStyle.value == "clock-classic-big":
					self.appendSkinFile(self.daten + "clock-classic-big3.xml")
				elif config.plugins.KravenFHD.ClockStyle.value == "clock-color":
					self.appendSkinFile(self.daten + "clock-color3.xml")
				elif config.plugins.KravenFHD.ClockStyle.value == "clock-flip":
					self.appendSkinFile(self.daten + "clock-flip3.xml")
				elif config.plugins.KravenFHD.ClockStyle.value == "clock-weather":
					self.appendSkinFile(self.daten + "clock-weather3.xml")
				else:
					self.appendSkinFile(self.daten + config.plugins.KravenFHD.ClockStyle.value + ".xml")

			### timeshift - ecm-info
			if config.plugins.KravenFHD.ECMVisible.value in ("ib","ib+sib"):
				if config.plugins.KravenFHD.FTA.value == "none":
					self.skinSearchAndReplace.append(['FTAVisible</convert>', 'FTAInvisible</convert>'])

				if config.plugins.KravenFHD.InfobarStyle.value == "infobar-style-x1":
					self.skinSearchAndReplace.append(['<convert type="KravenFHDECMLine">ShortReader', '<convert type="KravenFHDECMLine">' + config.plugins.KravenFHD.ECMLine1.value])
				elif config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-nopicon","infobar-style-x2","infobar-style-x3","infobar-style-z1","infobar-style-z2"):
					self.skinSearchAndReplace.append(['<convert type="KravenFHDECMLine">ShortReader', '<convert type="KravenFHDECMLine">' + config.plugins.KravenFHD.ECMLine2.value])
				elif config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-zz1","infobar-style-zz2","infobar-style-zz3","infobar-style-zz4","infobar-style-zzz1"):
					self.skinSearchAndReplace.append(['<convert type="KravenFHDECMLine">ShortReader', '<convert type="KravenFHDECMLine">' + config.plugins.KravenFHD.ECMLine3.value])

				if config.plugins.KravenFHD.InfobarStyle.value == "infobar-style-x1":
					if config.plugins.KravenFHD.tuner2.value == "8-tuner":
						self.skinSearchAndReplace.append(['position="409,1039" size="604,33"', 'position="409,1039" size="525,33"'])
					elif config.plugins.KravenFHD.tuner2.value == "10-tuner":
						self.skinSearchAndReplace.append(['position="409,1039" size="604,33"', 'position="409,1039" size="742,33"'])
					self.appendSkinFile(self.daten + "infobar-ecminfo-x1.xml")
				elif config.plugins.KravenFHD.InfobarStyle.value == "infobar-style-nopicon":
					self.appendSkinFile(self.daten + "infobar-ecminfo-nopicon.xml")
				elif config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-x2","infobar-style-z1"):
					self.appendSkinFile(self.daten + "infobar-ecminfo-x2.xml")
				elif config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-x3","infobar-style-z2"):
					self.appendSkinFile(self.daten + "infobar-ecminfo-x3.xml")
				elif config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-zz1","infobar-style-zz4","infobar-style-zzz1"):
					self.appendSkinFile(self.daten + "infobar-ecminfo-zz1.xml")
				elif config.plugins.KravenFHD.InfobarStyle.value == "infobar-style-zz2":
					self.appendSkinFile(self.daten + "infobar-ecminfo-zz2.xml")
				elif config.plugins.KravenFHD.InfobarStyle.value == "infobar-style-zz3":
					self.appendSkinFile(self.daten + "infobar-ecminfo-zz3.xml")

			### Timeshift_system-info
			self.appendSkinFile(self.daten + config.plugins.KravenFHD.SystemInfo.value + ".xml")

			### Timeshift_weather-style
			self.appendSkinFile(self.daten + self.actWeatherstyle + ".xml")

			### Timeshift_end
			self.appendSkinFile(self.daten + "timeshift-end.xml")

			### InfobarTunerState
			if self.actWeatherstyle in ("weather-big","weather-left"):
				if config.plugins.KravenFHD.SystemInfo.value == "systeminfo-bigsat":
					self.appendSkinFile(self.daten + "infobartunerstate-low.xml")
				else:
					self.appendSkinFile(self.daten + "infobartunerstate-mid.xml")
			else:
				self.appendSkinFile(self.daten + "infobartunerstate-high.xml")

		elif config.plugins.KravenFHD.IBStyle.value == "box":
			self.appendSkinFile(self.daten + "timeshift-ibts-ar.xml")

		### Players
		self.appendSkinFile(self.daten + "player-movie.xml")
		self.appendSkinFile(self.daten + config.plugins.KravenFHD.PlayerClock.value + ".xml")
		self.appendSkinFile(self.daten + "screen_end.xml")
		self.appendSkinFile(self.daten + "player-emc.xml")
		self.appendSkinFile(self.daten + config.plugins.KravenFHD.PlayerClock.value + ".xml")
		self.appendSkinFile(self.daten + "screen_end.xml")

		### Plugins
		self.appendSkinFile(self.daten + "plugins.xml")
		if fileExists("/usr/lib/enigma2/python/Plugins/Extensions/PermanentTimeshift/plugin.py"):
			config.plugins.pts.showinfobar.value = False
			config.plugins.pts.showinfobar.save()

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

		### EMC
		self.appendSkinFile(self.daten + config.plugins.KravenFHD.EMCStyle.value + ".xml")
		if fileExists("/usr/lib/enigma2/python/Plugins/Extensions/EnhancedMovieCenter/plugin.py"):
			config.EMC.skin_able.value = True
			config.EMC.skin_able.save()

		### NumberZapExt
		self.appendSkinFile(self.daten + config.plugins.KravenFHD.NumberZapExt.value + ".xml")
		if not config.plugins.KravenFHD.NumberZapExt.value == "none":
			config.usage.numberzap_show_picon.value = True
			config.usage.numberzap_show_picon.save()
			config.usage.numberzap_show_servicename.value = True
			config.usage.numberzap_show_servicename.save()

		### PVRState
		self.appendSkinFile(self.daten + config.plugins.KravenFHD.PVRState.value + ".xml")

		### SplitScreen
		self.appendSkinFile(self.daten + config.plugins.KravenFHD.SplitScreen.value + ".xml")

		### cooltv
		self.appendSkinFile(self.daten + config.plugins.KravenFHD.CoolTVGuide.value + ".xml")

		### MovieSelection (Event-Description) Font-Size
		if config.plugins.KravenFHD.MovieSelection.value == "movieselection-no-cover":
			if config.plugins.KravenFHD.MovieSelectionEPGSize.value == "big":
				self.skinSearchAndReplace.append(['<constant-widget name="msnc33"/>', '<constant-widget name="msnc36"/>'])
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
		self.appendSkinFile(self.daten + config.plugins.KravenFHD.SerienRecorder.value + ".xml")

		### MediaPortal
		console = eConsoleAppContainer()
		if fileExists("/usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/plugin.py"):
			if config.plugins.KravenFHD.MediaPortal.value == "mediaportal":
				if config.plugins.KravenFHD.IBColor.value == "all-screens" and config.plugins.KravenFHD.IconStyle.value == "icons-light" and config.plugins.KravenFHD.IBStyle.value == "gradient":
					console.execute("tar xf /usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/data/MediaPortal.tar.gz -C /usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins_1080/; tar xf /usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/data/MediaPortal_IB_icons-light.tar.gz -C /usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins_1080/KravenFHD/; tar xf /usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/data/Player_IB_icons-light.tar.gz -C /usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins_1080/KravenFHD/simpleplayer/")
				elif config.plugins.KravenFHD.IBColor.value == "all-screens" and config.plugins.KravenFHD.IconStyle.value == "icons-light" and config.plugins.KravenFHD.IBStyle.value == "box":
					console.execute("tar xf /usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/data/MediaPortal.tar.gz -C /usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins_1080/; tar xf /usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/data/MediaPortal_box_icons-light.tar.gz -C /usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins_1080/KravenFHD/; tar xf /usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/data/Player_box_icons-light.tar.gz -C /usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins_1080/KravenFHD/simpleplayer/")
				elif config.plugins.KravenFHD.IBColor.value == "all-screens" and config.plugins.KravenFHD.IconStyle.value == "icons-dark" and config.plugins.KravenFHD.IBStyle.value == "gradient":
					console.execute("tar xf /usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/data/MediaPortal.tar.gz -C /usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins_1080/; tar xf /usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/data/MediaPortal_IB_icons-dark.tar.gz -C /usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins_1080/KravenFHD/; tar xf /usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/data/Player_IB_icons-dark.tar.gz -C /usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins_1080/KravenFHD/simpleplayer/")
				elif config.plugins.KravenFHD.IBColor.value == "all-screens" and config.plugins.KravenFHD.IconStyle.value == "icons-dark" and config.plugins.KravenFHD.IBStyle.value == "box":
					console.execute("tar xf /usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/data/MediaPortal.tar.gz -C /usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins_1080/; tar xf /usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/data/MediaPortal_box_icons-dark.tar.gz -C /usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins_1080/KravenFHD/; tar xf /usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/data/Player_box_icons-dark.tar.gz -C /usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins_1080/KravenFHD/simpleplayer/")
				elif config.plugins.KravenFHD.IBColor.value == "only-infobar" and config.plugins.KravenFHD.IconStyle.value == "icons-light" and config.plugins.KravenFHD.IBStyle.value == "gradient":
					console.execute("tar xf /usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/data/MediaPortal.tar.gz -C /usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins_1080/; tar xf /usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/data/Player_IB_icons-light.tar.gz -C /usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins_1080/KravenFHD/simpleplayer/")
				elif config.plugins.KravenFHD.IBColor.value == "only-infobar" and config.plugins.KravenFHD.IconStyle.value == "icons-light" and config.plugins.KravenFHD.IBStyle.value == "box":
					console.execute("tar xf /usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/data/MediaPortal.tar.gz -C /usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins_1080/; tar xf /usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/data/Player_box_icons-light.tar.gz -C /usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins_1080/KravenFHD/simpleplayer/")
				elif config.plugins.KravenFHD.IBColor.value == "only-infobar" and config.plugins.KravenFHD.IconStyle.value == "icons-dark" and config.plugins.KravenFHD.IBStyle.value == "gradient":
					console.execute("tar xf /usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/data/MediaPortal.tar.gz -C /usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins_1080/; tar xf /usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/data/MediaPortal_icons-dark.tar.gz -C /usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins_1080/KravenFHD/; tar xf /usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/data/Player_IB_icons-dark.tar.gz -C /usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins_1080/KravenFHD/simpleplayer/")
				elif config.plugins.KravenFHD.IBColor.value == "only-infobar" and config.plugins.KravenFHD.IconStyle.value == "icons-dark" and config.plugins.KravenFHD.IBStyle.value == "box":
					console.execute("tar xf /usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/data/MediaPortal.tar.gz -C /usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins_1080/; tar xf /usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/data/MediaPortal_icons-dark.tar.gz -C /usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins_1080/KravenFHD/; tar xf /usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/data/Player_box_icons-dark.tar.gz -C /usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins_1080/KravenFHD/simpleplayer/")

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
		if config.plugins.KravenFHD.Logo.value in ("metrix-icons","minitv-metrix-icons"):
			self.installIcons(config.plugins.KravenFHD.MenuIcons.value)

		### Get weather data to make sure the helper config values are not empty
		self.get_weather_data()

		# Make ibar graphics
		if config.plugins.KravenFHD.IBStyle.value == "gradient":
			self.makeIbarpng(self.skincolorinfobarcolor, config.plugins.KravenFHD.InfobarColorTrans.value) # ibars

			if config.plugins.KravenFHD.SystemInfo.value == "systeminfo-small":
				self.makeRectpng(self.skincolorinfobarcolor, config.plugins.KravenFHD.InfobarColorTrans.value, 600, 277, "info") # sysinfo small
			elif config.plugins.KravenFHD.SystemInfo.value == "systeminfo-big":
				self.makeRectpng(self.skincolorinfobarcolor, config.plugins.KravenFHD.InfobarColorTrans.value, 600, 412, "info") # sysinfo big
			else:
				self.makeRectpng(self.skincolorinfobarcolor, config.plugins.KravenFHD.InfobarColorTrans.value, 600, 562, "info") # sysinfo bigsat

			self.makeRectpng(self.skincolorinfobarcolor, config.plugins.KravenFHD.InfobarColorTrans.value, 1358, 255, "shift") # timeshift bar

			self.makeRectpng(self.skincolorinfobarcolor, config.plugins.KravenFHD.InfobarColorTrans.value, 600, 300, "wsmall") # weather small

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
			pFile=open(fname,"r")
			for line in pFile:
				try:
					line=line.split("|")
					name=line[0]
					value=line[1]
					type=line[2].strip('\n')
					if not (name in ("customProfile","DebugNames","weather_owm_latlon","weather_accu_latlon","weather_realtek_latlon","weather_accu_id","weather_foundcity","weather_gmcode","weather_cityname","weather_language","weather_server") or (loadDefault and name == "defaultProfile")):
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
			# fix possible inconsistencies between boxes
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
					if not name in ("customProfile","DebugNames","weather_owm_latlon","weather_accu_latlon","weather_realtek_latlon","weather_accu_id","weather_foundcity","weather_gmcode","weather_cityname","weather_language","weather_server"):
						value=getattr(config.plugins.KravenFHD,name).value
						pFile.writelines(name+"|"+str(value)+"|"+str(type(value))+"\n")
				pFile.close()
				if msg:
					self.session.open(MessageBox,_("Profile ")+str(profile)+_(" saved successfully."), MessageBox.TYPE_INFO, timeout=5)
			except:
				self.session.open(MessageBox,_("Profile ")+str(profile)+_(" could not be saved!"), MessageBox.TYPE_INFO, timeout=15)

	def installIcons(self,author):

		pathname="http://coolskins.de/downloads/kraven/"
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

	def makeIbarpng(self, newcolor, newtrans):
		if config.plugins.KravenFHD.IBStyle.value == "gradient":

			width = 1920 # width of the png file
			gradientspeed = 2.0 # look of the gradient. 1 is flat (linear), higher means rounder

			ibarheight = 465 # height of ibar
			ibargradientstart = 75 # start of ibar gradient (from top)
			ibargradientsize = 150 # size of ibar gradient

			ibaroheight = 428 # height of ibaro
			ibarogradientstart = 98 # start of ibaro gradient (from top)
			ibarogradientsize = 150 # size of ibaro gradient

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
			img.save("/usr/share/enigma2/KravenFHD/ibar.png")

			img = Image.new("RGBA",(width,ibaroheight),(r,g,b,0))
			gradient = Image.new("L",(1,ibaroheight),0)
			for pos in range(0,ibarogradientstart):
				gradient.putpixel((0,pos),int(255*trans))
			for pos in range(0,ibarogradientsize):
				gradient.putpixel((0,ibarogradientstart+ibarogradientsize-pos-1),int(self.dexpGradient(ibarogradientsize,gradientspeed,pos)*trans))
			alpha = gradient.resize(img.size)
			img.putalpha(alpha)
			img.save("/usr/share/enigma2/KravenFHD/ibaro.png")
		else:
			pass

	def makeRectpng(self, newcolor, newtrans, width, height, pngname):
		if config.plugins.KravenFHD.IBStyle.value == "gradient":

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

			img.save("/usr/share/enigma2/KravenFHD/"+pngname+".png")
		else:
			pass

	def dexpGradient(self,len,spd,pos):
		if config.plugins.KravenFHD.IBStyle.value == "gradient":
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
		else:
			pass

	def makeBackpng(self):
		if config.plugins.KravenFHD.IBStyle.value == "gradient":
			# this makes a transparent png
			# not needed above, use it manually
			width = 1920 # width of the png file
			height = 1080 # height of the png file
			img = Image.new("RGBA",(width,height),(0,0,0,0))
			img.save("/usr/share/enigma2/KravenFHD/backg.png")
		else:
			pass

	def calcBrightness(self,color,factor):
		if config.plugins.KravenFHD.IBStyle.value == "gradient":
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
		else:
			pass

	def calcTransparency(self,trans1,trans2):
		if config.plugins.KravenFHD.IBStyle.value == "gradient":
			t1 = int(trans1,16)
			t2 = int(trans2,16)
			return str(hex(min(t1,t2))[2:4]).zfill(2)
		else:
			pass

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
			self.zipcode = ''
			self.accu_id = ''
			self.woe_id = ''
			self.gm_code = ''
			self.preview_text = ''
			self.preview_warning = ''
			
			if config.plugins.KravenFHD.weather_search_over.value == 'ip':
			  self.get_latlon_by_ip()
			elif config.plugins.KravenFHD.weather_search_over.value == 'name':
			  self.get_latlon_by_name()
			elif config.plugins.KravenFHD.weather_search_over.value == 'gmcode':
			  self.get_latlon_by_gmcode()
			
			self.generate_owm_accu_realtek_string()
			if config.plugins.KravenFHD.weather_server.value == '_accu':
			  self.get_accu_id_by_latlon()
	
			self.actCity=self.preview_text+self.preview_warning
			config.plugins.KravenFHD.weather_foundcity.value=self.city
			config.plugins.KravenFHD.weather_foundcity.save()
	
	def get_latlon_by_ip(self):
		try:
			res = requests.request('get', 'http://api.wunderground.com/api/2b0d6572c90d3e4a/geolookup/q/autoip.json')
			data = res.json()
			
			self.city = data['location']['city']
			self.lat = data['location']['lat'] 
			self.lon = data['location']['lon']
			
			self.preview_text = str(self.city) + '\nLat: ' + str(self.lat) + '\nLong: ' + str(self.lon)
		except:
			self.preview_text = _('No data for IP')
			
	def get_latlon_by_name(self):
		try:
			name = config.plugins.KravenFHD.weather_cityname.getValue()
			res = requests.request('get', 'http://maps.googleapis.com/maps/api/geocode/json?address=%s&sensor=true' % str(name))
			data = res.json()
			
			self.city = data['results'][0]['address_components'][1]['long_name']
			self.lat = data['results'][0]['geometry']['location']['lat']
			self.lon = data['results'][0]['geometry']['location']['lng']
			
			self.preview_text = str(self.city) + '\nLat: ' + str(self.lat) + '\nLong: ' + str(self.lon)
		except:
			self.get_latlon_by_ip()
			self.preview_warning = _('\n\nNo data for search string,\nfallback to IP')
	
	def get_latlon_by_gmcode(self):
		try:		  
			gmcode = config.plugins.KravenFHD.weather_gmcode.value
			res = requests.request('get', 'http://wxdata.weather.com/wxdata/weather/local/%s?cc=*' % str(gmcode))
			data = fromstring(res.text)
			
			self.city = data[1][0].text.split(',')[0]
			self.lat = data[1][2].text
			self.lon = data[1][3].text
			
			self.preview_text = str(self.city) + '\nLat: ' + str(self.lat) + '\nLong: ' + str(self.lon)
		except:
			self.get_latlon_by_ip()
			self.preview_warning = _('\n\nNo data for GM code,\nfallback to IP')
			
	def get_accu_id_by_latlon(self):
		try:
			res = requests.request('get', 'http://realtek.accu-weather.com/widget/realtek/weather-data.asp?%s' % config.plugins.KravenFHD.weather_realtek_latlon.value)
			cityId = re.search('cityId>(.+?)</cityId', str(res.text)).groups(1)
			self.accu_id = str(cityId[0])
			config.plugins.KravenFHD.weather_accu_id.value = str(self.accu_id)
			config.plugins.KravenFHD.weather_accu_id.save()
		except:
			self.preview_warning = _('No Accu ID found')
		if self.accu_id is None or self.accu_id=='':
			self.preview_warning = _('No Accu ID found')
			
	def generate_owm_accu_realtek_string(self):
		config.plugins.KravenFHD.weather_owm_latlon.value = 'lat=%s&lon=%s&units=metric&lang=%s' % (str(self.lat),str(self.lon),str(config.plugins.KravenFHD.weather_language.value))
		config.plugins.KravenFHD.weather_accu_latlon.value = 'lat=%s&lon=%s&metric=1&language=%s' % (str(self.lat), str(self.lon), str(config.plugins.KravenFHD.weather_language.value))
		config.plugins.KravenFHD.weather_realtek_latlon.value = 'lat=%s&lon=%s&metric=1&language=%s' % (str(self.lat), str(self.lon), str(config.plugins.KravenFHD.weather_language.value))
		config.plugins.KravenFHD.weather_owm_latlon.save()
		config.plugins.KravenFHD.weather_accu_latlon.save()
		config.plugins.KravenFHD.weather_realtek_latlon.save()
