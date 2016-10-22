# -*- coding: utf-8 -*-

# -*- coding: utf-8 -*-
from third import youtube_dl
domain="https://openload.co/"
timeout=60*60*24
def run(hash,ump,referer=""):
	ydl = youtube_dl.YoutubeDL({"quiet":True,"nocheckcertificate":True})

	with ydl:
		result = ydl.extract_info(domain+"embed/"+hash,	download=False)

	if 'entries' in result:
		# Can be a playlist or a list of videos
		audio = result['entries'][0]
	else:
		# Just a video
		audio = result
	
	print audio
	return {"audio":audio["url"]}

import urllib2
import base64
import math
import re
from third import png
from third.jj import JJDecoder
from third.aa import AADecoder
import urllib
from HTMLParser import HTMLParser

domain="https://openload.co/"
encoding="utf-8"

def deobfus1(src):
	yvar=re.findall("magic\s*\=\s*(.*?)\.slice",src)[0]
	print yvar
	y=re.findall('var\s*'+yvar+'\s*\=.*?"(.*?)"',src)[0]
	print y
	mgc=ord(y[-1])
	y="	".join(y.split(unichr(mgc-1)))
	print y
	y=unichr(mgc-1).join(y.split(y[-1]))
	print y
	y=unichr(mgc).join(y.split("	"))
	print "."+y+"."
	s=[]
	for c in y:
		cc=ord(c)
		if cc>=33 and cc<=126:s.append(unichr(33+((cc+14)%94)))
		else:s.append(c)
	tmp="".join(s)
	print tmp
	str=tmp[0:len(tmp)-1]+unichr(ord(tmp[-1])+2)
	print str
	return str

def caesar_shift(s, shift=13):
	s2 = ''
	for c in s:
		if c.isalpha():
			limit = 90 if c <= 'Z' else 122
			new_code = ord(c) + shift
			if new_code > limit:
				new_code -= 26
			s2 += chr(new_code)
		else:
			s2 += c
	return s2

def unpack(html):
	strings = re.findall('{\s*var\s+a\s*=\s*"([^"]+)', html)
	shifts = re.findall('\)\);}\((\d+)\)', html)
	for s, shift in zip(strings, shifts):
		s = caesar_shift(s, int(shift))
		s = urllib.unquote(s)
		for i, replace in enumerate(['j', '_', '__', '___']):
			s = s.replace(str(i), replace)
		html += '<script>%s</script>' % (s)
	return html

def run2(hash,ump,referer=None):
	url=domain+"embed/"+hash
	html = ump.get_page(url, None)
	try: html = html.encode('utf-8')
	except: pass
	html = unpack(html) 
	
	decodes = []
	hidden_id = ''
	for match in re.finditer('<script[^>]*>(.*?)</script>', html, re.DOTALL):
		decode = ''
		encoded = match.group(1)
		match = re.search("(ﾟωﾟﾉ.*?\('_'\);)", encoded, re.DOTALL)
		if match:
			print 444
			decode = AADecoder(match.group(1)).decode()
			print decode
			decodes.append(decode)
			
		match = re.search('(.=~\[\].*\(\);)', encoded, re.DOTALL)
		if match:
			print 555
			decode = JJDecoder(match.group(1)).decode()
			print decode
			decodes.append(decode)
		
		match = re.search(r'=\s*\$\("#([^"]+)"', decode, re.DOTALL | re.IGNORECASE)
		yvar=re.findall("magic\s*\=\s*(.*?)\.slice",decode)
		if len(yvar):
			yvar=yvar[0]
			print yvar
			y=re.findall('var\s*'+yvar+'\s*\=.*?"(.*?)"',decode)[0]
			print y
			mgc=ord(y[-1])
			y="	".join(y.split(unichr(mgc-1)))
			print y
			y=unichr(mgc-1).join(y.split(y[-1]))
			print y
			y=unichr(mgc).join(y.split("	"))
			print "."+y+"."
			s=""
			for c in y:
				cc=ord(c)
				if cc>=33 and cc<=126:s=s+(unichr(33+((cc+14)%94)))
				else:s=s+c
			print s
			hidden_id=s[:-1]+unichr(ord(s[-1])+2)
			print hidden_id
		
	'''	if len(var):
			divid=re.findall(var[0]+'\s*\=\s*\$\("#(.*?)"\)',decode)
			if len(divid):
				hidden_id = divid[0]
				print hidden_id'''
	for d in decodes:
		print 11
		print d
	print html
	match = re.search(r'<span[^>]+id\s*="%s"[^>]*>([^<]+)' % (re.escape(hidden_id)), html, re.DOTALL | re.IGNORECASE)
	hidden_url = match.group(1)
	hiddenurl = HTMLParser().unescape(hidden_url)
	magic_number = 0
	for decode in decodes:
		match = re.search('charCodeAt\(\d+\)\s*\+\s*(\d+)\)', decode, re.DOTALL | re.I)
		if match:
			magic_number = match.group(1)
			break
	
	s = []
	for idx, i in enumerate(hiddenurl):
		j = ord(i)
		if (j >= 33 & j <= 126):
			j = 33 + ((j + 14) % 94)
			
		if idx == len(hiddenurl) - 1:
			j += int(magic_number)
		s.append(chr(j))
	res = ''.join(s)
	
	videoUrl = 'https://openload.co/stream/{0}?mime=true'.format(res)
	#dtext = videoUrl.replace('https', 'http')
	return {"url":videoUrl,"referer":url}