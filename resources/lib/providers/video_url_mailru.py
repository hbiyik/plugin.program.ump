import json

def run(hash,ump,referer=None):
	js=json.loads(ump.get_page("http://videoapi.my.mail.ru/videos/"+hash+".json","utf8"))
	videos=js["videos"]
	opts={}
	for video in videos:
		opts[video["key"]]=video["url"]
	return opts