## Simulater for testing spawn algorithms of monsters
### How to use:
start faster.bat and pythonServer.bat
load a map bevore walking
### commands:
- "updateMap" downloads mapData from mapzen and loads it
- "route x" walk route x (names in routes.json)
- "loadLocalMap" loads last downloaded map
- "walk lat,lng,x" walks to lat,lng in x steps
- "[zoom,lat,lng...] x" sets variable to x 

### toDo List
- [x] contact mapzen api
- [x] show a map
- [ ] contact spawn Algorithm
- [ ] get weather data
- [ ] show monster on the map
- [ ] selection of paths
- [ ] analysis of paths


encounters.json from https://github.com/pkmn-world/test-spawner