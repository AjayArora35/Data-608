#!/usr/bin/env python
# coding: utf-8

# In[2]:


import os
import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import json
import requests
import numpy as np

from sodapy import Socrata

#client = Socrata("data.cityofnewyork.us",
#                  "lC3qS0jidlOyzG8Buf4G6VGf2",
#                  "aj@cisinc.org",
#                  "XXXXXXXXXX")
#treedata = client.get("uvpi-gqnh", limit=683788)

#treedata = pd.read_json("https://data.cityofnewyork.us/resource/uvpi-gqnh.json")

# Get all distinct tree types
tt = pd.read_json("https://data.cityofnewyork.us/resource/uvpi-gqnh.json?$select=spc_common&$group=spc_common&$limit=5000")
ttdf = pd.DataFrame.from_records(tt)
#print ttdf

# Get all distinct NY boroughs
boro = pd.read_json("https://data.cityofnewyork.us/resource/uvpi-gqnh.json?$select=boroname&$group=boroname&$limit=5000")
borodf = pd.DataFrame.from_records(boro)
#print borodf


#https://soda.demo.socrata.com/resource/4tka-6guv.json?select=region,MAX(magnitude)&select=region,MAX(magnitude)&select=region,MAX(magnitude)&group=region
#treesdf = pd.DataFrame.from_records(treedata)
#treetypedf = pd.DataFrame()
#treetypedf = treesdf.spc_common.unique()
#print treesdf['health'].count() 


#print treetypedf
#treetypedf.drop()
#treetypedf.replace('', np.nan, inplace=True)
#treetypedf.dropna(subset=['spc_common'], inplace=True)
#print treedata

app = dash.Dash(__name__)

server = app.server

#data = pd.read_json('https://data.cityofnewyork.us/resource/uvpi-gqnh.json')
#response = requests.get('https://data.cityofnewyork.us/resource/uvpi-gqnh.json')
#print(response.status_code)

#url = 'https://data.cityofnewyork.us/resource/uvpi-gqnh.json'
#trees = pd.read_json(url)
#trees.head(10)



app.layout = html.Div([
    
    
    html.H2('Choose Borough'),

    dcc.Dropdown(

        id='borough',

        options=[{'label': i, 'value': i} for i in sorted(borodf['boroname'])],

        value='Select', 

    ),
    
    html.H2('Choose Tree Type'),    
    
    dcc.Dropdown(

        id='treetype',

        options=[{'label': i, 'value': i} for i in sorted(ttdf['spc_common'])],

        value='Select', 

    ), 
    
 

    
    html.Div(id='display-borough'),
    
    html.H2('Stewardship Activities '),
    
    html.Div([
        html.P('Below is a short list of the most common examples of what counts as one stewardship activity'),
        html.P('-Helpful tree guards that do not appear professionally installed'),
        html.P('-Mulch or woodchips'),
        html.P('-Intentionally-planted flowers or other plants'),
        html.P('-Signs related to care of the tree or bed, other than those installed by Parks'),
        html.P('-Decorations (not including wires or lights added to the tree)'),
        html.P('-Seating in the tree bed, usually as part of the tree guard'),
        html.P('-Viewing someone performing a stewardship activity during the survey')
               ]),
    html.Div(id='display-treetype'),
    
])


app.css.append_css({"external_url": "https://codepen.io/chriddyp/pen/bWLwgP.css"})

@app.callback(dash.dependencies.Output('display-borough', 'children'), [dash.dependencies.Input('borough', 'value')])

def display_borough(value):

    url = "https://data.cityofnewyork.us/resource/uvpi-gqnh.json?$select=spc_common&$group=spc_common&$where=boroname='" + value +"'&$limit=5000"
    url = url.replace(' ', '%20')
    tt = pd.read_json(url)
    ttdf = pd.DataFrame.from_records(tt)
    return 'You have selected "{}"'.format(value)

@app.callback(dash.dependencies.Output('display-treetype', 'children'), [dash.dependencies.Input('treetype', 'value'), dash.dependencies.Input('borough', 'value')])

def display_treetype(treetype_value, borough_value):
    
    #print treetype_value
    #print borough_value
    if treetype_value != "Select" and borough_value != "Select":
        print treetype_value
        treetype_value = treetype_value.replace("\'", "")
        borough_value = borough_value.replace("\'", "")
        print treetype_value
    #Get tree health
        url = "https://data.cityofnewyork.us/resource/uvpi-gqnh.json?$select=health,steward&$where=spc_common='" + treetype_value + "'AND boroname='" + borough_value + "'&$limit=50000" 
        url = url.replace(' ', '%20')
        #print url
        th = pd.read_json(url)
        thdf = pd.DataFrame.from_records(th)
        if not thdf.empty:
            totalrecords = float(thdf['health'].count())
            goodratio = round((float(thdf.query('health == "Good"').health.count()) / totalrecords) * 100,2)
            poorratio = round((float(thdf.query('health == "Poor"').health.count()) / totalrecords) * 100,2)
            fairratio = round((float(thdf.query('health == "Fair"').health.count()) / totalrecords) * 100,2)

            totalrecords_good = thdf.query('health == "Good"').health.count()
            totalrecords_fair = thdf.query('health == "Fair"').health.count()
            totalrecords_poor = thdf.query('health == "Poor"').health.count()

            oneortwo_good = round((float(thdf.query('health == "Good" and steward == "1or2"').steward.count()) / totalrecords_good) * 100,2)
            threeorfour_good = round((float(thdf.query('health == "Good" and steward == "3or4"').steward.count()) / totalrecords_good) * 100,2)
            fourormore_good = round((float(thdf.query('health == "Good" and steward == "4orMore"').steward.count()) / totalrecords_good) * 100,2)
            none_good = round((float(thdf.query('health == "Good" and steward == "None"').steward.count()) / totalrecords_good) * 100,2)

            oneortwo_fair = round((float(thdf.query('health == "Fair" and steward == "1or2"').steward.count()) / totalrecords_fair) * 100,2)
            threeorfour_fair = round((float(thdf.query('health == "Fair" and steward == "3or4"').steward.count()) / totalrecords_fair) * 100,2)
            fourormore_fair = round((float(thdf.query('health == "Fair" and steward == "4orMore"').steward.count()) / totalrecords_fair) * 100,2)
            none_fair = round((float(thdf.query('health == "Fair" and steward == "None"').steward.count()) / totalrecords_fair) * 100,2)

            oneortwo_poor = round((float(thdf.query('health == "Poor" and steward == "1or2"').steward.count()) / totalrecords_poor) * 100,2)
            threeorfour_poor = round((float(thdf.query('health == "Poor" and steward == "3or4"').steward.count()) / totalrecords_poor) * 100,2)
            fourormore_poor = round((float(thdf.query('health == "Poor" and steward == "4orMore"').steward.count()) / totalrecords_poor) * 100,2)
            none_poor = round((float(thdf.query('health == "Poor" and steward == "None"').steward.count()) / totalrecords_poor) * 100,2)

            #print totalrecords
            #print goodratio
            #print poorratio
            #print fairratio

            graphs = []
            graphs.append(html.Div(dcc.Graph(
                id='Health',
                figure={
                    'data': [
                        {'x': ['Good Health'], 'y': [goodratio], 'type': 'bar', 'name': 'Health'},
                        {'x': ['1 or 2', '3 or 4', '4 or More', 'None'], 'y': [oneortwo_good, threeorfour_good, fourormore_good, none_good], 'type': 'bar', 'name': 'Steward'}
                        #{'x': ['Fair Health'], 'y': [fairratio], 'type': 'bar', 'name': 'Health'},
                        #{'x': ['Poor Health'], 'y': [poorratio], 'type': 'bar', 'name': 'Health'},
                    ],
                    'layout': {
                        'title': 'Trees Good Health / Stewardship # Of Activities',
                        'yaxis':{
                             'title': 'Good Health / Stewardship Activites (%)'
                            },
                        },
                    },
                ),  
            ))

            graphs.append(html.Div(dcc.Graph(
                id='Fair',
                figure={
                    'data': [
                        {'x': ['Fair Health'], 'y': [fairratio], 'type': 'bar', 'name': 'Health'},
                        {'x': ['1 or 2', '3 or 4', '4 or More', 'None'], 'y': [oneortwo_fair, threeorfour_fair, fourormore_fair, none_fair], 'type': 'bar', 'name': 'Steward'}
                        #{'x': ['Fair Health'], 'y': [fairratio], 'type': 'bar', 'name': 'Health'},
                        #{'x': ['Poor Health'], 'y': [poorratio], 'type': 'bar', 'name': 'Health'},
                    ],
                    'layout': {
                        'title': 'Trees Fair Health / Stewardship # Of Activities',
                        'yaxis':{
                             'title': 'Fair Health / Stewardship Activites (%)'
                            },
                        }
                    }
                ),  
            ))

            graphs.append(html.Div(dcc.Graph(
                id='Poor',
                figure={
                    'data': [
                        {'x': ['Poor Health'], 'y': [poorratio], 'type': 'bar', 'name': 'Health'},
                        {'x': ['1 or 2', '3 or 4', '4 or More', 'None'], 'y': [oneortwo_poor, threeorfour_poor, fourormore_poor, none_poor], 'type': 'bar', 'name': 'Steward'}
                        #{'x': ['Fair Health'], 'y': [fairratio], 'type': 'bar', 'name': 'Health'},
                        #{'x': ['Poor Health'], 'y': [poorratio], 'type': 'bar', 'name': 'Health'},
                    ],
                    'layout': {
                        'title': 'Trees Poor Health / Stewardship # Of Activities',
                        'yaxis':{
                             'title': 'Poor Health / Stewardship Activites (%)'
                            },
                        }
                    }
                ),  
            ))

            return graphs
        else:
            return 'No data available for "{}"'.format(treetype_value)


if __name__ == '__main__':

    app.run_server(debug=False, port=8000)


# In[ ]:




