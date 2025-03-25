"""
Class representing a single registered player
"""

import random
import string

class Player:
    def __init__(self,
        username = None,
        password = None,
        len_id = 10,
    ):
        self.username = username;
        self.__password = password;

        # Set game details
        self.__active_game = None;
        self.active_game_score = 0;

        # Create collections
        self.games = {};
    
    """
    Get the game the player is currently playing
    """
    def __get_active_game(self,
        no_active_game = "Player is not in a game"
    ):
        if self.__active_game is None:
            raise Exception(no_active_game);
        
        return self.__active_game;

    """
    Set the game the player is currently playing
    """
    def __set_active_game(self, game):
        if game is not None and self.__active_game is not None and game.id == self.__active_game.id:
            raise Exception("Player is already in this game");

        self.__active_game = game;
        self.games[game.id] = game; 

    """
    Get player to join a game
    """
    def join_game(self, game):
        game.add_player(self);
        self.__set_active_game(game);

    """
    Check if password is correct
    """
    def check_password(self, password):
        return self.__password == password;

    """
    Place a fence in the current game
    """
    def place_fence(self, 
        x = None, 
        y = None, 
        orientation = None,
    ):
        active_game = self.__get_active_game();
        active_game.tryPlaceFence(self, x, y, orientation);

    """
    Leave currently active game
    """
    def leave_active_game(self):
        # Clean up active game
        active_game = self.__get_active_game();
        active_game.remove_player(self);
        
        # Unset active game
        self.__set_active_game(None);


