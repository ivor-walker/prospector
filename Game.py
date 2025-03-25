from Grid import Grid
from Player import Player
from Enums import CellType
from Enums import CellWorth

gParamBoundary_dimensions = [1, 30]
gParamBoundary_maxPlayers = [2, 5]
gParamBoundary_resourceAbundance = [0, 100]

"""
Class representing the logic of a single game
"""

import random
import string

class Game:
    def __init__(self, 
        name = None, 
        host_username = None,
        dimX = None, 
        dimY = None,
        maxPlayers = 2, 
        resourceAbundance = None,
        len_id = 10,
    ):
        # Set game state
        self.name = name
        self.host_username = host_username;
        self.grid = Grid(dimX, dimY)
        self.maxPlayers = maxPlayers
        self.resourceAbundance = resourceAbundance
        self.id = ''.join(random.choices(string.ascii_uppercase + string.digits, k = len_id));

        # Set player states
        self.players = [];
        self.__current_player_index = 0;
        self.__current_player = None;
        self.__current_player_username = None;

        # cell worth hyperparameters
        self.cellPointWorths = dict()
        self.cellPointWorths[CellWorth.NORMAL] = 1
        self.cellPointWorths[CellWorth.COPPER] = 2
        self.cellPointWorths[CellWorth.SILVER] = 3
        self.cellPointWorths[CellWorth.GOLD] = 5

    def getGrid(self):      
        return self.grid
    
    def getCellAt(self, x, y):
        return self.grid.getCellAt(x, y)

    """
    Try to place a fence on the grid
    """
    def tryPlaceFence(self, cell,
        player_id = None,
    ):
        if player_id is None:
            player_id = self.__current_player_username

        if self.grid.tryPlaceFence(cell, player_id):
            self.checkAdjacentLandClaims(cell)
            self.nextTurn()

            return True

        return False

    def checkAdjacentLandClaims(self, cell):
        adjacent = self.getAdjacentCells(cell)
        for cellAdj in adjacent:
            if cellAdj.getCellType() == CellType.LAND and (not cellAdj.isClaimed()):
                if self.checkLandClaim(cellAdj):
                    self.onLandClaimed(cellAdj)
    
    def checkLandClaim(self, cell):
        landAjcaent = self.getAdjacentCells(cell)
        for fences in landAjcaent:
            if (fences.getCellType() != CellType.FENCE) or (fences.getPlayerOwner() != self.__current_player_username):
                return False
        return True

    def onLandClaimed(self, cell):
        cell.setPlayerOwner(self.__current_player_username);
        cellWorth = cell.getCellWorth()
        self.__current_player.active_game_score += self.cellPointWorths[cellWorth]

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
    
    """
    Get score of all players
    """
    def getScores(self):
        playerDict = dict()
        for player in self.players:
            playerDict[player] = player.active_game_score
        return playerDict
    
    """
    Get the current player
    """
    def getCurrentPlayer(self):
        return self.__current_player

    """
    Change the current player
    """
    def nextTurn(self):
        self.__current_player_index += 1
        if self.__current_player_index >= len(self.players):
            self.__current_player_index = 0

        self.__current_player = self.players[self.__current_player_index];
        self.__current_player_username = self.__current_player.username;

    """
    Add a player to the game
    """
    def add_player(self, player):
        if len(self.players) == self.maxPlayers:
            raise Exception("Max players reached");

        if player in self.players:
            raise Exception("Player already in game");

        self.players.append(player);
