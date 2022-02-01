import random


class Item():
    def __init__(self, value, name, type, damage, durability, quantity, protection):
        self.value = value
        self.name = name
        self.type = type
        self.damage = damage
        self.durability = durability
        self.quantity = quantity
        self.protection = protection


class Monster():
    def __init__(self, id, name, hp, att, res, xp, imagePath):
        self.id = id
        self.name = name
        self.hp = hp
        self.att = att
        self.res = res
        self.xp = xp
        self.imagePath = imagePath


class Player():
    def __init__(self, currentExp, level, currentHp, inventory, posX, posY, mapId, hpEvolution, xpEvolution):
        self.currentExp = currentExp
        self.level = level
        self.currentHp = currentHp
        self.inventory = inventory
        self.posX = posX
        self.posY = posY
        self.mapId = mapId
        self.hpEvolution = hpEvolution
        self.xpEvolution = xpEvolution


class Craft():
    def __init__(self, id, itemId, idResource1, nbResource1, idResource2, nbResource2, zone):
        self.id = id
        self.itemId = itemId
        self.idResource1 = idResource1
        self.nbResource1 = nbResource1
        self.idResource2 = idResource2
        self.nbResource2 = nbResource2
        self.zone = zone


class Game():
    def __init__(self, maps, itemList, player, craftList, monsterList, storage):
        self.maps = maps
        self.itemList = itemList
        self.player = player
        self.craftList = craftList
        self.monsterList = monsterList
        self.storage = storage

    def displayMap(self):
        for x in range(len(self.maps[game.player.mapId])):
            for y in range(len(self.maps[game.player.mapId][0])):
                print(self.maps[game.player.mapId][x][y], end=" ")
            print("")


def initMap(height, width):
    map = [[0 for x in range(width)] for y in range(height)]
    return map


def initAllMaps(height, width):
    maps = []
    for i in range(3):
        for j in range(3):
            maps.append(initMap(height, width))
        height += 2
        width += 2
    return maps


def fillBaseMap(map, basemap):
    for i in range(len(map)):
        for j in range(len(map[0])):
            if map[i][j] != 0:
                basemap[i][j] = map[i][j]


def placeThings(map, id, proportion, min):
    cptThings = 0
    while cptThings < (min + proportion * (len(map) * len(map[0]))):
        randomPosX = random.randint(0, len(map) - 1)
        randomPosY = random.randint(0, len(map[0]) - 1)
        if map[randomPosX][randomPosY] == 0:
            map[randomPosX][randomPosY] = id
            cptThings += 1
    return map


def placeMonsters(map, zone):
    cptMonsters = 0
    while cptMonsters < (10 + 0.05 * (len(map) * len(map[0]))):
        randomPosX = random.randint(0, len(map) - 1)
        randomPosY = random.randint(0, len(map[0]) - 1)
        if map[randomPosX][randomPosY] == 0:
            map[randomPosX][randomPosY] = random.randint(0, 2) % 3 + 9 + (zone * 3)
            cptMonsters += 1
    return map


def fillMap(map, zone):
    print("test")
    if zone == 3:
        map = placeThings(map, 99, 0, 1)
        map = placeThings(map, -3, 0, 1)
    elif zone == 2:
        map = placeThings(map, -2, 0, 1)
        map = placeThings(map, -3, 0, 1)
    else:
        map = placeThings(map, -2, 0, 1)

    map = placeThings(map, 2, 0, 1)
    map = placeThings(map, 3 + (zone * 3), 0.1, 3)
    map = placeThings(map, 4 + (zone * 3), 0.1, 3)
    map = placeThings(map, 5 + (zone * 3), 0.1, 3)
    map = placeThings(map, -1, 0.1, 3)
    map = placeMonsters(map, zone)
    return map


def fillAllMaps(maps):
    maps[0][4][4] = 1
    for i in range(0, 3):
        maps[0 + i * 3] = fillMap(maps[0 + i * 3], i)
        fillBaseMap(maps[0 + i * 3], maps[2 + i * 3])
    return maps


item1 = Item(1, "testItem", "weapon", 1, 10, 1, 0)
print(item1.value, item1.name, item1.type, item1.damage, item1.durability, item1.quantity, item1.protection)

monster1 = Monster(99, "testMonster", 10, 3, 0, 5, "testImagePath")
print(monster1.id, monster1.name, monster1.hp, monster1.att, monster1.res, monster1.xp, monster1.imagePath)

player = Player(0, 1, 100, [[1]], 4, 4, 0, 150, 100)

game = Game(fillAllMaps(initAllMaps(10, 10)), [], player, [], [], [])

game.displayMap()
