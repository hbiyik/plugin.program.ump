import re

def run(hash,ump,referer=None):
	src=ump.get_page("http://ishared.eu/video/"+hash,"utf-8")
	fname=re.findall('file: ([\w]*?)',src)
	vid=re.findall(fname[0]+' = "(.*?)"',src)
	return {"url1":vid[0]}