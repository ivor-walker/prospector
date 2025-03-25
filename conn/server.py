"""
Recieves and processes requests from clients
"""
from conn.server_connection import ServerConnection;
from Leaderboard import Leaderboard;

import asyncio;


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
            asyncio.run(self.__start_server())
    
    """
    Listen for new sockets
    """
    async def __start_server(self,
        host = "localhost",
        port = 12345,
        max_incoming_connections = 5,
    ):
        # Create and bind socket
        self.__server_socket = await asyncio.start_server(self.__create_network_client, host, port);
    
        async with self.__server_socket:
            await self.__server_socket.serve_forever();

    """
    Create a new server connection synchronously
    """
    def create_client(self):
        client = ServerConnection();
        self.__register_client(client)
        return client;

    """
    Create a new server connection to a client asynchronously
    """
    async def __create_network_client(self, reader, writer):
        client = ServerConnection(
            server = self,
            reader = reader,
            writer = writer,
        );
        self.__register_client(client);

        print(f"New client registered with server at serverConnection id {client.id}")
        
        await client._listen();
    
    """
    Register a client with the server
    """
    def __register_client(self, client):
        self.__clients[client.id] = client;
    
    
    
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
