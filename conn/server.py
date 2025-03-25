"""
Recieves and processes requests from clients
"""
from conn.server_connection import ServerConnection;
from Leaderboard import Leaderboard;

import socket;


class Server:
    def __init__(self,
        no_socket = False,
    ):
        # Initialise server components
        self.leaderboard = Leaderboard();

        # Initialise internal state
        self.games = {};
        self.__clients = {};
    
        if not no_socket:
            self.__start_server();
    
    """
    Listen for new sockets
    """
    def __start_server(self,
        host = "localhost",
        port = 12345,
        max_incoming_connections = 5,
    ):
        # Create and bind socket
        self.__server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM);
        self.__server_socket.bind((host, port));
    
        self.__server_socket.listen(max_incoming_connections)

        self.__listening = True;
        while self.__listening:
            # Block until new connection, then create a server connection and pass opened socket to it
            client_socket, client_address = self.__server_socket.accept();
            self.create_client(
                sock = client_socket
            );

    """
    Create a new server connection to a client
    """
    def create_client(self, sock = None):
        client = ServerConnection(
            server = self,
            sock = sock,
        );
        self.__clients[client.id] = client;
        print(f"New client registered with server at serverConnection id {client.id}")
        return client;

    """
    Get list of game names
    """
    def get_games_keys(self):
        return self.games.keys();
    
    """
    Remove a client from server 
    """
    def disconnect(self, client):
        del self.__clients[client.id];

    """
    Register a new game
    """
    def add_game(self, game,
        existing_game = "This game already exists",
        name_taken = "This game name is already taken",
    ):
        # Check if game or game name already exists
        if game.id in self.games:
            raise Exception(existing_game);

        searched_game = self.get_game(game.name, check_no_game = False);
        if searched_game is not None:
            raise Exception(name_taken);
        
        # Add game to server
        self.games[game.id] = game;
    
    """
    Get a game by name
    """
    def get_game(self, name,
        check_no_game = True,
        no_game = "No game with that name",
        multiple_games = "Multiple games with the same name",
    ):
        # Get all games with requested name
        games = [game for game in self.games.values() if game.name == name];        
        # Return errors if no game or multiple games found
        if len(games) == 0:
            if check_no_game:
                raise Exception(no_game);
            else:
                return None;

        if len(games) > 1:
            raise Exception(multiple_games);
        
        # Return only game found
        return games[0];

    """
    Send message to clients by player id
    """
    def send_to_players(self,
        players = None,
        category = None,
        status = None,
        message = None,
    ):
        clients = [client for client in self.__clients.values() if client.player.username in players];

        [client.send(category, status, message) for client in clients];
