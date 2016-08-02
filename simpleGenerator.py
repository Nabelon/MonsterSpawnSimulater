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
def simulate(data):
    print data    
    ftr = [3600,60,1]
    time = sum([a*b for a,b in zip(ftr, map(int,data["time"].split(':')))])
    monsters = json.load(
        open(path + '/monsters.json'))
    for i in range(1,len(monsters)):
        monster = monsters[str(i)]
        spawnChanceAbs = 0
        mTime = sum([a*b for a,b in zip(ftr, map(int,monster["spawnTime"]["time"].split(':')))])
        spawnChanceAbs += 100 - min(100,math.pow(pow((max(abs(mTime - time),3600)/3600.0),2.0),(monster["spawnTime"]["timeImportance"]/30.0))-1)
        spawnChanceAbs += 100 - min(100,math.pow(pow((max(abs(monster["spawnWeather"]["temperature"] - data["temperature"]),3.0)/3.0),3.0),(monster["spawnWeather"]["temperatureImportance"]/30.0))-1)
        print pow((max(abs(monster["spawnWeather"]["temperature"] - data["temperature"]),3.0)/3.0),2.0)
        print math.pow(pow((max(abs(monster["spawnWeather"]["temperature"] - data["temperature"]),3.0)/3.0),3),(monster["spawnWeather"]["temperatureImportance"]/30.0))
        print spawnChanceAbs
        print "-------------------------"
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
def walk(x1,y1,x2,y2,steps):
    distance = math.sqrt(pow(x1-x2,2)+pow(y1-y2,2))
    stepDistance = distance / steps
    xAdd = ((x2-x1)/(math.fabs(y1-y2)+math.fabs(x1-x2))) * stepDistance
    yAdd = ((y2-y1)/(math.fabs(y1-y2)+math.fabs(x1-x2))) * stepDistance
    currX = x1;
    currY = y1;
    while (distance > 0.0):
        point = Point(currX,currY)
        print "point: %s,%s" % (str(point.x),str(point.y)) 
        landuse = ''
        for i in range(0,len(polygonsGeo)):
            polygon = shape(polygonsGeo[i])
            if polygon.contains(point):
                print 'Found containing polygon:', polygonsLanduse[i]
                landuse += str(polygonsLanduse[i])
        mapData.append({
            'lat': currY,
            'lng': currX,
            'landuse': landuse})
        currX += xAdd
        currY += yAdd
        distance -= stepDistance
    with open(MAPDATA_FILE, 'w') as f:
            json.dump(mapData, f, indent=2)
    point = Point(currX,currY)
    print "point: %s,%s" % (str(point.x),str(point.y))  
    for i in range(0,len(polygonsGeo)):
            polygon = shape(polygonsGeo[i])
            if polygon.contains(point):
                print 'Found containing polygon:', polygonsLanduse[i]
def main():
    global path
    full_path = os.path.realpath(__file__)
    (path, filename) = os.path.split(full_path)
    locationData = {"lat": 42.252306,
        "lng": -87.820463,
        "height": 100.0,
        "time": "12:00:00",
        "temperature": 20.0,
        "rain": 0.0,
        "sun": 50.0,
        "forest": 20.0,
        "town": 80.0,
        "water": 1.0}
    zoom = 9
    #tiles = deg2num(locationData["lat"],locationData["lng"],zoom)
    #request = Request('http://vector.mapzen.com/osm/landuse/' + str(zoom) + '/' +str(tiles[0])+'/'+str(tiles[1])+'.json?api_key=vector-tiles-vx5RUiN')
    
    try:
        #response = urlopen(request)
        #with open(DATA_FILE, 'w') as f:
         #   json.dump(json.load(response), f, indent=2)
        createPolygons(open("data.json"))
        points = [Point(locationData["lng"],locationData["lat"]),Point(-87.88130,42.2750),Point(-87.88130,42.2749),Point(-87.88125,42.2750)]
        for point in points:
            print "point: %s,%s" % (str(point.x),str(point.y))
            for i in range(0,len(polygonsGeo)):
                polygon = shape(polygonsGeo[i])
                if polygon.contains(point):
                    print 'Found containing polygon:', polygonsLanduse[i]
        walk(locationData["lng"],locationData["lat"],-87.88530,42.2750,10)
            
    except URLError, e:
        print 'No kittez. Got an error code:', e
    
    while True:
        userInput = raw_input("What to do?")
        if userInput == "start":
            simulate(locationData)
        else:
            if re.match("[a-z]* [0-9.]",userInput):
                data = re.split(" ",userInput)[0]
                if(data == "time"):
                    locationData["time"] =  re.split(" ",userInput)[1]
                elif data == "walk":
                    print "hi"
                else:
                    value = float(re.split(" ",userInput)[1])
                    if data in locationData.keys():
                        locationData[data] = value
                

if __name__ == '__main__':
    main()
