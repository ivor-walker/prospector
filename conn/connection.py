"""
Generic representation of a single connection between any two nodes. Abstract methods outline the communication protocol between the two nodes.
"""

from abc import ABC, abstractmethod

import asyncio

import json

import random
import string

import socket

import traceback

class Connection:

    """
    Constructor: Get connection ID and optionally start listening
    """
    def __init__(self,
        lenid= 10,
        server = None,
        sock = None,
        connection = None,
        send_acknowledgement = True,
        debug = False,
    ):
        self.__debug = debug;

        # Randomly generate an id
        self.id = ''.join(random.choices(string.ascii_uppercase + string.digits, k = lenid));

        if server is not None:
            self._server = server;
        
        self.__connection_type = "server" if server is not None else "client";
        self.__send_acknowledgement = send_acknowledgement;

        # Start listening for messages asynchronously
        if sock is not None:
            self.__sock = sock;
            asyncio.create_task(self._listen());

        # Write to in-memory connection directly
        elif connection is not None:
            self.__connection = connection;
    
    """
    Listen for messages from the server
    """
    async def _listen(self):
        try:
            self.__reader, self.__writer = await asyncio.open_connection(sock = self.__sock);
            self._listening = True;

            # Listen for messages
            while self._listening:

                # Read a message
                message = await self.__reader.read();
                if not message:
                    break;
                
                self.handle_message(message);

        except Exception as e:
            self._handle_error(e);

        finally:
            self._handle_error(f"Connection {self.id} closed");

            if hasattr(self, "__writer"):
                self.__writer.close()
                await self.__writer.wait_closed();

    
    """
    Send a message to the client
    """
    def send(self, category, status, message):
        try:
            # Convert message to serialisable format
            if isinstance(message, type({}.keys())):
                message = list(message);

            # Wrap string in message object
            if isinstance(message, str):
                message = {"message": message};
            # Send the message
            message = {
                "category": category,
                "status": status,
                "message": message
            };

            message = json.dumps(message);
            message_info = f"Connection ID {self.id} ({self.__connection_type}) sending message: {message}";
            
            # Check if connection is still open 
            if hasattr(self, "__writer"):
                self.__writer.write(message);

                if self.__debug:
                    print(message_info + " through socket");
            
            # Write to in-memory connection directly
            elif hasattr(self, "_Connection__connection"):
                self.__connection.handle_message(message);

                if self.__debug:
                    print(message_info + " through memory");

        except Exception as e:
            self._handle_error(f"Error in sending message: {message}, {e}", attempt_send = False);

    """
    Handle an error in the client
    """
    def _handle_error(self, message,
        category = "generic_error",
        attempt_send = True
    ):
        if self.__debug:
            traceback.print_exc();

        # Turn error object into string
        if not isinstance(message, str):
            message = str(message);
        
        if self.__debug:
            print(f"Error in connection {self.id} ({self.__connection_type}): {message}");
        
        # Send error message to client
        if not attempt_send:
            return;

        self.send(category, "error", message);

    """
    Handle a message from the client
    """
    def handle_message(self, message,
        unknown_message = "Unknown message category",
        message_category_no_reply = ["disconnect", "listGamesNames"],
        message_status_no_reply = ["error"],
    ):
        
        # Handle the message
        try:
            message = json.loads(message);

        except json.JSONDecodeError as e:
            self._handle_error(e); 
        
        # Get the message category
        message_category = message["category"];
        message_status = message["status"];
        message = message["message"];
        
        # Handle the message
        try:
            if message_status == "error":
                self._handle_error(message, attempt_send = False);

            elif message_category == "disconnect":
                self.disconnect();
            
            elif message_category == "listGamesNames":
                self.list_games_names(**message);
            
            elif message_category == "listPlayersInGame":
                self.list_players_in_game(**message)

            elif message_category == "login":
                self.login(**message);

            elif message_category == "signup":
                self.signup(**message);

            elif message_category == "newGame":
                self.new_game(**message);

            elif message_category == "existingGame":
                self.existing_game(**message);
            
            elif message_category == "placeFence":
                self.place_fence(**message);

            elif message_category == "leaveGame":
                self.leave_game(**message);
                        
            # Valid message category not sent
            else:
                raise Exception(unknown_message);
            
            # Send success message to client
            if self.__send_acknowledgement and message_category not in message_category_no_reply and message_status not in message_status_no_reply:
                self.send(message_category, "success", {
                    "message": "success"
                });

        # Handle errors in message handling
        except Exception as e:
            self._handle_error(e, category = message_category);

    """
    Abstract methods for communication between client and server
    """
    
    """
    Connecting: client sends connection request, only client needs to implement
    """
    @abstractmethod
    def connect(self):
        if hasattr(self, "_server"):
            raise NotImplementedError("Method not implemented");

    """
    Disconnect: both client and server need to be able to send and recieve disconnect messages
    """
    @abstractmethod
    def disconnect(self):
        raise NotImplementedError("Method not implemented");
    
    @abstractmethod
    def recieve_disconnect(self):
        raise NotImplementedError("Method not implemented");

    
    """
    Logging into a player: client sends login request, server sends login response, client recieves login response
    """
    @abstractmethod
    def login(self, username, password):
        raise NotImplementedError("Method not implemented");

    @abstractmethod
    def recieve_login(self, username, password):
        if not hasattr(self, "_server"):
            raise NotImplementedError("Method not implemented");
    
    """
    Signing up a new player
    """
    @abstractmethod
    def signup(self, username, password):
        raise NotImplementedError("Method not implemented");
    
    @abstractmethod
    def recieve_signup(self, username, password):
        if not hasattr(self, "_server"):
            raise NotImplementedError("Method not implemented");

    
    """
    Creating a new game
    """
    @abstractmethod
    def new_game(self, game_name):
        raise NotImplementedError("Method not implemented");
    
    @abstractmethod
    def recieve_new_game(self, game_name):
        if not hasattr(self, "_server"):
            raise NotImplementedError("Method not implemented");

    
    @abstractmethod
    def existing_game(self, game_name):
        raise NotImplementedError("Method not implemented");

    @abstractmethod
    def recieve_existing_game(self, game_name):
        raise NotImplementedError("Method not implemented");


    @abstractmethod
    def place_fence(self, x, y, orientation):
        raise NotImplementedError("Method not implemented");

    @abstractmethod
    def recieve_place_fence(self, x, y, orientation):
        raise NotImplementedError("Method not implemented");

    
    @abstractmethod
    def leave_game(self, game_name):
        raise NotImplementedError("Method not implemented");

    @abstractmethod
    def recieve_leave_game(self, game_name):
        raise NotImplementedError("Method not implemented");

    
    @abstractmethod
    def list_games_names(self):
        raise NotImplementedError("Method not implemented");

    @abstractmethod
    def recieve_list_games_names(self):
        raise NotImplementedError("Method not implemented");
