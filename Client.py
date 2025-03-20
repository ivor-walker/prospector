#!/usr/bin/env python
from Game import Game
from Game import gParamBoundary_dimensions
from Game import gParamBoundary_maxPlayers
from Game import gParamBoundary_resourceAbundance

from Enums import CellType
from View import View
from Enums import UserState
from Enums import Helpers

import curses
from curses import wrapper

# single-player
from Server import Server

class Client:
    def __init__(self, stdscr):
        self.serverDummy = Server() # single-player

        # init
        self.stdscr = stdscr
        self.view = View(stdscr)
        self.username = ""
        self.password = ""
        self.game = None
        self.playing = True
        self.userState = UserState.NONE
        self.selectedElement = None
        self.resetLocalGame()

        # curses options
        self.stdscr.keypad(True)
        self.stdscr.nodelay(False)
    
        self.onUserStateChanged(UserState.LOGIN)
        self.stdscr.refresh()
        self.userLoop()

    def userLoop(self):
        while self.playing:         
            self.captureInput()
            self.stdscr.refresh()
    
    def captureInput(self):
        if self.userState == UserState.LOGIN:
            self.navigateMenu(True, False)

            key = self.stdscr.getstr()
            self.username = Helpers.convertString(key)
            self.selectedElement.setDisplayString(self.username)

            self.navigateMenu(False, False)

            key = self.stdscr.getstr()
            self.password = Helpers.convertString(key)
            self.selectedElement.setDisplayString(self.password)

            self.onUserStateChanged(UserState.ROOMSLIST) # replace with call to server for validating user
            return
        elif self.userState == UserState.ROOMSLIST:
            key = -1
            while key != 10 or self.selectedElement == None:
                key = self.stdscr.getch()
                if key == curses.KEY_UP:
                    self.navigateMenu(True, True)
                elif key == curses.KEY_DOWN:
                    self.navigateMenu(False, True)

            gameName = self.selectedElement.getName()
            if gameName == "MakeGame":
                self.onUserStateChanged(UserState.MAKEGAME)
                return
            else:
                # ask server to join game with this name
                self.onStartGame(Game(self.optionNameGame, self.optionMapX, self.optionMapY, self.optionNumPlayers, self.optionResourceAbundance)) # delete me later, should ask server
            return
        elif self.userState == UserState.MAKEGAME:
            self.resetLocalGame()

            self.navigateMenu(True, False)
            invalid = True
            while invalid:
                self.selectCurrentElement()
                key = self.stdscr.getstr()
                value = Helpers.convertString(key)
                if (value != None) and (value != ""):
                    self.optionNameGame = value
                    invalid = False
                    self.selectedElement.setDisplayString(self.optionNameGame)

            self.navigateMenu(False, False)
            invalid = True
            while invalid:
                self.selectCurrentElement()
                key = self.stdscr.getstr()
                value = Helpers.convertStringToNumber(key)
                if (value != None) and (value >= gParamBoundary_dimensions[0]) and (value <= gParamBoundary_dimensions[1]):
                    self.optionMapX = value
                    invalid = False
                    self.selectedElement.setDisplayString(self.optionMapX)

            self.navigateMenu(False, False)
            invalid = True
            while invalid:
                self.selectCurrentElement()
                key = self.stdscr.getstr()
                value = Helpers.convertStringToNumber(key)
                if (value != None) and (value >= gParamBoundary_dimensions[0]) and (value <= gParamBoundary_dimensions[1]):
                    self.optionMapY = value
                    invalid = False
                    self.selectedElement.setDisplayString(self.optionMapY)

            self.navigateMenu(False, False)
            invalid = True
            while invalid:
                self.selectCurrentElement()
                key = self.stdscr.getstr()
                value = Helpers.convertStringToNumber(key)
                if (value != None) and (value >= gParamBoundary_maxPlayers[0]) and (value <= gParamBoundary_maxPlayers[1]):
                    self.optionNumPlayers = value
                    invalid = False
                    self.selectedElement.setDisplayString(self.optionNumPlayers)

            self.navigateMenu(False, False)
            invalid = True
            while invalid:
                self.selectCurrentElement()
                key = self.stdscr.getstr()
                value = Helpers.convertStringToNumber(key)
                if (value != None) and (value >= gParamBoundary_resourceAbundance[0]) and (value <= gParamBoundary_resourceAbundance[1]):
                    self.optionResourceAbundance = value
                    invalid = False
                    self.selectedElement.setDisplayString(self.optionResourceAbundance)

            self.onStartGame(Game(self.optionNameGame, self.optionMapX, self.optionMapY, self.optionNumPlayers, self.optionResourceAbundance)) # delete me later, ask server to create game
            return
        elif self.userState == UserState.GAME:
            currentX = self.selectedCell.getPosX()
            currentY = self.selectedCell.getPosY()

            key = self.stdscr.getch()
            if Helpers.convertChar(key) == "q":
                self.exitGame()
                return
            if key == curses.KEY_UP:
                self.tryMoveCursor(currentX, currentY, 0, -1)
            elif key == curses.KEY_DOWN:
                self.tryMoveCursor(currentX, currentY, 0, 1)
            elif key == curses.KEY_LEFT:
                self.tryMoveCursor(currentX, currentY, -1, 0)
            elif key == curses.KEY_RIGHT:
                self.tryMoveCursor(currentX, currentY, 1, 0)
            elif key == 10: # press enter to place fence
                self.game.tryPlaceFence(self.selectedCell) # replace with call to server
            
            self.onStateChange() # changes view. delete this call and call it in method coming from server upon game update (fence places)
            self.stdscr.move(self.selectedCell.getPosY(), self.selectedCell.getPosX())

    def resetLocalGame(self):
        self.game = None
        self.selectedCell = None
        self.selectedElement = None

        # game options
        self.optionNameGame = "Game"
        self.optionMapX = 5
        self.optionMapY = 5
        self.optionNumPlayers = 2
        self.optionResourceAbundance = 20

    def onStartGame(self, game):
        self.game = game
        self.selectedCell = self.game.getGrid().getCellAt(0, 0)
        self.onUserStateChanged(UserState.GAME)

    def exitGame(self):
        self.resetLocalGame()
        self.onUserStateChanged(UserState.ROOMSLIST)

    def tryMoveCursor(self, currentX, currentY, moveX, moveY):
        while True:
            currentX += moveX
            currentY += moveY
            cell = self.game.getGrid().getCellAt(currentX, currentY)
            if cell == None:
                return

            if self.canMoveTo(cell):
                break
            else:
                # try to move by one left or right
                if abs(moveY) > 0:
                    if (currentY % 2 == 0):
                        cell = self.game.getGrid().getCellAt(currentX - 1, currentY)
                        if self.canMoveTo(cell):
                            currentX -= 1
                            break
                    else:
                        cell = self.game.getGrid().getCellAt(currentX + 1, currentY)
                        if self.canMoveTo(cell):
                            currentX += 1
                            break
        self.selectCell(currentX, currentY, cell)

    def onUserStateChanged(self, newState):
        self.userState = newState
        self.view.onUserStateChanged(newState)
        self.selectedElement = None

        self.stdscr.clear()
        self.draw()

        if newState == UserState.LOGIN:
            curses.echo()
            curses.curs_set(1)
        elif newState == UserState.ROOMSLIST:
            curses.noecho()
            curses.curs_set(1)
        elif newState == UserState.MAKEGAME:
            curses.echo()
            curses.curs_set(1)
        elif newState == UserState.GAME:
            curses.noecho()
            curses.curs_set(1)

    def onStateChange(self):
        self.draw()

    def selectCurrentElement(self):
        if self.selectedElement == None:
            return

        pos = self.selectedElement.getPosition()
        self.stdscr.move(pos[0], pos[1])

    def navigateMenu(self, up, highlight):
        if self.selectedElement:
            self.selectedElement.display(self.stdscr, False)

        element = self.view.navigateMenu(self.selectedElement, up)
        pos = element.getPosition()
        self.selectedElement = element
        self.stdscr.move(pos[0], pos[1])

        # highlighting
        if highlight:
            element.display(self.stdscr, highlight)            

    def canMoveTo(self, cell):
        return cell != None and (cell.getCellType() == CellType.BORDER or cell.getCellType() == CellType.FENCE)

    def selectCell(self, x, y ,cell):
        self.selectedCell = cell

    def draw(self):
        grid = None
        userScores = None
        currentUser = None
        if self.game != None:
            grid = self.game.getGrid()
            userScores = self.game.getScores()
            currentUser = self.game.getCurrentPlayer()
        gamesList = None
        if self.serverDummy != None:
            gamesList = self.serverDummy.getGamesList()
        
        self.view.draw(grid, currentUser, userScores, gamesList)

def main(stdscr):
    client = Client(stdscr)

wrapper(main)