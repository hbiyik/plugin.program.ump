import re
import urlparse

def run(hash,ump,referer=None):
    url = "http://embed.yourupload.com/%s" % hash
    src = ump.get_page(url, "utf-8")
    url = ump.get_page(re.findall("file:\s'(.+?)\.mp4',", src, re.DOTALL)[0], None, referer=url, head=True)
    return {"url": url.geturl()}
