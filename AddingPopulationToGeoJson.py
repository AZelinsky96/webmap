#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun  1 14:35:41 2019

@author: zeski
"""

import os 
import requests
from bs4 import BeautifulSoup as bs
import json

import pandas as pd


def pop_scraper():
    """
    This function will scrape and wrangle population data from the web for the 50 states of USA. 
    
    """
    
    ## Requesting the url 0
    url = requests.get("http://worldpopulationreview.com/states/")
    ## Parsing the url content
    soup = bs(url.content, 'html.parser')
    
    ## Finding all of the table data tags    
    td_tags = soup.find_all("td")
    
    ## Creating a list to hold the table data columns
    headers = list()
    
    
    counter = 1    
    for i in td_tags[:9]: 
        ## Strippping the strings and replacing the spaces between words with underscores
        if (counter == 2) or (counter ==3) or (counter == 9): 
            headers.append(i.get_text().strip().replace(" ", "_"))
        counter +=1
        if counter == 10: 
            counter = 1

    df = pd.DataFrame(columns = headers)
    

    ## Dealing with the table body: 
    
    body = {
            "State"   : [], 
            "Pop"     : [],
            "Density" : []
            }

    counter = 1
    for i in td_tags[9:]:
        if (counter == 2):
            body['State'].append(i.get_text().strip())
        elif counter == 3: 
            body['Pop'].append(int(i.get_text().strip().replace(",", "")))
        elif counter == 9: 
            body['Density'].append(i.get_text().strip())
            
        counter +=1
        if counter == 10: 
            counter = 1
    ## Setting the column data as the body values per key and column name
    for i, k in zip(df.columns, body.keys()):
        df[i] = body[k]
    
    return df    


def main(): 
    df = pop_scraper()
    
    ## Puerto Rico is not in the dataframe scraped from the web: Inserting Puerto Rico To insert into the json
    df.loc[len(df)] = ['Puerto Rico', "3654978", "412"]
    df['2019_Pop.'] = df['2019_Pop.'].astype("int")
    
    df.to_csv("State_Population.csv", index = False)
    ## Creating a dictonary to insert data according to state name
    df_dict = {}
    for i, k in df.iterrows(): 
        df_dict[k[0]] = [k[1], k[2]]   
    
    json_ = json.load(open("state.json", "r"))
    
    json_states = list()
    ## Checking to see if the state values match        
    if len((set(json_states) - set(df['State']))) > 0: 
        return print("Error, Make sure Data to insert and Json have same states!")
    
    ## The json is set up as a nested dictionary. Because This is a geo Json, The Data collections follow 
    ## A similar format accross all files. For each collection of data, there is a nested properties dictionary. It is into the nested properties
    ## Dictionary that we will be inserting the apprpoiate data population and density data. This is accomplished by 
    ## Inserting data linked by the Name property to parse through the dataframe dictionary using the Name property as a key. 
    for i in json_['features']: 
        json_states.append(i['properties']['NAME'])
        
        i['properties'].update(Pop=df_dict[i['properties']['NAME']][0])
        i['properties'].update(Density=df_dict[i['properties']["NAME"]][1])
        


    ## Dumping the Json Data
    with open ("state_updated.json", "w") as f:
        json.dump(json_, f)
    

    
    min_ = min(df['2019_Pop.'])
    max_ = max(df['2019_Pop.'])
    
    
    
    step = (max(df['2019_Pop.']) -  min(df['2019_Pop.']) ) / 4
    
    counter = 1
    
    for i in range(4): 
        print(min_ + step ** counter)
        
        counter +=1 
if __name__ == "__main__": 
    main()