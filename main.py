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


def displayMap(game):
    for x in range(len(game.maps[game.player.mapId])):
        for y in range(len(game.maps[game.player.mapId][0])):
            print(game.maps[game.player.mapId][x][y], end=" ")
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


item1 = Item(1, "testItem", "weapon", 1, 10, 1, 0)
print(item1.value, item1.name, item1.type, item1.damage, item1.durability, item1.quantity, item1.protection)

monster1 = Monster(99, "testMonster", 10, 3, 0, 5, "testImagePath")
print(monster1.id, monster1.name, monster1.hp, monster1.att, monster1.res, monster1.xp, monster1.imagePath)

player = Player(0, 1, 100, [[1]], 4, 4, 0, 150, 100)

game = Game(initAllMaps(10, 10), [], player, [], [], [])

displayMap(game)
