import sys
import zlib

def resolve():
	if sys.argv[2].startswith("?hash="):
		sys.argv[2]=zlib.decompress(sys.argv[2][6:].decode("hex"))

def create(url=None):
	if not url is None:
		return sys.argv[0]+"?hash="+zlib.compress(url).encode("hex")
	elif not sys.argv[2].startswith("?hash="):
		return sys.argv[0]+"?hash="+zlib.compress(sys.argv[2]).encode("hex")
	else:
		return sys.argv[0]+sys.argv[2]
