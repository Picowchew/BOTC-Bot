"""Contains the Barber Character class"""

import json
from botc import Character, Outsider
from ._utils import SectsAndViolets, SnVRole

with open('botc/gamemodes/sectsandviolets/character_text.json') as json_file:
    character_text = json.load(json_file)[SnVRole.barber.value.lower()]


class Barber(Outsider, SectsAndViolets, Character):
    """Barber: If you die, tonight the Demon may choose 2 players to swap characters.
    """

    def __init__(self):

        Character.__init__(self)
        SectsAndViolets.__init__(self)
        Outsider.__init__(self)

        self._desc_string = character_text["description"]
        self._examp_string = character_text["examples"]
        self._instr_string = character_text["instruction"]
        self._lore_string = character_text["lore"]

        self._art_link = "https://bloodontheclocktower.com/wiki/images/0/08/Barber_Token.png"
        self._wiki_link = "https://bloodontheclocktower.com/wiki/Barber"

        self._role_enum = SnVRole.barber
