#!/usr/bin/env python

# Dummy Server
class Server:
    def __init__(self):
        self.gamesList = ["lobbyOne", "northLobbyIsBestLobby", "baseTradeLobby", "ProspectorLloby"]

    def getGamesList(self):
        return self.gamesList