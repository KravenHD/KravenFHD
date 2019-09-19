# -*- coding: utf-8 -*-

#  Menu Icon Path Converter
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
from Tools.Directories import fileExists
from Poll import Poll

class KravenFHDMenuIconPath(Poll,Converter,object):
	def __init__(self, type):
		Poll.__init__(self)
		Converter.__init__(self, type)
		self.poll_interval = 100
		self.poll_enabled = True
		self.type = str(type)
		self.path = "/usr/share/enigma2/Kraven-menu-icons/"
		self.userpath = "/usr/share/enigma2/Kraven-user-icons/"
		if fileExists("/usr/share/enigma2/Kraven-menu-icons/kravenfhd_logo.png"):
			self.logo="/usr/share/enigma2/Kraven-menu-icons/kravenfhd_logo.png"
		else:
			self.logo = "/usr/share/enigma2/KravenFHD/logo.png"
		
		self.names=[
		("about_screen","about.png"), #ATV
		("about_screen","info.png"),
		("animation_setup","usage_setup.png"), #ATV
		("audio_menu","audio.png"), #ATV
		("audio_menu","setup.png"),
		("audio_setup","audio.png"), #ATV
		("audio_setup","setup.png"),
		("auto_scan","tuner.png"),
		("autolanguage_setup","setup.png"),
		("autores_setup","service_info.png"),
		("autoshutdown_setup","shutdowntimer.png"),
		("autotimer_setup","autotimers.png"), #ATV
		("av_setup","movie_list.png"),
		("blindscan","tuner.png"),
		("buttonsetup_setup","buttonsetup.png"), #ATV
		("buttonsetup_setup","setup.png"),
		("cablescan","search.png"), #ATV
		("cam_setup","camd.png"),
		("channelselection_setup","setup.png"),
		("ci_assign","ci.png"), #ATV
		("ci_assign","setup.png"),
		("ci_setup","ci.png"), #ATV
		("ci_setup","setup.png"),
		("crontimer_edit","crontimers.png"), #ATV
		("crontimer_edit","timer.png"),
		("deep_standby","shutdown.png"),
		("default_lists","paket.png"),
		("default_wizard","paket.png"),
		("device_manager","hdd.png"),
		("device_screen","device.png"), #ATV
		("device_screen","hdd.png"),
		("device_setup","setup.png"),
		("display_selection","look.png"),
		("display_setup","look.png"),
		("dns_setup","net.png"),
		("dreamplex","plex.png"), #ATV
		("dreamplex","plugin.png"),
		("dvd_player","dvd.png"), #ATV
		("dvdplayer","dvd.png"),
		("dvdplayer_setup","dvd.png"),
		("ecm_info","tuner.png"),
		("epg_menu","movie_list.png"),
		("epg_setup","movie_list.png"),
		("epgloadsave_menu","epg_menu.png"), #ATV
		("epgloadsave_menu","movie_list.png"),
		("epgrefresh","refresh.png"), #ATV
		("epgrefresh","setup.png"), #ATV
		("extended_selection","setup.png"),
		("factory_reset","reset.png"),
		("fansetup_config","fan.png"), #ATV
		("fansetup_config","setup.png"),
		("fastscan","fast_scan.png"), #ATV
		("fastscan","tuner.png"),
		("filecommand","filecom.png"),
		("googlemaps","google.png"),
		("harddisk_check","hdd.png"),
		("harddisk_convert","hdd.png"),
		("harddisk_init","hdd.png"),
		("harddisk_setup","hdd.png"),
		("hardisk_selection","hdd.png"),
		("hardreset","restart.png"),
		("hdmicec","setup.png"),
		("inadyn_setup","Inadyn_setup.png"), #ATV
		("inadyn_setup","setup.png"),
		("info_screen","info.png"),
		("infopanel","info.png"),
		("input_device_setup","keyb.png"),
		("ipbox_client_start","streamconvert.png"), #ATV
		("ipbox_client_start","webb.png"),
		("keyboard","keyb.png"),
		("keyboard_setup","keyb.png"),
		("language_setup","webb.png"),
		("lcd4linux","lcd_skin_setup.png"), #ATV
		("lcd4linux","plugin.png"),
		("lcd_setup","setup.png"),
		("lcd_skin_setup","lcd4linux.png"),
		("led_giga","LED_giga.png"), #ATV
		("led_giga","setup.png"),
		("ledmanager","led.png"), #ATV
		("ledmanager","setup.png"),
		("loadepgcache","setup.png"),
		("logs_setup","setup.png"),
		("manual_scan","tuner.png"),
		("media_player","media.png"), #ATV
		("mediaplayer","media.png"),
		("mediaportal","plugin.png"),
		("merlin_music_player","music.png"), #ATV
		("merlin_music_player","plugin.png"),
		("minidlna_setup","setup.png"),
		("movie_list","movie.png"),
		("moviebrowser","service_info.png"), #ATV
		("moviebrowser","plugin.png"),
		("multi_quick","remotecontrol.png"), #ATV
		("multi_quick","mqb.png"),
		("multi_quick","keyb.png"),
		("multi_quick","plugin.png"),
		("netafp_setup","net.png"),
		("netftp_setup","net.png"),
		("netmounts_setup","net.png"),
		("netnfs_setup","net.png"),
		("netrts_setup","net.png"),
		("netsabnzbd_setup","net.png"),
		("netsmba_setup","net.png"),
		("nettelnet_setup","net.png"),
		("netushare_setup","net.png"),
		("netvpn_setup","net.png"),
		("network_menu","net.png"),
		("network_setup","net.png"),
		("numzapext_setup","setup.png"),
		("openstore","webb.png"),
		("openwebif","webif.png"), #ATV
		("openwebif","plugin.png"),
		("osd3dsetup","look.png"),
		("osd_setup","look.png"),
		("osdsetup","look.png"),
		("osdsetup","osdsetup.png"), #ATV
		("parental_setup","look.png"),
		("parental_setup","parental.png"), #ATV
		("picturecenterfs","plugin.png"),
		("plugin_select","pluginmanager.png"), #ATV
		("plugin_select","plugin.png"),
		("plugin_selection","pluginmanager.png"), #ATV
		("plugin_selection","plugin.png"),
		("pluginhider_setup","pluginhider.png"), #ATV
		("pluginhider_setup","plugin.png"),
		("positioner_setup","positioner_setup.png"), #ATV
		("positioner_setup","tuner.png"),
		("powertimer_edit","powertimers.png"), #ATV
		("powertimer_edit","shutdowntimer.png"),
		("powertimer_edit","timer.png"),
		("pvmc_mainmenu","pvmc.png"), #ATV
		("pvmc_mainmenu","plugin.png"),
		("rcu select","remotecontrol.png"), #ATV
		("rcu select","setup.png"),
		("rec_setup","recording_setup.png"), #ATV
		("rec_setup","setup.png"),
		("recording_setup","setup.png"),
		("recordpaths","hdd.png"),
		("remote_setup","setup.png"),
		("remotecode","setup.png"),
		("remotecontrolcode","remotecontrol.png"), #ATV
		("remotecontrolcode","setup.png"),
		("rfmod_setup","setup.png"),
		("run_kodi","menu_kodi.png"), #ATV
		("run_kodi","plugin.png"),
		("sat_ip_client","satip.png"), #ATV
		("sat_ip_client","net.png"),
		("satfinder","satfinder.png"), #ATV
		("satfinder","tuner.png"),
		("saveepgcache","saveepgcache.png"), #ATV
		("saveepgcache","movie_list.png"),
		("scart_switch","scart.png"), #ATV
		("scart_switch","setup.png"),
		("select_menu","movie.png"),
		("select_menu","plugin.png"),
		("service_info_screen","info.png"), #ATV
		("service_info_screen","service_info.png"),
		("service_searching_selection","tuner.png"),
		("setup_epgenhanced","setup.png"),
		("setup_epggraphical","setup.png"),
		("setup_epginfobar","setup.png"),
		("setup_epginfobargraphical","setup.png"),
		("setup_epgmulti","setup.png"),
		("setup_selection","setup.png"),
		("sibsetup","plugin.png"),
		("skin_setup","setup.png"),
		("sleep","shutdowntimer.png"),
		("software_manager","setup.png"),
		("specialfeatures_menu","setup.png"),
		("sportspub_plugin","plugin.png"),
		("standby","power.png"),
		("standby_restart_list","shutdown.png"),
		("start_kodi","menu_kodi.png"), #ATV
		("start_kodi","plugin.png"), #ATV
		("startwizzard","paket.png"),
		("streamconvert","webb.png"),
		("subtitle_selection","sub.png"),
		("subtitle_setup","sub.png"),
		("sundtek_control_enter","plugin.png"),
		("supportchannel_ytchannel","supportchannel.png"), #ATV
		("supportchannel_ytchannel","plugin.png"),
		("system_selection","setup.png"),
		("tempfancontrol","fan.png"), #ATV
		("tempfancontrol","setup.png"),
		("time_setup","timer.png"),
		("timer_edit","timers.png"), #ATV
		("timer_edit","timer.png"),
		("timer_menu","timer.png"),
		("timezone_setup","timezone.png"), #ATV
		("timezone_setup","webb.png"),
		("timshift_setup","movie_list.png"),
		("timshift_setup","timshift_setup.png"), #ATV
		("tuner_setup","setup.png"),
		("usage_setup","setup.png"),
		("user_interface","setup.png"),
		("vfd_ew","VFD_INI.png"), #ATV
		("vfd_ew","setup.png"),
		("vfd_ini","VFD_INI.png"), #ATV
		("vfd_ini","setup.png"),
		("video_clipping","service_info.png"), #ATV
		("video_clipping","movie_list.png"),
		("video_finetune","videofinetune_setup.png"), #ATV
		("video_finetune","movie_list.png"),
		("video_menu","service_info.png"), #ATV
		("video_menu","movie_list.png"),
		("video_setup","service_info.png"), #ATV
		("video_setup","movie_list.png"),
		("videoenhancement_setup","movie_list.png"),
		("vmc_init_setup","vmc_setup.png"), #ATV
		("vmc_init_setup","setup.png"),
		("vmc_init_startvmc","vmc.png"), #ATV
		("vmc_init_startvmc","plugin.png"),
		("volume_adjust","AutomaticVolumeAdjustment.png"), #ATV
		("volume_adjust","setup.png"),
		("vps","streamconvert.png"), #ATV
		("vps","movie_list.png"),
		("vti_epg_panel","epg_setup.png"), #ATV
		("vti_epg_panel","paket.png"),
		("vti_menu","vtimenu.png"),
		("vti_menu","setup.png"), #ATV
		("vti_movies","movie_list.png"),
		("vti_movies","movie.png"), #ATV
		("vti_panel","vtimenu.png"),
		("vti_panel_news","info.png"), #ATV
		("vti_servicelist","service_info.png"),
		("vti_servicelist","info.png"), #ATV
		("vti_panel_news","webb.png"),
		("vti_subtitles","sub.png"),
		("vti_system_setup","setup.png"),
		("vti_timer","timer.png"),
		("vti_tv_radio","movie_list.png"),
		("vti_tv_radio","movie.png"), #ATV
		("vti_user_interface","user_interface.png"), #ATV
		("vti_user_interface","camd.png"),
		("webradiofs","webradioFS.png"), #ATV
		("webradiofs","plugin.png"),
		("xbmc_starten","plugin.png"),
		("yamp","plugin.png"),
		("yamp_music_player","plugin.png"),
		("youtube_tv","youtube.png"), #ATV
		("youtube_tv","plugin.png")
		]
	
	@cached
	def getText(self):
		try: # is it a screen? then we handle it according to title
			text=self.source.text
			if text in ("zapHistory","Senderhistorie","SkinSelector","Skinauswahl","LCD-Skinauswahl"):
				return self.logo
			if text in ("PluginBrowser","Erweiterungsmenü"):
				name=self.userpath+"plugin.png"
				if fileExists(name):
					return name
				name=self.path+"plugin.png"
				if fileExists(name):
					return name
			return self.logo
		except:
			try: # is it a menu? then we handle it according to current selection
				cur = self.source.current
				if cur and len(cur) > 2:
					selection = cur[2]
					name = self.userpath+selection+".png"
					if fileExists(name):
						return name
					name = self.path+selection+".png"
					if fileExists(name):
						return name
					name=""
					for pair in self.names:
						if pair[0] == selection.lower():
							name=self.userpath+pair[1]
							if name != "" and fileExists(name):
								return name
							name=self.path+pair[1]
							if name != "" and fileExists(name):
								return name
			except:
				pass
		name=self.userpath+"setup.png"
		if fileExists(name):
			return name
		name=self.path+"setup.png"
		if fileExists(name):
			return name
		return self.logo
	
	text = property(getText)
