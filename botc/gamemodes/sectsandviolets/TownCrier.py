"""Contains the Town Crier Character class"""

import json
import discord
import datetime
import random
from botc import Character, Townsfolk, NonRecurringAction, BOTCUtils
from ._utils import SectsAndViolets, SnVRole

with open('botc/gamemodes/sectsandviolets/character_text.json') as json_file:
    character_text = json.load(json_file)[SnVRole.towncrier.value.lower()]

with open('botc/game_text.json') as json_file:
    strings = json.load(json_file)
    yes = strings["gameplay"]["yes"]
    no = strings["gameplay"]["no"]
    yes_image = strings["images"]["yes"]
    no_image = strings["images"]["no"]
    town_crier_nightly = strings["gameplay"]["town_crier_nightly"]
    copyrights_str = strings["misc"]["copyrights"]


class TownCrier(Townsfolk, SectsAndViolets, Character, NonRecurringAction):
    """Town Crier: Each night*, you learn if a Minion nominated today.

    ===== TOWN CRIER =====

    true_self = town crier
    ego_self = town crier
    social_self = town crier
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

        self._art_link = "https://bloodontheclocktower.com/wiki/images/8/85/Town_Crier_Token.png"
        self._art_link_cropped = "https://imgur.com/NBqr1eS.png"
        self._wiki_link = "https://bloodontheclocktower.com/wiki/Town_Crier"

        self._role_enum = SnVRole.towncrier

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
        """Create drunk/poisoned information for the town crier information"""

        import globvars
        droisoned_whether_minion_has_nominated = random.choice([yes, no])
        log_msg = f">>> Town Crier: [droisoned] {droisoned_whether_minion_has_nominated}, a Minion has\
                    {'' if droisoned_whether_minion_has_nominated == yes else ' not'} nominated"
        globvars.logging.info(log_msg)
        return droisoned_whether_minion_has_nominated

    async def send_regular_night_end_dm(self, recipient):
        """Send whether a Minion has nominated"""

        player = BOTCUtils.get_player_from_id(recipient.id)

        # Dead players do not receive anything
        if not player.is_alive():
            return

        # Droisoned information
        if player.is_droisoned():
            whether_minion_has_nominated = self.__create_droisoned_info()
        # Good information
        else:
            import globvars
            whether_minion_has_nominated = yes if [player for player in globvars.master_state.game.nominator_list
                                                    if player.role.true_self.is_minion()] else no
            log_msg = f">>> Town Crier: {whether_minion_has_nominated}, a Minion has\
                        {'' if whether_minion_has_nominated == yes else ' not'} nominated"
            globvars.logging.info(log_msg)
        link = yes_image if whether_minion_has_nominated == yes else no_image

        msg = f"***{recipient.name}#{recipient.discriminator}***, the **{self.name}**:"
        msg += "\n"
        msg += self.emoji + " " + self.instruction
        msg += "\n"
        msg += town_crier_nightly.format(whether_minion_has_nominated)

        embed = discord.Embed(description = msg)
        embed.set_thumbnail(url = link)
        embed.set_footer(text = copyrights_str)
        embed.timestamp = datetime.datetime.utcnow()

        try:
            await recipient.send(embed = embed)
        except discord.Forbidden:
            pass
