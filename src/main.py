import copy
import json
import math
import os
import pygame
import random
import sys


class Item:
    def __init__(self, id, name, type, damage, durability, quantity, protection):
        self.id = id
        self.name = name
        self.type = type
        self.damage = damage
        self.durability = durability
        self.quantity = quantity
        self.protection = protection

    def __str__(self):
        return self.name + " " + str(self.quantity)


class Monster:
    def __init__(self, id, name, hp, att, res, xp, imagePath):
        self.id = id
        self.name = name
        self.hp = hp
        self.att = att
        self.res = res
        self.xp = xp
        self.imagePath = imagePath

    def __str__(self):
        return self.name + " hp : " + str(self.hp) + " att : " + str(self.att) + " def : " + str(self.res)


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
        self.xpEvolution = level * 50

    def __str__(self):
        return "Perso hp : " + str(self.currentHp) + " level : " + str(self.level) + " exp : " + str(self.currentExp)

    def newGameInventory(self, itemDict):
        self.inventory.append(copy.deepcopy(itemDict[1]))
        self.inventory.append(copy.deepcopy(itemDict[2]))
        self.inventory.append(copy.deepcopy(itemDict[3]))
        self.inventory.append(copy.deepcopy(itemDict[4]))
        self.inventory.append(copy.deepcopy(itemDict[15]))
        self.inventory[4].quantity = 10

    def checkInInventoryAndUseTool(self, itemId):
        for i in range(len(self.inventory)):
            if self.inventory[i].id == itemId and self.inventory[i].durability >= 1:
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

    def getValidWeapons(self):
        tab = []
        for i in range(len(self.inventory)):
            if self.inventory[i].type == "Arme":
                tab.append(i)
        return tab

    def getArmor(self):
        armor = 0
        for i in range(len(self.inventory)):
            if self.inventory[i].type == "Armure" and self.inventory[i].protection > armor:
                armor = self.inventory[i].protection
        return armor

    def repareItems(self, itemsDict):
        for elt in self.inventory:
            if elt.type == "Outil":
                elt.durability = itemsDict[elt.id].durability

    def checkQuantity(self, id, quantity):
        for elt in self.inventory:
            if elt.id == id:
                if elt.quantity >= quantity:
                    return 1
        return 0

    def removeItem(self, id, quantity):
        for i in range(0, len(self.inventory)):
            if self.inventory[i].id == id:
                self.inventory[i].quantity -= quantity
                if self.inventory[i].quantity == 0:
                    del self.inventory[i]
                return

    def appendInventory(self, itemDict, itemId, quantity):
        if itemDict[itemId].type == "Ressource de craft":
            for i in range(0, quantity):
                self.appendCraftResource(itemDict, itemId)
        elif len(self.inventory) < 11:
            if itemDict[itemId].type == "Soin":
                done = 0
                for elt in self.inventory:
                    if elt.name == itemDict[itemId].name:
                        elt.quantity += quantity
                if done == 0 and len(self.inventory) < 11:
                    self.inventory.append(copy.deepcopy(itemDict[itemId]))
                    self.inventory[-1].quantity = quantity
            else:
                while len(self.inventory) < 11 and quantity > 0:
                    self.inventory.append(copy.deepcopy(itemDict[itemId]))
                    quantity -= 1


class Craft:
    def __init__(self, itemId, idResource1, nbResource1, idResource2, nbResource2, zone):
        self.itemId = itemId
        self.idResource1 = idResource1
        self.nbResource1 = nbResource1
        self.idResource2 = idResource2
        self.nbResource2 = nbResource2
        self.zone = zone

    def __str__(self):
        if self.idResource2 == 0:
            return str(self.itemId.name + " : " + str(self.nbResource1) + " " + self.idResource1.name)
        else:
            return str(self.itemId.name + " : " + str(self.nbResource1) + " " + self.idResource1.name + str(
                self.nbResource2) + " " + self.idResource2.name)


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
        self.font = None
        self.text = None

    def saveGame(self):
        pathToSave = os.path.abspath(pathToResources + "/save.json")
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
        pathToSave = os.path.abspath(pathToResources + "/save.json")
        with open(pathToSave, "r") as f:
            try:
                data = json.load(f)
                self.maps = data['maps']
                self.storage = data['storage']
                playerList = list(data['player'].values())
                self.player = Player(*playerList)
                return 1
            except json.decoder.JSONDecodeError:
                return -1

    def displayMap(self):
        for x in range(len(self.maps[self.player.mapId])):
            for y in range(len(self.maps[self.player.mapId][0])):
                print(self.maps[self.player.mapId][x][y], sep="\t", end=" ")
            print("")

    @staticmethod
    def initItemsDict():
        itemsDict = {}
        names = ["Epee en bois", "Serpe en bois", "Pioche en bois", "Hache en bois", "Herbe", "Pierre",
                 "Sapin", "Epee en pierre", "Lance en pierre", "Marteau en pierre", "Plastron en pierre",
                 "Serpe en pierre", "Pioche en pierre", "Hache en pierre", "Potion de vie I", "Lavande", "Fer",
                 "Hetre", "Epee en fer", "Lance en fer", "Marteau en fer", "Plastron en fer",
                 "Serpe en fer", "Pioche en fer", "Hache en fer", "Potion de vie II", "Chanvre", "Diamant",
                 "Chene", "Epee en diamant", "Lance en diamant", "Marteau en diamant",
                 "Plastron en diamant", "Potion de vie III"]

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
            itemsDict[i + 1] = Item(i + 1, names[i], types[i], damages[i], durability[i], 1, protection[i])
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
        imagePath = [pathToResources + "/textures/monstres/sanglier.png",
                     pathToResources + "/textures/monstres/slime.png",
                     pathToResources + "/textures/monstres/macron.png",
                     pathToResources + "/textures/monstres/petit_ours_brun.png",
                     pathToResources + "/textures/monstres/flan.png",
                     pathToResources + "/textures/monstres/caribou.png",
                     pathToResources + "/textures/monstres/glados.png",
                     pathToResources + "/textures/monstres/sananes.png",
                     pathToResources + "/textures/monstres/dragon.png",
                     pathToResources + "/textures/monstres/armand_jesus.png"]

        for i in range(len(names) - 1):
            monstersDict[i + 12] = Monster(i + 12, names[i], hp[i], att[i], defense[i], xp[i], imagePath[i])
        monstersDict[99] = Monster(99, names[-1], hp[-1], att[-1], defense[-1], xp[-1], imagePath[-1])
        return monstersDict

    @staticmethod
    def initCraftsDict():
        craftsDict = {}
        itemId = [1, 8, 19, 30, 9, 20, 31, 10, 21, 32, 11, 22, 33, 3, 13, 24, 4, 14, 25, 2, 12, 23, 15,
                  26, 34]

        idResource1 = [7, 7, 18, 29, 7, 18, 29, 7, 18, 29, 6, 17, 28, 7, 7, 18, 7, 7, 18, 7, 7, 18, 5,
                       16, 27]

        nbResource1 = [3, 2, 2, 2, 3, 3, 3, 2, 2, 2, 10, 12, 16, 3, 2, 2, 3, 2, 2, 3, 2, 2, 2, 2, 2]

        idResource2 = [0, 6, 17, 17, 6, 17, 28, 6, 17, 28, 0, 0, 0, 0, 6, 17, 0, 6, 17, 0, 6, 17, 0, 0,
                       0]

        nbResource2 = [0, 3, 4, 5, 4, 5, 6, 6, 7, 8, 0, 0, 0, 0, 3, 4, 0, 3, 4, 0, 3, 4, 0, 0, 0]

        zone = [6, 6, 5, 3, 6, 5, 3, 6, 5, 3, 6, 5, 3, 6, 6, 5, 6, 6, 5, 6, 6, 5, 6, 5, 3]

        for i in range(len(itemId)):
            craftsDict[i] = Craft(itemId[i], idResource1[i], nbResource1[i], idResource2[i], nbResource2[i], zone[i])
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
            pygame.mixer.music.load(pathToResources + "/music/Zone_2.mp3")
        elif self.player.mapId == 6:
            self.maps[self.player.mapId][self.player.posX][self.player.posY] = 0
            self.player.mapId = 3
            self.findPortal(idPortal)
            pygame.mixer.music.load(pathToResources + "/music/Zone_2.mp3")
        elif self.player.mapId == 3:
            if idPortal == -2:
                self.maps[self.player.mapId][self.player.posX][self.player.posY] = 0
                self.player.mapId = 0
                self.findPortal(idPortal)
                pygame.mixer.music.load(pathToResources + "/music/Zone_1.mp3")
            elif idPortal == -3 and self.player.level >= 7:
                self.maps[self.player.mapId][self.player.posX][self.player.posY] = 0
                self.player.mapId = 6
                self.findPortal(idPortal)
                pygame.mixer.music.load(pathToResources + "/music/Zone_3.mp3")
        else:
            return 0
        self.zoneSetup()

    def movePlayerAddTimer(self, posX, posY, timer):
        self.maps[self.player.mapId][self.player.posX][self.player.posY] = 0
        self.maps[self.player.mapId][posX][posY] = 1
        self.maps[self.player.mapId + 1][posX][posY] = timer
        self.player.posX = posX
        self.player.posY = posY

    def collectResources(self, posX, posY):
        value = self.maps[self.player.mapId][posX][posY]
        if value < 6:
            if self.player.checkInInventoryAndUseTool(value - 1) != -1 or self.player.checkInInventoryAndUseTool(
                    value + 9) != -1 or self.player.checkInInventoryAndUseTool(value + 20) != -1:
                self.player.appendCraftResource(self.itemsDict, value + 2)
                self.movePlayerAddTimer(posX, posY, 10)
                self.text = self.itemsDict[value + 2].name + " ajouté dans l'inventaire"
        elif value < 9:
            if self.player.checkInInventoryAndUseTool(value + 6) != -1 or self.player.checkInInventoryAndUseTool(
                    value + 17) != -1:
                self.player.appendCraftResource(self.itemsDict, value + 10)
                self.movePlayerAddTimer(posX, posY, 10)
                self.text = self.itemsDict[value + 10].name + " ajouté dans l'inventaire"
        else:
            if self.player.checkInInventoryAndUseTool(value + 14) != -1:
                self.player.appendCraftResource(self.itemsDict, value + 18)
                self.movePlayerAddTimer(posX, posY, 10)
                self.text = self.itemsDict[value + 18].name + " ajouté dans l'inventaire"
        

    def move(self, posX, posY):
        if 12 > self.maps[self.player.mapId][posX][posY] > 2:
            self.collectResources(posX, posY)
            self.decrementTimers()
        elif self.maps[self.player.mapId][posX][posY] == 2:
            self.pnjMenu()
            self.zoneSetup()
        elif self.maps[self.player.mapId][posX][posY] == -1:
            print("Mur")
        elif 22 > self.maps[self.player.mapId][posX][posY] > 11 or self.maps[self.player.mapId][posX][posY] == 99:
            if self.battle(posX, posY) == -1:
                print("Pas d'arme")
            self.zoneSetup()
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
        image = pygame.image.load(pathToResources + "/textures/0.png")
        for x in range(len(self.maps[self.player.mapId])):
            for y in range(len(self.maps[self.player.mapId][0]) + 1):
                screen.blit(image, [x * 32, y * 32])

    def renderMap(self, screen):
        for x in range(len(self.maps[self.player.mapId])):
            for y in range(len(self.maps[self.player.mapId][0])):
                image = pygame.image.load(
                    pathToResources + "/textures/" + str(self.maps[self.player.mapId][x][y]) + ".png")
                screen.blit(image, [y * 32, x * 32])

    def attack(self, weapon, monster):
        monster.hp -= math.ceil(self.player.inventory[weapon].damage * (1 - monster.res / 100))
        if monster.hp <= 0:
            if self.player.currentExp + monster.xp >= self.player.xpEvolution:
                self.player.currentExp = 0
                self.player.level += 1
                self.player.currentHp = self.player.level * 50
                self.player.xpEvolution = self.player.level * 50
            else:
                self.player.currentExp = self.player.currentExp + monster.xp
            return 1

    def monsterAttack(self, monster, armor):
        self.player.currentHp -= math.ceil(monster.att * (1 - armor / 100))
        if self.player.currentHp <= 0:
            return -1

    def usePotion(self, pos):
        if self.player.inventory[pos].name == "Potion de vie I":
            self.player.currentHp += 30
        elif self.player.inventory[pos].name == "Potion de vie II":
            self.player.currentHp += 80
        elif self.player.inventory[pos].name == "Potion de vie III":
            self.player.currentHp += 200
        if self.player.currentHp > self.player.level * 50:
            self.player.currentHp = self.player.level * 50
        self.player.inventory[pos].quantity -= 1
        if self.player.inventory[pos].quantity == 0:
            self.player.inventory.pop(pos)

    def potionMenu(self):
        res = []
        for i in range(len(self.player.inventory)):
            if self.player.inventory[i].type == "Soin":
                res.append(i)
        if res is not None:
            image = pygame.image.load(pathToResources + "/textures/fonds/battle.jpg")
            self.screen.blit(image, [0, 0])
            for i in range(len(res)):
                self.font.render_to(self.screen, (100, 200 + 100 * i), str(i + 1) + str(self.player.inventory[res[i]]),
                                    (0, 0, 0))
            self.font.render_to(self.screen, (100, 600), "0 - Retour", (0, 0, 0))
            pygame.display.flip()
            while 1:
                for event in pygame.event.get():
                    match event.type:
                        case pygame.QUIT:
                            sys.exit()
                        case pygame.KEYUP:
                            match event.key:
                                case pygame.K_1:
                                    self.usePotion(res[0])
                                    return 1
                                case pygame.K_2:
                                    if len(res) > 1:
                                        self.usePotion(res[1])
                                        return 1
                                case pygame.K_3:
                                    if len(res) > 2:
                                        self.usePotion(res[2])
                                        return 1
                                case pygame.K_0:
                                    return 0

    def battleMenu(self, weapon, monster):
        if monster.id == 99:
            pygame.mixer.music.load(pathToResources + "/music/Boss.mp3")
        else:
            pygame.mixer.music.load(pathToResources + "/music/Battle.mp3")
        armor = self.player.getArmor()
        pygame.mixer.music.play(-1)
        image = pygame.image.load(pathToResources + "/textures/fonds/battleMenu.png")
        monsterImg = pygame.image.load(monster.imagePath)
        self.screen.blit(image, [0, 0])
        self.screen.blit(monsterImg, [500, 60])
        pygame.display.flip()
        while 1:
            for event in pygame.event.get():
                match event.type:
                    case pygame.QUIT:
                        sys.exit()
                    case pygame.KEYUP:
                        match event.key:
                            case pygame.K_1:
                                if self.attack(weapon, monster) == 1:
                                    return 1
                            case pygame.K_2:
                                if self.potionMenu() == 0:
                                    continue
                            case pygame.K_3:
                                if random.randint(1, 3) == 1:
                                    return 2
                        if self.monsterAttack(monster, armor) == -1:
                            return -1
            self.screen.blit(image, [0, 0])
            self.font.render_to(self.screen, (100, 50), str(monster), (0, 0, 0))
            self.screen.blit(monsterImg, [500, 60])
            self.font.render_to(self.screen, (100, 600), str(self.player), (0, 0, 0))
            pygame.display.flip()

    def weaponChoice(self, validWeapons):
        self.size = width, height = 1280, 720
        self.screen = pygame.display.set_mode(self.size)
        image = pygame.image.load(pathToResources + "/textures/fonds/battle.jpg")
        while 1:
            for event in pygame.event.get():
                match event.type:
                    case pygame.QUIT:
                        sys.exit()
                    case pygame.KEYUP:
                        if 0 < event.scancode - 29 < len(validWeapons) or event.scancode - 29 == 10:
                            if event.scancode - 29 == 10:
                                choice = 0
                            else:
                                choice = event.scancode - 29
                            return validWeapons[choice]
            self.screen.blit(image, [0, 0])
            for i in range(len(validWeapons)):
                weaponText = str(i) + " - " + self.player.inventory[validWeapons[i]].name + " dégâts : " + str(
                    self.player.inventory[validWeapons[i]].damage)
                self.font.render_to(self.screen, (100, 65 + i * 65), weaponText, (0, 0, 0))
            pygame.display.flip()

    def battle(self, posX, posY):
        monster = copy.deepcopy(self.monstersDict[self.maps[self.player.mapId][posX][posY]])
        validWeapons = self.player.getValidWeapons()
        if not validWeapons:
            return -1
        else:
            weapon = self.weaponChoice(validWeapons)
        res = self.battleMenu(weapon, monster)
        if res == 1:
            self.movePlayerAddTimer(posX, posY, 15)
        elif res == -1:
            pathToSave = os.path.abspath(pathToResources + "/save.json")
            f = open(pathToSave, "w")
            f.close()
            main()

    def zoneSetup(self):
        self.size = width, height = len(self.maps[self.player.mapId]) * 32, len(self.maps[self.player.mapId][0]) * 32 + 32
        self.screen = pygame.display.set_mode(self.size)
        if self.player.mapId == 0:
            pygame.mixer.music.load(pathToResources + "/music/Zone_1.mp3")
        elif self.player.mapId == 3:
            pygame.mixer.music.load(pathToResources + "/music/Zone_2.mp3")
        else:
            pygame.mixer.music.load(pathToResources + "/music/Zone_3.mp3")
        pygame.mixer.music.play(-1)

    def gamePlay(self):
        self.zoneSetup()
        self.fillRender(self.screen)
        self.renderMap(self.screen)
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
                                self.checkCanMove(1)
                            case pygame.K_d:
                                self.checkCanMove(2)
                            case pygame.K_s:
                                self.checkCanMove(3)
                            case pygame.K_q:
                                self.checkCanMove(4)
                        self.fillRender(self.screen)
                        self.renderMap(self.screen)
                        self.font.render_to(self.screen, (0, len(self.maps[self.player.mapId][0]) * 32), self.text, (0, 0, 0))
                        self.text = ""
                        pygame.display.flip()

    def turnMenu(self):
        self.size = width, height = 1280, 720
        self.screen = pygame.display.set_mode(self.size)
        image = pygame.image.load(pathToResources + "/textures/fonds/TurnMenu.png")
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
                                pygame.mixer.music.unload()
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
        pygame.mixer.music.load(pathToResources + "/music/MainMenu.mp3")
        pygame.mixer.music.play(-1)
        image = pygame.image.load(pathToResources + "/textures/fonds/MainMenu.png")
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
                                pygame.mixer.music.load(pathToResources + "/music/MainMenu.mp3")
                                pygame.mixer.music.play(-1)
                            case pygame.K_2:
                                if self.loadGame() == 1:
                                    self.turnMenu()
                                    pygame.mixer.music.load(pathToResources + "/music/MainMenu.mp3")
                                    pygame.mixer.music.play(-1)
                            case pygame.K_0:
                                sys.exit()
                        self.screen.blit(image, [0, 0])
                        pygame.display.flip()

    def pnjMenu(self):
        self.size = width, height = 1280, 720
        self.screen = pygame.display.set_mode(self.size)
        pygame.mixer.music.load(pathToResources + "/music/MainMenu.mp3")
        pygame.mixer.music.play(-1)
        image = pygame.image.load(pathToResources + "/textures/fonds/PNJMenu.png")
        imgPnj = pygame.image.load(pathToResources + "/textures/imgPnj.png")
        self.screen.blit(image, [0, 0])
        self.screen.blit(imgPnj, [600, 100])
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
                                self.player.repareItems(self.itemsDict)
                            case pygame.K_2:
                                self.craftMenu()
                                pygame.mixer.music.load(pathToResources + "/music/MainMenu.mp3")
                                pygame.mixer.music.play(-1)
                            case pygame.K_3:
                                self.storageMenu()
                                pygame.mixer.music.load(pathToResources + "/music/MainMenu.mp3")
                                pygame.mixer.music.play(-1)
                            case pygame.K_0:
                                return
                        self.screen.blit(image, [0, 0])
                        self.screen.blit(imgPnj, [600, 100])
                        pygame.display.flip()

    def craftMenu(self):
        self.size = width, height = 1280, 720
        self.screen = pygame.display.set_mode(self.size)
        pygame.mixer.music.load(pathToResources + "/music/MainMenu.mp3")
        pygame.mixer.music.play(-1)
        image = pygame.image.load(pathToResources + "/textures/fonds/586.jpg")
        self.screen.blit(image, [0, 0])
        pygame.display.flip()
        posC = 1
        listCraftZone = []

        for i in range(0, len(self.craftsDict)):
            if self.craftsDict[i].zone == 6 \
                    or (self.craftsDict[i].zone == 5 and self.player.mapId != 0) \
                    or (self.craftsDict[i].zone == 3 and self.player.mapId == 6):
                listCraftZone.append(i)

        for i in range(0, len(listCraftZone)):
            if self.craftsDict[listCraftZone[i]].idResource2 == 0:
                self.font.render_to(self.screen, (50, 50 + i * 50),
                                    str(self.itemsDict[self.craftsDict[listCraftZone[i]].itemId].name + " : " + str(
                                        self.craftsDict[listCraftZone[i]].nbResource1) + " " +
                                        self.itemsDict[self.craftsDict[listCraftZone[i]].idResource1].name), (0, 0, 0))
            else:
                self.font.render_to(self.screen, (50, 50 + i * 50),
                                    str(self.itemsDict[self.craftsDict[listCraftZone[i]].itemId].name + " : " + str(
                                        self.craftsDict[listCraftZone[i]].nbResource1) + " " +
                                        self.itemsDict[
                                            self.craftsDict[listCraftZone[i]].idResource1].name + " + " + str(
                                        self.craftsDict[listCraftZone[i]].nbResource2) + " " +
                                        self.itemsDict[self.craftsDict[listCraftZone[i]].idResource2].name), (0, 0, 0))

        self.font.render_to(self.screen, (25, 50 * posC), "->", (0, 0, 0))
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
                            case pygame.K_z:
                                if posC > 1:
                                    posC -= 1
                            case pygame.K_s:
                                if posC < len(listCraftZone):
                                    posC += 1
                            case pygame.K_RETURN:
                                if self.player.checkQuantity(self.craftsDict[listCraftZone[posC - 1]].idResource1,
                                                             self.craftsDict[listCraftZone[posC - 1]].nbResource1):
                                    if self.craftsDict[listCraftZone[posC - 1]].idResource2 != 0:
                                        if self.player.checkQuantity(
                                                self.craftsDict[listCraftZone[posC - 1]].idResource2,
                                                self.craftsDict[listCraftZone[posC - 1]].nbResource2):
                                            self.craft(listCraftZone[posC - 1])
                                            return
                                    else:
                                        self.craft(listCraftZone[posC - 1])
                                        return
                            case pygame.K_0:
                                return
                        self.screen.blit(image, [0, 0])
                        cnt = 0
                        for i in range(0, len(listCraftZone)):
                            if self.craftsDict[listCraftZone[i]].idResource2 == 0:
                                self.font.render_to(self.screen, (50, 50 + i * 50),
                                                    str(self.itemsDict[self.craftsDict[
                                                        listCraftZone[i]].itemId].name + " : " + str(
                                                        self.craftsDict[listCraftZone[i]].nbResource1) + " " +
                                                        self.itemsDict[
                                                            self.craftsDict[listCraftZone[i]].idResource1].name),
                                                    (0, 0, 0))
                            else:
                                self.font.render_to(self.screen, (50, 50 + i * 50),
                                                    str(self.itemsDict[self.craftsDict[
                                                        listCraftZone[i]].itemId].name + " : " + str(
                                                        self.craftsDict[listCraftZone[i]].nbResource1) + " " +
                                                        self.itemsDict[self.craftsDict[
                                                            listCraftZone[i]].idResource1].name + " + " + str(
                                                        self.craftsDict[listCraftZone[i]].nbResource2) + " " +
                                                        self.itemsDict[
                                                            self.craftsDict[listCraftZone[i]].idResource2].name),
                                                    (0, 0, 0))
                        self.font.render_to(self.screen, (25, 50 * posC), "->", (0, 0, 0))
                        pygame.display.flip()

    def craft(self, id):
        self.player.removeItem(self.craftsDict[id].idResource1,
                               self.craftsDict[id].nbResource1)
        if self.craftsDict[id].idResource2 != 0:
            self.player.removeItem(self.craftsDict[id].idResource2,
                                   self.craftsDict[id].nbResource2)
        self.player.inventory.append(copy.deepcopy(self.itemsDict[self.craftsDict[id].itemId]))

    def storageMenu(self):
        self.size = width, height = 1280, 720
        self.screen = pygame.display.set_mode(self.size)
        pygame.mixer.music.load(pathToResources + "/music/MainMenu.mp3")
        pygame.mixer.music.play(-1)
        image = pygame.image.load(pathToResources + "/textures/fonds/586.jpg")
        self.screen.blit(image, [0, 0])
        pygame.display.flip()
        self.font.render_to(self.screen, (100, 300), "1 - Stocker",(0, 0, 0))
        self.font.render_to(self.screen, (100, 500), "2 - Retirer", (0, 0, 0))
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
                                self.storeMenu()
                            case pygame.K_2:
                                self.removeStorageMenu()
                            case pygame.K_0:
                                return
                        self.screen.blit(image, [0, 0])
                        self.font.render_to(self.screen, (100, 300),"1 - Stocker", (0, 0, 0))
                        self.font.render_to(self.screen, (100, 500),"2 - Retirer", (0, 0, 0))
                        pygame.display.flip()

    def storeMenu(self):
        if len(self.player.inventory) == 0:
            return
        self.size = width, height = 1280, 720
        self.screen = pygame.display.set_mode(self.size)
        pygame.mixer.music.load(pathToResources + "/music/MainMenu.mp3")
        pygame.mixer.music.play(-1)
        image = pygame.image.load(pathToResources + "/textures/fonds/586.jpg")
        self.screen.blit(image, [0, 0])
        pygame.display.flip()
        posC = 0
        for i in range(0, len(self.player.inventory)):
            self.font.render_to(self.screen, (200 * (i // 14) + 50, 50 * (i % 14) + 50),
                                str(self.player.inventory[i].quantity) + ' : ' + self.player.inventory[i].name,
                                (0, 0, 0))
        self.font.render_to(self.screen, (200 * (posC // 14) + 25, 50 * (posC % 14) + 50), "->", (0, 0, 0))
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
                            case pygame.K_z:
                                if posC > 0:
                                    posC -= 1
                            case pygame.K_s:
                                if posC < len(self.player.inventory) - 1:
                                    posC += 1
                            case pygame.K_RETURN:
                                self.store(self.player.inventory[posC].id,
                                           self.quantityMenu(self.player.inventory[posC].quantity))
                                if len(self.player.inventory) == 0:
                                    return
                                posC = 0
                            case pygame.K_0:
                                return
                        self.screen.blit(image, [0, 0])
                        for i in range(0, len(self.player.inventory)):
                            self.font.render_to(self.screen, (200 * (i // 14) + 50, 50 * (i % 14) + 50),str(self.player.inventory[i].quantity) + ' : ' + self.player.inventory[i].name,
                                (0, 0, 0))
                        self.font.render_to(self.screen, (200 * (posC // 14) + 25, 50 * (posC % 14) + 50), "->", (0, 0, 0))
                        pygame.display.flip()

    def removeStorageMenu(self):
        self.size = width, height = 1280, 720
        self.screen = pygame.display.set_mode(self.size)
        pygame.mixer.music.load(pathToResources + "/music/MainMenu.mp3")
        pygame.mixer.music.play(-1)
        image = pygame.image.load(pathToResources + "/textures/fonds/586.jpg")
        self.screen.blit(image, [0, 0])
        pygame.display.flip()
        posC = 0
        for i in range(0, len(self.storage)):
            self.font.render_to(self.screen, (200 * (i // 14) + 50, 50 * (i % 14) + 50), str(self.storage[i][1]) + " : " + self.itemsDict[self.storage[i][0]].name,
                                       (0, 0, 0))
        self.font.render_to(self.screen, (200 * (posC // 14) + 25, 50 * (posC % 14) + 50), "->", (0, 0, 0))
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
                            case pygame.K_z:
                                if posC > 0:
                                    posC -= 1
                            case pygame.K_s:
                                if posC < len(self.storage) - 1:
                                    posC += 1
                            case pygame.K_RETURN:
                                self.unStore(posC, self.quantityMenu(self.storage[posC][1]))
                                if len(self.storage) == 0:
                                    return
                                posC = 0
                            case pygame.K_0:
                                return
                        self.screen.blit(image, [0, 0])
                        for i in range(0, len(self.storage)):
                            self.font.render_to(self.screen, (200 * (i // 14) + 50, 50 * (i % 14) + 50),
                                                str(self.storage[i][1]) + " : " + self.itemsDict[
                                                    self.storage[i][0]].name,
                                                (0, 0, 0))
                        self.font.render_to(self.screen, (200 * (posC // 14) + 25, 50 * (posC % 14) + 50), "->", (0, 0, 0))
                        pygame.display.flip()

    def quantityMenu(self, max):
        self.size = width, height = 1280, 720
        self.screen = pygame.display.set_mode(self.size)
        pygame.mixer.music.load(pathToResources + "/music/MainMenu.mp3")
        pygame.mixer.music.play(-1)
        image = pygame.image.load(pathToResources + "/textures/fonds/586.jpg")
        self.screen.blit(image, [0, 0])
        pygame.display.flip()
        quantity = 0
        self.font.render_to(self.screen, (600, 350), "< " + str(quantity) + " >", (0, 0, 0))
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
                            case pygame.K_q:
                                if quantity > 0:
                                    quantity -= 1
                            case pygame.K_d:
                                if quantity < max:
                                    quantity += 1
                            case pygame.K_RETURN:
                                return quantity
                            case pygame.K_0:
                                return 0
                        self.screen.blit(image, [0, 0])
                        self.font.render_to(self.screen, (600, 350), "< " + str(quantity) + " >", (0, 0, 0))
                        pygame.display.flip()

    def store(self, id, quantity):
        self.player.removeItem(id, quantity)
        for i in range(0, len(self.storage)):
            if self.storage[i][0] == id:
                self.storage[i][1] += quantity
                return
        self.storage.append([id, quantity])

    def unStore(self, id, quantity):
        self.player.appendInventory(self.itemsDict, self.itemsDict[self.storage[id][0]].id, quantity)
        if quantity == self.storage[id][1]:
            del self.storage[id]
        else:
            self.storage[id][1] -= quantity


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
    if zone == 2:
        map = placeThings(map, 99, 0, 1)
        map = placeThings(map, -3, 0, 1)
    elif zone == 1:
        map = placeThings(map, -3, 0, 1)
        map = placeThings(map, -2, 0, 1)
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
    for i in range(0, 9, 3):
        maps[i] = fillMap(maps[i], int(i / 3))
        fillBaseMap(maps[i], maps[2 + i])
    return maps


def main():
    pygame.init()
    pygame.mixer.init()
    pygame.mixer.music.set_volume(0.1)
    player = Player(0, 1, 50, 4, 4, 0)
    game = Game(fillAllMaps(initAllMaps(10, 10)), player, [])
    game.font = pygame.freetype.Font(pathToResources + "/font/OpenSans-Regular.ttf", 24)
    game.mainMenu()


pathToResources = os.path.abspath("resources")
main()
