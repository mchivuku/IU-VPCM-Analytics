#!/usr/bin/env python
import os
import json
import facebook
import pandas as pd

import datetime
import dateutil.parser
import requests 
from nltk.corpus import stopwords 
from wordcloud import WordCloud 
from sklearn.feature_extraction.text import CountVectorizer
import time
from nltk.tokenize import sent_tokenize, word_tokenize,TweetTokenizer
import nltk
nltk.download('stopwords')
try:
    from urllib.request import urlopen, Request
except ImportError:
    from urllib2 import urlopen, Request

from datetime import datetime,timedelta

def get_credentials(file):
    with open(file,'r') as f:
        lines = f.readlines()

    return lines[0], lines[1]



class FacebookAPI:
    ACCESS_TOKEN = 'EAAGgvJbWSpkBAN6sKhf0UWsKUxoF0bTSZBuTZBTP44932Eces6iYu5AIPYVLxjOTJRj1XhzqkuZCB2e4pSLndrX9VWG247NmMzgwXvlR9J2b5AAJD3TLlZBTFWg7ZCkpGGCYyofb6gd0ZBGhTnoYc55r9YWOQbDeegXoGJM4ZAiQ4mpFods4SSoK5hsQj0EUMhxXVdfavcbG4acFJvR3q9T'
    

    def __init__(self,settings):
        self.settings = settings
        self.graph = facebook.GraphAPI(FacebookAPI.ACCESS_TOKEN,version="3.1")
        self.pageid = settings.pageid
        appid, app_secret = get_credentials(settings.auth_file)
         
        ## Make directory for raw_data
        if not os.path.exists(self.settings.raw_data_dir):
            os.makedirs(self.settings.raw_data_dir)

        if not os.path.exists(self.settings.processed_data_dir):
            os.makedirs(self.settings.processed_data_dir)

    def get_request_until_succeed(self,url):
        success = False
        while success is False:
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    success = True
            except Exception as ex:
                print(ex)
                #time.sleep(5)

                print("Retrying")

        return response



    """
    pretty print json
    """
    def pp(self, o):
        print(json.dumps(o,indent=1))

    def get_page_profile(self):
        fields = ['id', 'name','about','likes','website','link','fan_count']
        fields = ", ".join(fields)
        
        page = self.graph.get_object(self.pageid,fields=fields)
        df = pd.DataFrame({'id':page['id'],'name':page['name'],'about':page['about'],'website':page['website'],'link':page['link'], 'fan_count':page['fan_count']},index=[0])

        print(df.head())
        return df

    def get_post_message(self,post):
        try:
            message = post['story']
        except KeyError:
            pass    
            message = post['message']
        except KeyError:
            # Post has neither
            message = ''
        return message.replace('\n', ' ')
        

    

    """
    can replace the tokenizer
    """
    def get_most_frequent_words(self, text_series, stop_words = None, ngram_range = (1,2)):
        def word_tokenizer(txt):
            try:
                tokenizer = TweetTokenizer()
                all_tokens = tokenizer.tokenize(txt.lower())
                # this line filters out all tokens that are entirely non-alphabetic characters
                filtered_tokens = [t for t in all_tokens if t.islower()]
                # filter out all tokens that are <=2 chars
                filtered_tokens = [x for x in filtered_tokens if len(x)>2]
            except IndexError:
                filtered_tokens = []
            return(filtered_tokens)

        count_vectorizer = CountVectorizer(analyzer = "word",
                                        tokenizer = word_tokenizer,
                                        stop_words = stop_words,
                                        ngram_range = ngram_range 
                                        )
        
        term_freq_matrix = count_vectorizer.fit_transform(text_series)
            
        terms = count_vectorizer.get_feature_names()
        term_frequencies = term_freq_matrix.sum(axis = 0).tolist()[0]
        
        
        term_freq_df = (pd.DataFrame(list(zip(terms, term_frequencies)), columns = ["token","count"])
                        .set_index("token")
                        .sort_values("count",ascending = False))
        
        ### Avoiding hashtags and mentions
        data = term_freq_df.index.str.startswith(("@","#"))

        data = [not(data[i]) for i in range(len(data))]
        term_freq_df = term_freq_df[data]
        return term_freq_df

    def get_page_engagement(self):
        get_datetime_from_iso_string = lambda x: dateutil.parser.parse(x)

        all_fields = ['id','message','created_time','shares','likes.summary(true)','comments.summary(true)','story']
        all_fields = ', '.join(all_fields)

        posts = self.graph.get_connections(self.pageid,'posts',fields = all_fields)
        n_likes = []
        n_shares= []
        n_comments = []
        n_all = []
        all_posts = []
        all_post_messages = []
        all_post_ids = []

        all_likes = []
        all_love = []
        all_wow = []
        all_haha = []
        all_sad = []
        all_angry  = []

        for post in posts['data']:
            created_time = datetime.strptime(post['created_time'], '%Y-%m-%dT%H:%M:%S+0000')
            created_time = created_time +  timedelta(hours=-5)  # EST
            created_time = created_time.strftime('%Y-%m-%d %H:%M:%S') 

            n_likes.append(post['likes']['summary']['total_count'])
            n_comments.append(post['comments']['summary']['total_count'])
            
            try:
                n_shares.append(post['shares']['count'])
            except KeyError:
                n_shares.append(0)

            n_all.append(n_likes[-1]+ n_shares[-1]+n_comments[-1])
            all_posts.append(created_time)
            all_post_messages.append(self.get_post_message(post))
            all_post_ids.append(post['id'])

            ## get reactions: like', 'love', 'wow', 'haha', 'sad', 'angry'
            like, love, wow, haha, sad, angry = self.get_post_reactions(post['id'])
            all_likes.append(like)
            all_love.append(love)
            all_wow.append(wow)
            all_haha.append(haha)
            all_sad.append(sad)
            all_angry.append(angry)

            
        last_year = datetime.now() - timedelta(days = 365)
        last_post_date = get_datetime_from_iso_string(posts['data'][-1]["created_time"]).date()

        while last_post_date > last_year.date():
            created_dates = []

            posts =   requests.get(posts['paging']['next']).json() 
            for post in posts['data']:
                created_dates.append(dateutil.parser.parse(post["created_time"]))
                created_time = datetime.strptime(post['created_time'], '%Y-%m-%dT%H:%M:%S+0000')
                created_time = created_time +  timedelta(hours=-5)  # EST
                created_time = created_time.strftime('%Y-%m-%d %H:%M:%S') 
                n_likes.append(post['likes']['summary']['total_count'])
                n_comments.append(post['comments']['summary']['total_count'])
                try:
                    n_shares.append(post['shares']['count'])
                except KeyError:
                    n_shares.append(0)

                n_all.append(n_likes[-1]+ n_shares[-1]+n_comments[-1])
                all_posts.append(created_time) 
                all_post_messages.append(self.get_post_message(post))

                 ## get reactions: like', 'love', 'wow', 'haha', 'sad', 'angry'
                like, love, wow, haha, sad, angry = self.get_post_reactions(post['id'])
                all_likes.append(like)
                all_love.append(love)
                all_wow.append(wow)
                all_haha.append(haha)
                all_sad.append(sad)
                all_angry.append(angry)
                all_post_ids.append(post['id'])

            last_post_date = created_dates[-1].date()
            print(f'last post date: {last_post_date}')

        data = { 
        'post_id':all_post_ids,
        'likes': n_likes, 
        'comments': n_comments, 
        'shares': n_shares, 
        'all_interactions': n_all ,
        'created_datetime' : all_posts,
        'post_message':all_post_messages,
        "all_likes":all_likes,
        "all_love":all_love,
        "all_wow":all_wow,
        "all_haha":all_haha,
        "all_sad":all_sad,
        "all_angry":all_angry
        } 

        all_posts_df = pd.DataFrame(data)
        print(all_posts_df.head())

        
        ## parse top words
        text = ' '.join(all_post_messages) 
        stop_list = ['save', 'free', 'today', 
               'get', 'title', 'titles', 'bit', 'ly',',','.'] 
        stop_list.extend(stopwords.words('english')) 
        
        terms_df = self.get_most_frequent_words(all_post_messages,stop_words=stop_list)
        all_posts_df["name"] = self.settings.full_name
        return all_posts_df, terms_df


    def get_page_impressions(self):
        page_impressions = self.graph.get_connections(id=self.pageid,
                                         connection_name='insights',
                                         metric='page_impressions',
                                         date_preset='yesterday',
                                         period='month',
                                         show_description_from_api_doc=True)
        print(page_impressions)

        return 

    def get_post_reactions(self,postid):
        reaction_types = ['like', 'love', 'wow', 'haha', 'sad', 'angry']
        reactions_dict = {}   # dict of {status_id: tuple<6>}
        
        def request_until_succeed(url):
            req = Request(url)
            success = False
            while success is False:
                try:
                    response = urlopen(req)
                    if response.getcode() == 200:
                        success = True
                except Exception as e:
                    print(e)
                    time.sleep(5)

                    print("Error for URL {}: {}".format(url, datetime.datetime.now()))
                    print("Retrying.")

            
            return response.read()

        base_url = f"https://graph.facebook.com/v3.3/{postid}?"
        reactions_dict = {}

        for reaction_type in reaction_types:
            
            fields = "fields=reactions.type({}).limit(0).summary(total_count)&access_token={}".format(reaction_type.upper(),self.ACCESS_TOKEN)
            url = base_url + fields
            status = json.loads(request_until_succeed(url))
            
            id = status["id"]
            count = status['reactions']['summary']['total_count']
            
            reactions_dict[reaction_type] = count

        ## like, love, wow, haha, sad, angry
        
        return reactions_dict["like"], reactions_dict["love"],reactions_dict["wow"], reactions_dict["haha"], reactions_dict["sad"], reactions_dict["angry"]

    def make_output_file(self):
        df_profile = self.get_page_profile()
        df_engagement, df_words = self.get_page_engagement()

        ## Save data
        with pd.ExcelWriter(os.path.join(self.settings.processed_data_dir, self.settings.output_file),engine='xlsxwriter') as writer:
            ## Metrics
            df_profile.to_excel(writer, sheet_name="pageinfo")
            df_engagement.to_excel(writer, sheet_name="page_engagement",index= False)
            ## hastags, hashtags and images
            df_words.to_excel(writer, sheet_name="top_words")
        
        writer.save()
