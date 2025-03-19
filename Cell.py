#!/usr/bin/env python
from enum import Enum

class CellType(Enum):
    SKIP = -1
    SELECTABLE = 0
    LAND = 1
    FENCE = 2

class CellWorth(Enum):
    NORMAL = 0
    COPPER = 1
    SILVER = 2
    GOLD = 3

class Cell:
    def __init__(self, x, y, type, worth):
        self.x = x
        self.y = y
        self.cellType = type
        self.cellWorth = worth
        self.playerOwnerID = -1

    def getCellType(self):
        return self.cellType
    
    def getCellWorth(self):
        return self.cellWorth
    
    def getPlayerOwner(self):
        return self.playerOwnerID
    
    def getPosX(self):
        return self.x
    
    def getPosY(self):
        return self.y
    
    def setCellType(self, type):
        self.cellType = type

    def setPlayerOwner(self, player):
        self.playerOwnerID = player

    def isClaimed(self):
        return self.playerOwnerID != -1