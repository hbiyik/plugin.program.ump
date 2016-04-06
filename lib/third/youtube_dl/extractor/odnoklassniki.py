# coding: utf-8
from __future__ import unicode_literals

from ..compat import compat_urllib_parse_unquote
from ..utils import (
    ExtractorError,
    unified_strdate,
    int_or_none,
    qualities,
    unescapeHTML,
)
from .common import InfoExtractor


class OdnoklassnikiIE(InfoExtractor):
    _VALID_URL = r'https?://(?:(?:www|m|mobile)\.)?(?:odnoklassniki|ok)\.ru/(?:video(?:embed)?|web-api/video/moviePlayer)/(?P<id>[\d-]+)'
    _TESTS = [{
        # metadata in JSON
        'url': 'http://ok.ru/video/20079905452',
        'md5': '6ba728d85d60aa2e6dd37c9e70fdc6bc',
        'info_dict': {
            'id': '20079905452',
            'ext': 'mp4',
            'title': 'Культура мен�?ет на�? (прекра�?ный ролик!))',
            'duration': 100,
            'upload_date': '20141207',
            'uploader_id': '330537914540',
            'uploader': 'Виталий Доброволь�?кий',
            'like_count': int,
            'age_limit': 0,
        },
        'skip': 'Video has been blocked',
    }, {
        # metadataUrl
        'url': 'http://ok.ru/video/63567059965189-0',
        'md5': '9676cf86eff5391d35dea675d224e131',
        'info_dict': {
            'id': '63567059965189-0',
            'ext': 'mp4',
            'title': 'Девушка без комплек�?ов ...',
            'duration': 191,
            'upload_date': '20150518',
            'uploader_id': '534380003155',
            'uploader': '☭ �?ндрей Мещанинов ☭',
            'like_count': int,
            'age_limit': 0,
        },
    }, {
        # YouTube embed (metadataUrl, provider == USER_YOUTUBE)
        'url': 'http://ok.ru/video/64211978996595-1',
        'md5': '5d7475d428845cd2e13bae6f1a992278',
        'info_dict': {
            'id': '64211978996595-1',
            'ext': 'mp4',
            'title': 'Ко�?миче�?ка�? �?реда от 26 авгу�?та 2015',
            'description': 'md5:848eb8b85e5e3471a3a803dae1343ed0',
            'duration': 440,
            'upload_date': '20150826',
            'uploader_id': '750099571',
            'uploader': '�?лина П',
            'age_limit': 0,
        },
    }, {
        'url': 'http://ok.ru/web-api/video/moviePlayer/20079905452',
        'only_matching': True,
    }, {
        'url': 'http://www.ok.ru/video/20648036891',
        'only_matching': True,
    }, {
        'url': 'http://www.ok.ru/videoembed/20648036891',
        'only_matching': True,
    }, {
        'url': 'http://m.ok.ru/video/20079905452',
        'only_matching': True,
    }, {
        'url': 'http://mobile.ok.ru/video/20079905452',
        'only_matching': True,
    }]

    def _real_extract(self, url):
        video_id = self._match_id(url)

        webpage = self._download_webpage(
            'http://ok.ru/video/%s' % video_id, video_id)

        error = self._search_regex(
            r'[^>]+class="vp_video_stub_txt"[^>]*>([^<]+)<',
            webpage, 'error', default=None)
        if error:
            raise ExtractorError(error, expected=True)

        player = self._parse_json(
            unescapeHTML(self._search_regex(
                r'data-options=(?P<quote>["\'])(?P<player>{.+?%s.+?})(?P=quote)' % video_id,
                webpage, 'player', group='player')),
            video_id)

        flashvars = player['flashvars']

        metadata = flashvars.get('metadata')
        if metadata:
            metadata = self._parse_json(metadata, video_id)
        else:
            metadata = self._download_json(
                compat_urllib_parse_unquote(flashvars['metadataUrl']),
                video_id, 'Downloading metadata JSON')

        movie = metadata['movie']
        title = movie['title']
        thumbnail = movie.get('poster')
        duration = int_or_none(movie.get('duration'))

        author = metadata.get('author', {})
        uploader_id = author.get('id')
        uploader = author.get('name')

        upload_date = unified_strdate(self._html_search_meta(
            'ya:ovs:upload_date', webpage, 'upload date', default=None))

        age_limit = None
        adult = self._html_search_meta(
            'ya:ovs:adult', webpage, 'age limit', default=None)
        if adult:
            age_limit = 18 if adult == 'true' else 0

        like_count = int_or_none(metadata.get('likeCount'))

        info = {
            'id': video_id,
            'title': title,
            'thumbnail': thumbnail,
            'duration': duration,
            'upload_date': upload_date,
            'uploader': uploader,
            'uploader_id': uploader_id,
            'like_count': like_count,
            'age_limit': age_limit,
        }

        if metadata.get('provider') == 'USER_YOUTUBE':
            info.update({
                '_type': 'url_transparent',
                'url': movie['contentId'],
            })
            return info

        quality = qualities(('mobile', 'lowest', 'low', 'sd', 'hd'))

        formats = [{
            'url': f['url'],
            'ext': 'mp4',
            'format_id': f['name'],
            'quality': quality(f['name']),
        } for f in metadata['videos']]
        self._sort_formats(formats)

        info['formats'] = formats
        return info
