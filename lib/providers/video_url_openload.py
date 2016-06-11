# -*- coding: utf-8 -*-

import re

domain="https://www.openload.co/"

def base10toN(num,n):
	num_rep={10:'a',
		11:'b',
		12:'c',
		13:'d',
		14:'e',
		15:'f',
		16:'g',
		17:'h',
		18:'i',
		19:'j',
		20:'k',
		21:'l',
		22:'m',
		23:'n',
		24:'o',
		25:'p',
		26:'q',
		27:'r',
		28:'s',
		29:'t',
		30:'u',
		31:'v',
		32:'w',
		33:'x',
		34:'y',
		35:'z'}
	new_num_string=''
	current=num
	while current!=0:
		remainder=current%n
		if 36>remainder>9:
			remainder_string=num_rep[remainder]
		elif remainder>=36:
			remainder_string='('+str(remainder)+')'
		else:
			remainder_string=str(remainder)
		new_num_string=remainder_string+new_num_string
		current=current/n
	return new_num_string

def decode(encoded):
	for octc in (c for c in re.findall(r'\\(\d{2,3})', encoded)):
		encoded = encoded.replace(r'\%s' % octc, chr(int(octc, 8)))
	return encoded.decode('utf8')


def run(hash,ump,referer=None):
	data=ump.get_page(domain+"embed/"+hash,None)
	# decodeOpenLoad made by mortael, please leave this line for proper credit :)
	aastring = re.compile("<script[^>]+>(ﾟωﾟﾉ[^<]+)<", re.DOTALL | re.IGNORECASE).findall(data)
	haha = re.compile(r"welikekodi_ya_rly = (\d+) - (\d+)", re.DOTALL | re.IGNORECASE).findall(data)
	haha = int(haha[0][0]) - int(haha[0][1])
	
	aastring = aastring[haha]

	aastring = aastring.replace("(ﾟДﾟ)[ﾟεﾟ]+(oﾟｰﾟo)+ ((c^_^o)-(c^_^o))+ (-~0)+ (ﾟДﾟ) ['c']+ (-~-~1)+","")
	aastring = aastring.replace("((ﾟｰﾟ) + (ﾟｰﾟ) + (ﾟΘﾟ))", "9")
	aastring = aastring.replace("((ﾟｰﾟ) + (ﾟｰﾟ))","8")
	aastring = aastring.replace("((ﾟｰﾟ) + (o^_^o))","7")
	aastring = aastring.replace("((o^_^o) +(o^_^o))","6")
	aastring = aastring.replace("((ﾟｰﾟ) + (ﾟΘﾟ))","5")
	aastring = aastring.replace("(ﾟｰﾟ)","4")
	aastring = aastring.replace("((o^_^o) - (ﾟΘﾟ))","2")
	aastring = aastring.replace("(o^_^o)","3")
	aastring = aastring.replace("(ﾟΘﾟ)","1")
	aastring = aastring.replace("(+!+[])","1")
	aastring = aastring.replace("(c^_^o)","0")
	aastring = aastring.replace("(0+0)","0")
	aastring = aastring.replace("(ﾟДﾟ)[ﾟεﾟ]","\\")
	aastring = aastring.replace("(3 +3 +0)","6")
	aastring = aastring.replace("(3 - 1 +0)","2")
	aastring = aastring.replace("(!+[]+!+[])","2")
	aastring = aastring.replace("(-~-~2)","4")
	aastring = aastring.replace("(-~-~1)","3")
	aastring = aastring.replace("(-~0)","1")
	aastring = aastring.replace("(-~1)","2")
	aastring = aastring.replace("(-~3)","4")
	aastring = aastring.replace("(0-0)","0")
	
	decodestring = re.search(r"\\\+([^(]+)", aastring, re.DOTALL | re.IGNORECASE).group(1)
	decodestring = "\\+"+ decodestring
	decodestring = decodestring.replace("+","")
	decodestring = decodestring.replace(" ","")
	
	decodestring = decode(decodestring)
	decodestring = decodestring.replace("\\/","/")
	
	if 'toString' in decodestring:
		base = re.compile(r"toString\(a\+(\d+)", re.DOTALL | re.IGNORECASE).findall(decodestring)[0]
		base = int(base)
		match = re.compile(r"(\(\d[^)]+\))", re.DOTALL | re.IGNORECASE).findall(decodestring)
		for repl in match:
			match1 = re.compile(r"(\d+),(\d+)", re.DOTALL | re.IGNORECASE).findall(repl)
			base2 = base + int(match1[0][0])
			repl2 = base10toN(int(match1[0][1]),base2)
			decodestring = decodestring.replace(repl,repl2)
		decodestring = decodestring.replace("+","")
		decodestring = decodestring.replace("\"","")
		videourl = re.search(r"(http[^\}]+)", decodestring, re.DOTALL | re.IGNORECASE).group(1)
	else:
		videourl = re.search(r"vr\s?=\s?\"|'([^\"']+)", decodestring, re.DOTALL | re.IGNORECASE).group(1)
	
#	headers = { 'User-Agent' : ump.ua,"Referer":domain+"embed/"+hash }
#	req = urllib2.Request(url, None, headers)
	return {"url":{"url":videourl,"referer":domain+"embed/"+hash}}