def run(ump):
	if ump.module == "ump" and ump.page == "root":
		from ump.providers import update_settings
		update_settings()
		#runs on root page only
		pass
	else:
		#runs on each addon run
		pass
