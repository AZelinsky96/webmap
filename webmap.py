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

    df.to_csv("State_Lat_Long.csv", index = False)
    return df



def main():

    ## Creating the base map object
    map_ =  folium.Map(location = [40.2171,-74.7429], zoom_start= 5, tiles = 'stamenwatercolor')


    def map_save(map_obj = map_, open_ = True):

        map_obj.save("webmap1.html")
        ## This will control the browser to open up the html file
        if open_ == True:
            webbrowser.open_new_tab(os.path.realpath("webmap1.html"))

# -------------------------------------------------------------------------------------

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

    ## This is a csv I created when scraping and editing the json in the AddingPopulationToJson python File
    population_df = pd.read_csv("State_Population.csv")

    df['State'] = df["State"].apply(lambda x: x.strip())


    #print(df)
    #print(population_df)

    df = pd.merge(df, population_df, left_on = "State", right_on = "State")
    

#    df.drop(["Unamed: 0_x", "Unamed: 0_y"], axis = 1, inplace = True)
    for i,k in df.iterrows():
        fg1.add_child(folium.Marker(location = [k[1], k[2]], tooltip = "State: {} - Click For Detail".format(k[0]), popup = "POP: {}   POP_DENSITY: {} (p/m^2)".format(k[3], k[4]), icon = folium.Icon(color = 'blue')))



# -------------------------------------------------------------------------------------


    ## Reading in the state capital data, and appending it to the web map
    state_df = pd.read_json("us_state_capitals.json", 'index')

    ## Creating a group to add the next batch of data into
    fg2 = folium.FeatureGroup(name = 'StateCapitals')
    ## Iterating over the rows in dataframe and appending it to the map
    for i, k in state_df.iterrows():
        fg2.add_child(folium.CircleMarker(location = [k[1], k[2]], popup = "{}".format(k[0]), tooltip = "State Capital - Click for Detail",  color = 'green', fill_color = 'green', fill_opacity = 1))
    ## Adding all of the edits to the file



# -------------------------------------------------------------------------------------

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
        color_ = step_finder(float(k[5]), step1, step2, step3)
        fg3.add_child(folium.CircleMarker(location = [k[8], k[9]],
                                    popup = "NAME: {} \n\nTYPE: {} \n\nELEVATION: {}".format(k[2], k[4], k[5]),
                                    tooltip = "Volcano! - Click for Detail",
                                    fill_color = color_ ,
                                     color = "grey",
                                     fill_opacity = 0.8))



# -------------------------------------------------------------------------------------
## Adding polygon layer to the map

    ## Loading in the geojson data:

    fg4 = folium.FeatureGroup(name = "us_polygon_layer")

    fg4.add_child(folium.GeoJson(data = open("world.json", "r", encoding = "utf-8-sig").read()))





## Adding the State Poly to the map:

    fg5 = folium.FeatureGroup(name = "us_state_poly")

    fg5.add_child(folium.GeoJson( data = open("state_updated.json", "r").read(),
                                  style_function =lambda x: {"fillColor" : "green" if int(x['properties']['Pop']) < 500000
                                  else "yellow" if 500000 <= int(x['properties']['Pop']) < 10000000 else "orange" if 10000000 <= int(x['properties']['Pop'])  < 25000000 else "red"},
                                    ))



## Inserting them by layer:
    map_.add_child(fg4)
    map_.add_child(fg5)
    map_.add_child(fg1)
    map_.add_child(fg2)
    map_.add_child(fg3)


# -------------------------------------------------------------------------------------
    ## Saving and plotting the map
    open_map = input("Open map? [y/n] ")
    if open_map.lower() == 'y':
        open_map = True
    else: open_map = False
    map_save(open_ = open_map)



    return None





if __name__ == "__main__":

    main()
