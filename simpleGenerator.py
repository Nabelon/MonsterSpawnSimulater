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
MONSTER_SPAWN_DATA_FILE = "\simpleSpawnAlgorithm\pokemonSpawnData.json"
monsterSpawnData = {}
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
def getMonster(landuse,iTime,weather):
    if iTime in range(0,5) or iTime in range(22,24):
        time = "night"
    elif iTime in range(5,11):
        time = "morning"
    elif iTime in range(11,17):
        time = "day"
    else:
        time = "evening"
    if len(landuse) == 0:
        return "16"
    encountersL = []
    #get encounters
    for i in landuse:
        print i
        for j in encounters[i][time][weather]:
            encountersL.append(j)
    #include rarity
    lenEncountersL = len(encountersL)
    for i in range(0,lenEncountersL):
        for j in range(1,monsterSpawnData[encountersL[i]]["rarity"]):
            encountersL.append(encountersL[i])
    return random.choice(encountersL)
def walk(x2,y2,steps,locationData):
    #should not have used x and y
    x1 = locationData["lng"]
    y1 = locationData["lat"]
    distance = math.sqrt(pow(x1-x2,2)+pow(y1-y2,2))
    stepDistance = distance / steps
    xAdd = (x2-x1) / steps
    yAdd = (y2-y1) / steps
    currX = x1
    currY = y1
    encounters = []
    for i in range(0,steps):
        currX = x1 + xAdd * i
        currY = y1 + yAdd * i
        point = Point(currX,currY)
        print "point: %s,%s" % (str(point.y),str(point.x)) 
        landuse = []
        spawns = []
        for i in range(0,len(polygonsGeo)):
            try:
                polygon = shape(polygonsGeo[i])
                if polygon.contains(point) and polygonsLanduse[i] not in landuse:
                    landuse.append(polygonsLanduse[i])             
            except Exception, e: #throws Topology Exceptions, dunno how to handle it
                i = i 
        print "Landuse: %s" % landuse
        spawn =  getMonster(landuse,locationData["time"],locationData["weather"])
        print monsters[spawn]["name"]
        encounters.append(spawn)
        mapData.append({
            'lat': currY,
            'lng': currX,
            'landuse': str(landuse),
            'id': spawn,
            'name': monsters[spawn]["name"]})
    locationData["lat"] = y2
    locationData["lng"] = x2
    with open(MAPDATA_FILE, 'w') as f:
            json.dump(mapData, f, indent=2)
    return encounters
#downloads map from mapzen and overwries old
def updateMap(locationData):
    global polygonsGeo,polygonsLanduse
    polygonsGeo = []
    polygonsLanduse = []
    try:    #get Water with zoom 9
        tiles = deg2num(locationData["lat"],locationData["lng"],9)
        requestWater = Request('http://vector.mapzen.com/osm/water/' + "9" + '/' +str(tiles[0])+'/'+str(tiles[1])+'.json?api_key=vector-tiles-vx5RUiN') 
        responseWater = urlopen(requestWater)
        createPolygons(responseWater)
    except URLError, e:
        print 'Got an error code:', e
    for i in locationData["zoom"].split(","): #get Landuse with selected zooms
        tiles = deg2num(locationData["lat"],locationData["lng"],int(i))
        requestLanduse = Request('http://vector.mapzen.com/osm/landuse/' + i + '/' +str(tiles[0])+'/'+str(tiles[1])+'.json?api_key=vector-tiles-vx5RUiN') 
        try:
            responseLanduse = urlopen(requestLanduse)
            #if(len(locationData["zoom"].split(",")) == 1):      #makes a local copy if we only one zoom is used
            #    with open(DATA_FILE, 'w') as f:
            #        json.dump(json.load(response), f, indent=2)
            createPolygons(responseLanduse)
            print "map updated"
        except URLError, e:
            print 'Got an error code:', e

#walks the route and prints spawned monsters
def route(locationData,name):
    if name not in routes.keys():
        print "Route not found"
        return
    if isinstance(routes[name],basestring):
        route = json.load(open(path+routes[name]))
    else:
        route = routes[name]
    locationData["lat"] = route[0][0]
    locationData["lng"] = route[0][1]
    updateMap(locationData)
    spawns = {}
    for i in range(1, len(route)):
        spawnLoc = walk(route[i][1],route[i][0],route[i][2],locationData)
        for spawn in spawnLoc:
            if spawn in spawns:
                spawns[spawn] += 1
            else:
                spawns[spawn] = 1
    print "Results:"
    for id in spawns.keys():
        print "%s: %d" % (monsters[id]["name"],spawns[id]) 
def main():
    global path, encounters, monsters, routes,monsterSpawnData
    full_path = os.path.realpath(__file__)
    (path, filename) = os.path.split(full_path)
    encounters = json.load(
        open(path + 'simpleSpawnAlgorithm\encounters.json'))
    monsters = json.load(
        open(path + '/pokemon.json'))
    routes = json.load(
        open(path + '/routes.json'))
    monsterSpawnData = json.load(
        open(path + MONSTER_SPAWN_DATA_FILE))
    locationData = {"lat": 42.252306,
        "lng": -87.820463,
        "time": "12:00:00",
        "weather": "sun",
        "landuse": "aerodrome",
        "zoom": "9"}
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
                    locationData[data] = re.split(" ",userInput)[1]
                else:
                    value = float(re.split(" ",userInput)[1])
                    if data in locationData.keys():
                        locationData[data] = value
                

if __name__ == '__main__':
    main()
