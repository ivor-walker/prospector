"""
Class representing a single connection from a client to the server
"""
from conn.connection import Connection;
import socket;

class ClientConnection(Connection):
    
    """
    Constructor: open socket connection to client
    """
    def __init__(self,
        host = "localhost",
        port = 9990,
        server_connection = None,
    ):
        self.listeners = []; 
        
        if not server_connection:
            # Establish a blocking socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM);
            sock.connect((host, port));
            
        # Start listening loop
        super().__init__(
            connection = server_connection,
            send_acknowledgement = False,
            sock = sock,
        );	
    
    """
    Register a listener (i.e Client) to this connection
    """
    def add_listener(self, listener):
        self.listeners.append(listener);

    # Requests where failure is possible    
    """
    Ask server to login an existing player
    """
    def send_login(self,
        username = None,
        password = None,
    ):
        self.send("login", "request", {
            "username": username,
            "password": password
        });

    """
    Recieve login response from server
    """
    def login(self, message):
        if message == "success":
            [listener.recieve_login_success() for listener in self.listeners];

        else:
            [listener.recieve_login_failure(message) for listener in self.listeners];

    """
    Ask server to sign up a new player
    """
    def send_signup(self,
        username = None,
        password = None,
    ):
        self.send("signup", "request", {
            "username": username,
            "password": password
        });

    """
    Recieve signup response from server
    """
    def signup(self, message):
        if message == "success":
            [listener.recieve_signup_success() for listener in self.listeners];

        else:
            [listener.recieve_signup_failure(message) for listener in self.listeners];

    """
    Ask server to create a new game or join an existing game 
    """
    def send_new_game(self,
        name = None,
        length = None,
        height = None,
        max_players = None,
        resource_abundance = None,
    ):
        self.send("newGame", "request", {
            "name": name,
            "length": length,
            "height": height,
            "max_players": max_players,
            "resource_abundance": resource_abundance
        });

    """
    Recieve new game response from server
    """
    def new_game(self, message):
        if message == "success":
            [listener.recieve_new_game_success() for listener in self.listeners];

        else:
            [listener.recieve_new_game_failure(message) for listener in self.listeners];

    """
    Ask server to join an existing game
    """
    def send_join_game(self,
        game_name = None,
    ):
        self.send("joinGame", "request", {
            "game_name": game_name,
        });

    """
    Recieve join game response from server
    """
    def join_game(self, message):
        if message == "success":
            [listener.recieve_join_game_success() for listener in self.listeners];

        else:
            [listener.recieve_join_game_failure(message) for listener in self.listeners];

    """
    Ask server to place a fence
    """
    def send_place_fence(self,
        x = None,
        y = None,
    ):
        self.send("placeFence", "request", {
            "x": x,
            "y": y,
        });
    
    """
    Recieve place fence response from server
    """
    def place_fence(self, message):
        if type(message) == str:
            if message == "success":
                [listener.recieve_place_fence_success() for listener in self.listeners];

            else:
                [listener.recieve_place_fence_failure(message) for listener in self.listeners];
        
        # Server telling player of a newly placed fence
        else:
            [listener.recieve_place_fence_request(**message) for listener in self.listeners];

    # Requests where failure is not possible
    """
    Ask server to leave
    """
    def send_disconnect(self):
        self.send("disconnect", "request", "client requested disconnect");
        self.disconnect();

    """
    Recieve a disconnect request from the server
    """
    def disconnect(self):
        # Stop listening loop and close socket
        self._listening = False;
        self._sock.close();

        [listener.recieve_disconnected() for listener in self.listeners];

    """
    Ask server to leave the active game
    """
    def send_leave_game(self):
        self.send("leaveGame", "request", {
            "player": "self"
        });

    """
    Recieve leave game request from server (either user was kicked or 
    """
    def leave_game(self, player):
        [listener.recieve_leave_game(player) for listener in self.listeners];
        
    """
    Ask server to list all games
    """
    def send_list_games_names(self):
        self.send("listGamesNames", "request", {
            "message": "Client requested list of all games"
        });

    """
    Recieve list of all games from server
    """
    def list_games_names(self, games):
        [listener.recieve_list_games_names(games) for listener in self.listeners];

    """
    Ask server to list players in current game
    """
    def send_list_players_in_game(self):
        self.send("listPlayersInGame", "request", {
            "message": "Client requested all players in currently active game"       
        });

    """
    Recieve list of players in current game
    """
    def list_players_in_game(self, players):
        [listener.recieve_players_in_game(players) for listener in self.listeners];
