# -*- coding: utf-8 -*-
import xbmc, xbmcplugin, xbmcaddon
import os, sys, uuid, re, json
import resources.lib.common as common

handle = common.handle
Addon = xbmcaddon.Addon(common.AddonID)
imagesDir = common.imagesDir
module = 'keshet'
AddonName = "Idan Plus"
icon = Addon.getAddonInfo('icon')
sortBy = int(Addon.getSetting("makoSortBy"))
deviceID = Addon.getSetting("makoDeviceID")
if deviceID.strip() == '':
	uuidStr = str(uuid.uuid1()).upper()
	deviceID = "W{0}{1}".format(uuidStr[:8], uuidStr[9:])
	Addon.setSetting("makoDeviceID", deviceID)
username = Addon.getSetting("makoUsername")
password = Addon.getSetting("makoPassword")
baseUrl = 'https://www.mako.co.il'
endings = 'type=service&device=desktop&strto=true'
entitlementsServices = 'https://mass.mako.co.il/ClicksStatistics/entitlementsServicesV2.jsp'
UA = common.GetUserAgent()
bitrate = Addon.getSetting('mako_res')
if bitrate == '':
	bitrate = 'best'
makoShowShortSubtitle = Addon.getSetting("makoShowShortSubtitle") == 'true'

def GetCategoriesList(iconimage):
	sortString = common.GetLocaleString(30002) if sortBy == 0 else common.GetLocaleString(30003)
	name = "{0}: {1}".format(common.GetLocaleString(30001), sortString)
	common.addDir(name, "toggleSortingMethod", 7, iconimage, infos={"Title": name, "Plot": "{0}[CR]{1}[CR]{2} / {3}".format(name, common.GetLocaleString(30004), common.GetLocaleString(30002), common.GetLocaleString(30003))}, module=module, isFolder=False)
	name = "חיפוש"
	common.addDir(name, "{0}/autocomplete/vodAutocompletion.ashx?query={{0}}&max=60&id=query".format(baseUrl), 6, os.path.join(imagesDir, 'search.jpg'), infos={"Title": name, "Plot": "חיפוש"}, module=module)
	name = common.GetLabelColor("תכניות MakoTV", bold=True, color="none")
	common.addDir(name, "{0}/mako-vod-index".format(baseUrl), 1, os.path.join(imagesDir, 'vod.jpg'), infos={"Title": name, "Plot": "צפיה בתכני MakoTV"}, module=module)
	name = common.GetLabelColor("לייף סטייל", bold=True, color="none")
	common.addDir(name, "{0}/mako-vod-more/lifestyle".format(baseUrl), 1, os.path.join(imagesDir, 'lifestyle.jpg'), infos={"Title": name, "Plot": "צפיה בתכניות לייף סטייל"}, module=module)
	name = common.GetLabelColor("אוכל", bold=True, color="none")
	common.addDir(name, "{0}/mako-vod-special/cook-with-keshet".format(baseUrl), 1, os.path.join(imagesDir, 'lifestyle.jpg'), infos={"Title": name, "Plot": "צפיה בתכניות בנושא אוכל"}, module=module)
	name = common.GetLabelColor("דוקומנטרי - תכניות", bold=True, color="none")
	common.addDir(name, "{0}/mako-vod-more/docu_tv".format(baseUrl), 1, os.path.join(imagesDir, 'docu.jpg'), infos={"Title": name, "Plot": "צפיה בתכנים דוקומנטריים"}, module=module)
	name = common.GetLabelColor("דוקומנטרי - סרטים", bold=True, color="none")
	common.addDir(name, "{0}/mako-vod-more/docu_tv".format(baseUrl), 1, os.path.join(imagesDir, 'docu.jpg'), infos={"Title": name, "Plot": "צפיה בתכנים דוקומנטריים"}, module=module)
	name = common.GetLabelColor("הופעות", bold=True, color="none")
	common.addDir(name, "{0}/mako-vod-more/concerts".format(baseUrl), 1, os.path.join(imagesDir, 'live-music.jpg'), infos={"Title": name, "Plot": "צפיה בהופעות חיות"}, module=module)
	name = common.GetLabelColor("הרצאות", bold=True, color="none")
	common.addDir(name, "{0}/mako-vod-more/lectures".format(baseUrl), 1, os.path.join(imagesDir, 'lectures.jpg'), infos={"Title": name, "Plot": "צפיה בהרצאות"}, module=module)
	name = common.GetLabelColor(common.GetLocaleString(30608), bold=True, color="none")
	common.addDir(name, "{0}/mako-vod-music24".format(baseUrl), 1, os.path.join(imagesDir, '24telad.png'), infos={"Title": name, "Plot": "צפיה בתכניות מערוץ 24 החדש"}, module=module)
	name = common.GetLabelColor("החדשות", bold=True, color="none")
	common.addDir(name, "{0}/mako-vod-channel2-news".format(baseUrl), 2, os.path.join(imagesDir, 'news.jpg'), infos={"Title": name, "Plot": "צפיה בתכניות מערוץ החדשות"}, module=module)

def GetSeriesList(catName, url, iconimage):
	url = "{0}&{1}".format(url, endings) if "?" in url else "{0}?{1}".format(url, endings)
	prms = GetJson(url)
	if prms is None:
		"Cannot get {0} list".format(catName)
		return
	key2 = None
	picKey = "picI"
	if catName == "תכניות MakoTV":
		key1 = "allPrograms"
		picKey = "picVOD"
	elif catName == "אוכל" or catName == common.GetLocaleString(30608):
		key1 = "specialArea"
		key2 = "items"
	elif catName == "הופעות" or catName == "הרצאות" or catName == "דוקומנטרי - סרטים":
		key1 = "moreVOD"
		key2 = "items"
	else:
		key1 = "moreVOD"
		key2 = "programItems"
	if key2 is None:
		series = prms.get(key1, {})
	else:
		series = prms.get(key1, {}).get(key2, {})
	seriesCount = len(series)
	programNameFormat = int(Addon.getSetting("programNameFormat"))
	for serie in series:
		try:
			mode = 2
			title = common.encode(serie.get("title", "").strip(), "utf-8")
			subtitle = common.encode(serie.get("subtitle", "").strip(), "utf-8")
			url = serie.get("url", "")
			if url == "":
				url = serie.get("link", "")
			url = "{0}{1}".format(baseUrl, url)
			if "VOD-" in url:
				mode = 5 
				title = common.getDisplayName(title, subtitle, programNameFormat, bold=False) if makoShowShortSubtitle and subtitle != "" else common.GetLabelColor(title, keyColor="prColor", bold=False)
			else:
				title = common.GetLabelColor(title, keyColor="prColor", bold=True)
			icon = GetImage(serie, picKey, iconimage)
			description = common.encode(serie.get("brief", "").strip(), "utf-8")
			if "plot" in serie:
				description = "{0} - {1}".format(description, common.encode(serie["plot"].strip(), "utf-8"))
			infos = {"Title": title, "Plot": description}
			if mode == 2:
				common.addDir(title, url, 2, icon, infos, module=module, totalItems=seriesCount)
			else:
				common.addDir(title, url, 5, icon, infos, contextMenu=[(common.GetLocaleString(30005), 'RunPlugin({0}?url={1}&name={2}&mode=5&iconimage={3}&moredata=choose&module=keshet)'.format(sys.argv[0], common.quote_plus(url), common.quote_plus(title), common.quote_plus(icon)))], moreData=bitrate, module='keshet', isFolder=False, isPlayable=True)
		except Exception as ex:
			xbmc.log(str(ex), 3)
	if sortBy == 1:
		xbmcplugin.addSortMethod(handle, xbmcplugin.SORT_METHOD_LABEL)

def GetImage(prm, picKey, iconimage):
	icon = prm.get(picKey)
	if icon is None or icon == 'null' or icon == '':
		icon = prm.get('picC')
	if icon is None or icon == 'null' or icon == '':
		icon = prm.get('picB')
	if icon is None or icon == 'null' or icon == '':
		icon = prm.get('pic')
	if icon is None or icon == 'null' or icon == '':
		icon = prm.get('picUrl')
	return common.GetImageUrl(icon) if icon is not None else iconimage

def GetSeasonsList(url, iconimage):
	url = "{0}&{1}".format(url, endings) if "?" in url else "{0}?{1}".format(url, endings)
	prms = GetJson(url)
	if prms is None or "programData" not in prms or "seasons" not in prms["programData"]:
		xbmc.log("Cannot get Seasons list", 2)
		return
	if iconimage == os.path.join(imagesDir, 'search.jpg'):
		iconimage = GetImage(prms["programData"], "picI", iconimage)
	for prm in prms["programData"]["seasons"]:
		try:
			if "vods" not in prm:
				continue
			name = common.GetLabelColor(common.encode(prm.get('name', ''), "utf-8"), keyColor="timesColor", bold=True)
			url = "{0}{1}".format(baseUrl, prm["url"])
			description = common.encode(prm.get('brief', ''), "utf-8")
			infos = {"Title": name, "Plot": description}
			common.addDir(name, url, 3, iconimage, infos, module=module, moreData=prm["id"])
		except Exception as ex:
			xbmc.log(str(ex), 3)

def GetEpisodesList(url, icon, moreData=""):
	url = "{0}&{1}".format(url, endings) if "?" in url else "{0}?{1}".format(url, endings)
	prms = GetJson(url)
	if prms is None or "channelId" not in prms or "programData" not in  prms or "seasons" not in  prms["programData"]:
		xbmc.log("Cannot get Seasons list", 2)
		return
	programNameFormat = int(Addon.getSetting("programNameFormat"))
	videoChannelId=prms["channelId"]
	grids_arr = []
	for prm in prms["programData"]["seasons"]:
		if prm is None or "vods" not in prm or "id" not in prm or prm["id"].lower() != moreData.lower():
			continue
		episodesCount = len(prm["vods"])
		for episode in prm["vods"]:
			try:
				vcmid = episode["guid"]
				name = common.getDisplayName(common.encode(episode["title"], "utf-8"), common.encode(episode["shortSubtitle"], "utf-8"), programNameFormat) if makoShowShortSubtitle else common.GetLabelColor(common.encode(episode["title"], "utf-8"), keyColor="prColor", bold=False)
				url = "{0}/VodPlaylist?vcmid={1}&videoChannelId={2}".format(baseUrl, vcmid, videoChannelId)
				iconimage = GetImage(episode, 'picI', icon)
				description = common.encode(episode.get('subtitle', ''), "utf-8")
				i = episode["date"].find('|')
				if i < 0:
					aired = episode["date"][episode["date"].find(' ')+1:]
				else:
					a = episode["date"][:i].strip().split('/')
					aired = '20{0}-{1}-{2}'.format(a[2], a[1], a[0])
				infos = {"Title": name, "Plot": description, "Aired": aired}
				grids_arr.append((aired, name, url, iconimage, infos, [(common.GetLocaleString(30005), 'RunPlugin({0}?url={1}&name={2}&mode=4&iconimage={3}&moredata=choose&module=keshet)'.format(sys.argv[0], common.quote_plus(url), common.quote_plus(name), common.quote_plus(iconimage))), (common.GetLocaleString(30023), 'RunPlugin({0}?url={1}&name={2}&mode=4&iconimage={3}&moredata=set_mako_res&module=keshet)'.format(sys.argv[0], common.quote_plus(url), common.quote_plus(name), common.quote_plus(iconimage)))]))
			except Exception as ex:
				xbmc.log(str(ex), 3)
	grids_sorted = sorted(grids_arr,key=lambda grids_arr: grids_arr[0])
	grids_sorted.reverse()
	for aired, name, url, iconimage, infos, contextMenu in grids_sorted:
		common.addDir(name, url, 4, iconimage, infos, contextMenu=contextMenu, moreData=bitrate, module='keshet', isFolder=False, isPlayable=True)

def GetChannels(url, iconimage):
	html = common.OpenURL(url, headers={"User-Agent": UA})
	if html == "":
		return None
	match = re.compile("var makoliveJson ='(.*?)';").findall(html)
	resultJSON = json.loads(match[0])
	if resultJSON is None or len(resultJSON) < 1:
		return None
	for channel in resultJSON['list']:
		name = common.GetLabelColor(common.encode(channel['title'], "utf-8"), keyColor="prColor")
		infos = {"Title": name, "Plot": common.encode(channel['subtitle'], "utf-8")}
		url = '{0}{1}'.format(baseUrl, channel['link'])
		iconimage = channel['picUrl']
		common.addDir(name, url, 5, iconimage, infos, contextMenu=[(common.GetLocaleString(30005), 'RunPlugin({0}?url={1}&name={2}&mode=5&iconimage={3}&moredata=choose&module=keshet)'.format(sys.argv[0], common.quote_plus(url), common.quote_plus(name), common.quote_plus(iconimage)))], moreData=bitrate, module='keshet', isFolder=False, isPlayable=True)

def WatchLive(url, name='', iconimage='', quality='best'):
	channels = {
		'12': '{0}/mako-vod-live-tv/VOD-6540b8dcb64fd31006.htm'.format(baseUrl),
		'12c': '{0}/mako-vod-live-tv/VOD-319a699f834e661006.htm'.format(baseUrl),
		'24': '{0}/mako-vod-live-tv/VOD-b3480d2eff3fd31006.htm'.format(baseUrl),
		'2025': '{0}/mako-vod-live-tv/VOD-7469dcd71dcb761006.htm'.format(baseUrl)
	}
	PlayItem(channels[url], name, iconimage, quality)
	
def PlayItem(url, name='', iconimage='', quality='best'):
	html = common.OpenURL(url, headers={"User-Agent": UA})
	if html == "":
		return None
	match = re.compile("var videoJson ='(.*?)';").findall(html)
	prms = json.loads(match[0].replace("\\'","'"))
	if prms is None or len(prms) < 1:
		return None
	iconimage = GetImage(prms, 'pic_I', iconimage)
	videoChannelId=prms["chId"]
	vcmid = prms["guid"]
	url = "vcmid={0}&videoChannelId={1}".format(vcmid,videoChannelId)
	Play(url, name, iconimage, quality)

def Play(url, name='', iconimage='', quality='best'):
	common.DelCookies()
	headers={"User-Agent": UA}
	dv = url[url.find('vcmid=')+6: url.find('&videoChannelId=')]
	ch = url[url.find('&videoChannelId=')+16:]
	media = common.OpenURL('{0}/AjaxPage?jspName=playlist.jsp&vcmid={1}&videoChannelId={2}&galleryChannelId={1}&isGallery=false&consumer=web_html5&encryption=no'.format(baseUrl, dv, ch), headers=headers, responseMethod='json')['media']
	link, cookie_jar = GetLink(media, 'AKAMAI', dv, headers, quality)
	if link is None:
		link, cookie_jar = GetLink(media, 'CASTTIME', dv, headers, quality)
		if link is None:
			return None
	cookies = ";".join(['{0}'.format(common.quote('{0}={1}'.format(_cookie.name, _cookie.value))) for _cookie in cookie_jar])
	final = '{0}|User-Agent={1}&Cookie={2}'.format(link, UA, cookies)
	common.PlayStream(final, quality, name, iconimage)

def GetLink(media, cdn, dv, headers, quality):
	url = ''
	for item in media:
		if item['cdn'] == cdn.upper():
			url = item['url']
			break
	if url == '':
		return None, None
	if username.strip() == '':
		l = '{0}?et=gt&lp={1}&rv={2}'.format(entitlementsServices, url, cdn)
	else:
		l = '{0}?et=gt&na=2.0&da=6gkr2ks9-4610-392g-f4s8-d743gg4623k2&du={1}&dv={2}&rv={3}&lp={4}'.format(entitlementsServices, deviceID, dv, cdn, url)
	ticket = GetTicket(l, headers)
	if url.startswith('//'):
		url = 'https:{0}'.format(url) 
	#xbmc.log('{0}?{1}'.format(url, ticket), 5)
	session = common.GetSession()
	link = common.GetStreams('{0}&{1}'.format(url, ticket) if '?' in url else '{0}?{1}'.format(url, ticket), headers=headers, session=session, quality=quality)
	return link, session.cookies

def GetTicket(link, headers):
	text = common.OpenURL(link, headers=headers)
	result = json.loads(text)
	if result['caseId'] == '4':
		result = Login()
		text = common.OpenURL(link, headers=headers)
		result = json.loads(text)
		if result['caseId'] != '1':
			xbmc.executebuiltin("Notification({0}, You need to pay if you want to watch this video., {1}, {2})".format(AddonName, 5000 ,icon))
			return
	elif result['caseId'] != '1':
		xbmc.executebuiltin("Notification({0}, Cannot get access for this video., {1}, {2})".format(AddonName, 5000 ,icon))
		return
	return common.unquote_plus(result['tickets'][0]['ticket'])

def Login():
	headers={"User-Agent": UA}
	text = common.OpenURL('{0}?eu={1}&da=6gkr2ks9-4610-392g-f4s8-d743gg4623k2&dwp={2}&et=ln&du={3}'.format(entitlementsServices, username, password, deviceID), headers=headers)
	result = json.loads(text)
	if result['caseId'] != '1':
		return result
	text = common.OpenURL('{0}?da=6gkr2ks9-4610-392g-f4s8-d743gg4623k2&et=gds&du={1}'.format(entitlementsServices, deviceID), headers=headers)
	return json.loads(text)

def GetJson(url):
	resultJSON = common.OpenURL(url, headers={"User-Agent": UA}, responseMethod='json')
	if resultJSON is None or len(resultJSON) < 1:
		return None
	if "root" in resultJSON:
		return resultJSON["root"]
	else:
		return resultJSON

def Search(url, iconimage):
	search_entered = common.GetKeyboardText('מילים לחיפוש', '')
	if search_entered != '':
		url = url.format(search_entered.replace(' ', '%20'))
		params = GetJson(url)
		suggestions = params["suggestions"]
		data = params["data"]
		for i in range(len(suggestions)):
			if "mako-vod-channel2-news" in data[i]:
				continue
			url = "{0}{1}".format(baseUrl, data[i])
			name = common.UnEscapeXML(common.encode(suggestions[i], "utf-8"))
			infos={"Title": name, "Plot": name}
			if "VOD-" in data[i]:
				name = common.GetLabelColor(name, keyColor="chColor")
				common.addDir(name, url, 5, iconimage, infos, contextMenu=[(common.GetLocaleString(30005), 'RunPlugin({0}?url={1}&name={2}&mode=5&iconimage={3}&moredata=choose&module=keshet)'.format(sys.argv[0], common.quote_plus(url), common.quote_plus(name), common.quote_plus(iconimage)))], moreData=bitrate, module='keshet', isFolder=False, isPlayable=True)
			else:
				name = common.GetLabelColor(name, keyColor="prColor", bold=True)
				common.addDir(name, url, 2, iconimage, infos, module=module)
	else:
		return

def Run(name, url, mode, iconimage='', moreData=''):
	if mode == 0:
		GetCategoriesList(iconimage)
	elif mode == 1:	#------------- Series: -----------------
		GetSeriesList(common.GetUnColor(name), url, iconimage)
	elif mode == 2:	#------------- Seasons: -----------------
		GetSeasonsList(url, iconimage)
	elif mode == 3:	#------------- Episodes: -----------------
		GetEpisodesList(url, iconimage, moreData)
	elif mode == 4:	#------------- Playing episode  -----------------
		Play(url, name, iconimage, moreData)
	elif mode == 5:	#------------- Playing item: -----------------
		if moreData == '':
			moreData = 'best'
		PlayItem(url, name, iconimage, moreData)
	elif mode == 6:	#------------- Search items: -----------------
		Search(url, iconimage)
	elif mode == 7:	#------------- Toggle Lists' sorting method: -----------------
		common.ToggleSortMethod('makoSortBy', sortBy)
	elif mode == 8:
		GetChannels(url, iconimage)
	elif mode == 10:
		WatchLive(url, name, iconimage, moreData)
	elif mode == 20:
		ShowYears(iconimage)
	elif mode == 21:
		ShowMonthes(url, iconimage)
		
	common.SetViewMode('episodes')
