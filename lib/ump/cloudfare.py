from StringIO import StringIO
import gzip
import re
import time
import urllib2
from socket import setdefaulttimeout
from third import recaptcha
from urlparse import urlparse

noredirs=["/cdn-cgi/l/chk_jschl","/cdn-cgi/l/chk_captcha"]
try:
	import xbmc 
	language=xbmc.getLanguage(xbmc.ISO_639_1).lower()
except AttributeError:
	#backwards compatability
	language="en"

max_sleep=30

def dec(s):
	offset=1 if s[0]=='+' else 0
	return int(eval(s.replace('!+[]','1').replace('!![]','1').replace('[]','0').replace('(','str(')[offset:]))

def readzip(err):
	if err.info().get('Content-Encoding') == 'gzip':
		buf = StringIO(err.read())
		f = gzip.GzipFile(fileobj=buf)
		stream = f.read()
	else:
		stream=err.read()
	return stream

def cflogin(new_url,ua,req,opener,tunnel,tmode,cj,cfagents,up):
	r2=urllib2.Request(new_url,headers={"Referer":req._Request__original,"User-agent":ua})
	r2=tunnel.pre(r2,tmode,cj)
	res=opener.open(r2)
	cookies=cj.make_cookies(res,r2)
	for cookie in cookies:
		cj.set_cookie(cookie)
	tunnel.cook(cj,cookies,tmode)
	cj.add_cookie_header(req)
	cfagents[up.netloc]={tmode:ua}
	
	
def check_cfagent(cj,up,tmode,cfagents):
	cval=None
	agent=None
	cdom=up.netloc
	if len(cdom.split("."))==3:
		cdom=".".join(cdom.split(".")[1:])
	for cookie in cj:
		if cdom in cookie.domain and cookie.name=="cf_clearance":
			cval=cookie.value
	if cval:
		agent=cfagents.get(up.netloc,{}).get(tmode,None)
	return agent	

def ddos_open(url,opener,req,data,timeout,cj,cfagents,cflocks,tunnel,tmode):
	up=urlparse(url)	
	cfagent=check_cfagent(cj,up,tmode,cfagents)
	if cfagent:
		req.add_header("User-agent",cfagent)
	setdefaulttimeout(timeout)
	try:
		response=opener.open(req,data,timeout)
	except urllib2.HTTPError, err:
		body=tunnel.post(readzip(err),tmode)
		ua=req.unredirected_hdrs.get("User-agent","")
		for p in ["Content-length","Cookie"]:
			if p in req.headers:
				req.headers.pop(p)
			if p in req.unredirected_hdrs:
				req.unredirected_hdrs.pop(p)
		if err.code == 503 and "/cdn-cgi/l/chk_jschl" in body:
			try:
				challenge = re.search(r'name="jschl_vc" value="(\w+)"', body).group(1)
				challenge_pass = re.search(r'name="pass" value="(.+?)"', body).group(1)
				builder = re.search(r"setTimeout\(function\(\){\s+(var t,r,a,f.+?\r?\n[\s\S]+?a\.value =.+?)\r?\n", body).group(1)
				builder = re.sub(r"a\.value =(.+?) \+ .+?;", r"\1", builder)
				builder = re.sub(r"\s{3,}[a-z](?: = |\.).+", "", builder)
			except Exception as e:
				raise
			d,k,m=re.findall(',\s(.*?)={"(.*?)":(.*?)}',builder)[0]
			ops=re.findall(d+"\."+k+"(.)\=(.*?)\;",builder)
			res=dec(m)
			for op in ops:
				res=eval("res"+op[0]+"dec('"+op[1]+"')")
			u=re.sub("https?://","",url)
			u=u.split("/")[0]
			answer= str(res+len(u))
			waittime=float(re.findall("\}\,\s([0-9]*?)\)\;",body)[0])/1000
			print "%s has been stalled for %d seconds due to cloudfare protection"%(err.url,waittime)
			time.sleep(waittime)
			new_url="%s://%s/cdn-cgi/l/chk_jschl?jschl_vc=%s&pass=%s&jschl_answer=%s"%(up.scheme,up.netloc,challenge,challenge_pass,answer)
			cflogin(new_url,ua,req,opener,tunnel,tmode,cj,cfagents,up)
			response=opener.open(req,data,timeout)
		elif err.code == 403 and "/cdn-cgi/l/chk_captcha" in body:
			hash=re.findall('data-sitekey="(.*?)"',body)[0]
			solver=recaptcha.UnCaptchaReCaptcha()
			token=solver.processCaptcha(hash, language, opener,ua,up.netloc+" requires Cloudfare Recaptcha")
			u=up.scheme+"://"+up.netloc+"/cdn-cgi/l/chk_captcha?g-recaptcha-response="+token
			cflogin(u,ua,req,opener,tunnel,tmode,cj,cfagents,up)
			response=opener.open(req,data,timeout)
		else:
			response=opener.open(req,data,timeout)
	return response