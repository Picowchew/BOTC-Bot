"""Contains the Sweetheart Character class"""

import json
import random
from botc import Character, Outsider, NonRecurringAction, AlreadyDead, Category, Drunkenness
from ._utils import SectsAndViolets, SnVRole

with open('botc/gamemodes/sectsandviolets/character_text.json') as json_file:
    character_text = json.load(json_file)[SnVRole.sweetheart.value.lower()]


class Sweetheart(Outsider, SectsAndViolets, Character, NonRecurringAction):
    """Sweetheart: If you die, 1 player is drunk from now on.

    ===== SWEETHEART =====

    true_self = sweetheart
    ego_self = sweetheart
    social_self = sweetheart
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
    override regular night instruction? -> NO  # default is to send nothing
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

        self._art_link = "https://bloodontheclocktower.com/wiki/images/3/34/Sweetheart_Token.png"
        self._art_link_cropped = "https://imgur.com/VhIAuPX.png"
        self._wiki_link = "https://bloodontheclocktower.com/wiki/Sweetheart"

        self._role_enum = SnVRole.sweetheart

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

    async def on_being_executed(self, executed_player):
        """Function that runs after the player has been executed"""
        try:
            await executed_player.exec_real_death()
        except AlreadyDead:
            pass
        else:
            import globvars
            game = globvars.master_state.game
            game.today_executed_player = executed_player
            self.make_player_drunk(executed_player)

    async def on_being_demon_killed(self, killed_player):
        """Function that runs after the player has been killed by the Demon at night"""
        try:
            await killed_player.exec_real_death()
        except AlreadyDead:
            pass
        else:
            import globvars
            globvars.master_state.game.night_deaths.append(killed_player)
            self.make_player_drunk(killed_player)

    def make_player_drunk(self, player):
        """This is a made-up algorithm whose purpose is to choose and make a player drunk"""

        import globvars

        if player.is_droisoned():
            log_msg = ">>> Sweetheart: [droisoned] made nobody drunk"
            globvars.logging.info(log_msg)

        else:
            alive_players = globvars.master_state.game.list_apparently_alive_players

            num_evil = 0
            num_good = 0

            demons = []
            minions = []
            outsiders = []
            townsfolks = []

            boundary = 0.7
            demon_base = 1
            minion_base = 2
            outsider_base = 3
            step = 0.1
            exponent = 2
            townsfolk_multiplier = 100

            categories_to_choose_from = []

            for player in alive_players:

                role_true_self = player.role.true_self

                if role_true_self.is_evil():
                    num_evil += 1
                else:
                    num_good += 1

                if role_true_self.is_demon():
                    demons.append(player)
                elif role_true_self.is_minion():
                    minions.append(player)
                elif role_true_self.is_outsider():
                    outsiders.append(player)
                else:
                    townsfolks.append(player)

            if num_good == 0:
                num_good = 1

            ratio_and_boundary_difference = num_evil / num_good - boundary

            if ratio_and_boundary_difference < 0:
                ratio_and_boundary_difference = 0

            demon_multiplier = self.calculate_multiplier(demon_base, ratio_and_boundary_difference, step, exponent, townsfolk_multiplier)
            categories_to_choose_from.extend([Category.demon] * demon_multiplier)

            if minions:
                minion_multiplier = self.calculate_multiplier(minion_base, ratio_and_boundary_difference, step, exponent, townsfolk_multiplier)
                categories_to_choose_from.extend([Category.minion] * minion_multiplier)
            if outsiders:
                outsider_multiplier = self.calculate_multiplier(outsider_base, ratio_and_boundary_difference, step, exponent, townsfolk_multiplier)
                categories_to_choose_from.extend([Category.outsider] * outsider_multiplier)
            if townsfolks:
                categories_to_choose_from.extend([Category.townsfolk] * townsfolk_multiplier)

            drunk_player_category = random.choice(categories_to_choose_from)
            drunk_player = random.choice([player for player in alive_players if player.role.true_self.category == drunk_player_category])
            drunk_status_effect = Drunkenness(player, drunk_player)
            drunk_status_effect.manually_enable()
            drunk_player.add_status_effect(drunk_status_effect)

            log_msg = f">>> Sweetheart: made {drunk_player} drunk"
            globvars.logging.info(log_msg)

    def calculate_multiplier(self, base, ratio_and_boundary_difference, step, exponent, townsfolk_multiplier):
        """This is a made-up algorithm whose purpose is to calculate a category's multiplier"""

        multiplier = round((base + ratio_and_boundary_difference / step) ** exponent)

        if multiplier > townsfolk_multiplier:
            multiplier = townsfolk_multiplier

        return multiplier
