import re

def run(hash,ump):
	html5=hash.get("html5",False)
	if html5:
		hash.pop("html5")
		return hash
	else:
		src = ump.get_page(hash["url"],"utf8",referer=hash["referer"])
		videos=re.findall('"?file"?: "(.*?)",\r?\n?\s*?"?label"?: "(.*?)",\r?\n?\s*?"?type',src)
		opts={}
		for video in videos:
			opts[video[1]]=video[0]
		return opts