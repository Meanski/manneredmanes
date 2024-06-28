from googleapiclient.discovery import build

YOUTUBE_API_KEY = 'AIzaSyBaffUHpfRhLOrDbqtPtvpoSlQuzr9_h1w'
CUSTOM_URL = 'TravWhiteStyle'

youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

request = youtube.search().list(
    part="snippet",
    q=CUSTOM_URL,
    type="channel"
)
response = request.execute()

if response['items']:
    channel_id = response['items'][0]['snippet']['channelId']
    print(f"Channel ID: {channel_id}")
else:
    print("Channel not found.")
