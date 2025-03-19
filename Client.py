#!/usr/bin/env python
from Game import Game
from Cell import Cell
from Cell import CellType
from View import View

import curses
from curses import wrapper

class Client:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        curses.cbreak()
        self.stdscr.keypad(True)
        self.playing = True
        self.game = Game()
        self.view = View(stdscr)

        self.selectedCell = self.game.getGrid().getCellAt(0, 0)
        self.gameLoop()

    def gameLoop(self):
        while self.playing:
            self.stdscr.clear()
            self.draw()
            self.stdscr.move(self.selectedCell.getPosY(), self.selectedCell.getPosX())
            
            self.captureInput()
            self.stdscr.refresh()
    
    def captureInput(self):
        currentX = self.selectedCell.getPosX()
        currentY = self.selectedCell.getPosY()

        key = self.stdscr.getch()
        if key == curses.KEY_UP:
            self.tryMoveCursor(currentX, currentY, 0, -1)
        elif key == curses.KEY_DOWN:
            self.tryMoveCursor(currentX, currentY, 0, 1)
        elif key == curses.KEY_LEFT:
            self.tryMoveCursor(currentX, currentY, -1, 0)
        elif key == curses.KEY_RIGHT:
            self.tryMoveCursor(currentX, currentY, 1, 0)
        elif key == 10: # press enter to place fence
            self.game.tryPlaceFence(self.selectedCell)

    def tryMoveCursor(self, currentX, currentY, moveX, moveY):
        while True:
            currentX += moveX
            currentY += moveY
            cell = self.game.getGrid().getCellAt(currentX, currentY)
            if cell == None:
                return

            cellType = cell.getCellType()
            if self.canMoveTo(cell):
                break
            else:
                # try to move by one left or right
                if abs(moveY) > 0:
                    if currentY % 2 == 0:
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

    def canMoveTo(self, cell):
        return cell != None and (cell.getCellType() == CellType.SELECTABLE or cell.getCellType() == CellType.FENCE)

    def selectCell(self, x, y ,cell):
        self.stdscr.move(y, x)
        self.selectedCell = cell

    def draw(self):
        self.view.draw(self.game.getGrid(), self.game.getScores())

def main(stdscr):
    client = Client(stdscr)

wrapper(main)