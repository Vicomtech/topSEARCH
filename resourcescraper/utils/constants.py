# -*- coding: utf-8 -*-
"""
    topSEARCH
    
    @author: tgarcianavarro - Vicomtech Foundation, Basque Research and Technology Alliance (BRTA)
    @author: afernandezc - Vicomtech Foundation, Basque Research and Technology Alliance (BRTA)
    @date: 03/02/2023
    @version: 0.2
"""

# Stdlib imports


# Third-party app imports


# Imports from your apps


ALLOWED_APP_FILTERS = {
    'keyword_search': bool,
    'score': float,
    'privacy_policy': bool,
    'free': bool,
    'recent_update': int,
    'developer_has_website': bool,
    'language': str,
}

ALLOWED_VIDEO_FILTERS = {
    'keywords': bool,
    'language': str,
    'licensed': bool,
    'duration': int,
    'views': int,
    'likes': int,
    'subscribers': int,
    'recent_update': int,
}

ALLOWED_PODCAST_FILTERS = {
    'free': bool,
    'recent_update': int,
    'language': str,
    'keywords_search': bool,
}

ALLOWED_NEWS_FILTERS = {
    'keywords_search': bool
}

ALLOWED_APP_METADATA = [
    'appId',
    'title',
    'description',
    'url',
    'genres',
    'developerWebsite',
    'score',
    'ratings',
    'currentVersionReleaseDate',
    'languageCodesISO2A',
    'os',
    'privacyPolicy',
    'free',
    'contentRating',
]

ALLOWED_VIDEO_METADATA = [
    'publishedAt',
    'channelId',
    'title',
    'description',
    'channelTitle',
    'licensedContent',
    'duration',
    'viewCount',
    'video_id',
    'video_URL',
    'likeCount',
    'likes_rate',
    'commentCount',
    'subscriberCount',
    'description_complete',
    'tags',
    'captions',
]

ALLOWED_PODCAST_METADATA = [
    'id',
    'title',
    'releaseDate',
    'description',
    'trackTimeMillis',
    'trackViewUrl',
    'languages',
    'free',
    'provider'
]

ALLOWED_NEWS_METADATA = [
    'publishedAt',
    'description',
    'title',
    'URL',
    'language',
    'mediaTitle',
    'authors',
    'summary',
    'content',
    'textLength',
    'keywords'
]

LANGS = ['en', 'es', 'it', 'cs', 'sl']
COUNTRIES = ['us', 'es']
