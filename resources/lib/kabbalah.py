# -*- coding: utf-8 -*-
import xbmc, xbmcaddon
import sys, re
import resources.lib.common as common

Addon = xbmcaddon.Addon(common.AddonID)
module = 'kabbalah'
userAgent = common.GetUserAgent()

def WatchLive(url, name='', iconimage='', quality='best'):
	headers = {
		'User-Agent': userAgent,
		'Connection': 'keep-alive',
		'Pragma': 'no-cache',
		'Cache-Control': 'no-cache',
		'Accept': 'application/json',
		'DNT': '1',
		'Referer': 'http://kab.tv/',
		'Accept-Encoding': 'gzip, deflate',
		'Accept-Language': 'en-US,en;q=0.9'
		}
	channels = common.OpenURL('http://kab.tv/api/streams', headers=headers, responseMethod='json')
	for channel in channels:
		if str(channel['id']) == url:
			link = channel['url'].strip()
			break
	if link == '':
		return None
	headers = {"User-Agent": userAgent}
	text = common.OpenURL(link, headers=headers)
	match = re.compile('hlsUrl":"(.*?)"').findall(text)
	link = common.GetStreams(match[0], headers=headers, quality=quality)
	final = '{0}|User-Agent={1}'.format(link, userAgent)
	common.PlayStream(final, quality, name, iconimage)

def Run(name, url, mode, iconimage='', moreData=''):
	if mode == 10:
		WatchLive(url, name, iconimage, moreData)
		
	common.SetViewMode('episodes')