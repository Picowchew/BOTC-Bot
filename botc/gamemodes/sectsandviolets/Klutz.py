"""Contains the Klutz Character class"""

import json
from botc import Character, Outsider
from ._utils import SectsAndViolets, SnVRole

with open('botc/gamemodes/sectsandviolets/character_text.json') as json_file:
    character_text = json.load(json_file)[SnVRole.klutz.value.lower()]


class Klutz(Outsider, SectsAndViolets, Character):
    """Klutz: When you learn that you died, publicly choose 1 alive player: if they are evil, your team loses.
    """

    def __init__(self):

        Character.__init__(self)
        SectsAndViolets.__init__(self)
        Outsider.__init__(self)

        self._desc_string = character_text["description"]
        self._examp_string = character_text["examples"]
        self._instr_string = character_text["instruction"]
        self._lore_string = character_text["lore"]
        self._brief_string = character_text["brief"]
        self._action = character_text["action"]

        self._art_link = "https://bloodontheclocktower.com/wiki/images/2/2a/Klutz_Token.png"
        self._art_link_cropped = "https://imgur.com/Do7c6Lq.png"
        self._wiki_link = "https://bloodontheclocktower.com/wiki/Klutz"

        self._role_enum = SnVRole.klutz

    def create_n1_instr_str(self):
        """Create the instruction field on the opening dm card"""

        # First line is the character instruction string
        msg = f"{self.emoji} {self.instruction}"
        addendum = character_text["n1_addendum"]

        # Some characters have a line of addendum
        if addendum:
            with open("botutils/bot_text.json") as json_file:
                bot_text = json.load(json_file)
                scroll_emoji = bot_text["esthetics"]["scroll"]
            msg += f"\n{scroll_emoji} {addendum}"

        return msg
