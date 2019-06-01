#! /home/zeski/anaconda3/bin/python
"""
Created by: Anthony Zelinsky

Purpose: Webmap script utilizing folium


Date Last edited: 5/30/2019

"""
import pandas as pd
import numpy as np
import folium

import os
import webbrowser

import requests
from bs4 import BeautifulSoup as bs

def scraper():
    """
    I am creating this function to scrape the data off of the specified webpage. I am keeping this out of main however,

    and calling it if only necessary.
    """

    ## Pulling in the data from the url.
    url = requests.get("https://inkplant.com/code/state-latitudes-longitudes")
    #Utilizing Beautiful soup to retrieve the page content
    soup = bs(url.content, "html.parser")
    # Finding all of the table data tags
    table_data = soup.find_all("td")

    ## Finding the column names
    headers = [i.get_text().strip() for i in table_data[:3]]
    #print(headers)
    state = list()
    lat   = list()
    long  = list()

    ## Utilizing this dictionary to append the data to the associated list based off of counter
    appender = {
        1 : state,
        2 : lat,
        3 : long
    }

    ## For loop designed to aggregate data to appropriate list
    counter = 1
    for i in table_data[3:]:
        appender[counter].append(i.get_text())
        counter += 1
        if counter == 4:
            counter = 1

    ## Creating a dataframe out of the list
    df = pd.DataFrame(columns = headers)
    df[headers[0]] = state
    df[headers[1]] = lat
    df[headers[2]] = long

    df.to_csv("State_Lat_Long.csv")
    return df

def main():

    ## Creating the base map object
    map_ =  folium.Map(location = [40.2171,-74.7429], zoom_start= 5, tiles = 'OpenStreetMap')


    def map_save(map_obj = map_, open_ = True):

        map_obj.save("webmap1.html")
        ## This will control the browser to open up the html file
        if open_ == True:
            webbrowser.open_new_tab(os.path.realpath("webmap1.html"))



    ## Adding children to the map: marker

    fg = folium.FeatureGroup(name = "First Markers")
    fg.add_child(folium.Marker(location = [40.2171, -74.76], popup  = "Trenton!", icon = folium.Icon(color = 'green')))

    map_.add_child(fg)
    ## Adding multiple markers

    fg1 = folium.FeatureGroup(name = "MultiMark")

    ## Reading in the state lat long dataframe
    try:
        ## If the file does not exist in directory
        df = pd.read_csv("State_Lat_Long.csv")
    except:
        ## The function will be called to recall the source data and create the file
        print("File not in Directory.")
        df = scraper()
        print("File Created and loaded")

    for i,k in df.iterrows():
        fg1.add_child(folium.Marker(location = [k[2], k[3]], popup = "{}".format(k[1]), icon = folium.Icon(color = 'blue')))

    map_.add_child(fg1)

    ## Reading in the state capital data, and appending it to the web map
    state_df = pd.read_json("us_state_capitals.json", 'index')
    ## Creating a group to add the next batch of data into
    fg2 = folium.FeatureGroup(name = 'StateCapitals')
    ## Iterating over the rows in dataframe and appending it to the map
    for i, k in state_df.iterrows():
        fg2.add_child(folium.Marker(location = [k[1], k[2]], popup = "{}".format(k[0]), icon = folium.Icon(color = 'green')))
    ## Adding all of the edits to the file
    map_.add_child(fg2)

    ## Playing around with volcano data.
    fg3 = folium.FeatureGroup(name = "Volcanoes")
    with open("Volcanoes.txt", "r") as f:
        ## Rearding a list of lines from the stream above
        contents = f.readlines()
        #[print(i) for i in contents[:5]]

    df_volcanoes = pd.read_csv("Volcanoes.txt")

    ## Calculating the range and 3 steps for the elevation values
    ## This will be used to bin the volcanoes into 3 categories
    min_   = min(df_volcanoes['ELEV'])
    max_   =  max(df_volcanoes["ELEV"])
    range_ = max_ - min_
    step_  = range_ / 3
    step1  = min_ + step_
    step2  = step1 + step_
    step3  = step2 + step_

    def step_finder(x, step1, step2, step3):
        """
        This function will return colors based on where the value x falls in relation to the 3 bins above
        """
        if x <= step1:
            return "pink"
        elif (x <= step2) and (x > step1):
            return "orange"
        else:
            return "red"


    for i, k in df_volcanoes.iterrows():
        color = step_finder(float(k[5]), step1, step2, step3)
        fg3.add_child(folium.Marker(location = [k[8], k[9]],
                                    popup = "Volcano: {} \nStatus: {} \nElevation: {}".format(k[2], k[4], k[5]),
                                    icon = folium.Icon(color = color)))

    map_.add_child(fg3)






    ## Saving and plotting the map
    open_map = input("Open map? [y/n] ")
    if open_map.lower() == 'y':
        open_map = True
    else: open_map = False
    map_save(open_ = open_map)



    return None





if __name__ == "__main__":

    main()
