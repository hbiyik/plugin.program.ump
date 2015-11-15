import urllib2
import re
import time
import urlparse

def dec(s):
	offset=1 if s[0]=='+' else 0
	return int(eval(s.replace('!+[]','1').replace('!![]','1').replace('[]','0').replace('(','str(')[offset:]))

def ddos_open(opener,req,data,timeout):
	try:
		response=opener.open(req,data,timeout)
	except urllib2.HTTPError, err:
		body=err.read()
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
			domainp=urlparse.urlparse(err.url)
			domain=domainp.netloc.replace("www.","")
			answer = str(res + len(domain))
			waittime=6
			print "%s has been stalled for %d seconds due to cloudfare protection"%(domain,waittime)
			time.sleep(waittime)
			new_headers=dict(req.header_items())
			new_headers["referrer"]=req.get_full_url()
			new_url="%s://%s/cdn-cgi/l/chk_jschl?jschl_vc=%s&pass=%s&jschl_answer=%s"%(req.get_type(),domainp.netloc,challenge,challenge_pass,answer)
			new_req=urllib2.Request(new_url,headers=new_headers,data=req.get_data())
			del req
			response=opener.open(new_req,data,timeout)
		else:
			response=opener.open(req,data,timeout)
	return response