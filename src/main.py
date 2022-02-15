import random, copy, pygame, sys, os, time, json


class Item:
    def __init__(self, id, name, type, damage, durability, quantity, protection):
        self.id = id
        self.name = name
        self.type = type
        self.damage = damage
        self.durability = durability
        self.quantity = quantity
        self.protection = protection


class Monster:
    def __init__(self, name, hp, att, res, xp, imagePath):
        self.name = name
        self.hp = hp
        self.att = att
        self.res = res
        self.xp = xp
        self.imagePath = imagePath


class Player:
    def __init__(self, currentExp, level, currentHp, posX, posY, mapId, inventory=None):
        if inventory is None:
            self.inventory = []
        else:
            for elt in inventory:
                self.inventory = []
                self.inventory.append(Item(*list(elt.values())))
        self.currentExp = currentExp
        self.level = level
        self.currentHp = currentHp
        self.posX = posX
        self.posY = posY
        self.mapId = mapId
        self.hpEvolution = level * 50
        self.xpEvolution = level * 50

    def newGameInventory(self, itemDict):
        self.inventory.append(copy.deepcopy(itemDict[1]))
        self.inventory.append(copy.deepcopy(itemDict[2]))
        self.inventory.append(copy.deepcopy(itemDict[3]))
        self.inventory.append(copy.deepcopy(itemDict[4]))

    def checkInInventoryAndUseTool(self, itemId):
        print("check tool")
        for i in range(len(self.inventory)):
            if self.inventory[i].id == itemId and self.inventory[i].durability >= 1:
                print("found")
                self.inventory[i].durability -= 1
                return 1
        return -1

    def appendCraftResource(self, itemDict, resourceId):
        result = 0
        for elt in self.inventory:
            if elt.id == resourceId and elt.quantity < 20:
                elt.quantity += 1
                result = 1
        if result == 0 and len(self.inventory) < 11:
            self.inventory.append(copy.deepcopy(itemDict[resourceId]))


class Craft:
    def __init__(self, itemId, idResource1, nbResource1, idResource2, nbResource2, zone):
        self.itemId = itemId
        self.idResource1 = idResource1
        self.nbResource1 = nbResource1
        self.idResource2 = idResource2
        self.nbResource2 = nbResource2
        self.zone = zone


class Game:
    def __init__(self, maps, player, storage):
        self.maps = maps
        self.itemsDict = self.initItemsDict()
        self.player = player
        self.craftsDict = self.initCraftsDict()
        self.monstersDict = self.initMonstersDict()
        self.storage = storage
        self.size = None
        self.screen = None

    def saveGame(self):
        pathToSave = os.path.abspath("resources/save.json")
        f = open(pathToSave, "w")
        jsonDict = {'maps': self.maps,
                    'storage': self.storage,
                    'player': {'currentExp': self.player.currentExp,
                               'level': self.player.level,
                               'currentHp': self.player.currentHp,
                               'posX': self.player.posX,
                               'posY': self.player.posY,
                               'mapId': self.player.mapId,
                               }
                    }
        jsonDict['player']['inventory'] = [elt.__dict__ for elt in self.player.inventory]
        jsonStr = json.dumps(jsonDict)
        f.write(jsonStr)
        f.close()

    def loadGame(self):
        pathToSave = os.path.abspath("resources/save.json")
        f = open(pathToSave, "r")
        data = json.load(f)
        self.maps = data['maps']
        self.storage = data['storage']
        playerList = list(data['player'].values())
        self.player = Player(*playerList)

    def displayMap(self):
        for x in range(len(self.maps[game.player.mapId])):
            for y in range(len(self.maps[game.player.mapId][0])):
                print(self.maps[game.player.mapId][x][y], sep="\t", end=" ")
            print("")

    @staticmethod
    def initItemsDict():
        itemsDict = {}
        names = ["Epee en bois", "Pioche en bois", "Serpe en bois", "Hache en bois", "Sapin", "Pierre",
                 "Herbe", "Epee en pierre", "Lance en pierre", "Marteau en pierre", "Plastron en pierre",
                 "Pioche en pierre", "Serpe en pierre", "Hache en pierre", "Potion de vie I", "Hetre", "Fer",
                 "Lavande", "Epee en fer", "Lance en fer", "Marteau en fer", "Plastron en fer",
                 "Pioche en fer", "Serpe en fer", "Hache en fer", "Potion de vie II", "Chene", "Diamant",
                 "Chanvre", "Epee en diamant", "Lance en diamant", "Marteau en diamant",
                 "Plastron en diamant",
                 "Potion de vie III"]

        types = ["Arme", "Outil", "Outil", "Outil", "Ressource de craft", "Ressource de craft",
                 "Ressource de craft", "Arme", "Arme", "Arme", "Armure",
                 "Outil", "Outil", "Outil", "Soin", "Ressource de craft", "Ressource de craft",
                 "Ressource de craft", "Arme", "Arme", "Arme", "Armure",
                 "Outil", "Outil", "Outil", "Soin", "Ressource de craft", "Ressource de craft",
                 "Ressource de craft", "Arme", "Arme", "Arme", "Armure",
                 "Soin"]

        damages = [1, 0, 0, 0, 0, 0, 0, 2, 3, 4, 0, 0, 0, 0, 0, 0, 0, 0, 5, 7, 10, 0, 0, 0, 0, 0, 0,
                   0, 0, 10, 15, 20, 0, 0]
        durability = [10, 10, 10, 10, 1, 1, 1, 15, 10, 8, 1, 15, 15, 15, 1, 1, 1, 1, 20, 15, 10, 1, 20, 20, 20, 1, 1,
                      1, 1, 25, 20, 15, 1, 1]
        protection = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 10, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 20, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                      0, 40, 0]

        for i in range(len(names)):
            itemsDict[i + 1] = Item(i + 1, names[i], types[i], damages[i], durability[i], 0, protection[i])
        return itemsDict

    @staticmethod
    def initMonstersDict():
        monstersDict = {}
        names = ["Sanglier", "Slime", "Emmanuel Macron", "Petit ours brun", "Flan", "Caribou",
                 "Pomme de terre vivante", "Sananes", "Ancien dragon", "Jesus"]

        hp = [5, 3, 7, 16, 2, 25, 7, 70, 60, 80]

        att = [5, 1, 4, 8, 35, 15, 3, 3, 60, 50]

        defense = [1, 0, 3, 6, 40, 15, 1, 2, 40, 20]

        xp = [5, 4, 8, 9, 60, 15, 20, 22, 60, 60]
        imagePath = ["../resources/textures/monstres/sanglier.png",
                     "../resources/textures/monstres/slime.png", "../resources/textures/monstres/macron.png",
                     "../resources/textures/monstres/petit_ours_brun.png",
                     "../resources/textures/monstres/flan.png", "../resources/textures/monstres/caribou.png",
                     "../resources/textures/monstres/glados.png",
                     "../resources/textures/monstres/sananes.png",
                     "../resources/textures/monstres/dragon.png",
                     "../resources/textures/monstres/armand_jesus.png"]

        for i in range(len(names) - 1):
            monstersDict[i + 12] = Monster(names[i], hp[i], att[i], defense[i], xp[i], imagePath[i])
        monstersDict[99] = Monster(names[-1], hp[-1], att[-1], defense[-1], xp[-1], imagePath[-1])
        return monstersDict

    @staticmethod
    def initCraftsDict():
        craftsDict = {}
        itemId = [1, 8, 19, 30, 9, 20, 31, 10, 21, 32, 11, 22, 33, 2, 12, 23, 4, 14, 25, 3, 13, 24, 15,
                  26, 34]

        idResource1 = [5, 5, 16, 27, 5, 16, 27, 5, 16, 27, 6, 17, 28, 5, 5, 16, 5, 5, 16, 5, 5, 16, 7,
                       18, 29]

        nbResource1 = [3, 2, 2, 2, 3, 3, 3, 2, 2, 2, 10, 12, 16, 3, 2, 2, 3, 2, 2, 3, 2, 2, 2, 2, 2]

        idResource2 = [0, 6, 17, 17, 6, 17, 28, 6, 17, 28, 0, 0, 0, 0, 6, 17, 0, 6, 17, 0, 6, 17, 0, 0,
                       0]

        nbResource2 = [0, 3, 4, 5, 4, 5, 6, 6, 7, 8, 0, 0, 0, 0, 3, 4, 0, 3, 4, 0, 3, 4, 0, 0, 0]

        zone = [6, 6, 5, 3, 6, 5, 3, 6, 5, 3, 6, 5, 3, 6, 6, 5, 6, 6, 5, 6, 6, 5, 6, 5, 3]

        for i in range(len(itemId)):
            craftsDict[i] = Craft(itemId[i], idResource1[i], nbResource1[i], idResource2[i], nbResource2, zone[i])
        return craftsDict

    def decrementTimers(self):
        for x in range(len(self.maps[self.player.mapId])):
            for y in range(len(self.maps[self.player.mapId][0])):
                if self.maps[self.player.mapId + 1][x][y] != 0:
                    if self.maps[self.player.mapId + 1][x][y] > 1:
                        self.maps[self.player.mapId + 1][x][y] -= 1
                    else:
                        if self.maps[self.player.mapId][x][y] != 1:
                            self.maps[self.player.mapId + 1][x][y] = 0
                            self.maps[self.player.mapId][x][y] = self.maps[self.player.mapId + 2][x][y]

    def findPortal(self, idPortal):
        for x in range(len(self.maps[self.player.mapId])):
            for y in range(len(self.maps[self.player.mapId][0])):
                if self.maps[self.player.mapId][x][y] == idPortal:
                    self.player.posX = x
                    self.player.posY = y
                    self.maps[self.player.mapId + 1][x][y] = 1
                    self.maps[self.player.mapId][x][y] = 1

    def passPortal(self, idPortal):
        global screen
        if self.player.mapId == 0 and self.player.level >= 3:
            self.maps[self.player.mapId][self.player.posX][self.player.posY] = 0
            self.player.mapId = 3
            self.findPortal(idPortal)
            # display text with pos
        elif self.player.mapId == 6:
            self.maps[self.player.mapId][self.player.posX][self.player.posY] = 0
            self.player.mapId = 3
            self.findPortal(idPortal)
        elif self.player.mapId == 3:
            if idPortal == -2:
                self.maps[self.player.mapId][self.player.posX][self.player.posY] = 0
                self.player.mapId = 0
                self.findPortal(idPortal)
            elif idPortal == -3 and self.player.level >= 7:
                self.maps[self.player.mapId][self.player.posX][self.player.posY] = 0
                self.player.mapId = 6
                self.findPortal(idPortal)
        else:
            return 0
        size = width, height = len(game.maps[game.player.mapId]) * 32, len(game.maps[game.player.mapId][0]) * 32
        screen = pygame.display.set_mode(size)

    def movePlayerAddTimer(self, posX, posY, timer):
        self.maps[self.player.mapId][self.player.posX][self.player.posY] = 0
        self.maps[self.player.mapId][posX][posY] = 1
        self.maps[self.player.mapId + 1][posX][posY] = timer
        self.player.posX = posX
        self.player.posY = posY

    def collectStone(self, value):
        match value:
            case 4:
                print("test Stone")
                if self.player.checkInInventoryAndUseTool(2) != -1 or self.player.checkInInventoryAndUseTool(
                        12) != -1 or self.player.checkInInventoryAndUseTool(23) != -1:
                    self.player.appendCraftResource(self.itemsDict, 6)
                    return 1
            case 7:
                if self.player.checkInInventoryAndUseTool(12) != -1 or self.player.checkInInventoryAndUseTool(23) != -1:
                    self.player.appendCraftResource(self.itemsDict, 17)
                    return 1
            case 10:
                if self.player.checkInInventoryAndUseTool(23) != -1:
                    self.player.appendCraftResource(self.itemsDict, 28)
                    return 1
        return -1

    def collectWood(self, value):
        match value:
            case 5:
                print("test wood")
                if self.player.checkInInventoryAndUseTool(4) != -1 or self.player.checkInInventoryAndUseTool(
                        14) != -1 or self.player.checkInInventoryAndUseTool(25) != -1:
                    self.player.appendCraftResource(self.itemsDict, 5)
                    return 1
            case 8:
                if self.player.checkInInventoryAndUseTool(14) != -1 or self.player.checkInInventoryAndUseTool(25) != -1:
                    self.player.appendCraftResource(self.itemsDict, 16)
                    return 1
            case 11:
                if self.player.checkInInventoryAndUseTool(25) != -1:
                    self.player.appendCraftResource(self.itemsDict, 27)
                    return 1
        return -1

    def collectPlant(self, value):
        match value:
            case 3:
                print("test plant")
                if self.player.checkInInventoryAndUseTool(3) != -1 or self.player.checkInInventoryAndUseTool(
                        13) != -1 or self.player.checkInInventoryAndUseTool(24) != -1:
                    self.player.appendCraftResource(self.itemsDict, 7)
                    return 1
            case 6:
                if self.player.checkInInventoryAndUseTool(13) != -1 or self.player.checkInInventoryAndUseTool(24) != -1:
                    self.player.appendCraftResource(self.itemsDict, 18)
                    return 1
            case 9:
                if self.player.checkInInventoryAndUseTool(24) != -1:
                    self.player.appendCraftResource(self.itemsDict, 29)
                    return 1
        return -1

    def collectResources(self, posX, posY):
        value = self.maps[self.player.mapId][posX][posY]
        if value == 3 or value == 6 or value == 9:
            if self.collectPlant(value) == 1:
                self.movePlayerAddTimer(posX, posY, 10)
        elif value == 4 or value == 7 or value == 10:
            if self.collectStone(value) == 1:
                self.movePlayerAddTimer(posX, posY, 10)
        elif value == 5 or value == 8 or value == 11:
            if self.collectWood(value) == 1:
                self.movePlayerAddTimer(posX, posY, 10)

    def move(self, posX, posY):
        if 12 > self.maps[self.player.mapId][posX][posY] > 2:
            self.collectResources(posX, posY)
            self.decrementTimers()
        elif self.maps[self.player.mapId][posX][posY] == 2:
            print("PNJ")
        elif self.maps[self.player.mapId][posX][posY] == -1:
            print("Mur")
        elif 22 > self.maps[self.player.mapId][posX][posY] > 11:
            print("monster")
        elif self.maps[self.player.mapId][posX][posY] == -2 or self.maps[self.player.mapId][posX][posY] == -3:
            self.passPortal(self.maps[self.player.mapId][posX][posY])
        else:
            self.maps[self.player.mapId][posX][posY] = 1
            self.maps[self.player.mapId][self.player.posX][self.player.posY] = 0
            self.player.posX, self.player.posY = posX, posY

    def checkCanMove(self, choice):
        match choice:
            case 1:
                if self.player.posX != 0:
                    self.move(self.player.posX - 1, self.player.posY)
                else:
                    print("pas possible")
            case 2:
                if self.player.posY != len(self.maps[self.player.mapId][0]) - 1:
                    self.move(self.player.posX, self.player.posY + 1)
                else:
                    print("pas possible")
            case 3:
                if self.player.posX != len(self.maps[self.player.mapId]) - 1:
                    self.move(self.player.posX + 1, self.player.posY)
                else:
                    print("pas possible")
            case 4:
                if self.player.posY != 0:
                    self.move(self.player.posX, self.player.posY - 1)
                else:
                    print("pas possible")
        self.decrementTimers()

    def fillRender(self, screen):
        image = pygame.image.load("resources/textures/0.png")
        for x in range(len(self.maps[self.player.mapId])):
            for y in range(len(self.maps[self.player.mapId][0])):
                screen.blit(image, [x * 32, y * 32])

    def renderMap(self, screen):
        for x in range(len(self.maps[self.player.mapId])):
            for y in range(len(self.maps[self.player.mapId][0])):
                image = pygame.image.load("resources/textures/" + str(self.maps[self.player.mapId][x][y]) + ".png")
                screen.blit(image, [y * 32, x * 32])

    def gamePlay(self):
        size = width, height = len(game.maps[game.player.mapId]) * 32, len(game.maps[game.player.mapId][0]) * 32
        screen = pygame.display.set_mode(size)
        game.fillRender(screen)
        game.renderMap(screen)
        pygame.display.flip()
        playOn = 1
        while playOn:
            for event in pygame.event.get():
                match event.type:
                    case pygame.QUIT:
                        sys.exit()
                    case pygame.KEYUP:
                        match event.key:
                            case pygame.K_ESCAPE:
                                playOn = 0
                            case pygame.K_z:
                                game.checkCanMove(1)
                            case pygame.K_d:
                                game.checkCanMove(2)
                            case pygame.K_s:
                                game.checkCanMove(3)
                            case pygame.K_q:
                                game.checkCanMove(4)
                        game.fillRender(screen)
                        game.renderMap(screen)
                        pygame.display.flip()

    def turnMenu(self):
        self.size = width, height = 1280, 720
        self.screen = pygame.display.set_mode(self.size)
        image = pygame.image.load("resources/textures/fonds/TurnMenu.png")
        self.screen.blit(image, [0, 0])
        pygame.display.flip()
        menuOn = 1
        while menuOn:
            for event in pygame.event.get():
                match event.type:
                    case pygame.QUIT:
                        menuOn = 0
                    case pygame.KEYUP:
                        match event.key:
                            case pygame.K_ESCAPE:
                                sys.exit()
                            case pygame.K_1:
                                self.gamePlay()
                                self.size = width, height = 1280, 720
                                self.screen = pygame.display.set_mode(self.size)
                            case pygame.K_2:
                                self.saveGame()
                            case pygame.K_0:
                                menuOn = 0
                        self.screen.blit(image, [0, 0])
                        pygame.display.flip()

    def mainMenu(self):
        self.size = width, height = 1280, 720
        self.screen = pygame.display.set_mode(self.size)
        image = pygame.image.load("resources/textures/fonds/MainMenu.png")
        self.screen.blit(image, [0, 0])
        pygame.display.flip()
        while 1:
            for event in pygame.event.get():
                match event.type:
                    case pygame.QUIT:
                        sys.exit()
                    case pygame.KEYUP:
                        match event.key:
                            case pygame.K_ESCAPE:
                                sys.exit()
                            case pygame.K_1:
                                self.player.newGameInventory(self.itemsDict)
                                self.turnMenu()
                            case pygame.K_2:
                                self.loadGame()
                                self.turnMenu()
                            case pygame.K_0:
                                sys.exit()
                        self.screen.blit(image, [0, 0])
                        pygame.display.flip()


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


def placeThings(mapTemp, id, proportion, min):
    cptThings = 0
    while cptThings < (min + proportion * (len(mapTemp) * len(mapTemp[0]))):
        randomPosX = random.randint(0, len(mapTemp) - 1)
        randomPosY = random.randint(0, len(mapTemp[0]) - 1)
        if mapTemp[randomPosX][randomPosY] == 0:
            mapTemp[randomPosX][randomPosY] = id
            cptThings += 1
    return mapTemp


def placeMonsters(map, zone):
    cptMonsters = 0
    while cptMonsters < (10 + 0.05 * (len(map) * len(map[0]))):
        randomPosX = random.randint(0, len(map) - 1)
        randomPosY = random.randint(0, len(map[0]) - 1)
        if map[randomPosX][randomPosY] == 0:
            map[randomPosX][randomPosY] = random.randint(0, 2) % 3 + 12 + (zone * 3)
            cptMonsters += 1
    return map


def fillMap(map, zone):
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
    for i in range(0, 6, 3):
        maps[i] = fillMap(maps[i], int(i / 3))
        fillBaseMap(maps[i], maps[2 + i])
    return maps


pygame.init()

player = Player(0, 1, 100, 4, 4, 0)

game = Game(fillAllMaps(initAllMaps(10, 10)), player, [])

game.player.newGameInventory(game.itemsDict)

size = width, height = len(game.maps[game.player.mapId]) * 32, len(game.maps[game.player.mapId][0]) * 32
screen = pygame.display.set_mode(size)
game.size = size
game.screen = screen
game.player.level = 5

game.mainMenu()
"""
game.fillRender(screen)
game.renderMap(screen)
pygame.display.flip()
while 1:
    for event in pygame.event.get():
        match event.type:
            case pygame.QUIT:
                sys.exit()
            case pygame.KEYUP:
                match event.key:
                    case pygame.K_ESCAPE:
                        game.saveGame()
                        sys.exit()
                    case pygame.K_z:
                        game.checkCanMove(1)

                    case pygame.K_d:
                        game.checkCanMove(2)

                    case pygame.K_s:
                        game.checkCanMove(3)

                    case pygame.K_q:
                        game.checkCanMove(4)

                game.fillRender(screen)
                game.renderMap(screen)
                pygame.display.flip()"""
