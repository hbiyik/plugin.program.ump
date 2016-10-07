import re
domain="http://allmyvideos.net/"
encoding="utf-8"
def run(hash,ump,referer=None):
    print hash
    page=ump.get_page(domain+"embed-"+hash+".html",encoding)
    part={"video":re.findall('"file"\s*:\s*"(.*?)"',page)[0]}
    print part
    return part