# -*- coding: utf-8 -*-

import re
import urllib2

domain="https://www.openload.co/"

def base(decimal ,base) :
    list = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ".lower()
    otherbase = ""
    while decimal != 0 :
        otherbase = list[decimal % base] + otherbase
        decimal    = decimal / base
    return otherbase

def run(hash,ump,referer=None):
	data=ump.get_page(domain+"embed/"+hash,None)
	
	data = data.replace('\\/', '/') \
		.replace('&amp;', '&') \
		.replace('\xc9', 'E') \
		.replace('&#8211;', '-') \
		.replace('&#038;', '&') \
		.replace('&rsquo;', '\'') \
		.replace('\r', '') \
		.replace('\n', '') \
		.replace('\t', '') \
		.replace('&#039;', "'")

	content = ''

	patron = "<video(?:.|\s)*?<script\s[^>]*?>((?:.|\s)*?)<\/script"
	matches = re.compile(patron, re.IGNORECASE).findall(data)
	if len(matches) > 0:
		from third import aa
		content = aa.AADecoder(matches[0]).decode()

	if not content:
		patron = "(\s*eval\s*\(\s*function(?:.|\s)+?)<\/script>"
		matches = re.compile(patron, re.IGNORECASE).findall(data)
		if len(matches) > 0:
			from third import unpack
			from third import jj
			unpacked = unpack.unpack(matches[0])
			content = jj.JJDecoder(unpacked).decode()
	
	if content:
		url=""
		encoded=re.findall("}return (.*?)}\(\)",content)
		for p in encoded[0].split("+"):
			if p.startswith("\""):
				url=url+p[1:-1]
			else:
				n=int(p.split(")")[0].split(",")[1])
				b=int(p.split("(")[1].split(",")[0])
				url=url+base(n,27+b)
		#patron = r"window\.vr='(.*?)'\;"
		#matches = re.compile(patron, re.IGNORECASE).findall(content.replace('\\', ''))
		#if len(matches) > 0:
		headers = { 'User-Agent' : ump.ua,"Referer":domain+"embed/"+hash }
		req = urllib2.Request(url, None, headers)
		return {"url":{"url":urllib2.urlopen(req).geturl(),"referer":domain+"embed/"+hash}}