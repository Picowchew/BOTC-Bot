"""Contains the Dreamer Character class"""

import json
import discord
import datetime
import random
from botc import Character, Townsfolk, RecurringAction, ActionTypes, Action, GameLogic, BOTCUtils, Demon, Minion, Outsider
from ._utils import SectsAndViolets, SnVRole

with open('botc/gamemodes/sectsandviolets/character_text.json') as json_file:
    character_text = json.load(json_file)[SnVRole.dreamer.value.lower()]

with open('botutils/bot_text.json') as json_file:
    bot_text = json.load(json_file)
    butterfly = bot_text["esthetics"]["butterfly"]

with open('botc/game_text.json') as json_file:
    strings = json.load(json_file)
    dream = strings["images"]["dream"]
    dreamer_nightly = strings["gameplay"]["dreamer_nightly"]
    copyrights_str = strings["misc"]["copyrights"]


class Dreamer(Townsfolk, SectsAndViolets, Character, RecurringAction):
    """Dreamer: Each night, choose a player (not yourself): you learn 1 good character and 1 evil character, 1 of which is correct.

    ===== DREAMER =====

    true_self = dreamer
    ego_self = dreamer
    social_self = dreamer
    (note that in the Sects & Violets game mode, usually only true_self is used, since true_self, ego_self, and social_self are all the same in this game mode)

    commands:
    - dream <player>

    initialize setup? -> NO
    initialize role? -> NO

    ----- First night
    START:
    override first night instruction? -> YES  # default is to send instruction string only
                                      => Send query for "dream" command

    ----- Regular night
    START:
    override regular night instruction? -> YES  # default is to send nothing
                                        => Send query for "dream" command
    """

    def __init__(self):

        Character.__init__(self)
        SectsAndViolets.__init__(self)
        Townsfolk.__init__(self)

        self._desc_string = character_text["description"]
        self._examp_string = character_text["examples"]
        self._instr_string = character_text["instruction"]
        self._lore_string = character_text["lore"]

        self._art_link = "https://bloodontheclocktower.com/wiki/images/2/2c/Dreamer_Token.png"
        self._art_link_cropped = "https://imgur.com/Yo9eP5u.png"
        self._wiki_link = "https://bloodontheclocktower.com/wiki/Dreamer"

        self._role_enum = SnVRole.dreamer

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

    def add_action_field_n1(self, embed_obj):
        """Send the stats list n1"""

        import globvars
        msg = self.action
        msg += globvars.master_state.game.create_sitting_order_stats_string()
        embed_obj.add_field(name = butterfly + " **「 Your Action 」**", value = msg, inline = False)
        return embed_obj

    def has_finished_night_action(self, player):
        """Return True if dreamer has submitted the dream action"""

        import globvars
        if player.is_alive():
            current_phase_id = globvars.master_state.game._chrono.phase_id
            received_action = player.action_grid.retrieve_an_action(current_phase_id)
            return received_action is not None and received_action.action_type == ActionTypes.dream
        return True

    @GameLogic.no_self_targetting
    @GameLogic.requires_one_target
    @GameLogic.changes_not_allowed
    async def register_dream(self, player, targets):
        """Dream command"""

        import globvars

        # Must be 1 target
        assert len(targets) == 1, "Received a number of targets different than 1 for dreamer 'dream'"
        action = Action(player, targets, ActionTypes.dream, globvars.master_state.game._chrono.phase_id)
        player.action_grid.register_an_action(action, globvars.master_state.game._chrono.phase_id)
        msg = butterfly + " " + character_text["feedback"].format(targets[0].game_nametag)
        await player.user.send(msg)

    async def exec_dream(self, dreamer_player, dreamed_player):
        """Execute the dream action (night ability interaction)"""

        # Dreamer player has to be alive
        if dreamer_player.is_alive():

            import globvars

            demon_and_minion_choices = BOTCUtils.get_role_list(SectsAndViolets, Demon) + BOTCUtils.get_role_list(SectsAndViolets, Minion)
            outsider_and_townsfolk_choices = BOTCUtils.get_role_list(SectsAndViolets, Outsider) + BOTCUtils.get_role_list(SectsAndViolets, Townsfolk)
            outsider_and_townsfolk_choices = [choice for choice in outsider_and_townsfolk_choices
                                                if choice.name not in [SnVRole.artist.value, SnVRole.savant.value]] # To be removed if these roles are implemented

            # Droisoned information
            if dreamer_player.is_droisoned():
                demon_or_minion = random.choice(demon_and_minion_choices)
                outsider_or_townsfolk = random.choice(outsider_and_townsfolk_choices)
                log_msg = f">>> Dreamer: [droisoned] dreamed of {dreamed_player} as either the {demon_or_minion} or the {outsider_or_townsfolk}"
                globvars.logging.info(log_msg)
            # Good information
            else:
                correct_role = dreamed_player.role.true_self
                if correct_role.is_demon() or correct_role.is_minion():
                    demon_or_minion = correct_role
                    outsider_or_townsfolk = random.choice(outsider_and_townsfolk_choices)
                else:
                    demon_or_minion = random.choice(demon_and_minion_choices)
                    outsider_or_townsfolk = correct_role
                log_msg = f">>> Dreamer: dreamed of {dreamed_player} as either the {demon_or_minion} or the {outsider_or_townsfolk}"
                globvars.logging.info(log_msg)
            link = dream
            recipient = dreamer_player.user

            msg = f"***{recipient.name}#{recipient.discriminator}***, the **{self.name}**:"
            msg += "\n"
            msg += self.emoji + " " + self.instruction
            msg += "\n"
            msg += dreamer_nightly.format(demon_or_minion, outsider_or_townsfolk)

            embed = discord.Embed(description = msg)
            embed.set_thumbnail(url = link)
            embed.set_footer(text = copyrights_str)
            embed.timestamp = datetime.datetime.utcnow()

            try:
                await recipient.send(embed = embed)
            except discord.Forbidden:
                pass

    async def process_night_ability(self, player):
        """Process night actions for the dreamer character.
        @player : the Dreamer player (Player object)
        """

        import globvars

        phase = globvars.master_state.game._chrono.phase_id
        action = player.action_grid.retrieve_an_action(phase)

        # The dreamer has submitted an action. We call the execution function immediately. (If the dreamer has not submitted
        # an action, then we will not randomize the action since the dreaming ability is a "privileged" ability.)
        if action:
            assert action.action_type == ActionTypes.dream, f"Wrong action type {action} in dreamer"
            targets = action.target_player
            dreamed_player = targets[0]
            await self.exec_dream(player, dreamed_player)
