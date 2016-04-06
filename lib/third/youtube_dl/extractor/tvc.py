# coding: utf-8
from __future__ import unicode_literals

import re

from ..utils import (
    clean_html,
    int_or_none,
)
from .common import InfoExtractor


class TVCIE(InfoExtractor):
    _VALID_URL = r'https?://(?:www\.)?tvc\.ru/video/iframe/id/(?P<id>\d+)'
    _TEST = {
        'url': 'http://www.tvc.ru/video/iframe/id/74622/isPlay/false/id_stat/channel/?acc_video_id=/channel/brand/id/17/show/episodes/episode_id/39702',
        'md5': 'bbc5ff531d1e90e856f60fc4b3afd708',
        'info_dict': {
            'id': '74622',
            'ext': 'mp4',
            'title': 'Событи�?. "Событи�?". Эфир от 22.05.2015 14:30',
            'thumbnail': 're:^https?://.*\.jpg$',
            'duration': 1122,
        },
    }

    @classmethod
    def _extract_url(cls, webpage):
        mobj = re.search(
            r'<iframe[^>]+?src=(["\'])(?P<url>(?:http:)?//(?:www\.)?tvc\.ru/video/iframe/id/[^"]+)\1', webpage)
        if mobj:
            return mobj.group('url')

    def _real_extract(self, url):
        video_id = self._match_id(url)

        video = self._download_json(
            'http://www.tvc.ru/video/json/id/%s' % video_id, video_id)

        formats = []
        for info in video.get('path', {}).get('quality', []):
            video_url = info.get('url')
            if not video_url:
                continue
            format_id = self._search_regex(
                r'cdnvideo/([^/]+?)(?:-[^/]+?)?/', video_url,
                'format id', default=None)
            formats.append({
                'url': video_url,
                'format_id': format_id,
                'width': int_or_none(info.get('width')),
                'height': int_or_none(info.get('height')),
                'tbr': int_or_none(info.get('bitrate')),
            })
        self._sort_formats(formats)

        return {
            'id': video_id,
            'title': video['title'],
            'thumbnail': video.get('picture'),
            'duration': int_or_none(video.get('duration')),
            'formats': formats,
        }


class TVCArticleIE(InfoExtractor):
    _VALID_URL = r'https?://(?:www\.)?tvc\.ru/(?!video/iframe/id/)(?P<id>[^?#]+)'
    _TESTS = [{
        'url': 'http://www.tvc.ru/channel/brand/id/29/show/episodes/episode_id/39702/',
        'info_dict': {
            'id': '74622',
            'ext': 'mp4',
            'title': 'Событи�?. "Событи�?". Эфир от 22.05.2015 14:30',
            'description': 'md5:ad7aa7db22903f983e687b8a3e98c6dd',
            'thumbnail': 're:^https?://.*\.jpg$',
            'duration': 1122,
        },
    }, {
        'url': 'http://www.tvc.ru/news/show/id/69944',
        'info_dict': {
            'id': '75399',
            'ext': 'mp4',
            'title': 'Эк�?перты: в �?толице в�?тал вопро�? о мак�?имально безопа�?ных о�?тановках',
            'description': 'md5:f2098f71e21f309e89f69b525fd9846e',
            'thumbnail': 're:^https?://.*\.jpg$',
            'duration': 278,
        },
    }, {
        'url': 'http://www.tvc.ru/channel/brand/id/47/show/episodes#',
        'info_dict': {
            'id': '2185',
            'ext': 'mp4',
            'title': 'Ещё не поздно. Эфир от 03.08.2013',
            'description': 'md5:51fae9f3f8cfe67abce014e428e5b027',
            'thumbnail': 're:^https?://.*\.jpg$',
            'duration': 3316,
        },
    }]

    def _real_extract(self, url):
        webpage = self._download_webpage(url, self._match_id(url))
        return {
            '_type': 'url_transparent',
            'ie_key': 'TVC',
            'url': self._og_search_video_url(webpage),
            'title': clean_html(self._og_search_title(webpage)),
            'description': clean_html(self._og_search_description(webpage)),
            'thumbnail': self._og_search_thumbnail(webpage),
        }
