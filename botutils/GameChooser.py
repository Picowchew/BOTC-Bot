"""Contains the GameChooser class"""

from botc.Game import Game

class GameChooser:
    """A class to facilitate gamemode choosing and voting"""

    def __init__(self):
        self._default_game = Game()
        self._selected_game = Game()

    @property
    def default_game(self):
        return self._default_game

    @property
    def selected_game(self):
        return self._selected_game

    @selected_game.setter
    def selected_game(self, newly_selected_game):
        self._selected_game = newly_selected_game
