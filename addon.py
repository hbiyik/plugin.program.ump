from lib.ump import prerun
prerun.direct()
import sys
import gc
from lib.ump import defs
sys.path.append(defs.addon_ldir)
from lib.ump import api
from lib.ump import postrun
#bookmark.resolve()
ump=api.ump()
prerun.run(ump)

ump.add_log("HANDLE       : %s"%str(ump.handle))
ump.add_log("MODULE       : %s"%str(ump.module))
ump.add_log("PAGE         : %s"%str(ump.page))
#print "ARGS         : " + str(ump.args)
ump.add_log("CONTENT_TYPE : %s"%str(ump.content_type))
#print "INFO         : " + str(ump.info)
#print "ART          : " + str(ump.art)

if ump.module == "ump" and ump.page=="root":
	ump.list_indexers()
elif ump.page== "urlselect":
	ump.url_select()
else:
	ump.load_indexer()

postrun.run(ump)		
ump.shut()
ump.add_log("CONTENT_CAT  : %s"%str(ump.content_cat))
del gc.garbage[:]
gc.collect()
ump.add_log("UMP:EOF")
