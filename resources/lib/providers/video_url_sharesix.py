import re

def run(hash,ump):
	src=ump.get_page("http://sharesix.com/"+hash,"utf-8")
	link2=re.findall('href="(.*?)">Free</a>',src)
	src=ump.get_page("http://sharesix.com"+link2[0],"utf-8")
	key=re.findall("lnk1 = '(.*?)'",src)
	return {"url1":key[0]}