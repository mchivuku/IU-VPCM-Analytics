import requests
from InstagramAPI import InstagramAPI
from tqdm import tqdm
import pandas as pd
import os
import re
import numpy as np
import datetime
import urllib.parse
import json

from collections import  Counter

import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

import urllib3
urllib3.disable_warnings()

class InstaAPI:
    def __init__(self,settings):
        self.settings = settings
        
        username, password = self.get_credentials_username_passwd(settings.auth_file)
        self.api = InstagramAPI(username,password)
        
        response = self.api.login()
        self.user_id, self.name = self.settings.user_id, self.settings.username

        ## Make directory for raw_data
        if not os.path.exists(self.settings.raw_data_dir):
            os.makedirs(self.settings.raw_data_dir)

        if not os.path.exists(self.settings.processed_data_dir):
            os.makedirs(self.settings.processed_data_dir)


    def get_credentials_username_passwd(self, filename):
        with open(filename,'r') as f:
            lines = f.readlines()
            username=lines[0]
            password = lines[1]

        f.close()
        return username, password

    def get_user_info(self):
        """
        get user info
        """
        api = self.api
        api.getSelfUsernameInfo()
        result = api.LastJson
        user_id = result['user']['pk'] # my own personal user id
        me = result['user']['full_name'] # my own personal username
        follower_cnt = result["user"]["follower_count"]
        following_cnt = result["user"]["following_count"]
        media_cnt = result["user"]["media_count"]
        usertags_count = result["user"]["usertags_count"]
        username = self.settings.username
        data = {"follower_count":follower_cnt, 
        "following_count":following_cnt, 
        "media_count":media_cnt,
         "usertags_count":usertags_count, "userid":user_id, "full_name":me, "username":username }
        print(data)
        df = pd.DataFrame(data,index=[0])

        return df

    def get_users_follower_relationship(self):
        #first let's figure out who I am
        api = self.api
        
        user_id = self.user_id
        me = self.settings.full_name

        ## Get following
        api.getSelfUsersFollowing()
        result = api.LastJson
        follow_relationships = []
        for user in tqdm(result['users']):
            followed_user_id = user['pk'] 
            followed_user_name = user['full_name']
            follow_relationships.append((user_id, followed_user_id, me, followed_user_name))
            api.getUserFollowings(followed_user_id)
            result2 = api.LastJson
            if result2.get('users') is not None:
                for user2 in result2['users']:      
                    follow_relationships.append((followed_user_id, user2['pk'],
                                                followed_user_name, user2['full_name']))

        df = pd.DataFrame(follow_relationships,
            columns=['src_id','dst_id', 'src_name', 'dst_name'])

        return df
       
    ### Top hashtags and the images associated with the hashtags
    def get_tophashtags(self,all_posts_df):

        find_hashtags = lambda text: re.findall(r'#(\w+)',text)
        find_mentions = lambda text: re.findall(r'@(\w+)',text)

        api = self.api
        hashtags = []
        usermention = []

        
        # photos that i have liked
        # photos i have liked recently
        for idx, r in tqdm(all_posts_df.iterrows()):
            
            if r['captions'] is not None:
                hashtag = find_hashtags(r['captions'])
                mention = find_mentions(r['captions'])
                        
                [hashtags.append(i.lower()) for i in (hashtag)]
                [usermention.append(i.lower()) for i in (mention)]
                print("")

        """self.api.getSelfUserTags()
        result = api.LastJson
        # photos on which i was tagged
        for r in tqdm(result['items']):
            if r['caption'] is not None:
                hashtag = find_hashtags(r['caption']['text'])
                mention = find_mentions(r['caption']['text'])
                
                [hashtags.append(i.lower()) for i in (hashtag)]
                [usermention.append(i.lower()) for i in (mention)]
        """
        top_hashtags_df = pd.Series(hashtags).value_counts().to_frame()
        top_hashtags_df = top_hashtags_df[:50]
        

        hashtag_dic = {}
        for tag in top_hashtags_df.index:    
            api.getUserFeed(tag)
            result = api.LastJson
            print(tag,len(result["items"]))
            hashtag_dic[tag] = result

        urls = []
        numlikes = []
        tags = []

        for tag in hashtag_dic.keys():
            items = hashtag_dic[tag]['items']
            print(tag, " : ",len(items))
            for i in items:
                ## only images and not videoes
                if 'image_versions2' in i:
                    urls.append(i['image_versions2']['candidates'][1]['url'])
                    numlikes.append(i['like_count'])
                    tags.append(tag)
    
        df_tags = pd.DataFrame(
            {'urls': urls,
            'likes': numlikes,
            'tag': tags
            })

        return (top_hashtags_df,(df_tags))


    """
    Get all user posts over last year
    """
    def get_all_user_posts(self):
        api = self.api
        
        video_cnt = 0
        photo_cnt = 0
        other_cnt = 0
        find_hashtags = lambda text: re.findall(r'#(\w+)',text)
        find_mentions = lambda text: re.findall(r'@(\w+)',text)
        

        #grab all my likes from the past year
        last_year = datetime.datetime.now() - datetime.timedelta(days=400)
        now = datetime.datetime.now()
        last_result_time = now
        
        post_id  = []
        max_id = 0
        urls = []
        takenat = []
        numlikes = []
        numcomments = []
        media_type = []
        numhashtags = []
        nummentions = []
        captions = []

        hashtags = []
        mentions = []
        caption_tags = []
        caption_mentions = []
        

        ## Get user feed over last year
        while last_result_time > last_year:
            api.getUserFeed(self.user_id,maxid=max_id)
            results = api.LastJson
            max_id = results['items'][-1]['pk']
            last_result_time = pd.to_datetime(results['items'][-1]['taken_at'], unit='s')

            print("Last result time",last_result_time, ': ', len(results["items"]))

            for item in tqdm(results["items"]):
                
                post_id.append(item["id"])

                caption_text = item['caption']['text']
                captions.append(caption_text)


                if item['media_type'] == 1:
                    media_type.append("photo")
                elif item['media_type'] == 2:
                    media_type.append("video")
                    
                else:
                    media_type.append("carousel")

                ## get results
                if item['media_type']==1: #only grabbing pictures 
                   
                   url = item['image_versions2']['candidates'][0]['url']
                   urls.append(url)
                elif item['media_type'] == 2:
                    url = item['video_versions'][0]['url']
                    urls.append(url)
                else:
                    print(item['media_type'])
                    other_cnt+=1
                    url = ''
                    urls.append(url)
                    
    
                taken = item['taken_at']
                
                try:
                    likes = item['like_count']
                except KeyError:
                    likes = 0
                try:
                    comments = item['comment_count']
                except KeyError:
                     comments = 0
                
                takenat.append(datetime.datetime.fromtimestamp(taken).strftime('%Y-%m-%d %H:%M:%S'))
                numlikes.append(likes)
                numcomments.append(comments)


                ## Hashtags and usermentions only for images
                #### Hashtags and usenames performance
                tags = find_hashtags(caption_text)
                usernames = find_mentions(caption_text)
                numhashtags.append(len(tags))
                nummentions.append(len(usernames))
                
                ## hashtag and mention performance
                caption_tags.append(", ".join([tag for tag in tags]))
                caption_mentions.append(", ".join([mention for mention in usernames]))

                ## top hashtags only for images
                if item['media_type']==1:
                    [hashtags.append(tag) for tag in tags]
                    [mentions.append(mention) for mention in usernames]
                
        df = pd.DataFrame({ "taken_at":takenat,
                            "likes":numlikes,
                            "comments":numcomments,
                            'post_id':post_id,
                            'media_type':media_type,
                            'captions':captions,
                            'num_hashtags':numhashtags,
                            'num_mentions':nummentions, 
                            'hashtags':caption_tags,
                            'mentions':caption_mentions,'urls':urls})

        hashtag_freq = Counter(hashtags)
        hashtag_df = pd.DataFrame({"tag":list(hashtag_freq.keys()),"count": list(hashtag_freq.values())})
        hashtag_df.set_index("tag")
        hashtag_df.sort_values(by=['count'],ascending=False)
        

        for idx, row in hashtag_df.iterrows():
            tag = row["tag"]
            
            max_likes = 0
            max_likes_url = ""
            
            for index, r in df.iterrows():

                if r["media_type"]!="photo":
                    continue

                url = r['urls']
                t = r["hashtags"].split(", ")
                if tag.lower() in map(lambda x:x.lower(),t):
                    
                    if r["likes"] > max_likes:
                        max_likes = r["likes"]
                        max_likes_url = url

            hashtag_df.loc[idx,"likes"] = max_likes
            hashtag_df.loc[idx,"url"] = max_likes_url
            
        print(hashtag_df.head())
        hashtag_df = hashtag_df[hashtag_df["likes"]>1]
        ## break url
        def parse_url(df):
            for index, row in df.iterrows():

                parsed = urllib.parse.urlparse(str(row['url'])).query #<==
                parsed = urllib.parse.parse_qs(parsed)
                for k, v in parsed.items():
                    df.loc[index, k.strip()] = v[0].strip().lower()
            return df

        return (df, (hashtag_df))
    


    """
    Build output sheet
    """
    def make_output_file(self):
        ## users stats
        user_kpi_df = self.get_user_info()

        ## get user followers
        user_follower_relationship_df = self.get_users_follower_relationship()

        ## 
        all_posts_df, top_hashtags_df = self.get_all_user_posts()
        


        all_posts_df['username'] = self.settings.username


        ## Save data
        with pd.ExcelWriter(os.path.join(self.settings.processed_data_dir, self.settings.output_file),engine='xlsxwriter',options={'strings_to_urls': False}) as writer:
            ## Metrics
            user_kpi_df.to_excel(writer, sheet_name="userinfo")
            user_follower_relationship_df.to_excel(writer, sheet_name="user_followers_relationship",index= False)

            ## hastags, hashtags and images
            top_hashtags_df.to_excel(writer, sheet_name="top_hashtags",index=True)
       
            ## all posts
            all_posts_df.to_excel(writer, sheet_name="all_posts")
   
        
        writer.save()


            
