"""Contains the Oracle Character class"""

import json
import discord
import datetime
import random
from botc import Character, Townsfolk, NonRecurringAction, BOTCUtils, get_number_image
from ._utils import SectsAndViolets, SnVRole

with open('botc/gamemodes/sectsandviolets/character_text.json') as json_file:
    character_text = json.load(json_file)[SnVRole.oracle.value.lower()]

with open('botc/game_text.json') as json_file:
    strings = json.load(json_file)
    oracle_nightly = strings["gameplay"]["oracle_nightly"]
    copyrights_str = strings["misc"]["copyrights"]


class Oracle(Townsfolk, SectsAndViolets, Character, NonRecurringAction):
    """Oracle: Each night*, you learn how many dead players are evil.

    ===== ORACLE =====

    true_self = oracle
    ego_self = oracle
    social_self = oracle
    (note that in the Sects & Violets game mode, usually only true_self is used, since true_self, ego_self, and social_self are all the same in this game mode)

    commands:
    - None

    initialize setup? -> NO
    initialize role? -> NO

    ----- First night
    START:
    override first night instruction? -> NO  # default is to send instruction string only

    ----- Regular night
    START:
    override regular night instruction? -> YES  # default is to send nothing
                                        => Send passive nightly information
    """

    def __init__(self):

        Character.__init__(self)
        SectsAndViolets.__init__(self)
        Townsfolk.__init__(self)

        self._desc_string = character_text["description"]
        self._examp_string = character_text["examples"]
        self._instr_string = character_text["instruction"]
        self._lore_string = character_text["lore"]
        self._brief_string = character_text["brief"]
        self._action = character_text["action"]

        self._art_link = "https://bloodontheclocktower.com/wiki/images/2/26/Oracle_Token.png"
        self._art_link_cropped = "https://imgur.com/w1MjPPR.png"
        self._wiki_link = "https://bloodontheclocktower.com/wiki/Oracle"

        self._role_enum = SnVRole.oracle

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
        """Create drunk/poisoned information for the oracle information"""

        import globvars
        droisoned_num_evil = random.randrange(globvars.master_state.game.nb_dead_players + 1)
        log_msg = f">>> Oracle: [droisoned] {droisoned_num_evil} dead evil players"
        globvars.logging.info(log_msg)
        return droisoned_num_evil

    async def send_regular_night_end_dm(self, recipient):
        """Send the number of dead evil players"""

        player = BOTCUtils.get_player_from_id(recipient.id)

        # Dead players do not receive anything
        if not player.is_alive():
            return

        # Droisoned information
        if player.is_droisoned():
            num_evil = self.__create_droisoned_info()
        # Good information
        else:
            import globvars
            num_evil = len([player for player in globvars.master_state.game.list_apparently_dead_players if player.role.true_self.is_evil()])
            log_msg = f">>> Oracle: {num_evil} dead evil players"
            globvars.logging.info(log_msg)
        link = get_number_image(num_evil)

        msg = f"***{recipient.name}#{recipient.discriminator}***, the **{self.name}**:"
        msg += "\n"
        msg += self.emoji + " " + self.instruction
        msg += "\n"
        msg += oracle_nightly.format(num_evil)

        embed = discord.Embed(description = msg)
        embed.set_thumbnail(url = link)
        embed.set_footer(text = copyrights_str)
        embed.timestamp = datetime.datetime.utcnow()

        try:
            await recipient.send(embed = embed)
        except discord.Forbidden:
            pass
