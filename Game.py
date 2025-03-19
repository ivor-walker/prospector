#!/usr/bin/env python
from Grid import Grid
from Player import Player
from Cell import CellType
from Cell import CellWorth

class Game:
    def __init__(self):
        self.grid = Grid(7, 7)
        self.players = [Player(1), Player(2)]
        self.currentPlayerIndex = 0

        self.playerScores = dict()
        self.playerScores[self.players[0].getInternalID()] = 0
        self.playerScores[self.players[1].getInternalID()] = 0

        # cell worth hyperparameters
        self.cellPointWorths = dict()
        self.cellPointWorths[CellWorth.NORMAL] = 1
        self.cellPointWorths[CellWorth.COPPER] = 2
        self.cellPointWorths[CellWorth.SILVER] = 3
        self.cellPointWorths[CellWorth.GOLD] = 5

    def getGrid(self):      
        return self.grid
    
    def getScores(self):
        return self.playerScores
    
    def getCurrentPlayer(self):
        return self.players[self.currentPlayerIndex]
    
    def tryPlaceFence(self, cell):
        if self.grid.tryPlaceFence(cell, self.getCurrentPlayer().getInternalID()):
            self.checkAdjacentLandClaims(cell)
            self.nextTurn()

    def checkAdjacentLandClaims(self, cell):
        adjacent = self.getAdjacentCells(cell)
        for cellAdj in adjacent:
            if cellAdj.getCellType() == CellType.LAND and (not cellAdj.isClaimed()):
                if self.checkLandClaim(cellAdj):
                    self.onLandClaimed(cellAdj)
    
    def checkLandClaim(self, cell):
        landAjcaent = self.getAdjacentCells(cell)
        for fences in landAjcaent:
            if (fences.getCellType() != CellType.FENCE) or (fences.getPlayerOwner() != self.getCurrentPlayer().getInternalID()):
                return False
        return True

    def onLandClaimed(self, cell):
        cell.setPlayerOwner(self.getCurrentPlayer().getInternalID())
        cellWorth = cell.getCellWorth()
        self.playerScores[self.getCurrentPlayer().getInternalID()] += self.cellPointWorths[cellWorth]

    def getAdjacentCells(self, cell):
        adjacent = []
        adj = self.grid.getCellAt(cell.getPosX() + 1, cell.getPosY())
        if adj != None:
            adjacent.append(adj)
        adj = self.grid.getCellAt(cell.getPosX() - 1, cell.getPosY())
        if adj != None:
            adjacent.append(adj)
        adj = self.grid.getCellAt(cell.getPosX(), cell.getPosY() + 1)
        if adj != None:
            adjacent.append(adj)
        adj = self.grid.getCellAt(cell.getPosX(), cell.getPosY() - 1)
        if adj != None:
            adjacent.append(adj)
        
        return adjacent

    def nextTurn(self):
        self.currentPlayerIndex += 1
        if self.currentPlayerIndex >= len(self.players):
            self.currentPlayerIndex = 0