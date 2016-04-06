from __future__ import unicode_literals

import re

from ..utils import (
    int_or_none,
    parse_duration,
    qualities,
    unified_strdate,
)
from .common import InfoExtractor


class CCCIE(InfoExtractor):
    IE_NAME = 'media.ccc.de'
    _VALID_URL = r'https?://(?:www\.)?media\.ccc\.de/v/(?P<id>[^/?#&]+)'

    _TESTS = [{
        'url': 'https://media.ccc.de/v/30C3_-_5443_-_en_-_saal_g_-_201312281830_-_introduction_to_processor_design_-_byterazor#video',
        'md5': '3a1eda8f3a29515d27f5adb967d7e740',
        'info_dict': {
            'id': '30C3_-_5443_-_en_-_saal_g_-_201312281830_-_introduction_to_processor_design_-_byterazor',
            'ext': 'mp4',
            'title': 'Introduction to Processor Design',
            'description': 'md5:80be298773966f66d56cb11260b879af',
            'thumbnail': 're:^https?://.*\.jpg$',
            'view_count': int,
            'upload_date': '20131228',
            'duration': 3660,
        }
    }, {
        'url': 'https://media.ccc.de/v/32c3-7368-shopshifting#download',
        'only_matching': True,
    }]

    def _real_extract(self, url):
        video_id = self._match_id(url)
        webpage = self._download_webpage(url, video_id)

        if self._downloader.params.get('prefer_free_formats'):
            preference = qualities(['mp3', 'opus', 'mp4-lq', 'webm-lq', 'h264-sd', 'mp4-sd', 'webm-sd', 'mp4', 'webm', 'mp4-hd', 'h264-hd', 'webm-hd'])
        else:
            preference = qualities(['opus', 'mp3', 'webm-lq', 'mp4-lq', 'webm-sd', 'h264-sd', 'mp4-sd', 'webm', 'mp4', 'webm-hd', 'mp4-hd', 'h264-hd'])

        title = self._html_search_regex(
            r'(?s)<h1>(.*?)</h1>', webpage, 'title')
        description = self._html_search_regex(
            r'(?s)<h3>About</h3>(.+?)<h3>',
            webpage, 'description', fatal=False)
        upload_date = unified_strdate(self._html_search_regex(
            r"(?s)<span[^>]+class='[^']*fa-calendar-o'[^>]*>(.+?)</span>",
            webpage, 'upload date', fatal=False))
        view_count = int_or_none(self._html_search_regex(
            r"(?s)<span class='[^']*fa-eye'></span>(.*?)</li>",
            webpage, 'view count', fatal=False))
        duration = parse_duration(self._html_search_regex(
            r'(?s)<span[^>]+class=(["\']).*?fa-clock-o.*?\1[^>]*></span>(?P<duration>.+?)</li',
            webpage, 'duration', fatal=False, group='duration'))

        matches = re.finditer(r'''(?xs)
            <(?:span|div)\s+class='label\s+filetype'>(?P<format>[^<]*)</(?:span|div)>\s*
            <(?:span|div)\s+class='label\s+filetype'>(?P<lang>[^<]*)</(?:span|div)>\s*
            <a\s+download\s+href='(?P<http_url>[^']+)'>\s*
            (?:
                .*?
                <a\s+(?:download\s+)?href='(?P<torrent_url>[^']+\.torrent)'
            )?''', webpage)
        formats = []
        for m in matches:
            format = m.group('format')
            format_id = self._search_regex(
                r'.*/([a-z0-9_-]+)/[^/]*$',
                m.group('http_url'), 'format id', default=None)
            if format_id:
                format_id = m.group('lang') + '-' + format_id
            vcodec = 'h264' if 'h264' in format_id else (
                'none' if format_id in ('mp3', 'opus') else None
            )
            formats.append({
                'format_id': format_id,
                'format': format,
                'language': m.group('lang'),
                'url': m.group('http_url'),
                'vcodec': vcodec,
                'preference': preference(format_id),
            })

            if m.group('torrent_url'):
                formats.append({
                    'format_id': 'torrent-%s' % (format if format_id is None else format_id),
                    'format': '%s (torrent)' % format,
                    'proto': 'torrent',
                    'format_note': '(unsupported; will just download the .torrent file)',
                    'vcodec': vcodec,
                    'preference': -100 + preference(format_id),
                    'url': m.group('torrent_url'),
                })
        self._sort_formats(formats)

        thumbnail = self._html_search_regex(
            r"<video.*?poster='([^']+)'", webpage, 'thumbnail', fatal=False)

        return {
            'id': video_id,
            'title': title,
            'description': description,
            'thumbnail': thumbnail,
            'view_count': view_count,
            'upload_date': upload_date,
            'duration': duration,
            'formats': formats,
        }
