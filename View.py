#!/usr/bin/env python
from Grid import Grid
from Cell import CellType
from Cell import CellWorth

import curses

class View:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        
        # land colours
        curses.init_pair(1, curses.COLOR_RED, curses.COLOR_RED)
        curses.init_pair(2, curses.COLOR_BLUE, curses.COLOR_BLUE)
        curses.init_pair(3, curses.COLOR_MAGENTA, curses.COLOR_MAGENTA)
        curses.init_pair(4, curses.COLOR_CYAN, curses.COLOR_CYAN)
        curses.init_pair(5, curses.COLOR_GREEN, curses.COLOR_GREEN)
        self.landColours = [curses.color_pair(1), curses.color_pair(2), curses.color_pair(3), curses.color_pair(4), curses.color_pair(5)]
        
        # unclaimed colour
        curses.init_pair(6, curses.COLOR_WHITE, curses.COLOR_WHITE)
        self.colourUnclaimed = curses.color_pair(6)
        curses.init_pair(7, curses.COLOR_YELLOW, curses.COLOR_YELLOW)
        self.colourLandWorth = curses.color_pair(7)

        # fence colours
        curses.init_pair(8, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(9, curses.COLOR_BLUE, curses.COLOR_BLACK)
        curses.init_pair(10, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
        curses.init_pair(11, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(12, curses.COLOR_GREEN, curses.COLOR_BLACK)
        self.fenceColours = [curses.color_pair(8), curses.color_pair(9), curses.color_pair(10), curses.color_pair(11), curses.color_pair(12)]

    def draw(self, grid, playerScores):
        dimensionX = grid.getdimensionX()
        dimensionY = grid.getdimensionY()

        # draw grid
        for y in range(dimensionY):
            for x in range(dimensionX):
                cell = grid.getCellAt(x, y)
                self.drawCell(cell, x, y)

        # draw scores
        self.drawScores(playerScores)

    def drawCell(self, cell, x, y):
        cellType = cell.getCellType()
        playerOwner = cell.getPlayerOwner()

        if cellType == CellType.FENCE:
            colour = self.getPlayerColour(playerOwner, True)
            if y % 2 == 0:
                self.stdscr.addstr(y, x, "-", colour)
            else:
                self.stdscr.addstr(y, x, "|", colour)
        elif cellType == CellType.LAND:
            string = "#"
            worth = cell.getCellWorth()
            if worth == CellWorth.COPPER:
                string = "B"
            elif worth == CellWorth.SILVER:
                string = "S"
            elif worth == CellWorth.GOLD:
                string = "G"

            if cell.isClaimed() or worth == CellWorth.NORMAL:
                colour = self.getPlayerColour(playerOwner, False)
            else:
                colour = self.colourLandWorth

            self.stdscr.addstr(y, x, string, colour)
        elif cellType == CellType.SELECTABLE:
            self.stdscr.addstr(y, x, " ")
        elif cellType == CellType.SKIP:
            self.stdscr.addstr(y, x, ".")

    def drawScores(self, playerScores):
        offsetX = 40
        offsetY = 2
        for player in playerScores:
            colour = self.getPlayerColour(player, False)
            self.stdscr.addstr(offsetY, offsetX, str(player))
            self.stdscr.addstr(offsetY, offsetX + 5, str(playerScores[player]), self.getPlayerColour(player, True))
            offsetY += 1

    def getPlayerColour(self, playerID, isFence):
        if(playerID == -1):
            return curses.COLOR_WHITE
        if isFence:
            return self.fenceColours[playerID]
        else:    
            return self.landColours[playerID]