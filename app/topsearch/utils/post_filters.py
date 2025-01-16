import pandas as pd


def app_filter(data):
    # Convert the currentVersionReleaseDate column to a date format
    data['time'] = pd.to_datetime(data['currentVersionReleaseDate'])

    data.fillna('', inplace=True)

    filtered_df = data.drop_duplicates(subset='appId')

    return filtered_df


def video_filter(data):
    # Convert the publishedAt column to a date format
    data['time'] = pd.to_datetime(data['publishedAt'])
    data['time'] = data['time'].dt.tz_localize(None)

    data['duration'] = data['duration'] / 60

    data.fillna('', inplace=True)

    filtered_df = data.drop_duplicates(subset='video_id')
    return filtered_df


def podcast_filter(data):
    # Convert the releaseDate column to a date format
    data['time'] = pd.to_datetime(data['releaseDate'])

    # Convert trackTimeMillis to trackTime (in seconds)
    data['trackTimeMillis'] = data['trackTimeMillis'].replace('None', 0).astype(int)
    data = data.rename(columns={'trackTimeMillis': 'trackTime'})
    data['trackTime'] = data['trackTime'] / 60000
    data['trackTime'] = data['trackTime'].round(2)

    data.fillna('', inplace=True)

    filtered_df = data.drop_duplicates(subset='id')
    return filtered_df


def news_filter(data):
    # Convert the releaseDate column to a date format
    data['time'] = pd.to_datetime(data['publishedAt'])

    # Create duration column, assuming average reading speed of 238 WPM
    # data['duration'] = data['textLength'] / 238

    data.fillna('', inplace=True)

    filtered_df = data.drop_duplicates(subset='title')
    return filtered_df
