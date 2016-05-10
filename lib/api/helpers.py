from string import punctuation
from third.unidecode import unidecode

def is_same(name1,name2,strict=False):
    predicate = lambda x:x not in punctuation+" "
    if strict:
        return filter(predicate,name1.lower())==filter(predicate,name2.lower())
    else:
        name1=name1.lower()
        name2=name2.lower()
        for word in ["the"]:
            name1=name1.replace("%s "%word,"")
            name2=name2.replace("%s "%word,"")
        return filter(predicate,unidecode(name1))==filter(predicate,unidecode(name2))
    
def absuri(pre,post):
    if pre.startswith("//"):
        pre="http:"+pre
    if pre.endswith("/"):
        pre=pre[:-1]
    if post.startswith("http://") or post.startswith("https://"):
        return post
    elif post.startswith("/"):
        d=pre.split("/")
        return d[0]+"//"+d[2]+post
    else:
        return pre+post
    
def match_cast(casting,info):
    match_cast=False
    if len(casting)>0:
        infocasting=info["cast"]
        cast_found=0
        for cast in casting:
            for icast in infocasting:
                if is_same(cast,icast):
                    cast_found+=1
                    continue

        if len(casting)==cast_found or (len(infocasting)==cast_found and len(casting)>len(infocasting)) or (len(casting)==cast_found and len(casting)<len(infocasting)):
            match_cast=True
    return match_cast

def check_codes(codes,info):
    have=False
    for cnum in codes:
        if "code%d"%cnum in info.keys() and not (info["code%d"%cnum ] == "" or info["code%d"%cnum ]== " " ):
            have=True
            break
    return have

def get_vidnames(max=5,info,org_first=True):
    is_serie="tvshowtitle" in info.keys() and not info["tvshowtitle"].replace(" ","") == ""
    names=[]
    if is_serie:
        ww=info["tvshowtitle"]
    else:
        ww=info["title"]
    if org_first:
        names.append(info["originaltitle"])
        names.append(ww)
    else:
        names.append(ww)
        names.append(info["originaltitle"])
    names.append(info["localtitle"])
    names.extend(info["alternates"])
    names2=[]
    for name in names:
        if not name in names2:
            names2.append(name)

    if max==0:
        return is_serie,names2
    else:
        return is_serie,names2[:max]
        
def max_meta(parts):
    #get the highest quality info from each part and mirror
    q=0
    max_w=0
    max_h=0
    max_s=0
    part_s=0
    max_key=""
    for part in parts:
        ss=0
        part_s=0
        for key,mirror in part["urls"].iteritems():
            if not part["urls"][key]["meta"] == {}:
                t=part["urls"][key]["meta"]["type"]
                w=part["urls"][key]["meta"]["width"]
                h=part["urls"][key]["meta"]["height"]
                s=part["urls"][key]["meta"]["size"]
                if not (w is None or h is None) and w*h>=q:
                    max_w=w
                    max_h=h
                    q=w*h
                if not s is None and s>ss:
                    max_key=key
                    part_s=s
                    ss=s
        max_s+=part_s
    return max_key,max_w,max_h,max_s

def humanint(size,precision=2):
    suffixes=['B','KB','MB','GB','TB']
    suffixIndex = 0
    while size > 1024:
        suffixIndex += 1 #increment the index of the suffix
        size = size/1024.0 #apply the division
    return "%.*f %s"%(precision,size,suffixes[suffixIndex])

def humanres(w,h):
    res=""
    heights=[240,360,480,576,720,1080,2160,4320]
    if h == 0 or w == 0 :
        return "???p"
    for height in heights:
        if h>=height*height/w:
            res=str(height)+"p"
    return res