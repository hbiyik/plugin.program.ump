from prefs import dictate
import json

dictate(json.dumps({3:None}),1,2,3)
d={"1": {"2": {"3": "Test"}}, "3": None}
dictate(json.dumps(d),"1","2","3")