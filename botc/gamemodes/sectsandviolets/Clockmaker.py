"""Contains the Clockmaker Character class"""

import json
import discord
import datetime
import random
from math import floor
from botc import Character, Townsfolk, NonRecurringAction, BOTCUtils, get_number_image
from ._utils import SectsAndViolets, SnVRole

with open('botc/gamemodes/sectsandviolets/character_text.json') as json_file:
    character_text = json.load(json_file)[SnVRole.clockmaker.value.lower()]

with open('botc/game_text.json') as json_file:
    strings = json.load(json_file)
    clockmaker_init = strings["gameplay"]["clockmaker_init"]
    copyrights_str = strings["misc"]["copyrights"]


class Clockmaker(Townsfolk, SectsAndViolets, Character, NonRecurringAction):
    """Clockmaker: You start knowing how many steps from the Demon to nearest Minion.

    ===== CLOCKMAKER =====

    true_self = clockmaker
    ego_self = clockmaker
    social_self = clockmaker
    (note that in the Sects & Violets game mode, usually only true_self is used, since true_self, ego_self, and social_self are all the same in this game mode)

    commands:
    - None

    initialize setup? -> NO
    initialize role? -> NO

    ----- First night
    START:
    override first night instruction? -> YES  # default is to send instruction string only
                                      => Send passive initial information

    ----- Regular night
    START:
    override regular night instruction? -> NO  # default is to send nothing
    """

    def __init__(self):

        Character.__init__(self)
        SectsAndViolets.__init__(self)
        Townsfolk.__init__(self)

        self._desc_string = character_text["description"]
        self._examp_string = character_text["examples"]
        self._instr_string = character_text["instruction"]
        self._lore_string = character_text["lore"]

        self._art_link = "https://bloodontheclocktower.com/wiki/images/4/4b/Clockmaker_Token.png"
        self._art_link_cropped = "https://imgur.com/EMz0g5v.png"
        self._wiki_link = "https://bloodontheclocktower.com/wiki/Clockmaker"

        self._role_enum = SnVRole.clockmaker

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

    def __create_droisoned_info(self):
        """Create drunk/poisoned information for the n1 clockmaker information"""

        import globvars
        droisoned_num_steps = random.randint(1, floor(globvars.master_state.game.nb_players / 2))
        log_msg = f">>> Clockmaker: [droisoned] {droisoned_num_steps} steps from the Demon to nearest Minion"
        globvars.logging.info(log_msg)
        return droisoned_num_steps

    async def send_n1_end_message(self, recipient):
        """Send the number of steps from the Demon to nearest Minion"""

        player = BOTCUtils.get_player_from_id(recipient.id)

        # Dead players do not receive anything
        if not player.is_alive():
            return

        # Droisoned information
        if player.is_droisoned():
            num_steps = self.__create_droisoned_info()
        # Good information
        else:
            num_steps = self.get_num_steps()
        link = get_number_image(num_steps)

        msg = f"***{recipient.name}#{recipient.discriminator}***, the **{self.name}**:"
        msg += "\n"
        msg += self.emoji + " " + self.instruction
        msg += "\n"
        msg += clockmaker_init.format(num_steps)

        embed = discord.Embed(description = msg)
        embed.set_thumbnail(url = link)
        embed.set_footer(text = copyrights_str)
        embed.timestamp = datetime.datetime.utcnow()

        try:
            await recipient.send(embed = embed)
        except discord.Forbidden:
            pass

    def get_num_steps(self):
        """Get the number of steps from the Demon to nearest Minion"""

        import globvars

        num_players = globvars.master_state.game.nb_players
        ordered_players = globvars.master_state.game.sitting_order

        for i in range(num_players): # Just to ensure that infinite recursion does not occur
            if ordered_players[i].role.true_self.is_demon():
                demon_index = i
                return

        for j in range(1, floor(num_players / 2) + 1): # Just to ensure that infinite recursion does not occur
            if ordered_players[(demon_index + j) % num_players].role.true_self.is_minion() or ordered_players[demon_index - j].role.true_self.is_minion():
                log_msg = f">>> Clockmaker: {j} steps from the Demon to nearest Minion"
                globvars.logging.info(log_msg)
                return j
