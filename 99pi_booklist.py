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



#url = 'https://99percentinvisible.org/episodes/?view_option=list'


def get_episodes(url):
    """
    Returns episode information from one page of 99pi episodes list
    url = 99pi url of episode list
    """

    print(f"^ scraping basic episode information. 20 episodes per page")
    response = requests.get(url, timeout = 2)
    print(f"Testing link of each page. 200 is good: {response.status_code}")

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


#Scrape all pages or set page limit
#max_pages = soup.find("a",{"class": "page-numbers"}).find_next_siblings("a")[-1].get("data-page-number")
#max_pages = 4


def get_all_episodes(max_pages):
    link_first_part = "https://99percentinvisible.org/episodes/page/"
    link_2_part = "/?view_option=list"
    
    cols = ["date", "episode_number", "title", "episode_link"]
    episodes_multipage = pd.DataFrame(columns = cols)
    
    for page in tqdm(range(1, int(max_pages) + 1)):
        
        url = (
            link_first_part
            + str(page)
            + link_2_part
        )
        episodes_multipage = episodes_multipage.append(get_episodes(url), ignore_index=True)# = get_episodes(url).append(episodes_onepage, ignore_index=True)
        sleep(0.6) # to keep up with human speed we need to slow down program
    
    return episodes_multipage

# episode description extracted from each link
# appended to existing dataframe
def get_description(max_pages):
    """
    max_pages is the number of 99pi website episode list pages to scrape
    
    get_description calls 'get_all_episodes' which calls 'get_episodes'
    
    episode description extracted from each link
    appended to dataframe from get_all_episodes
    """
    df = get_all_episodes(max_pages)
    description = []
    print(f"Pulling every episode's description:")
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

def total_episode_pages(url): 
    response = requests.get(url, timeout = 2)
    soup = BeautifulSoup(response.content, "html.parser")

    total_pages = soup.find("a",{"class": "page-numbers"}).find_next_siblings("a")[-1].get("data-page-number")
    return f"99% Invisible has {total_pages} pages of episodes"


def author_episodes(max_pages):
    df_allepisodes = get_description(max_pages)

    df_credits = df_allepisodes[df_allepisodes.description != 'NA']
    df_credits['description'] = df_credits['description'].astype(str)
    df_authors = df_credits[df_credits['description'].str.contains("author of")].reset_index(drop=True)

    return df_authors

total_episode_pages('https://99percentinvisible.org/episodes/?view_option=list')

