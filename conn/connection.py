"""
Generic representation of a single connection between any two nodes. Contains methods for sending and receiving messages.
"""
import socket
import threading
import json

import random
import string

import traceback

class Connection:

    """
    Constructor: Get connection ID and optionally start listening
    """
    def __init__(self,
        len_id= 10,
        server = None,
        sock = None,
        connection = None,
        send_acknowledgement = True,
        debug = False,
    ):
        self.__debug = debug;
        self.__single_player = True;
        self.__listening = False;

        # Randomly generate an id
        self.id = ''.join(random.choices(string.ascii_uppercase + string.digits, k = len_id));

        if server is not None:
            self._server = server;
        
        self.__connection_type = "server" if server is not None else "client";
        self.__send_acknowledgement = send_acknowledgement;
        
        # Write over provided connection
        self.__sock = sock;
        if sock is not None:
            self.__reader = sock.makefile('r');
            self.__writer = sock.makefile('w');
            
        # Write to in-memory connection directly
        self.__connection = connection;

        # Start listening for messages
        self.__listening_thread = threading.Thread(target = self.start_listening);
        self.__listening_thread.start();
    
    """
    Listen for messages from the other connection
    """
    def start_listening(self):
        # Avoid starting multiple listeners
        if self.__listening is True:
            return;

        try:
            self.__listening = True;

            # Listen for messages
            while self.__listening:

                # Read a message
                line = self.__reader.readline();
                if line == "":
                    break;

                line = line.strip();
                if line:
                    self.handle_message(message);

        except Exception as e:
            self._handle_error(e);

        finally:
            self._handle_error(f"Connection {self.id} closed");

            if self.__sock is not None:
                self.__sock.close();

            return;
    
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
                self.send(message_category, "success", "succes");

        # Handle errors in message handling
        except Exception as e:
            self._handle_error(e, category = message_category);
    
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
            if self.__writer is not None: 
                self.__writer.write(message);

                if self.__debug:
                    print(message_info + " through socket");
            
            # Write to in-memory connection directly
            if self.__connection is not None: 
                self.__connection.handle_message(message);

                if self.__debug:
                    print(message_info + " through memory");

        except Exception as e:
            self._handle_error(f"Error in sending message: {message}, {e}", attempt_send = False);

    
