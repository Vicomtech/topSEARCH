import errno
import os

import googleapiclient.discovery
import googleapiclient.errors
import pandas as pd
from youtube_scraping_api import YoutubeAPI
from dotenv import load_dotenv

from resourcescraper.resource_scraper.scraper import Scraper
from resourcescraper.utils.timeout import timeout

api = YoutubeAPI()
load_dotenv(".topfind.env")


class VideoScraper(Scraper):

    def __init__(self, queries:list[str], api_service_name:str, api_version:str, groups:dict=None):
        """
        Args:
            queries (list[str]): A list of search queries, where each query is a string representing the search term or phrase.
            api_service_name (str): The name of the API service being used to fetch or process data.
            api_version (str): The version of the API service being used.
            groups (dict): A dictionary of group identifiers or names, where each group is a string.

        """
        super().__init__(groups)
        self.youtube = googleapiclient.discovery.build(
            api_service_name, api_version, developerKey="AIzaSyAvkOiA76LDMmqc4u12Pau1d1oUBQaqIyU")
        self.api_service_name = api_service_name
        self.api_version = api_version
        self.i = 0
        self.queries = queries
        self.videos = pd.DataFrame(
            columns=['publishedAt', 'channelId', 'title', 'description', 'channelTitle', 'licensedContent', 'duration',
                     'viewCount', 'video_id', 'video_URL', 'likeCount',
                     'likes_rate', 'commentCount', 'subscriberCount', 'description_complete', 'tags', 'captions'])
        self.generate_youtube_client()

    def generate_youtube_client(self, change:bool=False):
        """
        Generates a YouTube client for interacting with the YouTube API.

        Args:
            change (bool, optional): A boolean to indicate if the key has been changed or not.
        """
        keys = [os.environ.get('YOUTUBE_KEY')]

        # keys = ['AIzaSyBRT0U6jnN-pHHFBDoYLJ0kNbwoHBo-Rq8']

        # print(self.i)

        # Check if the API key needs to be changed (change=True) or it's the first call (change=False)
        if change:
            self.i = (self.i + 1) % len(keys)  # Move to the next API key and reset to 0 if it reaches the last key
            if self.i == 0:
                pass

        # print(self.i)

        # Get the current API key from the keys list based on the index self.i
        current_api_key = keys[self.i]

        # print(current_api_key)

        # Initialize the YouTube Data API client with the current API key
        self.youtube = googleapiclient.discovery.build(
            self.api_service_name, self.api_version, developerKey=current_api_key)

        # print(self.youtube)

        # Print some information for debugging purposes
        print("API Key changed:", change)  # Print whether the API key was changed
        print("Current API Key index:", self.i)  # Print the current index, indicating the API key being used

    def search(self) -> list:
        """
        Call API for each search term for each channel.

        Returns:
            list: List of all videos searched.
        """
        max_results = 50
        for query in self.queries:
            next_page = None
            cont = 0
            while (next_page is not None or cont == 0) and cont < 25:
                try:
                    request = self.youtube.search().list(
                        part="snippet",
                        q=query,
                        maxResults=max_results,
                        pageToken=next_page,
                        type="video"
                    )
                    response = request.execute()
                    next_page = response.get("nextPageToken", None)
                    cont += 1
                    yield from response['items']
                except Exception as e:
                    if "quota" in str(e).lower():
                        self.generate_youtube_client(True)
                    else:
                        print(f"Error: {e}")

    @timeout(15, "Timeout exceeded")
    def parse(self, resource):
        """
        Parses the given resource to retrieve video information.

        Args:
            resource: The resource containing information needed to fetch video details.

        Returns:
            A DataFrame or structured response containing the video information retrieved from the resource.
        """
        df_response = self.get_video_info(resource)
        return df_response

    def get_video_info(self, video):
        """
        Retrieves and processes detailed video information, including metadata for both the video and its
        associated channel.

        Args:
            video: Contains the video information.

        Returns:
             A pandas DataFrame containing the cleaned and enriched metadata of the video.
        """
        video_dict = video.to_dict()
        # Clean metadata
        video_id = video['id']['videoId']
        df_response = self.clean_video_metadata(video_dict)
        # Request video metadata
        self.get_video_metadata(video_id, df_response)
        # Request channel metadata
        df_response = self.get_channel_metadata(video_dict['snippet']['channelId'], df_response)
        return df_response

    @staticmethod
    def clean_video_metadata(video):
        """
        Cleans and processes the video metadata by removing unnecessary fields.

        Args:
            video (dict): A dictionary containing video information.

        Returns:
             A pandas DataFrame with the cleaned video metadata.
        """
        video_info = video['snippet']
        df_response = pd.DataFrame(video_info)
        df_response = df_response.drop('high')
        df_response = df_response.drop('medium')
        df_response = df_response.drop(columns=['thumbnails', 'publishTime', 'liveBroadcastContent'])
        return df_response

    def get_video_metadata(self, video_id:str, df_response):
        """
        Retrieves detailed metadata for a specific video using its video ID and appends this data to the existing
        DataFrame.

        Args:
            video_id (str): The unique identifier of the video for which metadata is being requested.
            df_response: A pandas DataFrame containing the current video information.

        Returns:
            Updated DataFrame.

        """
        # Query
        request = self.youtube.videos().list(
            part="contentDetails,statistics",
            id=video_id
        )
        response = request.execute()
        # Get specific values
        item = response['items'][0]
        df_response['licensedContent'] = item['contentDetails']['licensedContent']
        duration_dt = pd.Timedelta(item['contentDetails']['duration']).total_seconds()
        df_response['duration'] = duration_dt
        df_response['viewCount'] = item['statistics']['viewCount']
        df_response['video_id'] = video_id
        df_response['video_URL'] = f'https://www.youtube.com/watch?v={video_id}'
        for x in ["likeCount", "commentCount"]:
            try:
                df_response[x] = item['statistics'][x]
            except KeyError:
                df_response[x] = None
        # Compute rate
        # if df_response['likeCount'][0] is not None and df_response['viewCount'][0] is not None and \
        #         df_response['viewCount'][0] != 0:
        #     df_response['likes_rate'] = int(df_response['likeCount']) / int(df_response['viewCount'])
        # else:
        #     df_response['likes_rate'] = 0

        return df_response

    def get_channel_metadata(self, channel_id:str, df_response):
        """
        Retrieves detailed metadata for a specific YouTube channel using its channel ID and appends this data to the
        existing DataFrame.

        Args:
            channel_id (str): The unique identifier of the channel for which metadata is being requested.
            df_response: A pandas DataFrame containing the current video information.

        Returns:
            Updated DataFrame.

        """
        request = self.youtube.channels().list(
            part="statistics",
            id=channel_id
        )
        response = request.execute()
        df_response['subscriberCount'] = response['items'][0]['statistics']['subscriberCount']
        query = df_response['description'].values[0]
        try:
            result_id = api.search(query)[0].id
            df_response = self.get_metadata_on_error(result_id, df_response)
        except:
            pass
        return df_response

    @timeout(3, error_message=os.strerror(errno.ETIME))
    def get_metadata_on_error(self, result_id:str, df):
        """
        Retrieves metadata for a specific result when an error occurs during processing.

        Args:
            result_id (str): The unique identifier of the result for which metadata is being requested in case of an error.
            df: A pandas DataFrame where error-related metadata will be appended.

        Returns:
            The updated pandas DataFrame with additional metadata appended based on the provided result ID.

        """
        if result_id is not None:
            video = api.video(result_id)
            # df['description_complete'] = video.description
            if video.tags is not None:
                df['tags'] = ';'.join(video.tags)
            if video.captions:
                df['captions'] = video.captions.get_caption().xml
        return df

    @staticmethod
    def order(df_total):
        """
        Orders data by "relevance" using the likes_rate variable.

        Args:
            df_total: Dataframe containing all videos with metadata.

        Returns:
            Dataframe containing all videos with metadata but ordered by relevance.
        """
        df_total = df_total.sort_values('likes_rate', ascending=False)
        return df_total

    def __call__(self):
        self.videos = self.parse_resources()
        self.videos["licensedContent"] = self.videos["licensedContent"].astype(bool)
        # df_videos = self.order(self.videos)
        df = self.find_keywords(self.videos)
        print("Total videos: " + str(df.shape[0]))
        df = df.drop_duplicates(subset=['video_id'], keep='first')
        return df
