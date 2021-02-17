"""
99% Invisible Booklist
Author: Lindsey Viann Parkinson Last updated: February 11, 2021
Scrapes the 99% Invisible podcast website, 99pi.org, and pulls information from the episodes that interview an author. Specifically honing in on "author of" in the episode description
"""
# Packages
import requests
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
from tqdm.notebook import tqdm # this is a fancy progress bar! works on jupyter notebook
from time import sleep
from datetime import datetime



url = 'https://99percentinvisible.org/episodes/?view_option=list'
#response = requests.get(url, timeout = 2)
#response.status_code # 200 is good 

#soup = BeautifulSoup(response.content, "html.parser")
#one_episode = soup.find("article", class_ = "list-block post episode")


def get_episodes(url):
    """
    Returns episode information from one page of 99pi episodes list
    url = 99pi url of episode list
    """
    
    response = requests.get(url, timeout = 2)
    print(response.status_code) # 200 is good 

    soup = BeautifulSoup(response.content, "html.parser")

    cols = ["date", "episode_number", "title", "episode_link"]
    episodes_onepage = pd.DataFrame(columns = cols)

    all_episodes = soup.find_all("article", class_ = "list-block post episode")
    for episode in all_episodes:
        
        episode_link = episode.find("h3", {"class": "list-title"}).find("a").get("href")
        
        span_list = []
        for span in episode.find_all("span"):
            span_list.append(span.text) 
        
        date = span_list[3]

        episode_number = span_list[2]

        title = episode.find("a",{"class": "play"}).get("title")

        
        episodes_onepage = episodes_onepage.append(
            {
                "date": date,
                "episode_number": episode_number,
                "title": title,
                "episode_link": episode_link
            },
            ignore_index=True,
        )
        
    return episodes_onepage


# get information for all episode pages

#Scrape all pages or set page limit
#max_pages = soup.find("a",{"class": "page-numbers"}).find_next_siblings("a")[-1].get("data-page-number")
max_pages = 4

#can make this better. Don't need a second time
#cols = ["date", "episode_number", "title", "episode_link"]
#df = pd.DataFrame(columns = cols)

def get_all_episodes(max_pages):
    link_first_part = "https://99percentinvisible.org/episodes/page/"
    link_2_part = "/?view_option=list"

    for page in tqdm(range(1, int(max_pages) + 1)):
        """Make the urls dynamic"""
        url = (
            link_first_part
            + str(page)
            + link_2_part
        )
        response = requests.get(url, timeout=15)
        soup = BeautifulSoup(response.content, "html.parser")

        episodes_onepage = get_episodes(soup)  # function created earlier
        df = df.append(episodes_onepage, ignore_index=True)

        sleep(0.6) # to keep up with human speed we need to slow down program
    return df

# episode description extracted from each link
# appended to existing dataframe
def get_description(df):
    description = []
    for link in tqdm(df["episode_link"]):
        response2 = requests.get(link, timeout=15)
        soup2 = BeautifulSoup(response2.content, "html.parser")
        
        try: 
            footer = soup2.find("footer")
            desc = footer.find("div", {"class": "credit"}).find("p").contents
            description.append(desc)
        except:
            description.append('NA')
    
    df["description"] = description
    return df

