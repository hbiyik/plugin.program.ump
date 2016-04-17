
def run(ump):
	#runs on root page only
	if ump.module == "ump" and ump.page == "root":
		from ump.providers import update_settings
		# syncronize providers to settings.xml
		update_settings()
	else:
		#runs on each addon run
		pass

	if not ump.handle=="-1":
		#runs on each time addon is browsed
		from webtunnel import check_health
		check_health(ump)