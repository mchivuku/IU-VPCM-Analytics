#!/usr/bin/env python3
import os, sys
import pprint
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import settings
import app_logger

logger = app_logger.get_logger("linkedIn-preprocessing",logfile="linkedIn.log")
import pandas as pd

from datetime import date, timedelta, datetime
import csv

## Get settings:
file = "settings_linkedIn.json"
settings_obj = settings.Settings(file =file )
settings_data = settings_obj.get_settings()
    
def read_excel(filepath, sheet_name):
    return pd.read_excel(filepath,sheet_name = sheet_name)


"""
Visitor file path
"""
def get_visitor_dataframes(visitors_file_path,settings_data=settings_data):
    visitor = {}
    visitor["metrics"] = read_excel(visitors_file_path, sheet_name='Visitor metrics')
    logger.info(f"{settings_data.campus} - successfully read: visitor metrics and the file has " + str(visitor["metrics"].shape[0]) + " rows and "+ str(visitor["metrics"].shape[1]) + " columns")
    
    
    visitor["location"] = read_excel(visitors_file_path,sheet_name = "Location")
    logger.info(f"{settings_data.campus} successfully read: visitor location and the file has " + str(visitor["location"].shape[0]) + " rows and "+ str(visitor["location"].shape[1]) + " columns")
    


    visitor["job_function"] = read_excel(visitors_file_path,sheet_name = "Job function")
    logger.info(f"{settings_data.campus} successfully read: visitor job_function and the file has " + str(visitor["job_function"].shape[0]) + " rows and "+ str(visitor["job_function"].shape[1]) + " columns")
    
    visitor["industry"] = read_excel(visitors_file_path,sheet_name= "Industry")
    logger.info(f"{settings_data.campus} successfully read: visitor industry and the file has " + str(visitor["industry"].shape[0]) + " rows and "+ str(visitor["industry"].shape[1]) + " columns")
    

    visitor["company_size"] = read_excel(visitors_file_path, sheet_name = "Company size")
    logger.info(f"{settings_data.campus} successfully read: visitor company_size and the file has " + str(visitor["company_size"].shape[0]) + " rows and "+ str(visitor["company_size"].shape[1]) + " columns")
    
    visitor["Seniority"] = read_excel(visitors_file_path,sheet_name = "Seniority")
    logger.info(f"{settings_data.campus} successfully read: visitor Seniority and the file has " + str(visitor["Seniority"].shape[0]) + " rows and "+ str(visitor["Seniority"].shape[1]) + " columns")
    
    
    return visitor


"""
Engagements - Updates
"""
def get_engagements_dataframes(engagements_file_path,settings_data = settings_data):
    updates = {}
    updates["engagement_metrics_aggregate_df"] = read_excel(engagements_file_path,sheet_name = 'Update metrics (aggregated)')
    updates["engagement_metrics_update_df"] = read_excel(engagements_file_path,sheet_name = 'Update engagement')

    ## Fix the Header
    """
    new_header = updates["engagement_metrics_update_df"].iloc[0] #grab the first row for the header
    updates["engagement_metrics_update_df"] = updates["engagement_metrics_update_df"][1:] #take the data less the header row
    updates["engagement_metrics_update_df"].columns = new_header #set the header row as the df header
    
    new_header_agg = updates["engagement_metrics_aggregate_df"].iloc[0] #grab the first row for the header
    
    updates["engagement_metrics_aggregate_df"]  = updates["engagement_metrics_aggregate_df"] [1:] #take the data less the header row
    updates["engagement_metrics_aggregate_df"].columns = new_header_agg #set the header row as the df header
    """
    
    aggregagte = updates["engagement_metrics_aggregate_df"]
    metrics = updates["engagement_metrics_update_df"]


    print(aggregagte.columns)


    logger.info(f"{settings_data.campus} successfully read: updates, sheet: Update metrics (aggregated), and the file has " + str(updates["engagement_metrics_aggregate_df"].shape[0]) + " rows and "+ str(updates["engagement_metrics_aggregate_df"].shape[1]) + " columns")
    logger.info(f"{settings_data.campus} successfully read: updates file, sheet:Update engagement " + str(updates["engagement_metrics_aggregate_df"].shape[0]) + " rows and "+ str(updates["engagement_metrics_aggregate_df"].shape[1]) + " columns")
    
    ##
    
    updates["engagement_metrics_aggregate_df"]["Date"]= pd.to_datetime(updates["engagement_metrics_aggregate_df"]["Date"])
    updates["engagement_metrics_update_df"]["Created date"]= pd.to_datetime(updates["engagement_metrics_update_df"]["Created date"])

    return updates


def get_follower_dataframes(followers_file_path,settings_data = settings_data):
    followers = {}

    followers["new_followers"] = pd.read_excel(followers_file_path, sheet_name='New followers')
    logger.info(f"{settings_data.campus} - successfully read: followers, sheet: new followers, and the file has " + str(followers["new_followers"].shape[0]) + " rows and " + str(followers["new_followers"]) + " columns")
    
    followers["location"] = pd.read_excel(followers_file_path,sheet_name = "Location")
    logger.info(f"{settings_data.campus} - successfully read: followers, sheet: location, and the file has " + str(followers["location"].shape[0]) + " rows and " + str(followers["location"]) + " columns")
    
    followers["job_function"] = pd.read_excel(followers_file_path,sheet_name = "Job function")
    logger.info(f"{settings_data.campus} - successfully read: followers, sheet: job_function, and the file has " + str(followers["job_function"].shape[0]) + " rows and " + str(followers["job_function"]) + " columns")
    
    followers["industry"] = pd.read_excel(followers_file_path,sheet_name= "Industry")
    logger.info(f"{settings_data.campus} - successfully read: followers, sheet: industry, and the file has " + str(followers["industry"].shape[0]) + " rows and " + str(followers["industry"]) + " columns")
    
    followers["company_size"] = pd.read_excel(followers_file_path, sheet_name = "Company size")
    logger.info(f"{settings_data.campus} - successfully read: followers, sheet: company_size, and the file has " + str(followers["company_size"].shape[0]) + " rows and " + str(followers["company_size"]) + " columns")
    
    followers["seniority"] = pd.read_excel(followers_file_path,sheet_name = "Seniority")
    logger.info(f"{settings_data.campus} - successfully read: followers, sheet: seniority, and the file has " + str(followers["seniority"].shape[0]) + " rows and " + str(followers["seniority"]) + " columns")
    
    return followers

"""
Sheet 1 - Engagement Insights
"""
def make_engagement_insights(visitor_metrics_df, engagement_metrics_aggregate_df, new_followers_df,settings_data=settings_data):
    columns = ['Date',
                        'Total page views (desktop)',
                        'Total page views (mobile)',
                        'Total page views (total)',
                        'Total unique visitors (desktop)',
                        'Total unique visitors (mobile)',
                        'Total unique visitors (total)',
                        'Sponsored followers',
                        'Organic followers',
                        'Total followers',
                        'Impressions (organic)', 
                        'Impressions (sponsored)',
                        'Impressions (total)', 
                        'Unique impressions (organic)',
        'Clicks (organic)', 'Clicks (sponsored)', 'Clicks (total)',
        'Reactions (organic)', 'Reactions (sponsored)', 'Reactions (total)',
        'Comments (organic)', 'Comments (sponsored)', 'Comments (total)',
        'Shares (organic)', 'Shares (sponsored)', 'Shares (total)',
        'Engagement rate (organic)', 'Engagement rate (sponsored)',
        'Engagement rate (total)']


    # days between start and end date
    visitor_metrics_df['Date'] = pd.to_datetime(visitor_metrics_df['Date'])
    date_df = visitor_metrics_df['Date'].dt.date

    
    start_date =  (date_df.min())
    end_date   =  (date_df.max())

    logger.info(f"{settings_data.campus} start date {str(start_date)}  end date {end_date}")


    delta = end_date - start_date  # timedelta
    
    visitor_metrics_df = visitor_metrics_df.fillna(0)
    engagement_metrics_aggregate_df = engagement_metrics_aggregate_df.fillna(0)
    new_followers_df = new_followers_df.fillna(0)
    
    ## Set Index Date
    visitor_metrics_df["Date"] = pd.to_datetime(visitor_metrics_df["Date"])
    new_followers_df["Date"] = pd.to_datetime(new_followers_df["Date"])
    engagement_metrics_aggregate_df["Date"] = pd.to_datetime(engagement_metrics_aggregate_df["Date"])
    
    visitor_metrics_df = visitor_metrics_df.set_index("Date")
    new_followers_df = new_followers_df.set_index("Date")
    engagement_metrics_aggregate_df = engagement_metrics_aggregate_df.set_index("Date")

    lines = []
    for i in range(delta.days + 1):
        metric = []

        date = start_date + timedelta(days=i)
        

        ## visitor metrics
        v = visitor_metrics_df[visitor_metrics_df.index.date==date]
        metric.append(date)
        if not v.shape[0] == 0:
            metric.append(float(v["Total page views (desktop)"]))
            metric.append(float(v["Total page views (mobile)"]))
            metric.append(float(v["Total page views (total)"]))
            metric.append(float(v["Total unique visitors (desktop)"]))
            metric.append(float(v["Total unique visitors (mobile)"]))
            metric.append(float(v["Total unique visitors (total)"]))
        else:
            for m in range(7):
                metric.append(0.0)
            

        ## follower metrics

        f = new_followers_df[new_followers_df.index.date==date]
        
        if not f.shape[0]==0:
            metric.append(float(f["Sponsored followers"]))
            metric.append(float(f["Organic followers"]))
            metric.append(float(f['Total followers']))
        else:
            metric.append(0.0)
            metric.append(0.0)
            metric.append(0.0)

        ## engagement 
        try:
            e = engagement_metrics_aggregate_df[engagement_metrics_aggregate_df.index.date == date]
            metric.append(float(e['Impressions (organic)']))
            metric.append(float(e['Impressions (sponsored)']))
            metric.append(float(e['Impressions (total)']))
            metric.append(float(e['Unique impressions (organic)']))
            metric.append(float(e['Clicks (organic)']))
            metric.append(float(e['Clicks (total)']))
            metric.append(float(e['Clicks (sponsored)']))
            metric.append(float(e['Reactions (organic)']))
            metric.append(float(e['Reactions (sponsored)']))
            metric.append(float(e['Reactions (total)']))
            metric.append(float(e['Comments (organic)']))
            metric.append(float(e['Comments (sponsored)']))
            metric.append(float(e['Comments (total)']))
            metric.append(float(e['Shares (organic)']))
            metric.append(float(e['Shares (sponsored)']))
            metric.append(float(e['Shares (total)']))
            metric.append(float(e['Engagement rate (organic)']))
            metric.append(float(e['Engagement rate (sponsored)']))
            metric.append(float(e['Engagement rate (total)']))         
        except:   
            print("exception",str(e))
            for r in range(19):
                metric.append(0)
                
        lines.append(metric)
        
    
    ### 
    df = pd.DataFrame(lines, 
               columns =columns)

    
    
    return df
    
    
def make_engagement_posts(engagement_metrics_update_df,settings_data=settings_data):
    columns = ['Created date',
                        'Post title',
                        'Post link',
                        'Post type',
                        'Impressions',
                        'Video views',
                        'Clicks',
                        'Click through rate (CTR)',
                        'Likes',
                        'Comments',
                        'Shares', 
                        'Follows',
        'Engagement rate','Date'] 
    
    engagement_metrics_update_df = engagement_metrics_update_df.fillna(0)
    engagement_metrics_update_df["Created date"] = pd.to_datetime(engagement_metrics_update_df["Created date"])
    engagement_metrics_update_df["Date"] = engagement_metrics_update_df["Created date"].dt.date
    data = []
    for index, row in engagement_metrics_update_df.iterrows():
        data.append([row["Created date"], row["Update title"],row["Update link"],row["Update type"],
                           row["Impressions"],row["Video views"],row["Clicks"],row["Click through rate (CTR)"],
                           row["Likes"],row["Comments"], row["Shares"],row["Follows"],row["Engagement rate"],row["Date"]
                           ])
    
    engagement_posts_df = pd.DataFrame(data, 
               columns =columns)
    
    
    return engagement_posts_df

"""

Following files will be combined to draw - Engagement insights

Engagement Insights: Draw insight on:

total page views to date,
total unique visitors to
average engagement rate
linked In posts
Visitor Insights: Draw insight on visitor demographics:

Location of visitors
Visitor by industry
Follower Insights: Draw insight on follower demographics:

Location of followers
Follower Industry

"""
if __name__=="__main__":
    

    ## Get all files
    ## Read from
    visitors_file_path = os.path.join(settings_data.raw_data_dir,settings_data.visitor_file )
    followers_file_path = os.path.join(settings_data.raw_data_dir,settings_data.followers_file )
    engagements_file_path = os.path.join(settings_data.raw_data_dir, settings_data.engagements_file )

    
    visitors_dataframes = get_visitor_dataframes(visitors_file_path)
    updates_dataframes = get_engagements_dataframes(engagements_file_path)
    follower_dataframes = get_follower_dataframes(followers_file_path)



    engagement_insights_df = make_engagement_insights(visitors_dataframes["metrics"],updates_dataframes["engagement_metrics_aggregate_df"],follower_dataframes["new_followers"])
    engagement_posts_df = make_engagement_posts(updates_dataframes["engagement_metrics_update_df"])


    logger.info(f"{settings_data.campus} - Successfully built, {settings_data.engagement_insights_sheetname}, has rows: " + str(engagement_insights_df.shape[0]) +  " columns: " + str(engagement_insights_df.shape[1]))
    logger.info(f"{settings_data.campus} - Successfully built, {settings_data.engagement_top_posts_sheetname}, has rows: " + str(engagement_posts_df.shape[0]) +  " columns: " + str(engagement_posts_df.shape[1]))
    
    logger.info(f"{settings_data.campus} - Successfully built, visitors by location, has rows: " + str(visitors_dataframes["location"].shape[0]) +  " columns: " + str(visitors_dataframes["location"].shape[1]))
    logger.info(f"{settings_data.campus} - Successfully built, visitors by industry, has rows: " + str(visitors_dataframes["industry"].shape[0]) +  " columns: " + str(visitors_dataframes["industry"].shape[1]))
    logger.info(f"{settings_data.campus} - Successfully built, followers by location, has rows: " + str(follower_dataframes["location"].shape[0]) +  " columns: " + str(follower_dataframes["location"].shape[1]))
    logger.info(f"{settings_data.campus} - Successfully built, followers by industry, has rows: " + str(follower_dataframes["industry"].shape[0]) +  " columns: " + str(follower_dataframes["industry"].shape[1]))
    logger.info(f"{settings_data.campus} - Successfully built, followers by seniority, has rows: " + str(follower_dataframes["seniority"].shape[0]) +  " columns: " + str(follower_dataframes["seniority"].shape[1]))


    ## Save data
    with pd.ExcelWriter(os.path.join(settings_data.processed_data_dir,settings_data.output_file),engine='xlsxwriter') as writer:
        ## Metrics
        engagement_insights_df.to_excel(writer, sheet_name=settings_data.engagement_insights_sheetname,index= False)
        engagement_posts_df.to_excel(writer, sheet_name=settings_data.engagement_top_posts_sheetname,index= False)
        ## visitor demographics
        visitors_dataframes["location"].to_excel(writer, sheet_name = settings_data.visitor_demographics_location_sheetname,index=False)
        visitors_dataframes["industry"].to_excel(writer, sheet_name = settings_data.visitor_demographics_industry_sheetname,index=False)

        ## follower demographics
        follower_dataframes["location"].to_excel(writer, sheet_name = settings_data.follower_demographics_location_sheetname,index=False)
        follower_dataframes["industry"].to_excel(writer, sheet_name = settings_data.follower_demographics_industry_sheetname,index=False)
        follower_dataframes["seniority"].to_excel(writer, sheet_name = settings_data.follower_demographics_seniority_sheetname,index=False)
        
    
        writer.save()