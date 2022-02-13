import random, copy, pygame, sys, os, time


class Item:
    def __init__(self, name, type, damage, durability, quantity, protection):
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
    def __init__(self, currentExp, level, currentHp, posX, posY, mapId, hpEvolution, xpEvolution, inventory=None):
        if inventory is None:
            self.inventory = []
        else:
            self.inventory = inventory
        self.currentExp = currentExp
        self.level = level
        self.currentHp = currentHp
        self.posX = posX
        self.posY = posY
        self.mapId = mapId
        self.hpEvolution = hpEvolution
        self.xpEvolution = xpEvolution

    def newGameInventory(self, itemDict):
        self.inventory.append(copy.deepcopy(itemDict[1]))
        self.inventory.append(copy.deepcopy(itemDict[2]))
        self.inventory.append(copy.deepcopy(itemDict[3]))
        self.inventory.append(copy.deepcopy(itemDict[4]))


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
        durability = [10, 10, 10, 10, 1, 1, 1, 10, 8, 5, 1, 10, 10, 10, 1, 1, 1, 1, 10, 8, 5, 1, 10, 10, 10, 1, 1,
                      1, 1, 10, 8, 5, 1, 1]
        protection = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 10, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 20, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                      0, 40, 0]

        for i in range(len(names)):
            itemsDict[i + 1] = Item(names[i], types[i], damages[i], durability[i], 0, protection[i])
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
                     "../resources/textures/monstres/armand_jesus.png", ]

        for i in range(len(names)):
            monstersDict[i + 12] = Monster(names[i], hp[i], att[i], defense[i], xp[i], imagePath[i])
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

    def move(self, posX, posY):
        if 12 > self.maps[self.player.mapId][posX][posY] > 2:
            print("collecte ressource")
        elif self.maps[self.player.mapId][posX][posY] == 2:
            print("PNJ")
        elif self.maps[self.player.mapId][posX][posY] == -1:
            print("Mur")
        elif 22 > self.maps[self.player.mapId][posX][posY] > 11:
            print("monster")
        elif self.maps[self.player.mapId][posX][posY] == -2 or self.maps[self.player.mapId][posX][posY] == -3:
            print("portail")
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




pygame.init()
black = 0, 0, 0


player = Player(0, 1, 100, 4, 4, 0, 150, 100)

game = Game(fillAllMaps(initAllMaps(10, 10)), player, [])

game.player.newGameInventory(game.itemsDict)
size = width, height = len(game.maps[game.player.mapId]) * 32, len(game.maps[game.player.mapId][0]) * 32
screen = pygame.display.set_mode(size)

game.displayMap()
game.fillRender(screen)
game.renderMap(screen)
while 1:
    for event in pygame.event.get():
        match event.type:
            case pygame.QUIT:
                sys.exit()
            case pygame.KEYUP:
                match event.key:
                    case pygame.K_ESCAPE:
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
    pygame.display.flip()
