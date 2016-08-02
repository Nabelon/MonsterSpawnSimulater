import requests
import re
import struct
import json
import argparse
import pokemon_pb2
import time

from google.protobuf.internal import encoder

from datetime import datetime
from geopy.geocoders import GoogleV3
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
from s2sphere import *

def encode(cellid):
    output = []
    encoder._VarintEncoder()(output.append, cellid)
    return ''.join(output)

def getNeighbors():
    origin = CellId.from_lat_lng(LatLng.from_degrees(FLOAT_LAT, FLOAT_LONG)).parent(15)
    walk = [origin.id()]
    # 10 before and 10 after
    next = origin.next()
    prev = origin.prev()
    for i in range(10):
        walk.append(prev.id())
        walk.append(next.id())
        next = next.next()
        prev = prev.prev()
    return walk



API_URL = 'https://pgorelease.nianticlabs.com/plfe/rpc'
LOGIN_URL = 'https://sso.pokemon.com/sso/login?service=https%3A%2F%2Fsso.pokemon.com%2Fsso%2Foauth2.0%2FcallbackAuthorize'
LOGIN_OAUTH = 'https://sso.pokemon.com/sso/oauth2.0/accessToken'

SESSION = requests.session()
SESSION.headers.update({'User-Agent': 'Niantic App'})
SESSION.verify = False

DEBUG = False
COORDS_LATITUDE = 0
COORDS_LONGITUDE = 0
COORDS_ALTITUDE = 0
FLOAT_LAT = 0
FLOAT_LONG = 0
deflat, deflng = 0, 0
default_step = 0.001

NUM_STEPS = 5
DATA_FILE = 'data.json'
DATA = []

def f2i(float):
  return struct.unpack('<Q', struct.pack('<d', float))[0]

def f2h(float):
  return hex(struct.unpack('<Q', struct.pack('<d', float))[0])

def h2f(hex):
  return struct.unpack('<d', struct.pack('<Q', int(hex,16)))[0]

def prune():
    # prune despawned pokemon
    cur_time = int(time.time())
    for i, poke in reversed(list(enumerate(DATA))):
        poke['timeleft'] = poke['timeleft'] - (cur_time - poke['timestamp'])
        poke['timestamp'] = cur_time
        if poke['timeleft'] <= 0:
            DATA.pop(i)

def write_data_to_file():
    prune()

    with open(DATA_FILE, 'w') as f:
        json.dump(DATA, f, indent=2)

def add_pokemon(pokeId, name, lat, lng, timestamp, timeleft):
    DATA.append({
        'id': pokeId,
        'name': name,
        'lat': lat,
        'lng': lng,
        'timestamp': timestamp,
        'timeleft': timeleft
    });

def set_location(location_name):
    geolocator = GoogleV3()
    loc = geolocator.geocode(location_name)

    print('[!] Your given location: {}'.format(loc.address.encode('utf-8')))
    print('[!] lat/long/alt: {} {} {}'.format(loc.latitude, loc.longitude, loc.altitude))

    global deflat
    global deflng
    deflat, deflng = loc.latitude, loc.longitude

    set_location_coords(loc.latitude, loc.longitude, loc.altitude)


def scan(api_endpoint, access_token, response, origin, pokemons):
def main():
        x = 42.248270
        y = -87.818040
    while True:
        simulate(x, y)


if __name__ == '__main__':
    main()
