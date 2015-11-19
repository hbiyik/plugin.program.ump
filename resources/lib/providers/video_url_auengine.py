import re
import urlparse

def run(hash,ump,referer=None):
    src = ump.get_page("http://auengine.com/embed.php?file=%s" % hash, "utf-8")
    return {"url": re.findall("sources:\s\[\{file:\s\"(.+?)\",", src, re.DOTALL)[0]}
