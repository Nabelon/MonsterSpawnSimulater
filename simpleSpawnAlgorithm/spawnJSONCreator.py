import struct
import json

def main():
    monsters = json.load(open("pokemonSpawnData.json"))
    spawnPlaces = json.load(open("encounters.json"))  
    print "deleting old data"
    for i in spawnPlaces.keys():
        for j in ["morning","day","evening","night"]:
            for p in ["cloud","sun","rain"]:
                spawnPlaces[i][j][p] = []
    print "adding pokes"
    for i in range(1,27):
        print "next: %d" % i
        if str(i) in monsters.keys(): #pokedex is not full :/
            monster = monsters[str(i)]
            for q in monster["landuse"]:
                for j in monster["time"]:
                    for p in monster["weather"]:
                        spawnPlaces[q][j][p].append(str(i))
    print "adding 66"
    for i in spawnPlaces.keys():
        for j in ["morning","day","evening","night"]:
            for p in ["cloud","sun","rain"]:
                if len(spawnPlaces[i][j][p]) == 0:
                    spawnPlaces[i][j][p].append("66")
    with open("encounters.json", 'w') as f:
            json.dump(spawnPlaces, f, indent=2)
if __name__ == '__main__':
    main()
