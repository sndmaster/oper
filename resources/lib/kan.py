# -*- coding: utf-8 -*-
import xbmc, xbmcgui, xbmcplugin, xbmcaddon
import os, re, json
import resources.lib.common as common

handle = common.handle
Addon = xbmcaddon.Addon(common.AddonID)
icon = Addon.getAddonInfo('icon')
imagesDir = common.imagesDir
sortBy = int(Addon.getSetting("kanSortBy"))
pagesPerList = int(Addon.getSetting("kanPagesPerList"))
youtubePlugin = 'plugin://plugin.video.youtube' #if Addon.getSetting("youtubePlugin") == "0" else 'plugin://plugin.video.MyYoutube'
module = 'kan'
baseUrl = 'https://www.kan.org.il'
userAgent = common.GetUserAgent()
headers={"User-Agent": userAgent}

def GetCategoriesList(iconimage):
	sortString = common.GetLocaleString(30002) if sortBy == 0 else common.GetLocaleString(30003)
	name = "{0}: {1}".format(common.GetLocaleString(30001), sortString)
	common.addDir(name, "toggleSortingMethod", 4, iconimage, {"Title": name, "Plot": "{0}[CR]{1}[CR]{2} / {3}".format(name, common.GetLocaleString(30004), common.GetLocaleString(30002), common.GetLocaleString(30003))}, module=module, isFolder=False)
	name = common.GetLabelColor("כל התוכניות", bold=True, color="none")
	common.addDir(name, '{0}/page.aspx?landingpageId=1039'.format(baseUrl), 1, iconimage, infos={"Title": name}, module=module, moreData=common.GetLocaleString(30602))
	name = common.GetLabelColor("תוכניות אקטואליה", bold=True, color="none")
	common.addDir(name, '{0}/page.aspx?landingPageId=1037'.format(baseUrl), 1, iconimage, infos={"Title": name}, module=module, moreData=common.GetLocaleString(30602))
	name = common.GetLabelColor("דיגיטל", bold=True, color="none")
	common.addDir(name, '{0}/page.aspx?landingPageId=1041'.format(baseUrl), 1, iconimage, infos={"Title": name}, module=module, moreData=common.GetLocaleString(30602))
	name = common.GetLabelColor("כאן חינוכית 23", bold=True, color="none")
	common.addDir(name, 'https://www.kankids.org.il', 5, iconimage, infos={"Title": name}, module=module, moreData=common.GetLocaleString(30607))
	name = common.GetLabelColor("תכניות רדיו", bold=True, color="none")
	common.addDir(name, '', 21, iconimage, infos={"Title": name}, module=module)
	name = common.GetLabelColor("פודקאסטים", bold=True, color="none")
	common.addDir(name, '', 31, iconimage, infos={"Title": name}, module=module)
	name = common.GetLabelColor("פודקאסטים לילדים", bold=True, color="none")
	common.addDir(name, '', 33, iconimage, infos={"Title": name}, module=module)

def GetSeriesList(url, catName):
	text = common.OpenURL(url)
	#matches = re.compile('class="component_sm_item news w-clearfix.+?href=\'.+?\?list=(.+?)\'.+?url\(\'(.+?)\'.+?<h3.+?>(.*?)</h3>.+?<p.+?>(.*?)</p>', re.S|re.I).findall(text)
	#for id, iconimage, name, description in matches:
	#	name = common.GetLabelColor(name.strip(), keyColor="prColor", bold=True)
	#	common.addDir(name, id, 2, iconimage, infos={"Title": name, "Plot": description}, module=module, moreData='youtube|||{0}'.format(catName), isFolder=False, urlParamsData={'catName': catName})
	matches = re.compile('<div class="component_sm_item news">(.*?)</a>', re.S).findall(text)
	for match in matches:
		m = re.compile('<a.*?href="(.+?)".+?"background-image: url\(\'(.+?)\'\);.*?"\s*title="(.*?)">.*?"news_up_txt">(.*?)</div>', re.S).findall(match)
		AddSeries(m, catName)
	matches = re.compile('<a class="magazine_info_link w-inline-block.+?href=\'(.+?)\'.+?"background-image: url\(\'(.+?)\'\);.+?"magazine_info_title">(.*?)</h2>.*?"magazine_info_txt">(.*?)</div>', re.S|re.I).findall(text)
	AddSeries(matches, catName)
	for match in matches:
		item = match[0]
		description = match[1]
		m = re.compile('url\(\'(.+?)\'\);.+?href=".+?/Program/\?catId=(.+?)["\'].+?class="it_small_title">(.*?)</div>', re.S|re.I).findall(item)
		if len(m) == 0:
			continue
		iconimage, id, name = m[0]
		name = common.GetLabelColor(name.strip(), keyColor="prColor", bold=True)
		common.addDir(name, id, 2, iconimage, infos={"Title": name, "Plot": description.strip()}, module=module, moreData='kan|||{0}'.format(catName), urlParamsData={'catName': catName})

def GetSubCategoriesList(url, catName):
	text = common.OpenURL(url)
	matches = re.compile('class="gallery_sec\s*w-clearfix(.+?)<script>', re.S).findall(text)
	for match in matches:
		m = re.compile('img src="(.*?)".*?<h2.*?>(.*?)</h2>.*?<a href=\'(.*?)\'.*?/a>', re.S).findall(match)
		if len(m) < 1:
			continue
		iconimage, name, url = m[0]
		name = common.GetLabelColor(name.strip(), keyColor="prColor", bold=True)
		common.addDir(name, url, 1, iconimage, infos={"Title": name}, module=module, urlParamsData={'catName': catName})

def AddSeries(matches, catName):
	for link, iconimage, name, description in matches:
		i = link.lower().find('catid=')
		if i > 0:
			link = link[i+6:]
		elif 'page.aspx' in link.lower():
			try:
				t = common.OpenURL(link)
				m = re.compile('magazine_info_link w-inline-block\s*"\s*href=\'.*?catid=(.*?)&').findall(t)
				link = m[0]
			except:
				pass
		name = common.GetLabelColor(name.strip(), keyColor="prColor", bold=True)
		common.addDir(name, link, 2, iconimage, infos={"Title": name, "Plot": description}, module=module, moreData='kan|||{0}'.format(catName), urlParamsData={'catName': catName})

def GetEpisodesList(data, iconimage, moreData=''):
	d = data.split(';')
	catId = d[0]
	page = 0 if len(d) < 2 else int(d[1])
	stopPage = page + pagesPerList
	prevPage = page - pagesPerList if page > pagesPerList else 0
	md = moreData.split('|||')
	site = md[0]
	catName = '' if len(md) < 2 else md[1]
	if site == 'youtube':
		xbmc.executebuiltin('container.Update({0}/playlist/{1}/)'.format(youtubePlugin, catId))
		return
	bitrate = Addon.getSetting('kan_res')
	if bitrate == '':
		bitrate = 'best'
	while True:
		page += 1
		url = '{0}/Program/getMoreProgram.aspx?count={1}&catId={2}'.format(baseUrl, page, catId)
		text = common.OpenURL(url)
		if 'ol' not in text:
			if page > pagesPerList:
				name = common.GetLabelColor(common.GetLocaleString(30011), color="green")
				common.addDir(name, '{0};{1}'.format(catId, prevPage), 2, iconimage, infos={"Title": name, "Plot": name}, module=module, urlParamsData={'catName': catName})
			break
		matches = re.compile('w-clearfix">.*?url\(\'(.+?)\'.+?onclick="playVideo\(\'.*?\',\'.*?\',\'(\d*)\'.+?<iframe.+?src="(.+?)".+?"content_title">(.+?)</.+?<p>(.+?)</p>', re.S).findall(text)
		for image, id, url, name, description in matches:
			name = common.GetLabelColor(name.strip(), keyColor="chColor")
			common.addDir(name, '{0}|||{1}'.format(url, id), 3, image, infos={"Title": name, "Plot": description.replace('&nbsp;', '').strip()}, module=module, moreData=bitrate, isFolder=False, isPlayable=True, urlParamsData={'catName': catName})
		if page == stopPage:
			if page > pagesPerList:
				name = common.GetLabelColor(common.GetLocaleString(30011), color="green")
				common.addDir(name, '{0};{1}'.format(catId, prevPage), 2, iconimage, infos={"Title": name, "Plot": name}, module=module, urlParamsData={'catName': catName})
			name = common.GetLabelColor(common.GetLocaleString(30012), color="green")
			common.addDir(name, '{0};{1}'.format(catId, page), 2, iconimage, infos={"Title": name, "Plot": name}, module=module, urlParamsData={'catName': catName})
			break

def GetRadioCategoriesList(iconimage):
	name = common.GetLabelColor("כאן ב", bold=True, color="none")
	common.addDir(name, '{0}/live/radio.aspx?stationid=3'.format(baseUrl), 22, os.path.join(imagesDir, "bet.png"), infos={"Title": name}, module=module)
	name = common.GetLabelColor("כאן גימל", bold=True, color="none")
	common.addDir(name, '{0}/live/radio.aspx?stationid=9'.format(baseUrl), 22, os.path.join(imagesDir, "gimel.png"), infos={"Title": name}, module=module)
	name = common.GetLabelColor("כאן 88", bold=True, color="none")
	common.addDir(name, '{0}/live/radio.aspx?stationid=4'.format(baseUrl), 22, os.path.join(imagesDir, "88.png"), infos={"Title": name}, module=module)
	name = common.GetLabelColor("כאן תרבות", bold=True, color="none")
	common.addDir(name, '{0}/live/radio.aspx?stationid=5'.format(baseUrl), 22, os.path.join(imagesDir, "culture.png"), infos={"Title": name}, module=module)
	name = common.GetLabelColor("כאן קול המוסיקה", bold=True, color="none")
	common.addDir(name, '{0}/live/radio.aspx?stationid=7'.format(baseUrl), 22, os.path.join(imagesDir, "music.png"), infos={"Title": name}, module=module)
	name = common.GetLabelColor("כאן מורשת", bold=True, color="none")
	common.addDir(name, '{0}/live/radio.aspx?stationid=6'.format(baseUrl), 22, os.path.join(imagesDir, "moreshet.png"), infos={"Title": name}, module=module)
	name = common.GetLabelColor("כאן Reka", bold=True, color="none")
	common.addDir(name, '{0}/live/radio.aspx?stationid=10'.format(baseUrl), 22, os.path.join(imagesDir, "reka.png"), infos={"Title": name}, module=module)

def GetRadioSeriesList(url, catName):
	text = common.OpenURL(url)
	match = re.compile('radio_online_group(.*?)footer_section_1', re.S).findall(text)
	matches = re.compile('class="radio_online_block.*?<a href=".*?progId=(.+?)" class="radio_online_pict.*?url\(\'(.*?)\'\);".*?title=["\'](.*?)["\']>.*?station_future_name.*?">(.*?)</div>', re.S).findall(match[0])
	for id, iconimage, name, description in matches:
		name = common.GetLabelColor(name.strip(), keyColor="prColor", bold=True)
		common.addDir(name, id, 23, iconimage, infos={"Title": name, "Plot": description}, module=module, moreData=catName, urlParamsData={'catName': catName})

def GetRadioEpisodesList(data, iconimage, catName):
	d = data.split(';')
	progId = d[0]
	page = 0 if len(d) < 2 else int(d[1])
	stopPage = page + pagesPerList - 1
	prevPage = page - pagesPerList if page > pagesPerList else 0
	while True:
		url = '{0}/Radio/getMoreItems.aspx?index={1}&progId={2}&subcatid=0&isEng=False'.format(baseUrl, page, progId)
		text = common.OpenURL(url)
		matches = re.compile('class="radio_program_partgroup">.*?class="radio_program_toggle top_plus.*?<div>(.*?)</div>.*?onclick="playItem\(\'(.*?)\'\)"', re.S).findall(text)
		for name, itemId in matches:
			name = common.GetLabelColor(name.strip(), keyColor="chColor")
			common.addDir(name, '{0}/radio/player.aspx?ItemId={1}'.format(baseUrl, itemId), 12, iconimage, infos={"Title": name}, module=module, moreData='best', isFolder=False, isPlayable=True, urlParamsData={'catName': catName})
		if len(matches) < 10:
			if page > pagesPerList:
				name = common.GetLabelColor(common.GetLocaleString(30011), color="green")
				common.addDir(name, '{0};{1}'.format(progId, prevPage), 23, iconimage, infos={"Title": name, "Plot": name}, module=module, urlParamsData={'catName': catName})
			break
		if page == stopPage:
			if page > pagesPerList:
				name = common.GetLabelColor(common.GetLocaleString(30011), color="green")
				common.addDir(name, '{0};{1}'.format(progId, prevPage), 23, iconimage, infos={"Title": name, "Plot": name}, module=module, urlParamsData={'catName': catName})
			name = common.GetLabelColor(common.GetLocaleString(30012), color="green")
			common.addDir(name, '{0};{1}'.format(progId, page+1), 23, iconimage, infos={"Title": name, "Plot": name}, module=module, urlParamsData={'catName': catName})
			break
		page += 1

def PlayRadioProgram(url, name='', iconimage='', quality='best'):
	text = common.OpenURL(url, headers=headers)
	match = re.compile('iframe src="(.*?)"').findall(text)
	match = re.compile('(.+)embed').findall(match[0])
	Play(match[0], name, iconimage, quality)

def Play(url, name='', iconimage='', quality='best'):
	u = url.split('|||')
	url = u[0]
	if (Addon.getSetting("kanPreferYoutube") != "true") and (len(u) > 1) and ('youtube' in url or 'youtu.be' in url):
		text = common.OpenURL('{0}/Item/?itemId={1}'.format(baseUrl, u[1]))
		match = re.compile('<script class="w-json" type="application/json">(.*?)</script>').findall(text)
		match = re.compile('src=\\\\"(.*?)\\\\"').findall(match[0])
		if len(match) == 1:
			url = match[0]
	if 'youtube' in url or 'youtu.be' in url:
		if url.endswith('/'):
			url = url[:-1]
		video_id = url[url.rfind('/')+1:]
		if '?' in video_id:
			video_id = video_id[:video_id.find('?')]
		final = '{0}/play/?video_id={1}'.format(youtubePlugin, video_id)
	elif 'omny.fm' in url:
		#text = common.OpenURL(url)
		#matches = re.compile('AudioUrl":"(.+?)"').findall(text)
		#if len(matches) == 0:
		#	return
		#final = 'https://omny.fm{1}'.format(matches[-1])
		final = '{0}{1}'.format(url[:-1], '.mp3')
	elif 'kaltura' in url:
		text = common.OpenURL(url, headers=headers)
		match = re.compile('window\.kalturaIframePackageData\s*=\s*{(.*?)};').findall(text)
		result = json.loads('{'+match[0]+'}')
		#final = result['entryResult']['meta']['downloadUrl']
		playerConfig = result['playerConfig']
		flavorAssets = result['entryResult']['contextData']['flavorAssets'][-1]
		final = 'https://cdnapisec.kaltura.com/p/{0}/sp/{0}00/playManifest/entryId/{1}/flavorIds/{2}/format/applehttp/protocol/https/a.m3u8?referrer=aHR0cHM6Ly93d3cua2FuLm9yZy5pbA==&clientTag=html5:v2.86&uiConfId={3}'.format(flavorAssets['partnerId'], playerConfig['entryId'], flavorAssets['id'], playerConfig['uiConfId'])
	else:
		final = GetPlayerKanUrl(url, headers=headers, quality=quality)
	
	listitem = xbmcgui.ListItem(path=final)
	listitem.setInfo(type="Video", infoLabels={"Title": name})
	xbmcplugin.setResolvedUrl(handle=handle, succeeded=True, listitem=listitem)

def GetPlayerKanUrl(url, headers={}, quality='best'):
	url = url.replace('https', 'http')
	i = url.rfind('http://')
	if i > 0:
		url = url[i:]
	url = url.replace('HLS/HLS', 'HLS')
	text = common.OpenURL(url, headers=headers)
	if 'ByPlayer' in url:
		match = re.compile('bynetURL:\s*"(.*?)"').findall(text)
		if len(match) == 0:
			match = re.compile('"UrlRedirector":"(.*?)"').findall(text)
		link = match[0].replace('https', 'http').replace('\u0026', '&')
	elif len(re.compile('media\.(ma)?kan\.org\.il').findall(url)) > 0:
		match = re.compile('hls:\s*?"(.*?)"').findall(text)
		link = match[0]
	elif 'kaltura' in url:
		text = common.OpenURL(url, headers=headers)
		match = re.compile('window\.kalturaIframePackageData\s*=\s*{(.*?)};').findall(text)
		result = json.loads('{'+match[0]+'}')
		link = result['entryResult']['meta']['hlsStreamUrl']
		link = common.GetStreams(link, headers=headers, quality=quality)
	else:
		match = re.compile("var\s*metadataURL\s*?=\s*?'(.+?)'").findall(text)
		text = common.OpenURL(match[0].replace('https_streaming=true', 'https_streaming=false'), headers=headers)
		match = re.compile("<SmilURL.*>(.+)</SmilURL>").findall(text)
		smil = match[0].replace('amp;', '')
		match = re.compile("<Server priority=['\"]1['\"]>(.+)</Server>").findall(text)
		server = match[0]
		link = common.urlunparse(common.url_parse(smil)._replace(netloc=server))
	if 'api.bynetcdn.com/Redirector' not in link:
		link = common.GetStreams(link, headers=headers, quality=quality)
	return '{0}|User-Agent={1}'.format(link, userAgent)

def WatchLive(url, name='', iconimage='', quality='best', type='video'):
	channels = {
		'11': '{0}/live/tv.aspx?stationid=2'.format(baseUrl),
		'11c': '{0}/live/tv.aspx?stationid=23'.format(baseUrl),
		'23': '{0}/live/tv.aspx?stationid=20'.format(baseUrl),
		'33': 'https://www.makan.org.il/live/tv.aspx?stationid=3',
		'kan4K': '{0}/live/tv.aspx?stationid=18'.format(baseUrl),
		'wfb2019': '{0}/Item/?itemId=53195'.format(baseUrl),
		'yfb2019': '{0}/Item/?itemId=52450'.format(baseUrl),
		'bet': '{0}/radio/player.aspx?stationId=3'.format(baseUrl),
		'gimel': '{0}/radio/player.aspx?stationid=9'.format(baseUrl),
		'culture': '{0}/radio/player.aspx?stationid=5'.format(baseUrl),
		'88': '{0}/radio/player.aspx?stationid=4'.format(baseUrl),
		'moreshet':'{0}/radio/player.aspx?stationid=6'.format(baseUrl),
		'music': '{0}/radio/player.aspx?stationid=7'.format(baseUrl),
		'kankids': 'https://www.kankids.org.il/radio/radio-kids.aspx',
		'reka': '{0}/radio/player.aspx?stationid=10'.format(baseUrl),
		'makan': '{0}/radio/player.aspx?stationId=13'.format(baseUrl)
		#'persian': 'http://farsi.kan.org.il/',
		#'nos': '{0}/radio/radio-nos.aspx'.format(baseUrl),
		#'oriental': '{0}/radio/oriental.aspx'.format(baseUrl),
		#'international': '{0}/radio/radio-international.aspx'.format(baseUrl)
	}
	channelUrl = channels[url]
	text = common.OpenURL(channelUrl, headers=headers)
	if text is None:
		return
	if url == 'persian':
		match = re.compile('id="playerFrame".*?src="(.*?)"', re.S).findall(text)
	elif '?itemId=' in channelUrl:
		match = re.compile('<div class=\'videoWrapper\'><iframe.*?src="(.*?)"').findall(text)
	elif type == 'video':
		match = re.compile('<iframe.*class="embedly-embed".*src="(.+?)"').findall(text)
	else:
		match = re.compile('<div class="player_content">.*?iframe src="(.*?)"', re.S).findall(text)
		if len(match) == 0:
			match = re.compile('iframeLink\s*?=\s*?"(.*?)"').findall(text)
	if 'dailymotion' in match[0]:
		id = re.compile('.*?video/(.*?)\?').findall(match[0])
		link = 'plugin://plugin.video.dailymotion_com/?url={0}&mode=playLiveVideo'.format(id[0])
	else:
		link = GetPlayerKanUrl(match[0], headers=headers, quality=quality)
	common.PlayStream(link, quality, name, iconimage)

def GetPodcastsList(page, iconimage):
	page = -1 if page == '' else int(page)
	stopPage = page + 1 + pagesPerList
	prevPage = page - pagesPerList if page  >= pagesPerList else -1
	while True:
		page += 1
		url = '{0}/podcast/morePrograms.aspx?index={1}'.format(baseUrl, page)
		text = common.OpenURL(url)
		matches = re.compile('title="(.+?)".+?url\(\'(.+?)\'.+?href=".+?\?progId=(.+?)".+?<p.+?>(.*?)</p>', re.S).findall(text)
		for name, image, id, description in matches:
			name = common.GetLabelColor(name.strip(), keyColor="prColor", bold=True)
			common.addDir(name, id, 32, image, infos={"Title": name, "Plot": description.replace('&nbsp;', '').strip()}, module=module, urlParamsData={'catName': 'כאן פודקאסטים'})
		if len(matches) < 10:
			if page >= pagesPerList:
				name = common.GetLabelColor(common.GetLocaleString(30011), color="green")
				common.addDir(name, str(prevPage), 31, iconimage, infos={"Title": name, "Plot": name}, module=module, urlParamsData={'catName': 'כאן פודקאסטים'})
			break
		if page + 1 == stopPage:
			if page >= pagesPerList:
				name = common.GetLabelColor(common.GetLocaleString(30011), color="green")
				common.addDir(name, str(prevPage), 31, iconimage, infos={"Title": name, "Plot": name}, module=module, urlParamsData={'catName': 'כאן פודקאסטים'})
			name = common.GetLabelColor(common.GetLocaleString(30012), color="green")
			common.addDir(name, str(page), 31, iconimage, infos={"Title": name, "Plot": name}, module=module, urlParamsData={'catName': 'כאן פודקאסטים'})
			break

def GetKidsPodcastsList():
	text = common.OpenURL('https://kankids.azurewebsites.net/page.aspx?landingPageId=1275')
	matches = re.compile('class="video_it_full.*?url\(\'(.*?)\'\).+?href=\'.+?\?progId=(.+?)\'.*?sm_il_videotitle">(.*?)<.*?sm_it_videotxt">(.*?)<', re.S|re.I).findall(text)
	for image, id, name, description in matches:
		name = common.GetLabelColor(name.strip(), keyColor="prColor", bold=True)
		common.addDir(name, id, 32, image, infos={"Title": name, "Plot": description.replace('&nbsp;', '').strip()}, module=module, urlParamsData={'catName': 'כאן פודקאסטים'})

def GetPodcastEpisodesList(data, iconimage):
	d = data.split(';')
	progId = d[0]
	page = -1 if len(d) < 2 else int(d[1])
	stopPage = page + 1 + pagesPerList
	prevPage = page - pagesPerList if page  >= pagesPerList else -1
	while True:
		page += 1
		url = '{0}/Podcast/getMorePodcasts.aspx?index={1}&leftToRight=0&progId={2}'.format(baseUrl, page, progId)
		text = common.OpenURL(url)
		matches = re.compile('<iframe src="(.+?)embed.+?<h2.+?>(.+?)</h2>.+?<p.+?>(.*?)</p>', re.S).findall(text)
		for link, name, description in matches:
			name = common.GetLabelColor(name.strip(), keyColor="chColor")
			common.addDir(name, link, 3, iconimage, infos={"Title": name, "Plot": description.replace('&nbsp;', '').strip()}, module=module, isFolder=False, isPlayable=True, urlParamsData={'catName': 'כאן פודקאסטים'})
		if len(matches) < 10:
			if page >= pagesPerList:
				name = common.GetLabelColor(common.GetLocaleString(30011), color="green")
				common.addDir(name, '{0};{1}'.format(progId, prevPage), 32, iconimage, infos={"Title": name, "Plot": name}, module=module, urlParamsData={'catName': 'כאן פודקאסטים'})
			break
		if page + 1 == stopPage:
			if page >= pagesPerList:
				name = common.GetLabelColor(common.GetLocaleString(30011), color="green")
				common.addDir(name, '{0};{1}'.format(progId, prevPage), 32, iconimage, infos={"Title": name, "Plot": name}, module=module, urlParamsData={'catName': 'כאן פודקאסטים'})
			name = common.GetLabelColor(common.GetLocaleString(30012), color="green")
			common.addDir(name, '{0};{1}'.format(progId, page), 32, iconimage, infos={"Title": name, "Plot": name}, module=module, urlParamsData={'catName': 'כאן פודקאסטים'})
			break


def Run(name, url, mode, iconimage='', moreData=''):
	if mode == 0:	#------------- Categories: ----------------------
		GetCategoriesList(iconimage)
	elif mode == 5:	#------------- Series: --------------------------
		GetSubCategoriesList(url, moreData)
	elif mode == 6:	#------------- Sub-Categories: ------------------
		GetSubCategorySeriesList(url)
	elif mode == 1:	#------------- Sub-Categories: ------------------
		GetSeriesList(url, moreData)
	elif mode == 2:	#------------- Episodes: ------------------------
		GetEpisodesList(url, iconimage, moreData)
	elif mode == 3:	#------------- Playing episode  -----------------
		Play(url, name, iconimage, moreData)
	elif mode == 4:	#------------- Toggle Lists' sorting method -----
		common.ToggleSortMethod('kanSortBy', sortBy)
	elif mode == 21: #------------- Radio Categories: ---------------
		GetRadioCategoriesList(iconimage)
	elif mode == 22: #------------- Radio Series: -------------------
		GetRadioSeriesList(url, common.GetUnColor(name))
	elif mode == 23: #------------- Radio Episodes: -----------------
		GetRadioEpisodesList(url, iconimage, moreData)
	elif mode == 31: #------------- Podcast Series: -----------------
		GetPodcastsList(url, iconimage)
	elif mode == 33: #------------- Kids Podcast Series: ------------
		GetKidsPodcastsList()
	elif mode == 32: #------------- Podcast Episodes: ---------------
		GetPodcastEpisodesList(url, iconimage)
	elif mode == 10:
		WatchLive(url, name, iconimage, moreData, type='video')
	elif mode == 11:
		WatchLive(url, name, iconimage, moreData, type='radio')
	elif mode == 12:
		PlayRadioProgram(url, name, iconimage, moreData)
		
	if mode != 0:
		common.SetViewMode('episodes')
	if sortBy == 1 and mode == 1:
		xbmcplugin.addSortMethod(handle, 1)