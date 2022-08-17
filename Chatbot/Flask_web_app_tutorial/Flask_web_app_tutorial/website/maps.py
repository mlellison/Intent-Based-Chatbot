import folium
import pandas as pd
import os
import re
import numpy as np



data = pd.read_csv("website\static\data\listingHk.csv")
#if 'x' in locals():
#    data=data[data['id'].isin(x)]
#else:
#    data=data[data['id'].isin([767022,1253977])]
data = pd.DataFrame(data, columns = ['latitude','longitude','host_name', 'id'][:5]) #[:50]  <-this kind of slice is useful for developing a map
data.head()

#create a map
this_map = folium.Map(prefer_canvas=True)

def plotDot(point):
    '''input: series that contains a numeric named latitude and a numeric named longitude
    this function creates a CircleMarker and adds it to your this_map'''
    folium.CircleMarker(location=[point.latitude, point.longitude],
                        radius=1,
                        weight=0.5,#remove outline
                        tooltip= point.host_name,
                        popup = point.id,
                        parse_html=True,
                        fill_color='#000000').add_to(this_map)

#use df.apply(,axis=1) to iterate through every row in your dataframe
data.apply(plotDot, axis = 1)


#Set the zoom to the maximum possible
this_map.fit_bounds(this_map.get_bounds())

#Save the map to an HTML file
#this_map.save(os.path.join('html_map_output/simple_dot_plot.html'))

this_map