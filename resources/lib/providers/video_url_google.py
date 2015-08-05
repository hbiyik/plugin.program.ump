import re
import json

def run(hash,ump):
	hash=json.loads(hash)
	html5=hash.get("html5",False)
	if html5:
		#html5 player
		hash.pop("html5")
		return hash
	else:
		#flash player
		src = ump.get_page(hash["url"],"utf8",referer=hash["referer"])
		videos=re.findall('"file": "(.*?)", "label": "(.*?)"',src)
		opts={}
		for video in videos:
			opts[video[1]]=video[0]
		return opts