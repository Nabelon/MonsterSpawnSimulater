import requests
import re
import struct
import json
import argparse
import time
import re
import os
import math
import matplotlib.path as mplPath
import numpy as np
import random
from shapely.geometry import shape, Point
from urllib2 import Request, urlopen, URLError

from datetime import datetime
path = ""
DATA_FILE = 'data.json'
DATA = []
MAPDATA_FILE = "mapdata.json"
mapData = []
polygonsGeo = []
polygonsLanduse = []
encounters = {}
monsters = {}
routes = {}
def getSpawn(landuse,iTime,weather):
    if iTime in range(0,5) or iTime in range(22,24):
        time = "night"
    elif iTime in range(5,11):
        time = "morning"
    elif iTime in range(11,17):
        time = "day"
    else:
        time = "evening"
    spawns = encounters[landuse][time][weather]
    return random.choice(spawns)
    
def deg2num(lat_deg, lon_deg, zoom):
  lat_rad = math.radians(lat_deg)
  n = 2.0 ** zoom
  xtile = int((lon_deg + 180.0) / 360.0 * n)
  ytile = int((1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad))) / math.pi) / 2.0 * n)
  return (xtile, ytile)
def createPolygons(polys):
    features = json.load(polys)["features"]
    for i in range(0,len(features)):
        polygonsGeo.append(features[i]["geometry"])
        polygonsLanduse.append(features[i]["properties"]["kind"])
def walk(x2,y2,steps,locationData):
    x1 = locationData["lng"]
    y1 = locationData["lat"]
    distance = math.sqrt(pow(x1-x2,2)+pow(y1-y2,2))
    stepDistance = distance / steps
    xAdd = ((x2-x1)/(math.fabs(y1-y2)+math.fabs(x1-x2))) * stepDistance
    yAdd = ((y2-y1)/(math.fabs(y1-y2)+math.fabs(x1-x2))) * stepDistance
    currX = x1;
    currY = y1;
    encounters = []
    for i in range(0,steps):
        point = Point(currX,currY)
        print "point: %s,%s" % (str(point.y),str(point.x)) 
        landuse = ''
        spawns = []
        for i in range(0,len(polygonsGeo)):
            try:
                polygon = shape(polygonsGeo[i])
                if polygon.contains(point):
                    print 'Found containing polygon:', polygonsLanduse[i]
                    landuse += str(polygonsLanduse[i])+", "
                    spawns.append(getSpawn(polygonsLanduse[i],locationData["time"],locationData["weather"]))               
            except Exception, e:
                print 'Got an polygon error code:', e
        mapData.append({
                    'lat': currY,
                    'lng': currX,
                    'landuse': landuse})
        if len(spawns) > 0:
            spawn =  random.choice(spawns)
            print monsters[spawn]["name"]
            encounters.append(spawn)
        currX += xAdd
        currY += yAdd
            
    locationData["lat"] = y2
    locationData["lng"] = x2
    with open(MAPDATA_FILE, 'w') as f:
            json.dump(mapData, f, indent=2)
    return encounters
def updateMap(locationData):
    tiles = deg2num(locationData["lat"],locationData["lng"],locationData["zoom"])
    request = Request('http://vector.mapzen.com/osm/landuse/' + str(locationData["zoom"]) + '/' +str(tiles[0])+'/'+str(tiles[1])+'.json?api_key=vector-tiles-vx5RUiN') 
    try:
        response = urlopen(request)
        with open(DATA_FILE, 'w') as f:
           json.dump(json.load(response), f, indent=2)
        createPolygons(open("data.json"))
        print "map updated"
    except URLError, e:
        print 'Got an error code:', e
def route(locationData,name):
    if name not in routes.keys():
        print "Route not found"
        return
    locationData["lat"] = routes[name][0][0]
    locationData["lng"] = routes[name][0][1]
    updateMap(locationData)
    for i in range(1, len(routes[name])):
        walk(routes[name][i][1],routes[name][i][0],routes[name][i][2],locationData)
def main():
    global path, encounters, monsters, routes
    full_path = os.path.realpath(__file__)
    (path, filename) = os.path.split(full_path)
    encounters = json.load(
        open(path + '/encounters.json'))
    monsters = json.load(
        open(path + '/pokemon.json'))
    routes = json.load(
        open(path + '/routes.json'))
    locationData = {"lat": 42.252306,
        "lng": -87.820463,
        "time": "12:00:00",
        "weather": "sun",
        "landuse": "aerodrome",
        "zoom": 9}
    while True:
        userInput = raw_input("What to do?")
        if userInput == "start":
            simulate(locationData)
        else:
                data = re.split(" ",userInput)[0]
                if(data == "time" or data == "weather"):
                    locationData[data] =  re.split(" ",userInput)[1]
                elif data == "walk":
                    strValues = re.split(" ",userInput)[1]
                    walk(locationData["lng"],locationData["lat"],float(re.split(",",strValues)[1]),float(re.split(",",strValues)[0]),int(re.split(",",strValues)[2]))
                elif data == "example":
                    walk(-87.8662583951751,42.26833512994285,locationData["zoom"],locationData)
                elif data == "route":
                    route(locationData, re.split(" ",userInput)[1])
                elif data == "updateMap":
                    updateMap(locationData)
                elif data == "loadLocalMap":
                    print "loadingMap..."
                    createPolygons(open("data.json"))
                elif data == "zoom":
                    locationData[data] = int(re.split(" ",userInput)[1])
                else:
                    value = float(re.split(" ",userInput)[1])
                    if data in locationData.keys():
                        locationData[data] = value
                

if __name__ == '__main__':
    main()
