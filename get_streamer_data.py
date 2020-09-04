# -*- coding: utf-8 -*-
"""
Matthew Guerrero
8/2020
"""

from selenium import webdriver
import pandas as pd
import time

def get_streamer_stats(date_range=30, pages=20, sort_by='watched'):
    '''
    Gathers streamer information as a dataframe.
    Source: https://sullygnome.com/
    '''
    #date_range options: 3,7,14,30,90,180,365
    #each page contains 50 streamers
    #sort_by options: 'watched','peakviewers','mostfollowers', and more

    #initialize webdriver
    driver = webdriver.Firefox()
    
    #resize and reposition window
    #driver.set_window_position(-1000,-100)
    #driver.set_window_size(900,1200)
    
    #initialize list for final dataframe
    streamers= []
    
    #initialize streamer url list
    streamer_urls = []

    #starting page
    driver.get(f"https://sullygnome.com/channels/{date_range}/{sort_by}")

    #iterate through pages and create list of streamers to scrape
    for page_num in range(1, pages+1):
        
        #necessary for page to load and not cause 'stale element' error
        time.sleep(3)
        
        #selects 'channel name' column from table
        channel_col = driver.find_elements_by_xpath("//tbody/tr/td[3]")
        for channel_name in channel_col:
            streamer_urls.append(f"https://sullygnome.com/channel/{channel_name.text}/{date_range}")
        
        #click 'next' button
        driver.find_element_by_xpath("//a[@id='tblControl_next']").click()

    #collect features
    for url in streamer_urls:
        
        #fix non-ascii urls
        if not str.isascii(url) or " " in url:
            pos1 = url.find("(")
            pos2 = url.find(")")
            ascii_name = url[pos1+1:pos2]
            url = f"https://sullygnome.com/channel/{ascii_name}/{date_range}"
            
        #print()
        #print(url)
        
        #open streamer overview
        driver.get(url)
        time.sleep(1)
        
        #case: webpage doesn't load fast enough
        try:
            channel = driver.find_element_by_xpath("//span[@class='PageHeaderMiddleWithImageHeaderP1']").text
        except:
            driver.get(url)
            time.sleep(1)
            channel = driver.find_element_by_xpath("//span[@class='PageHeaderMiddleWithImageHeaderP1']").text
    
        subheader = driver.find_elements_by_xpath("//div[@class='MiddleSubHeaderRow']/div")
        
        partner = True if subheader[5].text == "Partnered" else False
        mature = True if subheader[7].text == "Yes" else False
        lang = subheader[9].text
        date = subheader[11].text
        followers = int(subheader[1].text.replace(",",""))
        views = int(subheader[3].text.replace(",",""))
            
        avg_viewers = driver.find_element_by_xpath("//div[@class='InfoStatPanelTLCell']")
        avg_viewers = int(avg_viewers.text.replace(",",""))
        
        hours_in_range = int(driver.find_element_by_xpath("//div[@title='Amount of time streamed']/div[@class='InfoStatPanelTLCell']").text)
        num_of_streams = int(driver.find_element_by_xpath("//div[@class='InfoPanelCombinedBottom']/a").text[19:].split()[0])
        if num_of_streams == 0:
            num_of_streams = 1
        avg_duration = round(hours_in_range/num_of_streams,1)
        
        #navigate to 'games' section of streamer page
        driver.get(url+"/games")
        time.sleep(2)
        games = driver.find_elements_by_xpath("//tbody/tr")
        
        #case: webpage doesn't load fast enough
        try:
            game1 = games[0].find_element_by_css_selector('a').get_attribute('data-gamename')
        except:
            driver.get(url+"/games")
            time.sleep(2)
            games = driver.find_elements_by_xpath("//tbody/tr")
            game1 = games[0].find_element_by_css_selector('a').get_attribute('data-gamename')
        
        #case: channel plays only 1 or 2 games
        try:
            game2 = games[1].find_element_by_css_selector('a').get_attribute('data-gamename')
        except IndexError:
            game2 = ""
        try:
            game3 = games[2].find_element_by_css_selector('a').get_attribute('data-gamename')
        except IndexError:
            game3 = ""
    
        streamers.append({
            "Channel": channel,
            "Partner":partner,
            "Mature":mature,
            "Language": lang,
            "Date Created": date,
            "Total Followers": followers,
            "Total Views": views,
            #"Total Subscribers": subs,
            #"Total Hours Streamed": hours,
            "Average Viewers": avg_viewers,
            "Average Stream Duration": avg_duration,
            "Game 1":game1,
            "Game 2":game2,
            "Game 3":game3
            })

    return pd.DataFrame(streamers)
       
df = get_streamer_stats()
df.to_csv("twitch-top1000-30days.csv", index=False)
