import urllib
import json
import xbmcgui
import re

def run(hash,ump):
	[hash,ref]=json.loads(hash)
	src=ump.get_page("http://webteizle.org/player/plusplayer.asp?v="+hash,"iso-8859-9")
	opts={}
	partlar=re.findall('video="(.*?)" id="(.*?)"',src)
	for part in partlar:
		opts[part[1]]="http://webteizle.org"+part[0]
	return opts

#run("mail/webteizle/_myvideo/1644")