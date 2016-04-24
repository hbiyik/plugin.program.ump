import xbmcaddon
import xbmc
from os import path

loglevel=1
addon = xbmcaddon.Addon('plugin.program.ump')
addon_dir = xbmc.translatePath( addon.getAddonInfo('path') )
addon_ldir = path.join(addon_dir,"lib")
addon_pdir = path.join(addon_ldir ,'providers')
addon_bdir = path.join(addon_dir,"resources","backup")
addon_setxml = path.join(addon_dir,"resources","settings.xml")
addon_bsetxml = path.join(addon_bdir,"settings.xml")
addon_ddir = xbmc.translatePath('special://home/userdata/addon_data/plugin.program.ump')
addon_preffile= path.join(xbmc.translatePath('special://home/userdata/addon_data/plugin.program.ump'),"prefs.json")
addon_cookfile= path.join(xbmc.translatePath('special://home/userdata/addon_data/plugin.program.ump'),"cookie")
kodi_ddir = xbmc.translatePath('special://home/userdata/')
kodi_sdir=xbmc.translatePath('special://skin/')
kodi_setxml = xbmc.translatePath('special://home/userdata/advancedsettings.xml')
kodi_bsetxml = path.join(addon_bdir,"advancedsettings.xml")
kodi_favxml = xbmc.translatePath('special://home/userdata/favourites.xml')
kodi_bfavxml = path.join(addon_bdir,"favourites.xml")
kodi_guixml = xbmc.translatePath('special://home/userdata/guisettings.xml')
arturi = "https://offshoregit.com/boogiepop/dataserver/ump/images/"
#arturi = "http://boogie.us.to/dataserver/ump/images/"
#arturi="D:/projects/git/dataserver/dataserver/ump/images/"
CT_AUDIO, CT_IMAGE, CT_VIDEO, CT_UMP = "audio", "image","video","ump" ##content types
LI_CTS={CT_AUDIO:"music",CT_IMAGE:"pictures",CT_VIDEO:"video",CT_UMP:"video"}
WID={CT_AUDIO:10502,CT_IMAGE:10002,CT_VIDEO:10025}
CC_FILES, CC_SONGS, CC_ARTISTS, CC_ALBUMS, CC_MOVIES, CC_TVSHOWS, CC_EPISODES, CC_MUSICVIDEOS = "files", "songs", "artists", "albums", "movies", "tvshows", "episodes", "musicvideos"  ##content categories
VIEW_MODES={
	"list":{
        'skin.confluence': 50,
        'skin.aeon.nox': 50,
        'skin.aeon.nox.5': 50,
        'skin.confluence-vertical': 50,
        'skin.jx720': 50,
        'skin.pm3-hd': 50,
        'skin.rapier': 50,
        'skin.simplicity': 50,
        'skin.slik': 50,
        'skin.touched': 50,
        'skin.transparency': 50,
        'skin.xeebo': 50,
		},
	"thumb":{
        'skin.confluence': 500,
        'skin.aeon.nox': 551,
        'skin.aeon.nox.5': 500,
        'skin.confluence-vertical': 500,
        'skin.jx720': 52,
        'skin.pm3-hd': 53,
        'skin.rapier': 50,
        'skin.simplicity': 500,
        'skin.slik': 53,
        'skin.touched': 500,
        'skin.transparency': 53,
        'skin.xeebo': 55,
		},
	}