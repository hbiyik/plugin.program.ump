import json

def run(hash,ump,referer=None):
	if not type(hash) is dict or not hash.get("html5",False):
		src = ump.get_page("http://ok.ru/dk?cmd=videoPlayerMetadata&mid="+hash,"utf8",referer=referer)
		js=json.loads(src)
		videos=js["videos"]
		opts={}
		for video in videos:
			if not video["disallowed"]:
				opts[video["name"]]=video["url"]
		return opts
	else:
		hash.pop("html5")
		return hash