def direct():
	from sys import argv
	query=argv[2][1:]
	#run only on root
	if not "module=" in query and not "page=" in query:
		from dom import check
		from defs import addon_setxml,addon_bsetxml,kodi_setxml,kodi_bsetxml,kodi_favxml,kodi_bfavxml
		check(addon_setxml,addon_bsetxml)
		check(kodi_setxml,kodi_bsetxml)
		check(kodi_favxml,kodi_bfavxml)
	
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