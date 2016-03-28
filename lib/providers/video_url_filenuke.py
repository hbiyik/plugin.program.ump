import re

def run(hash,ump,referer=None):
	src=ump.get_page("http://filenuke.com/f/"+hash,"utf-8",referer=referer)
	link2=re.findall('href="(.*?)">Free</a>',src)
	src=ump.get_page("http://filenuke.com"+link2[0],"utf-8",referer="http://filenuke.com/"+hash)
	key=re.findall("lnk234 = '(.*?)'",src)
	return {"url1":key[0]}