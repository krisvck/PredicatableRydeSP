#!/usr/bin/env python
# coding: utf-8

# In[480]:


import folium
from folium.plugins import BeautifyIcon
import shapely
import math
import pandas as pd
import openrouteservice as ors
from IPython.core.interactiveshell import InteractiveShell
import sys


# In[481]:


# Define number of vehicles to use
numOfVehicles = int(sys.argv[1])

# Define name of CSV file, must be located inside the data folder
dataFilePath = str(sys.argv[2])
csvPath = "data/" + dataFilePath



# Define how long (in seconds) each bus stops at each location
numOfSecondsPerStop = 15


# In[482]:


# First define the map centered around Beira
m = folium.Map(location=[43.640565, -116.339269], tiles='cartodbpositron', zoom_start=13)

# Next load the delivery locations from CSV file selected from data directory
# ID, Lat, Lon, Open_From, Open_To, Needed_Amount
deliveries_data = pd.read_csv(
    csvPath,
    index_col="ID",
    parse_dates=["Open_From", "Open_To"]
)

# Number of locations to visit and pickup from
# This is added to below for every location imported from the .csv file
numOfPoints = 0

# Plot the locations on the map with more info in the ToolTip
for location in deliveries_data.itertuples():
    tooltip = folium.map.Tooltip("<h4><b>ID {}</b></p><p>Supplies needed: <b>{}</b></p>".format(
        location.Index, location.Needed_Amount
    ))

    # Add to the total number of locations to visit
    numOfPoints += 1

    folium.Marker(
        location=[location.Lat, location.Lon],
        tooltip=tooltip,
        icon=BeautifyIcon(
            icon_shape='marker',
            number=int(location.Index),
            spin=True,
            text_color='red',
            background_color="#FFF",
            inner_icon_style="font-size:12px;padding-top:-5px;"
        )
    ).add_to(m)

# The vehicles are all located Centennial High School
depot = [43.649839, -116.336241]

folium.Marker(
    location=depot,
    icon=folium.Icon(color="green", icon="bus", prefix='fa'),
    setZIndexOffset=1000
).add_to(m)
#m


# In[483]:


# Divide up students per vehicle
# Number of locations to visit / number of vehicles
maxStudentsPerVehicle = math.ceil(numOfPoints/numOfVehicles)


# In[484]:


# Define the vehicles
# https://openrouteservice-py.readthedocs.io/en/latest/openrouteservice.html#openrouteservice.optimization.Vehicle
vehicles = list()
for idx in range(numOfVehicles):
    vehicles.append(
        ors.optimization.Vehicle(
            id=idx,
            start=list(reversed(depot)),
            end=list(reversed(depot)),
            capacity=[maxStudentsPerVehicle],
            time_window=[1553241600, 1553245200]  # Fri 8-20:00, expressed in POSIX timestamp
        )
    )

# Next define the delivery stations
# https://openrouteservice-py.readthedocs.io/en/latest/openrouteservice.html#openrouteservice.optimization.Job
deliveries = list()
for delivery in deliveries_data.itertuples():
    deliveries.append(
        ors.optimization.Job(
            id=delivery.Index,
            location=[delivery.Lon, delivery.Lat],
            service=numOfSecondsPerStop,
            amount=[delivery.Needed_Amount],
            time_windows=[[
                int(delivery.Open_From.timestamp()),  # VROOM expects UNIX timestamp
                int(delivery.Open_To.timestamp())
            ]]
        )
    )


# In[485]:


# Initialize a client and make the request
ors_client = ors.Client(key='5b3ce3597851110001cf6248a4a8f689bb5f4ee5865a9e838a21f443')  # Get an API key from https://openrouteservice.org/dev/#/signup
result = ors_client.optimization(
    jobs=deliveries,
    vehicles=vehicles,
    geometry=True
)

#print(result)

# Add the output to the map
for color, route in zip(['green', 'red', 'blue', 'purple', 'yellow', 'orange', 'aqua','magenta'], result['routes']):
    decoded=ors.convert.decode_polyline(route['geometry'])    # Route geometry is encoded
    gj = folium.GeoJson(
        name='Vehicle {}'.format(route['vehicle']),
        data={"type": "FeatureCollection", "features": [{"type": "Feature",
                                                         "geometry": decoded,
                                                         "properties": {"color": color}
                                                        }]},
        style_function=lambda x: {"color": x['properties']['color']}
    )
    gj.add_child(folium.Tooltip(
        """<h4>Vehicle {vehicle}</h4>
        <b>Distance</b> {distance} m <br>
        <b>Duration</b> {duration} secs
        """.format(**route)
    ))
    gj.add_to(m)

folium.LayerControl().add_to(m)
#m


# In[486]:


# Only extract relevant fields from the response
extract_fields = ['distance', 'amount', 'duration']
data = [{key: route[key] for key in extract_fields} for route in result['routes']]

vehicles_df = pd.DataFrame(data)
vehicles_df.index.name = 'vehicle'
vehicles_df


# In[487]:


# Create a list to display the schedule for all vehicles
stations = list()
for route in result['routes']:
    vehicle = list()
    for step in route["steps"]:
        vehicle.append(
            [
                step.get("job", "Depot"),  # Station ID
                step["arrival"],  # Arrival time
                step["arrival"] + step.get("service", 0),  # Departure time

            ]
        )
    stations.append(vehicle)


# Create an array to hold lists of coordinates for each vehicle
vehicles = [[] for i in range(0, numOfVehicles)]

# Create an array to hold each bus route to be used for getting route directions
bus_routes = [[] for i in range(0, numOfVehicles)]

# Iterate through each bus route
# Extract driver instructions and write them to a text file for each route
for i in range(numOfVehicles):
    for route in result['routes']:
        #print('Vehicle: ' + str(route['vehicle']))
        for step in route['steps']:
            if(route['vehicle'] == i):
                #print(step['location'])
                vehicles[i].append(step['location'])

    request_params_bus = {'coordinates': vehicles[i],
                'format_out': 'geojson',
                'profile': 'driving-car',
                'preference': 'shortest',
                'instructions': 'True',}
    bus_routes[i] = ors_client.directions(**request_params_bus)

    f= open("directions/route_" + str(i) + "_instructions.txt","w+")
    for l in range(len(bus_routes[i]['features'])):
        for j in range(len(bus_routes[i]['features'][l]['properties']['segments'])):
            for k in range(len(bus_routes[i]['features'][l]['properties']['segments'][j]['steps'])):
                f.write(str(bus_routes[i]['features'][l]['properties']['segments'][j]['steps'][k]['instruction']) + "\n")
    f.close()


# In[488]:


df_stations_0 = pd.DataFrame(stations[0], columns=["Station ID", "Arrival", "Departure"])
df_stations_0['Arrival'] = pd.to_datetime(df_stations_0['Arrival'], unit='s')
df_stations_0['Departure'] = pd.to_datetime(df_stations_0['Departure'], unit='s')
df_stations_0


# In[489]:


df_stations_1 = pd.DataFrame(stations[1], columns=["Station ID", "Arrival", "Departure"])
df_stations_1['Arrival'] = pd.to_datetime(df_stations_1['Arrival'], unit='s')
df_stations_1['Departure'] = pd.to_datetime(df_stations_1['Departure'], unit='s')
df_stations_1


# In[490]:


df_stations_2 = pd.DataFrame(stations[2], columns=["Station ID", "Arrival", "Departure"])
df_stations_2['Arrival'] = pd.to_datetime(df_stations_2['Arrival'], unit='s')
df_stations_2['Departure'] = pd.to_datetime(df_stations_2['Departure'], unit='s')
df_stations_2


# In[491]:


m
m.save(outfile= "templates/map.html")


# In[492]:


print("There will be " + str(numOfVehicles) + " vehicles delivering " + str(numOfPoints) + " students with a max of " + str(maxStudentsPerVehicle) + " students per vehicle.")

if numOfPoints != sum(vehicles_df.amount.sum()):
    print("Not all kids were picked up! \n")
    print('Number of locations:  %d' % numOfPoints)
    print('Number visited: %d' % sum(vehicles_df.amount.sum()))
else:
    print('All kids were picked up.')


# In[ ]:
