CT_AUDIO, CT_IMAGE, CT_VIDEO = "audio", "image","video" ##content types
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
VIEW_SETTINGS={
	CC_FILES:"list",
	CC_SONGS:"thumb",
	CC_ARTISTS:"list",
	CC_ALBUMS:"thumb",#
	CC_MOVIES:"thumb",#
	CC_TVSHOWS:"default",
	CC_EPISODES:"default",
	CC_MUSICVIDEOS:"default",
	"N/A":"default"
	}