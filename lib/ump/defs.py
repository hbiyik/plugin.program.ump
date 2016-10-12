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
addon_stdir = xbmc.translatePath('special://home/userdata/addon_data/plugin.program.ump/stats')
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
addonsxmluri="http://boogie.us.to/repository.boogie.dist/addons.xml"
#content types
CT_AUDIO, CT_IMAGE, CT_VIDEO, CT_UMP = "audio", "image","video","ump" ##content types
LI_CTS={CT_AUDIO:"music",CT_IMAGE:"pictures",CT_VIDEO:"video",CT_UMP:"video"}
LI_SIS={CT_AUDIO:"audio",CT_IMAGE:"video",CT_VIDEO:"video",CT_UMP:"video"}
WID={CT_AUDIO:10502,CT_IMAGE:10002,CT_VIDEO:10025}
#media types
MT_MOVIE,MT_EPISODE,MT_ANIMEMOVIE,MT_ANIMEEPISODE="movie","episode","animemovie","animeepisode"
MT_MUSIC,MT_MUSICALBUM="song","musicalbum"
MT_ANIMECHAPTER="animechapter"
MT_OTHER="other"

mediapointer={
         defs.MT_MOVIE:["code"],
         defs.MT_SERIE:["code"],
         defs.MT_SEASON:["code","season"],
         defs.MT_EPISODE:["code","season","episode"],
         defs.MT_ANIMEMOVIE:["code"],
         defs.MT_ANIMESERIE:["code"],
         defs.MT_ANIMEEPISODE:["code","epsiode"],
         defs.MT_ARTIST:["code"],
         defs.MT_MUSICALBUM:["code","album"],
         defs.MT_MUSIC:["code","album","title"],
         defs.MT_MANGA:["code"],
         defs.MT_MANGACHAPTER:["code","episode"],
         defs.MT_OTHER:["code"]
         }

#media type to kodi content categories
media_to_cc={
         defs.MT_MOVIE:"movies",
         defs.MT_SERIE:"tvshows",
         defs.MT_SEASON:"albums",
         defs.MT_EPISODE:"episodes",
         defs.MT_ANIMEMOVIE:"movies",
         defs.MT_ANIMESERIE:"tvshows",
         defs.MT_ANIMEEPISODE:"episodes",
         defs.MT_ARTIST:"albums",
         defs.MT_MUSICALBUM:"albums",
         defs.MT_MUSIC:"albums",
         defs.MT_MANGA:"albums",
         defs.MT_MANGACHAPTER:"albums",
         defs.MT_OTHER:"files"      
             }

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