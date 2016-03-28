import re
import urlparse

def run(hash,ump,referer=None):
    src = ump.get_page("http://mp4upload.com/embed-%s.html" % hash, "utf-8")
    return {"url": re.findall("'file':\s'(.+?)',", src, re.DOTALL)[0]}
