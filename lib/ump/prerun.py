
def run(ump):
	#runs on root page only
	if ump.module == "ump" and ump.page == "root":
		from ump.providers import update_settings
		# syncronize providers to settings.xml
		update_settings()
		
		#sync webtunnel states
		from webtunnel import check_health
		check_health(ump)
	else:
		#runs on each addon run
		pass
