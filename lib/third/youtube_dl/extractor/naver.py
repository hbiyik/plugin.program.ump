# encoding: utf-8
from __future__ import unicode_literals

import re

from ..compat import (
    compat_urllib_parse_urlencode,
    compat_urlparse,
)
from ..utils import (
    ExtractorError,
)
from .common import InfoExtractor


class NaverIE(InfoExtractor):
    _VALID_URL = r'https?://(?:m\.)?tvcast\.naver\.com/v/(?P<id>\d+)'

    _TESTS = [{
        'url': 'http://tvcast.naver.com/v/81652',
        'info_dict': {
            'id': '81652',
            'ext': 'mp4',
            'title': '[9μ λͺ¨μ?κ³ μ¬ ν΄μ€κ°μ?][μν_κΉμ?ν?¬] μν Aν 16~20λ²',
            'description': 'ν©κ²©λΆλ³μ? λ²μΉ λ©κ°μ€ν°λ | λ©κ°μ€ν°λ μν κΉμ?ν?¬ μ μ?λμ?΄ 9μ λͺ¨μ?κ³ μ¬ μνAν 16λ²μ?μ 20λ²κΉμ§ ν΄μ€κ°μ?λ₯Ό κ³΅κ°ν©λλ€.',
            'upload_date': '20130903',
        },
    }, {
        'url': 'http://tvcast.naver.com/v/395837',
        'md5': '638ed4c12012c458fefcddfd01f173cd',
        'info_dict': {
            'id': '395837',
            'ext': 'mp4',
            'title': '9λμ?΄ μ§λλ? μν κΈ°μ΅, μ ν¨μ±μ? μλ²μ§',
            'description': 'md5:5bf200dcbf4b66eb1b350d1eb9c753f7',
            'upload_date': '20150519',
        },
        'skip': 'Georestricted',
    }]

    def _real_extract(self, url):
        video_id = self._match_id(url)
        webpage = self._download_webpage(url, video_id)

        m_id = re.search(r'var rmcPlayer = new nhn.rmcnmv.RMCVideoPlayer\("(.+?)", "(.+?)"',
                         webpage)
        if m_id is None:
            error = self._html_search_regex(
                r'(?s)<div class="(?:nation_error|nation_box|error_box)">\s*(?:<!--.*?-->)?\s*<p class="[^"]+">(?P<msg>.+?)</p>\s*</div>',
                webpage, 'error', default=None)
            if error:
                raise ExtractorError(error, expected=True)
            raise ExtractorError('couldn\'t extract vid and key')
        vid = m_id.group(1)
        key = m_id.group(2)
        query = compat_urllib_parse_urlencode({'vid': vid, 'inKey': key, })
        query_urls = compat_urllib_parse_urlencode({
            'masterVid': vid,
            'protocol': 'p2p',
            'inKey': key,
        })
        info = self._download_xml(
            'http://serviceapi.rmcnmv.naver.com/flash/videoInfo.nhn?' + query,
            video_id, 'Downloading video info')
        urls = self._download_xml(
            'http://serviceapi.rmcnmv.naver.com/flash/playableEncodingOption.nhn?' + query_urls,
            video_id, 'Downloading video formats info')

        formats = []
        for format_el in urls.findall('EncodingOptions/EncodingOption'):
            domain = format_el.find('Domain').text
            uri = format_el.find('uri').text
            f = {
                'url': compat_urlparse.urljoin(domain, uri),
                'ext': 'mp4',
                'width': int(format_el.find('width').text),
                'height': int(format_el.find('height').text),
            }
            if domain.startswith('rtmp'):
                # urlparse does not support custom schemes
                # https://bugs.python.org/issue18828
                f.update({
                    'url': domain + uri,
                    'ext': 'flv',
                    'rtmp_protocol': '1',  # rtmpt
                })
            formats.append(f)
        self._sort_formats(formats)

        return {
            'id': video_id,
            'title': info.find('Subject').text,
            'formats': formats,
            'description': self._og_search_description(webpage),
            'thumbnail': self._og_search_thumbnail(webpage),
            'upload_date': info.find('WriteDate').text.replace('.', ''),
            'view_count': int(info.find('PlayCount').text),
        }
