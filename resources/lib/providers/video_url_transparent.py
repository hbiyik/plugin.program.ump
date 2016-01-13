import json

def run(hash,ump,referer=None):
	try:
		return json.dumps(hash)
	except:
		return hash