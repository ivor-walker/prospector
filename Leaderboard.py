"""
Class representing all players in the game
"""
class Leaderboard:
    def __init__(self):
        self.__players = {}
    
    """
    Adds a player to the leaderboard
    """
    def add_player(self, player):
        # Check player and player name is unique
        matched_player = self.get_player(player.username, check_no_player = False)
        if matched_player is not None:
            raise Exception(f"Player with name {player.name} already exists")

        self.__players[player.username] = player

    """
    Get a player by their username
    """
    def get_player(self, username,
        check_no_player = True,
    ):
        matched_keys = [key for key, value in self.__players.items() if value.username == username]

        # Check if no players found
        if len(matched_keys) == 0:
            if check_no_player:
                raise Exception(f"Player with name {username} does not exist")
            else:
                return None
        
        # Check if multiple players found
        if len(matched_keys) > 1:
            raise Exception(f"Multiple players with name {username} exist")

        # Return only player
        matched_key = matched_keys[0]
        return self.__players[matched_key]
