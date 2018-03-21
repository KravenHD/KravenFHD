# -*- coding: utf-8 -*-
#######################################################################
#
#
#  This plugin is licensed under the Creative Commons
#  Attribution-NonCommercial-ShareAlike 3.0 Unported License.
#  To view a copy of this license, visit http://creativecommons.org/licenses/by-nc-sa/3.0/
#  or send a letter to Creative Commons, 559 Nathan Abbott Way, Stanford, California 94305, USA.
#
#  This plugin is NOT free software. It is open source, you are allowed to
#  modify it (if you keep the license), but it may not be commercially
#  distributed other than under the conditions noted above.
#
#
#######################################################################

from Components.config import config, configfile, ConfigYesNo, ConfigSubsection, getConfigListEntry, ConfigSelection, ConfigNumber, ConfigText, ConfigInteger, ConfigClock, ConfigSlider, ConfigBoolean
from Components.SystemInfo import SystemInfo
from Components.PluginComponent import plugins
from shutil import move, rmtree
from os import environ, listdir, remove, rename, system, popen, path
from PIL import Image, ImageFilter
from boxbranding import getBoxType
from copy import deepcopy
import time, subprocess, re, requests
from Tools.Directories import fileExists

try:
	from boxbranding import getImageDistro
	if getImageDistro() == "openatv":
		from lxml import etree
		from xml.etree.cElementTree import fromstring
except ImportError:
	brand = False
	from xml import etree
	from xml.etree.cElementTree import fromstring

#######################################################################

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

config.plugins.KravenFHD.VEPGBorderList = ConfigSelection(default="ffffff", choices = ColorSelfList)
config.plugins.KravenFHD.VEPGBorderSelf = ConfigText(default="ffffff")
config.plugins.KravenFHD.VEPGBorder = ConfigText(default="ffffff")

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
				("steptime=66", _("15 px/sec")),
				("steptime=50", _("20 px/sec"))
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

config.plugins.KravenFHD.CategoryDebug = ConfigSelection(default="category", choices = [
				("category", _(" "))
				])

config.plugins.KravenFHD.Unskinned = ConfigSelection(default="none", choices = [
				("none", _("off")),
				("unskinned-colors-on", _("on"))
				])

config.plugins.KravenFHD.UnwatchedColorList = ConfigSelection(default="F0A30A", choices = ColorSelfList)
config.plugins.KravenFHD.UnwatchedColorSelf = ConfigText(default="F0A30A")
config.plugins.KravenFHD.UnwatchedColor = ConfigText(default="F0A30A")

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

config.plugins.KravenFHD.emptyline = ConfigSelection(default="emptyline", choices = [
				("emptyline", _("      "))
				])

config.plugins.KravenFHD.hidden = ConfigSelection(default="hidden-on", choices = [
				("hidden-on", _("      ")),
				("hidden-off", _("      "))
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

#############################################################

class ActivateSkinSettings:

	def __init__(self):
		self.datei = "/usr/share/enigma2/KravenFHD/skin.xml"
		self.dateiTMP = self.datei + ".tmp"
		self.daten = "/usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/data/"
		self.komponente = "/usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/comp/"
		self.picPath = "/usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/images/"
		self.profiles = "/etc/enigma2/"
		self.BoxName=self.getBoxName()
		self.E2DistroVersion=self.getE2DistroVersion()
		self.InternetAvailable=self.getInternetAvailable()

	def WriteSkin(self, silent=False):
		#silent = True  -> returned 0 or 1 (no gui mode)
		#silent = False -> returned some optional code for messages or another things in gui mode

		#error codes for silent mode 
		#0:"No Error"
		#1:"Error occurred"

		self.silent = silent

		if self.silent:
			if config.skin.primary_skin.value != "KravenFHD/skin.xml":
				print 'KravenFHD is not the primary skin. No restore action needed!'
				return 0
			self.E2settings = open("/etc/enigma2/settings", "r").read()

		return self.save()

	def calcBackgrounds(self, bg = None):
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

		if bg == 'background':
			return self.skincolorbackgroundcolor
		elif bg == 'infobar':
			return self.skincolorinfobarcolor

	def save(self):
		#refresh internet
		if not self.silent:
			self.InternetAvailable=self.getInternetAvailable()

		#clock
		self.actClockstyle="none"
		if not config.plugins.KravenFHD.InfobarStyle.value == "infobar-style-zz4":
			if self.InternetAvailable:
				self.actClockstyle=config.plugins.KravenFHD.ClockStyle.value
			else:
				self.actClockstyle=config.plugins.KravenFHD.ClockStyleNoInternet.value
		#weather
		self.actWeatherstyle="none"
		if self.InternetAvailable:
			if config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-nopicon","infobar-style-x1","infobar-style-x3","infobar-style-z2","infobar-style-zz1","infobar-style-zz2","infobar-style-zz3","infobar-style-zz4","infobar-style-zzz1"):
				self.actWeatherstyle=config.plugins.KravenFHD.WeatherStyle.value
			elif config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-x2","infobar-style-z1"):
				if fileExists("/usr/lib/enigma2/python/Plugins/Extensions/Netatmo/plugin.py"):
					self.actWeatherstyle=config.plugins.KravenFHD.WeatherStyle3.value
				else:
					self.actWeatherstyle=config.plugins.KravenFHD.WeatherStyle2.value
		#channelselection
		self.actChannelselectionstyle="none"
		if self.E2DistroVersion == "VTi":
			if config.plugins.KravenFHD.alternativeChannellist.value == "none":
				if SystemInfo.get("NumVideoDecoders",1) > 1:
					self.actChannelselectionstyle=config.plugins.KravenFHD.ChannelSelectionStyle2.value
				else:
					self.actChannelselectionstyle=config.plugins.KravenFHD.ChannelSelectionStyle.value
		elif self.E2DistroVersion == "openatv":
			if SystemInfo.get("NumVideoDecoders",1) > 1:
				self.actChannelselectionstyle=config.plugins.KravenFHD.ChannelSelectionStyle2.value
			else:
				self.actChannelselectionstyle=config.plugins.KravenFHD.ChannelSelectionStyle.value

		### Calculate Backgrounds
		self.calcBackgrounds()

		self.skin_lines = []
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

		### Channelname. Transparency 50%, color always grey
		self.skinSearchAndReplace.append(['name="KravenNamebg" value="#A01B1775', 'name="KravenNamebg" value="#7F7F7F7F'])

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
		else:
			if not self.actChannelselectionstyle in ("channelselection-style-minitv2","channelselection-style-minitv22","channelselection-style-minitv33","channelselection-style-nobile-minitv33","channelselection-style-minitv3","channelselection-style-nobile-minitv3"):
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
		if self.E2DistroVersion == "VTi":
			system("tar xf /usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/data/logo-vti.tar.gz -C /usr/share/enigma2/KravenFHD/")
		else:
			system("tar xf /usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/data/logo-openatv.tar.gz -C /usr/share/enigma2/KravenFHD/")

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
				elif config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-x2","infobar-style-x3"):
					self.skinSearchAndReplace.append(['<!-- Infobar ibar -->', '<constant-widget name="box2-ib-x2-x3"/>'])
				elif config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-z1","infobar-style-z2"):
					self.skinSearchAndReplace.append(['<!-- Infobar ibar -->', '<constant-widget name="box2-ib-z1-z2"/>'])
				elif config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-zz1","infobar-style-zz4"):
					self.skinSearchAndReplace.append(['<!-- Infobar ibar -->', '<constant-widget name="box2-ib-zz1-zz4"/>'])
				elif config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-zz2","infobar-style-zz3"):
					self.skinSearchAndReplace.append(['<!-- Infobar ibar -->', '<constant-widget name="box2-ib-zz2-zz3"/>'])
				elif config.plugins.KravenFHD.InfobarStyle.value == "infobar-style-zzz1":
					self.skinSearchAndReplace.append(['<!-- Infobar ibar -->', '<constant-widget name="box2-ib-zzz1"/>'])
			elif config.plugins.KravenFHD.InfobarBoxColor.value == "texture":
				self.skinSearchAndReplace.append(['<constant-widget name="gradient-ib-top"/>', '<constant-widget name="texture-ib-top"/>'])
				if config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-nopicon","infobar-style-x1"):
					self.skinSearchAndReplace.append(['<!-- Infobar ibar -->', '<constant-widget name="texture-ib-np-x1"/>'])
				elif config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-x2","infobar-style-x3"):
					self.skinSearchAndReplace.append(['<!-- Infobar ibar -->', '<constant-widget name="texture-ib-x2-x3"/>'])
				elif config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-z1","infobar-style-z2"):
					self.skinSearchAndReplace.append(['<!-- Infobar ibar -->', '<constant-widget name="texture-ib-z1-z2"/>'])
				elif config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-zz1","infobar-style-zz4"):
					self.skinSearchAndReplace.append(['<!-- Infobar ibar -->', '<constant-widget name="texture-ib-zz1-zz4"/>'])
				elif config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-zz2","infobar-style-zz3"):
					self.skinSearchAndReplace.append(['<!-- Infobar ibar -->', '<constant-widget name="texture-ib-zz2-zz3"/>'])
				elif config.plugins.KravenFHD.InfobarStyle.value == "infobar-style-zzz1":
					self.skinSearchAndReplace.append(['<!-- Infobar ibar -->', '<constant-widget name="texture-ib-zzz1"/>'])
			else:
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

			### clock-android - Position
			if config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-x2","infobar-style-x3","infobar-style-z1","infobar-style-z2") and self.actClockstyle == "clock-android":
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
			self.skinSearchAndReplace.append(['font="Regular;45" position="904,815" size="726,55"', 'font="Regular;33" position="904,824" size="726,42"']) # ZZ4 now
			self.skinSearchAndReplace.append(['font="Regular;45" position="904,965" size="726,55"', 'font="Regular;33" position="904,974" size="726,42"']) # ZZ4 next
			self.skinSearchAndReplace.append(['font="Regular;45" position="657,921" size="708,55"', 'font="Regular;33" position="657,930" size="708,42"']) # ZZ2, ZZ3 now
			self.skinSearchAndReplace.append(['font="Regular;45" position="765,999" size="655,55"', 'font="Regular;33" position="765,1008" size="655,42"']) # ZZ3 next
			self.skinSearchAndReplace.append(['font="Regular;45" position="644,921" size="722,55"', 'font="Regular;33" position="644,930" size="722,42"']) # X2, X3, Z1, Z2 now
			self.skinSearchAndReplace.append(['font="Regular;45" position="644,999" size="722,55"', 'font="Regular;33" position="644,1008" size="722,42"']) # X2, X3, Z1, Z2 next
			self.skinSearchAndReplace.append(['font="Regular;45" position="644,837" size="722,55"', 'font="Regular;33" position="644,846" size="722,42"']) # X1 now
			self.skinSearchAndReplace.append(['font="Regular;45" position="644,972" size="722,55"', 'font="Regular;33" position="644,981" size="722,42"']) # X1 next
			self.skinSearchAndReplace.append(['font="Regular;45" position="298,876" size="1061,55"', 'font="Regular;33" position="298,885" size="1061,42"']) # no picon now
			self.skinSearchAndReplace.append(['font="Regular;45" position="298,954" size="1061,55"', 'font="Regular;33" position="298,963" size="1061,42"']) # no picon next
		elif config.plugins.KravenFHD.IBFontSize.value == "size-39":
			self.skinSearchAndReplace.append(['font="Regular;45" position="904,813" size="504,55"', 'font="Regular;39" position="904,816" size="504,49"']) # ZZ1, ZZZ1 now
			self.skinSearchAndReplace.append(['font="Regular;45" position="904,959" size="504,55"', 'font="Regular;39" position="904,962" size="504,49"']) # ZZ1, ZZZ1 next
			self.skinSearchAndReplace.append(['font="Regular;45" position="904,815" size="726,55"', 'font="Regular;39" position="904,818" size="726,49"']) # ZZ4 now
			self.skinSearchAndReplace.append(['font="Regular;45" position="904,965" size="726,55"', 'font="Regular;39" position="904,968" size="726,49"']) # ZZ4 next
			self.skinSearchAndReplace.append(['font="Regular;45" position="657,921" size="708,55"', 'font="Regular;39" position="657,924" size="708,49"']) # ZZ2, ZZ3 now
			self.skinSearchAndReplace.append(['font="Regular;45" position="765,999" size="655,55"', 'font="Regular;39" position="765,1002" size="655,49"']) # ZZ3 next
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

		if config.plugins.KravenFHD.IconStyle2.value == "icons-light2":
			system("tar xf /usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/data/icons-white.tar.gz -C /usr/share/enigma2/KravenFHD/")
		else:
			system("tar xf /usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/data/icons-black.tar.gz -C /usr/share/enigma2/KravenFHD/")

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
		if self.E2DistroVersion == "VTi":
			if config.plugins.KravenFHD.ScrollBar.value == "scrollbarWidth=0":
				self.skinSearchAndReplace.append(['scrollbarMode="showOnDemand"', 'scrollbarMode="showNever"'])
				self.skinSearchAndReplace.append(['scrollbarWidth="5"', 'scrollbarWidth="0"'])
			elif config.plugins.KravenFHD.ScrollBar.value == "scrollbarWidth=10":
				self.skinSearchAndReplace.append(['scrollbarWidth="5"', 'scrollbarWidth="15"'])
			elif config.plugins.KravenFHD.ScrollBar.value == "scrollbarWidth=15":
				self.skinSearchAndReplace.append(['scrollbarWidth="5"', 'scrollbarWidth="22"'])
		elif self.E2DistroVersion == "openatv":
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
		if self.E2DistroVersion == "openatv":
			self.skinSearchAndReplace.append(['skin_default/rc_vu_1.png,skin_default/rc_vu_2.png,skin_default/rc_vu_3.png,skin_default/rc_vu_4.png,skin_default/rc_vu_5.png', 'skin_default/rc.png,skin_default/rcold.png'])

		### KravenIconVPosition
		if config.plugins.KravenFHD.hidden.value == "hidden-on":
			if config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-nopicon","infobar-style-zz1","infobar-style-zzz1"):
				self.skinSearchAndReplace.append([',1030" valign="center" foregroundColor="KravenIcon"', ',1029" valign="center" foregroundColor="KravenIcon"'])
			elif config.plugins.KravenFHD.InfobarStyle.value == "infobar-style-x1":
				self.skinSearchAndReplace.append([',1038" valign="center" foregroundColor="KravenIcon"', ',1037" valign="center" foregroundColor="KravenIcon"'])
			elif config.plugins.KravenFHD.InfobarStyle.value == "infobar-style-zz4":
				self.skinSearchAndReplace.append([',1035" valign="center" foregroundColor="KravenIcon"', ',1034" valign="center" foregroundColor="KravenIcon"'])
			elif config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-x2","infobar-style-z1"):
				self.skinSearchAndReplace.append([',34" valign="center" foregroundColor="KravenIcon"', ',33" valign="center" foregroundColor="KravenIcon"'])
			self.skinSearchAndReplace.append([',1020" valign="center" foregroundColor="KravenIcon"', ',1019" valign="center" foregroundColor="KravenIcon"'])
		else:
			if config.plugins.KravenFHD.KravenIconVPosition.value == "vposition-3":
				if config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-nopicon","infobar-style-zz1","infobar-style-zzz1"):
					self.skinSearchAndReplace.append([',1030" valign="center" foregroundColor="KravenIcon"', ',1027" valign="center" foregroundColor="KravenIcon"'])
				elif config.plugins.KravenFHD.InfobarStyle.value == "infobar-style-x1":
					self.skinSearchAndReplace.append([',1038" valign="center" foregroundColor="KravenIcon"', ',1035" valign="center" foregroundColor="KravenIcon"'])
				elif config.plugins.KravenFHD.InfobarStyle.value == "infobar-style-zz4":
					self.skinSearchAndReplace.append([',1035" valign="center" foregroundColor="KravenIcon"', ',1032" valign="center" foregroundColor="KravenIcon"'])
				elif config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-x2","infobar-style-z1"):
					self.skinSearchAndReplace.append([',34" valign="center" foregroundColor="KravenIcon"', ',31" valign="center" foregroundColor="KravenIcon"'])
				self.skinSearchAndReplace.append([',1020" valign="center" foregroundColor="KravenIcon"', ',1017" valign="center" foregroundColor="KravenIcon"'])
			elif config.plugins.KravenFHD.KravenIconVPosition.value == "vposition-2":
				if config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-nopicon","infobar-style-zz1","infobar-style-zzz1"):
					self.skinSearchAndReplace.append([',1030" valign="center" foregroundColor="KravenIcon"', ',1028" valign="center" foregroundColor="KravenIcon"'])
				elif config.plugins.KravenFHD.InfobarStyle.value == "infobar-style-x1":
					self.skinSearchAndReplace.append([',1038" valign="center" foregroundColor="KravenIcon"', ',1036" valign="center" foregroundColor="KravenIcon"'])
				elif config.plugins.KravenFHD.InfobarStyle.value == "infobar-style-zz4":
					self.skinSearchAndReplace.append([',1035" valign="center" foregroundColor="KravenIcon"', ',1033" valign="center" foregroundColor="KravenIcon"'])
				elif config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-x2","infobar-style-z1"):
					self.skinSearchAndReplace.append([',34" valign="center" foregroundColor="KravenIcon"', ',32" valign="center" foregroundColor="KravenIcon"'])
				self.skinSearchAndReplace.append([',1020" valign="center" foregroundColor="KravenIcon"', ',1018" valign="center" foregroundColor="KravenIcon"'])
			elif config.plugins.KravenFHD.KravenIconVPosition.value == "vposition-1":
				if config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-nopicon","infobar-style-zz1","infobar-style-zzz1"):
					self.skinSearchAndReplace.append([',1030" valign="center" foregroundColor="KravenIcon"', ',1029" valign="center" foregroundColor="KravenIcon"'])
				elif config.plugins.KravenFHD.InfobarStyle.value == "infobar-style-x1":
					self.skinSearchAndReplace.append([',1038" valign="center" foregroundColor="KravenIcon"', ',1037" valign="center" foregroundColor="KravenIcon"'])
				elif config.plugins.KravenFHD.InfobarStyle.value == "infobar-style-zz4":
					self.skinSearchAndReplace.append([',1035" valign="center" foregroundColor="KravenIcon"', ',1034" valign="center" foregroundColor="KravenIcon"'])
				elif config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-x2","infobar-style-z1"):
					self.skinSearchAndReplace.append([',34" valign="center" foregroundColor="KravenIcon"', ',33" valign="center" foregroundColor="KravenIcon"'])
				self.skinSearchAndReplace.append([',1020" valign="center" foregroundColor="KravenIcon"', ',1019" valign="center" foregroundColor="KravenIcon"'])
			elif config.plugins.KravenFHD.KravenIconVPosition.value == "vposition+1":
				if config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-nopicon","infobar-style-zz1","infobar-style-zzz1"):
					self.skinSearchAndReplace.append([',1030" valign="center" foregroundColor="KravenIcon"', ',1031" valign="center" foregroundColor="KravenIcon"'])
				elif config.plugins.KravenFHD.InfobarStyle.value == "infobar-style-x1":
					self.skinSearchAndReplace.append([',1038" valign="center" foregroundColor="KravenIcon"', ',1039" valign="center" foregroundColor="KravenIcon"'])
				elif config.plugins.KravenFHD.InfobarStyle.value == "infobar-style-zz4":
					self.skinSearchAndReplace.append([',1035" valign="center" foregroundColor="KravenIcon"', ',1036" valign="center" foregroundColor="KravenIcon"'])
				elif config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-x2","infobar-style-z1"):
					self.skinSearchAndReplace.append([',34" valign="center" foregroundColor="KravenIcon"', ',35" valign="center" foregroundColor="KravenIcon"'])
				self.skinSearchAndReplace.append([',1020" valign="center" foregroundColor="KravenIcon"', ',1021" valign="center" foregroundColor="KravenIcon"'])
			elif config.plugins.KravenFHD.KravenIconVPosition.value == "vposition+2":
				if config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-nopicon","infobar-style-zz1","infobar-style-zzz1"):
					self.skinSearchAndReplace.append([',1030" valign="center" foregroundColor="KravenIcon"', ',1032" valign="center" foregroundColor="KravenIcon"'])
				elif config.plugins.KravenFHD.InfobarStyle.value == "infobar-style-x1":
					self.skinSearchAndReplace.append([',1038" valign="center" foregroundColor="KravenIcon"', ',1040" valign="center" foregroundColor="KravenIcon"'])
				elif config.plugins.KravenFHD.InfobarStyle.value == "infobar-style-zz4":
					self.skinSearchAndReplace.append([',1035" valign="center" foregroundColor="KravenIcon"', ',1037" valign="center" foregroundColor="KravenIcon"'])
				elif config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-x2","infobar-style-z1"):
					self.skinSearchAndReplace.append([',34" valign="center" foregroundColor="KravenIcon"', ',36" valign="center" foregroundColor="KravenIcon"'])
				self.skinSearchAndReplace.append([',1020" valign="center" foregroundColor="KravenIcon"', ',1022" valign="center" foregroundColor="KravenIcon"'])
			elif config.plugins.KravenFHD.KravenIconVPosition.value == "vposition+3":
				if config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-nopicon","infobar-style-zz1","infobar-style-zzz1"):
					self.skinSearchAndReplace.append([',1030" valign="center" foregroundColor="KravenIcon"', ',1033" valign="center" foregroundColor="KravenIcon"'])
				elif config.plugins.KravenFHD.InfobarStyle.value == "infobar-style-x1":
					self.skinSearchAndReplace.append([',1038" valign="center" foregroundColor="KravenIcon"', ',1041" valign="center" foregroundColor="KravenIcon"'])
				elif config.plugins.KravenFHD.InfobarStyle.value == "infobar-style-zz4":
					self.skinSearchAndReplace.append([',1035" valign="center" foregroundColor="KravenIcon"', ',1038" valign="center" foregroundColor="KravenIcon"'])
				elif config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-x2","infobar-style-z1"):
					self.skinSearchAndReplace.append([',34" valign="center" foregroundColor="KravenIcon"', ',37" valign="center" foregroundColor="KravenIcon"'])
				self.skinSearchAndReplace.append([',1020" valign="center" foregroundColor="KravenIcon"', ',1023" valign="center" foregroundColor="KravenIcon"'])

		### Header
		if self.E2DistroVersion == "openatv":
			self.skinSearchAndReplace.append(['<parameter name="VirtualKeyboard" value="67" />', '<parameter name="VirtualKeyboard" value="67,67" />'])
		if config.plugins.KravenFHD.EPGListSize.value == "big":
			self.skinSearchAndReplace.append(['<parameter name="EPGlistFont1" value="Regular;33" />', '<parameter name="EPGlistFont1" value="Regular;36" />'])
			self.skinSearchAndReplace.append(['<parameter name="EPGlistText1" value="0,5,40,40" />', '<parameter name="EPGlistText1" value="0,4,50,45" />'])
			self.skinSearchAndReplace.append(['<parameter name="EPGlistText2" value="0,5,250,40" />', '<parameter name="EPGlistText2" value="15,4,250,45" />'])
			self.skinSearchAndReplace.append(['<parameter name="EPGlistText3" value="280,0,700,40" />', '<parameter name="EPGlistText3" value="280,0,700,45" />'])
			self.skinSearchAndReplace.append(['<parameter name="EPGlistRecText" value="320,5,720,40" />', '<parameter name="EPGlistRecText" value="320,4,720,45" />'])
			self.skinSearchAndReplace.append(['<parameter name="EPGlistNonRecText" value="280,5,745,40" />', '<parameter name="EPGlistNonRecText" value="280,4,745,45" />'])
		if (not self.silent and config.usage.movielist_show_picon.value == True) or (self.silent and 'config.usage.movielist_show_picon=true' in self.E2settings):
			self.skinSearchAndReplace.append(['<parameter name="MovieListMinimalVTITitle" value="40,0,1000,40" />', '<parameter name="MovieListMinimalVTITitle" value="40,0,800,40" />'])
		self.appendSkinFile(self.daten + "header_begin.xml")
		if not config.plugins.KravenFHD.SelectionBorderList.value == "none":
			self.appendSkinFile(self.daten + "header_middle.xml")
		self.appendSkinFile(self.daten + "header_end.xml")

		### Volume
		self.appendSkinFile(self.daten + config.plugins.KravenFHD.Volume.value + ".xml")

		### ChannelSelection - VTi
		if self.E2DistroVersion == "VTi":
			self.skinSearchAndReplace.append(['name="giopet"', ' '])
			if config.plugins.KravenFHD.alternativeChannellist.value == "none":
				self.appendSkinFile(self.daten + self.actChannelselectionstyle + ".xml")
				if not self.silent and self.actChannelselectionstyle in ("channelselection-style-minitv33","channelselection-style-nobile-minitv33","channelselection-style-minitv2","channelselection-style-minitv22"):
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
				elif not self.silent and self.actChannelselectionstyle in ("channelselection-style-minitv","channelselection-style-minitv4","channelselection-style-nobile-minitv","channelselection-style-minitv-picon"):
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
				elif not self.silent and self.actChannelselectionstyle in ("channelselection-style-minitv3","channelselection-style-nobile-minitv3"):
					config.usage.use_pig.value = True
					config.usage.use_pig.save()
					config.usage.use_extended_pig.value = False
					config.usage.use_extended_pig.save()
					config.usage.use_extended_pig_channelselection.value = False
					config.usage.use_extended_pig_channelselection.save()
					config.usage.servicelist_preview_mode.value = False
					config.usage.servicelist_preview_mode.save()
				elif not self.silent:
					config.usage.use_pig.value = True
					config.usage.use_pig.save()
					config.usage.use_extended_pig.value = False
					config.usage.use_extended_pig.save()
					config.usage.use_extended_pig_channelselection.value = False
					config.usage.use_extended_pig_channelselection.save()
				if not self.silent:
					config.usage.servicelist_alternative_mode.value = False
					config.usage.servicelist_alternative_mode.save()
			else:
				self.appendSkinFile(self.daten + config.plugins.KravenFHD.ChannelSelectionHorStyle.value + ".xml")
				if not self.silent:
					config.usage.servicelist_alternative_mode.value = True
					config.usage.servicelist_alternative_mode.save()
		
		### ChannelSelection - openatv
		elif self.E2DistroVersion == "openatv":
			if not self.silent:
				config.usage.servicelist_mode.value = "standard"
				config.usage.servicelist_mode.save()
			self.skinSearchAndReplace.append(['name="giopet"', 'fieldMargins="15" nonplayableMargins="15" itemsDistances="8" progressBarWidth="78" progressPercentWidth="80" progressbarHeight="15"'])
			if not self.silent and (self.actChannelselectionstyle in ("channelselection-style-nopicon","channelselection-style-nopicon2","channelselection-style-xpicon","channelselection-style-zpicon","channelselection-style-zzpicon","channelselection-style-zzzpicon","channelselection-style-minitv3","channelselection-style-nobile-minitv3") or config.plugins.KravenFHD.ChannelSelectionMode.value == "zap"):
				config.usage.servicelistpreview_mode.value = False
			elif not self.silent:
				config.usage.servicelistpreview_mode.value = True
			if not self.silent:
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

		### Infobox
		if config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-nopicon","infobar-style-x1","infobar-style-x2","infobar-style-z1","infobar-style-zz1","infobar-style-zz4","infobar-style-zzz1"):
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
			elif self.E2DistroVersion == "openatv":
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
		if config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-nopicon","infobar-style-x1","infobar-style-zz1","infobar-style-zz4","infobar-style-zzz1"):
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
					self.skinSearchAndReplace.append(['position="409,1039" size="604,33" foregroundColor="KravenECM"', 'position="409,1039" size="508,33" foregroundColor="KravenECM"'])
				elif config.plugins.KravenFHD.tuner2.value == "10-tuner":
					self.skinSearchAndReplace.append(['position="409,1039" size="604,33" foregroundColor="KravenECM"', 'position="409,1039" size="556,33" foregroundColor="KravenECM"'])
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
		if config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-nopicon","infobar-style-x1","infobar-style-x3","infobar-style-z2","infobar-style-zz1","infobar-style-zz2","infobar-style-zz3","infobar-style-zz4","infobar-style-zzz1"):
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
					self.skinSearchAndReplace.append(['position="409,1039" size="604,33" foregroundColor="KravenECM"', 'position="409,1039" size="508,33" foregroundColor="KravenECM"'])
				elif config.plugins.KravenFHD.tuner2.value == "10-tuner":
					self.skinSearchAndReplace.append(['position="409,1039" size="604,33" foregroundColor="KravenECM"', 'position="409,1039" size="556,33" foregroundColor="KravenECM"'])
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

		if config.plugins.KravenFHD.SIBFont.value == "sibfont-small":
			self.appendSkinFile(self.daten + config.plugins.KravenFHD.SIB.value + "-small.xml")
		else:
			self.appendSkinFile(self.daten + config.plugins.KravenFHD.SIB.value + ".xml")
		if fileExists("/usr/lib/enigma2/python/Plugins/Extensions/SecondInfoBar/plugin.py"):
			config.plugins.SecondInfoBar.HideNormalIB.value = True
			config.plugins.SecondInfoBar.HideNormalIB.save()

		### Main XML
		if self.E2DistroVersion == "openatv":
			self.skinSearchAndReplace.append(['skin_default/rc_vu_1.png,skin_default/rc_vu_2.png,skin_default/rc_vu_3.png', 'skin_default/rc.png,skin_default/rcold.png'])
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
		if fileExists("/usr/lib/enigma2/python/Plugins/Extensions/PermanentTimeshift/plugin.py"):
			config.plugins.pts.showinfobar.value = False
			config.plugins.pts.showinfobar.save()

		### MSNWeatherPlugin XML
		if self.E2DistroVersion == "openatv" and self.InternetAvailable:
			if fileExists("/usr/lib/enigma2/python/Components/Converter/MSNWeather.pyo"):
				self.appendSkinFile(self.daten + "MSNWeatherPlugin.xml")
				if not fileExists("/usr/share/enigma2/KravenFHD/msn_weather_icons/1.png"):
					system("wget -q http://picons.mynonpublic.com/msn-icon.tar.gz -O /tmp/msn-icon.tar.gz; tar xf /tmp/msn-icon.tar.gz -C /usr/share/enigma2/KravenFHD/")
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
		if not self.silent and not config.plugins.KravenFHD.NumberZapExt.value == "none":
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

		### TimerEditScreen
		if self.E2DistroVersion == "VTi":
			self.appendSkinFile(self.daten + config.plugins.KravenFHD.TimerEditScreen.value + ".xml")
		elif self.E2DistroVersion == "openatv":
			self.appendSkinFile(self.daten + "timer-openatv.xml")

		### TimerListStyle
		if not self.silent and self.E2DistroVersion == "VTi":
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

		### EPGSelection
		if config.plugins.KravenFHD.EPGListSize.value == "big":
			self.skinSearchAndReplace.append(['font="Regular;33" foregroundColor="EPGSelection" itemHeight="45"', 'font="Regular;36" foregroundColor="KravenFont1" itemHeight="54"'])
		else:
			self.skinSearchAndReplace.append(['font="Regular;33" foregroundColor="EPGSelection" itemHeight="45"', 'font="Regular;33" foregroundColor="KravenFont1" itemHeight="45"'])
		if config.plugins.KravenFHD.EPGSelectionEPGSize.value == "big":
			self.skinSearchAndReplace.append(['font="Regular;33" foregroundColor="EPGSelection" position="1230,493" size="627,420"', 'font="Regular;36" foregroundColor="KravenFont1" position="1230,493" size="627,414"'])
			self.skinSearchAndReplace.append(['font="Regular;33" foregroundColor="EPGSelection" position="1230,440" size="627,462"', 'font="Regular;36" foregroundColor="KravenFont1" position="1230,440" size="627,460"'])
			self.skinSearchAndReplace.append(['font="Regular;33" foregroundColor="EPGSelection" position="1230,165" size="627,756"', 'font="Regular;36" foregroundColor="KravenFont1" position="1230,165" size="627,736"'])
			self.skinSearchAndReplace.append(['font="Regular;33" foregroundColor="EPGSelection" position="1230,112" size="627,798"', 'font="Regular;36" foregroundColor="KravenFont1" position="1230,112" size="627,782"'])
		else:
			self.skinSearchAndReplace.append(['font="Regular;33" foregroundColor="EPGSelection" position="1230,493" size="627,420"', 'font="Regular;33" foregroundColor="KravenFont1" position="1230,493" size="627,420"'])
			self.skinSearchAndReplace.append(['font="Regular;33" foregroundColor="EPGSelection" position="1230,440" size="627,462"', 'font="Regular;33" foregroundColor="KravenFont1" position="1230,440" size="627,462"'])
			self.skinSearchAndReplace.append(['font="Regular;33" foregroundColor="EPGSelection" position="1230,165" size="627,756"', 'font="Regular;33" foregroundColor="KravenFont1" position="1230,165" size="627,756"'])
			self.skinSearchAndReplace.append(['font="Regular;33" foregroundColor="EPGSelection" position="1230,112" size="627,798"', 'font="Regular;33" foregroundColor="KravenFont1" position="1230,112" size="627,798"'])
		self.appendSkinFile(self.daten + config.plugins.KravenFHD.EPGSelection.value + ".xml")

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
			if not self.silent and config.plugins.KravenFHD.GraphicalEPG.value == "text":
				config.epgselection.graph_type_mode.value = False
				config.epgselection.graph_type_mode.save()
				config.epgselection.graph_pig.value = False
				config.epgselection.graph_pig.save()
			elif not self.silent and config.plugins.KravenFHD.GraphicalEPG.value == "text-minitv":
				config.epgselection.graph_type_mode.value = False
				config.epgselection.graph_type_mode.save()
				config.epgselection.graph_pig.value = "true"
				config.epgselection.graph_pig.save()
			elif not self.silent and config.plugins.KravenFHD.GraphicalEPG.value == "graphical":
				config.epgselection.graph_type_mode.value = "graphics"
				config.epgselection.graph_type_mode.save()
				config.epgselection.graph_pig.value = False
				config.epgselection.graph_pig.save()
			elif not self.silent and config.plugins.KravenFHD.GraphicalEPG.value == "graphical-minitv":
				config.epgselection.graph_type_mode.value = "graphics"
				config.epgselection.graph_type_mode.save()
				config.epgselection.graph_pig.value = "true"
				config.epgselection.graph_pig.save()

		### VerticalEPG
		if self.E2DistroVersion == "VTi":
			self.appendSkinFile(self.daten + config.plugins.KravenFHD.VerticalEPG.value + ".xml")

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
		if config.plugins.KravenFHD.SerienRecorder.value == "serienrecorder":
			self.appendSkinFile(self.daten + config.plugins.KravenFHD.SerienRecorder.value + ".xml")

		### MediaPortal
		if fileExists("/usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/plugin.py"):
			if config.plugins.KravenFHD.MediaPortal.value == "mediaportal":
				if config.plugins.KravenFHD.IBColor.value == "all-screens" and config.plugins.KravenFHD.IconStyle.value == "icons-light" and config.plugins.KravenFHD.IBStyle.value == "grad":
					system("tar xf /usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/data/MediaPortal.tar.gz -C /usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins_1080/; tar xf /usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/data/MediaPortal_IB_icons-light.tar.gz -C /usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins_1080/KravenFHD/; tar xf /usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/data/Player_IB_icons-light.tar.gz -C /usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins_1080/KravenFHD/simpleplayer/")
				elif config.plugins.KravenFHD.IBColor.value == "all-screens" and config.plugins.KravenFHD.IconStyle.value == "icons-light" and config.plugins.KravenFHD.IBStyle.value == "box":
					system("tar xf /usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/data/MediaPortal.tar.gz -C /usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins_1080/; tar xf /usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/data/MediaPortal_box_icons-light.tar.gz -C /usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins_1080/KravenFHD/; tar xf /usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/data/Player_box_icons-light.tar.gz -C /usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins_1080/KravenFHD/simpleplayer/")
				elif config.plugins.KravenFHD.IBColor.value == "all-screens" and config.plugins.KravenFHD.IconStyle.value == "icons-dark" and config.plugins.KravenFHD.IBStyle.value == "grad":
					system("tar xf /usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/data/MediaPortal.tar.gz -C /usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins_1080/; tar xf /usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/data/MediaPortal_IB_icons-dark.tar.gz -C /usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins_1080/KravenFHD/; tar xf /usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/data/Player_IB_icons-dark.tar.gz -C /usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins_1080/KravenFHD/simpleplayer/")
				elif config.plugins.KravenFHD.IBColor.value == "all-screens" and config.plugins.KravenFHD.IconStyle.value == "icons-dark" and config.plugins.KravenFHD.IBStyle.value == "box":
					system("tar xf /usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/data/MediaPortal.tar.gz -C /usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins_1080/; tar xf /usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/data/MediaPortal_box_icons-dark.tar.gz -C /usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins_1080/KravenFHD/; tar xf /usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/data/Player_box_icons-dark.tar.gz -C /usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins_1080/KravenFHD/simpleplayer/")
				elif config.plugins.KravenFHD.IBColor.value == "only-infobar" and config.plugins.KravenFHD.IconStyle.value == "icons-light" and config.plugins.KravenFHD.IBStyle.value == "grad":
					system("tar xf /usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/data/MediaPortal.tar.gz -C /usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins_1080/; tar xf /usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/data/Player_IB_icons-light.tar.gz -C /usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins_1080/KravenFHD/simpleplayer/")
				elif config.plugins.KravenFHD.IBColor.value == "only-infobar" and config.plugins.KravenFHD.IconStyle.value == "icons-light" and config.plugins.KravenFHD.IBStyle.value == "box":
					system("tar xf /usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/data/MediaPortal.tar.gz -C /usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins_1080/; tar xf /usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/data/Player_box_icons-light.tar.gz -C /usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins_1080/KravenFHD/simpleplayer/")
				elif config.plugins.KravenFHD.IBColor.value == "only-infobar" and config.plugins.KravenFHD.IconStyle.value == "icons-dark" and config.plugins.KravenFHD.IBStyle.value == "grad":
					system("tar xf /usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/data/MediaPortal.tar.gz -C /usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins_1080/; tar xf /usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/data/MediaPortal_icons-dark.tar.gz -C /usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins_1080/KravenFHD/; tar xf /usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/data/Player_IB_icons-dark.tar.gz -C /usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins_1080/KravenFHD/simpleplayer/")
				elif config.plugins.KravenFHD.IBColor.value == "only-infobar" and config.plugins.KravenFHD.IconStyle.value == "icons-dark" and config.plugins.KravenFHD.IBStyle.value == "box":
					system("tar xf /usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/data/MediaPortal.tar.gz -C /usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins_1080/; tar xf /usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/data/MediaPortal_icons-dark.tar.gz -C /usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins_1080/KravenFHD/; tar xf /usr/lib/enigma2/python/Plugins/Extensions/KravenFHD/data/Player_box_icons-dark.tar.gz -C /usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins_1080/KravenFHD/simpleplayer/")
			else:
				if fileExists("/usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins_1080/KravenFHD/skin.xml"):
					system("rm -rf /usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/skins_1080/KravenFHD")

		### vti - atv
		if self.E2DistroVersion == "VTi":
			self.appendSkinFile(self.daten + "vti.xml")
		elif self.E2DistroVersion == "openatv":
			self.appendSkinFile(self.daten + "openatv.xml")

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
		return 0

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

	def installIcons(self,author):

		if self.InternetAvailable==False: 
			return

		if self.E2DistroVersion == "VTi":
			print "VTI Image found. Use VTI Server"
			pathname="http://coolskins.de/downloads/kraven/"
		elif self.E2DistroVersion == "openatv":
			print "ATV Image found. Use ATV Server"
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
			("infobar-style-zzz1",371)
			]
		for pair in ibarheights:
			if config.plugins.KravenFHD.InfobarStyle.value == pair[0]:
				self.makeGradientpng("ibar",width,pair[1],config.plugins.KravenFHD.InfobarGradientColorPrimary.value,config.plugins.KravenFHD.InfobarGradientColorSecondary.value,config.plugins.KravenFHD.InfobarColorTrans.value)
		if config.plugins.KravenFHD.InfobarStyle.value in ("infobar-style-x2","infobar-style-x3"):
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
			else:
				self.preview_text = _('No data for IP')

		except:
			self.preview_text = _('No data for IP')

	def get_latlon_by_name(self):

		if self.InternetAvailable==False: 
			return
		
		try:
			name = config.plugins.KravenFHD.weather_cityname.getValue()
			res = requests.get('http://maps.googleapis.com/maps/api/geocode/json?address=%s&sensor=true' % str(name), timeout=1)
			data = res.json()

			for entry in data['results'][0]['address_components']:
				if entry['types'][0]=='locality':
					self.city = entry['long_name']
					break
					
			self.lat = data['results'][0]['geometry']['location']['lat']
			self.lon = data['results'][0]['geometry']['location']['lng']

			self.preview_text = str(self.city) + '\nLat: ' + str(self.lat) + '\nLong: ' + str(self.lon)
		except:
			self.get_latlon_by_ip()
			self.preview_warning = _('\n\nNo data for search string,\nfallback to IP')

	def get_latlon_by_gmcode(self):

		if self.InternetAvailable==False: 
			return
		
		try:
			gmcode = config.plugins.KravenFHD.weather_gmcode.value
			res = requests.get('http://wxdata.weather.com/wxdata/weather/local/%s?cc=*' % str(gmcode), timeout=1)
			data = fromstring(res.text)

			self.city = data[1][0].text.split(',')[0]
			self.lat = data[1][2].text
			self.lon = data[1][3].text

			self.preview_text = str(self.city) + '\nLat: ' + str(self.lat) + '\nLong: ' + str(self.lon)
		except:
			self.get_latlon_by_ip()
			self.preview_warning = _('\n\nNo data for GM code,\nfallback to IP')

	def get_accu_id_by_latlon(self):

		if self.InternetAvailable==False: 
			return
		
		try:
			res = requests.get('http://realtek.accu-weather.com/widget/realtek/weather-data.asp?%s' % config.plugins.KravenFHD.weather_realtek_latlon.value, timeout=1)
			cityId = re.search('cityId>(.+?)</cityId', str(res.text)).groups(1)
			self.accu_id = str(cityId[0])
			config.plugins.KravenFHD.weather_accu_id.value = str(self.accu_id)
			config.plugins.KravenFHD.weather_accu_id.save()
		except:
			self.preview_warning = '\n\n'+_('No Accu ID found')
		if self.accu_id is None or self.accu_id=='':
			self.preview_warning = '\n\n'+_('No Accu ID found')

	def generate_owm_accu_realtek_string(self):
		config.plugins.KravenFHD.weather_owm_latlon.value = 'lat=%s&lon=%s&units=metric&lang=%s' % (str(self.lat),str(self.lon),str(config.plugins.KravenFHD.weather_language.value))
		config.plugins.KravenFHD.weather_accu_latlon.value = 'lat=%s&lon=%s&metric=1&language=%s' % (str(self.lat), str(self.lon), str(config.plugins.KravenFHD.weather_language.value))
		config.plugins.KravenFHD.weather_realtek_latlon.value = 'lat=%s&lon=%s&metric=1&language=%s' % (str(self.lat), str(self.lon), str(config.plugins.KravenFHD.weather_language.value))
		config.plugins.KravenFHD.weather_owm_latlon.save()
		config.plugins.KravenFHD.weather_accu_latlon.save()
		config.plugins.KravenFHD.weather_realtek_latlon.save()
