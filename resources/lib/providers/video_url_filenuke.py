import re

def run(hash,ump,referer=None):
	src=ump.get_page("http://filenuke.com/"+hash,"utf-8")
	link2=re.findall('href="(.*?)">Free</a>',src)
	src=ump.get_page("http://filenuke.com"+link2[0],"utf-8")
	key=re.findall("lnk234 = '(.*?)'",src)
	return {"url1":key[0]}