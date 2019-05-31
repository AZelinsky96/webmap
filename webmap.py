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

def main():

    ## Creating the base map object
    map_ =  folium.Map(location = [40.2171,-74.7429], zoom_start= 5, tiles = 'OpenStreetMap')


    def map_save(map_obj = map_, open_ = True):

        map_obj.save("webmap1.html")
        ## This will control the browser to open up the html file
        webbrowser.open_new_tab(os.path.realpath("webmap1.html"))



    ## Adding children to the map: marker

    fg = folium.FeatureGroup(name = "First Markers")
    fg.add_child(folium.Marker(location = [40.2171, -74.76], popup  = "Trenton!", icon = folium.Icon(color = 'green')))




    map_.add_child(fg)





    ## Saving and plotting the map
    map_save()



    return None





if __name__ == "__main__":

    main()
