import re
import urlparse

def run(hash,ump,referer=None):
    url = "http://animebam.com/embed/%s" % hash
    src = ump.get_page(url, "utf-8")
    url = ump.get_page(re.findall("sources:\s\[\{file:\s\"(.+?)\",", src, re.DOTALL)[0], None, referer=url, head=True)
    return {"url": url.geturl()}
