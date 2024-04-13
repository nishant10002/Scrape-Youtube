from googleapiclient.discovery import build
import pandas as pd
import seaborn as sb
import matplotlib.pyplot as plt

api_key='AIzaSyBti8qUDQoqpRxL1N9bKyAr884_RzU9H2w'
channel_ids=['UCBJycsmduvYEL83R_U4JriQ','UCHnyfMqiRRG1u-2MsSQLbXA','UCNIuvl7V8zACPpTmmNIqP2A','UCY1kMZp36IQSyNx_9h4mpCg','UCtHaxi4GTYDpJgMSGy7AeSw']
youtube=build('youtube','v3',developerKey=api_key)

def get_channel_stats(youtube,channel_ids):
    all_data=[]
    request=youtube.channels().list(
        part='snippet,contentDetails,statistics',
        id=','.join(channel_ids))
    response=request.execute()
    for i in range(len(response['items'])):
            data=dict(channel_name=response['items'][i]['snippet']['title'],
              	  subs=response['items'][i]['statistics']['subscriberCount'],
              	  views=response['items'][i]['statistics']['viewCount'],
                  videos=response['items'][i]['statistics']['videoCount'],
                  playlist_id=response['items'][i]['contentDetails']['relatedPlaylists']['uploads'])
            all_data.append(data)
    return all_data

channel_stats=get_channel_stats(youtube,channel_ids)
channel_data=pd.DataFrame(channel_stats)
channel_data['subs']=pd.to_numeric(channel_data['subs'])
channel_data['views']=pd.to_numeric(channel_data['views'])
channel_data['videos']=pd.to_numeric(channel_data['videos'])
sb.set(rc={'figure.figsize':(10,8)})

def show_subs_graph():
      ax=sb.barplot(x='channel_name',y='subs',data=channel_data, color='red')
      plt.title('Youtubers Subs Comparison'); 
      plt.show() 
      
def show_views_graph():
      ax=sb.barplot(x='channel_name',y='views',data=channel_data, color='green')
      plt.title('Youtubers Views Comparison')
      plt.show() 
      
def show_videos_graph():
      ax=sb.barplot(x='channel_name',y='videos',data=channel_data, color='blue')
      plt.title('Youtubers Videos Comparison')
      plt.show() 

playlist_id=channel_data.loc[channel_data['channel_name']=='Veritasium','playlist_id'].iloc[0]

def get_videoID(youtube,playlist_id):
    request=youtube.playlistItems().list(
            part='contentDetails',
            playlistId=playlist_id,
            maxResults=50)
    response=request.execute()
    video_ids=[]
    for i in range(len(response['items'])):
        video_ids.append(response['items'][i]['contentDetails']['videoId'])       
    next_page=response.get('nextPageToken')
    more_pages=True
    while more_pages:
        if next_page is None:
            more_pages=False
        else:
            request=youtube.playlistItems().list(
                 part='contentDetails',
                 playlistId=playlist_id,
                 maxResults=50,
                 pageToken=next_page
			)
            response=request.execute()
            for i in range(len(response['items'])):
                 video_ids.append(response['items'][i]['contentDetails']['videoId'])
            next_page=response.get('nextPageToken')
    return video_ids

video_ids=get_videoID(youtube,playlist_id)

def get_video_details(youtube, video_ids):
     all_video_stats=[]
     for i in range(0, len(video_ids),50):
          request=youtube.videos().list(
               part='snippet,statistics',
               id=','.join(video_ids[i:i+50])
		  )
          response=request.execute()
          for video in response['items']:
               video_stats=dict(Title=video['snippet']['title'],
                                Published_date=video['snippet']['publishedAt'],
                                Views=video['statistics']['viewCount'],
                                Likes=video['statistics']['likeCount'],
                                Comments=video['statistics']['commentCount'])
               all_video_stats.append(video_stats)
     return all_video_stats

video_details=get_video_details(youtube,video_ids)
video_data=pd.DataFrame(video_details)
video_data['Published_date']=pd.to_datetime(video_data['Published_date']).dt.date
video_data['Views']=pd.to_numeric(video_data['Views'])
video_data['Likes']=pd.to_numeric(video_data['Likes'])

def show_top_10_videos():
     top_10=video_data.sort_values(by='Views',ascending=False).head(10)
     ax2=sb.barplot(x='Views',y='Title',data=top_10,color='orange')
     plt.title('Best Performing Videos of Veritasium')
     plt.show() 
     
def videos_per_month():
     video_data['Month']=pd.to_datetime(video_data['Published_date']).dt.strftime('%b')
     videos_per_month=video_data.groupby('Month', as_index=False).size()
     sort_order=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
     videos_per_month.index=pd.CategoricalIndex(videos_per_month['Month'],categories=sort_order,ordered=True)
     videos_per_month=videos_per_month.sort_index()
     ax2=sb.barplot(x='Month',y='size',data=videos_per_month,color='purple')
     plt.title('Average Videos released by Veritasium per Month')
     plt.show() 
     
def move_to_csv():
     video_data.to_csv('Video_Details(Veritasium).csv')

