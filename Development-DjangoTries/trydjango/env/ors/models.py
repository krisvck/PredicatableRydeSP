from django.conf import settings
from django.db import models
from django.utils import timezone

# Create your models here.

import folium
from folium.plugins import BeautifyIcon
import shapely
import math
import pandas as pd
import openrouteservice as ors
from IPython.core.interactiveshell import InteractiveShell


# Define number of vehicles to use
numOfVehicles = 3

# Define how long (in seconds) each bus stops at each location
numOfSecondsPerStop = 15

m = folium.Map(location=[43.640565, -116.339269], tiles='cartodbpositron', zoom_start=13)    

# Next load the delivery locations from CSV file at ../resources/data/idai_health_sites.csv
# ID, Lat, Lon, Open_From, Open_To, Needed_Amount
deliveries_data = pd.read_csv(
    'data/demo_data.csv',
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

# Divide up students per vehicle
# Number of locations to visit / number of vehicles
maxStudentsPerVehicle = math.ceil(numOfPoints/numOfVehicles)

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




