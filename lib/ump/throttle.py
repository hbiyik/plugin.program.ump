import md5
import time
import os

throttle_path=""
def check():
    pass

def read(tid):
    if os.path.exists(os.path.join(throttle_path,tid)):
        pass

def write():
    pass

def id(*args,**kwargs):
    vals=""
    keys={}
    for arg in args:
        if isinstance(args,(tuple,list,dict)) 
    keys=sorted(keys)
    return md5.new(str(keys)).hexdigest()