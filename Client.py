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
from conn.server import Server
from conn.server_connection import ServerConnection

# multi-player
import asyncio
from conn.client_connection import ClientConnection

from Player import Player

class Client:
    def __init__(self, stdscr, single_player = False):
        # Connect to 'server' object in memory if single player
        if single_player:
            self.__server = Server();
            self.__server_connection = self.__server.create_client();
            self.__connection = ClientConnection(server_connection = self.__server_connection);
            self.__server_connection._Connection__connection = self.__connection;
            
            
        # Connect to server via socket if multiplayer
        else:
            self.__connection = ClientConnection();
        
        self.__connection.add_listener(self);

        # init
        self.stdscr = stdscr
        self.view = View(stdscr)
        self.username = ""
        self.password = ""
        self.game = None
        self.gamesList = None
        self.playing = True
        self.userState = UserState.NONE
        self.selectedElement = None
        self.resetLocalGame()

        # curses options
        self.stdscr.keypad(True)
        self.stdscr.nodelay(False)
    
        self.onUserStateChanged(UserState.LOGIN)
        self.stdscr.refresh()
        self.draw()
        self.userLoop()

    def userLoop(self):
        while self.playing:
            self.captureInput()
            self.stdscr.refresh()
    
    """
    Listeners for login
    """
    def recieve_login_success(self):
        self.onUserStateChanged(UserState.ROOMSLIST)
    
    def recieve_login_failure(self, message):
        self.onUserStateChanged(UserState.LOGIN)
        # TODO Display failure message
    
    """
    Listeners for joining an existing game
    """
    def recieve_join_game_success(self):
        game = Game(
            name = self.optionNameGame,
            length = self.optionMapX,
            height = self.optionMapY,
            max_players = self.optionNumPlayers,
            resource_abundance = self.optionResourceAbundance
        );

        self.onStartGame(game);

    def recieve_join_game_failure(self, message):
        self.onUserStateChanged(UserState.ROOMSLIST);
        # TODO Display failure message
    
    """
    Listeners for listing games
    """
    def recieve_list_games_names(self, games):
        self.gamesList = games
        self.draw()
    
    """
    Listener for recieving players in a game
    """
    def recieve_players_in_game(self, players):
        players = [Player(player) for player in players]
        self.game.players = players;
        index = 0
        for player in players:
            self.view.onPlayerAdded(player.username, index)
            index += 1

        self.draw()

    """
    Listeners for creating a new game
    """
    def recieve_new_game_success(self):
        # Create local copy of game and start it
        game = Game(
            name = self.optionNameGame, 
            dimX = self.optionMapX,
            dimY = self.optionMapY,
            maxPlayers = self.optionNumPlayers,
            resourceAbundance = self.optionResourceAbundance,
        );

        self.onStartGame(game);
    
    def recieve_new_game_failure(self, message):
        self.onUserStateChanged(UserState.MAKEGAME);
        # TODO Display failure message

    """
    Listeners for placing a fence
    """
    def recieve_place_fence_success(self):
        #self.stdscr.move(self.selectedCell.getPosY(), self.selectedCell.getPosX());
        self.draw()

    def recieve_place_fence_failure(self, message):
        ();
        # TODO Display failure message

    def recieve_place_fence_request(self, x, y, owner):
        cell = self.game.getCellAt(x, y)
        self.game.tryPlaceFence(cell, player_id = owner);
        self.draw()

    
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

            self.__connection.send_login( 
                username = self.username,
                password = self.password
            );

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
                self.__connection.send_join_game(
                    game_name = gameName
                );
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
                
            self.__connection.send_new_game(
                name = self.optionNameGame,
                length = self.optionMapX,
                height = self.optionMapY,
                max_players = self.optionNumPlayers,
                resource_abundance = self.optionResourceAbundance
            );
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
                self.__connection.send_place_fence( 
                    x = currentX,
                    y = currentY,
                );

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
        self.onUserStateChanged(UserState.GAME)
        self.selectedCell = self.game.getGrid().getCellAt(0, 0)
        self.__connection.send_list_players_in_game();

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
        self.stdscr.refresh()
        self.draw()
        self.stdscr.move(self.selectedCell.getPosY(), self.selectedCell.getPosX());
        

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
            self.__connection.send_list_games_names();
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
        self.draw()
        self.selectCurrentElement()     

    def canMoveTo(self, cell):
        return cell != None and (cell.getCellType() == CellType.BORDER or cell.getCellType() == CellType.FENCE)

    def selectCell(self, x, y ,cell):
        self.selectedCell = cell

    def draw(self):
        grid = None
        userScores = None
        currentUser = None
        currentUserName = None
        roomsList = []
        if self.game != None:
            grid = self.game.getGrid()
            userScores = self.game.getScores()
            currentUser = self.game.getCurrentPlayer()
            roomsList = self.gamesList
            if currentUser != None:
                currentUserName = currentUser.username

        self.view.draw(grid, currentUserName, userScores, roomsList)
        

def main(stdscr):
    client = Client(stdscr)

wrapper(main)
