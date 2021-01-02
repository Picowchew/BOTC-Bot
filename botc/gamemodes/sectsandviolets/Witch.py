"""Contains the Witch Character class"""

import json
from botc import Character, Minion, RecurringAction, ActionTypes, Action, GameLogic, WitchCurse
from ._utils import SectsAndViolets, SnVRole

with open('botc/gamemodes/sectsandviolets/character_text.json') as json_file:
    character_text = json.load(json_file)[SnVRole.witch.value.lower()]

with open('botutils/bot_text.json') as json_file:
    bot_text = json.load(json_file)
    butterfly = bot_text["esthetics"]["butterfly"]


class Witch(Minion, SectsAndViolets, Character, RecurringAction):
    """Witch: Each night, choose a player: if they nominate tomorrow, they die. If just 3 players live, you lose this ability.

    ===== WITCH =====

    true_self = witch
    ego_self = witch
    social_self = witch
    (note that in the Sects & Violets game mode, usually only true_self is used, since true_self, ego_self, and social_self are all the same in this game mode)

    commands:
    - curse <player>

    initialize setup? -> NO
    initialize role? -> NO

    ----- First night
    START:
    override first night instruction? -> YES  # default is to send instruction string only
                                      => Send query for "curse" command

    ----- Regular night
    START:
    override regular night instruction? -> YES  # default is to send nothing
                                        => Send query for "curse" command
    """

    def __init__(self):

        Character.__init__(self)
        SectsAndViolets.__init__(self)
        Minion.__init__(self)

        self._desc_string = character_text["description"]
        self._examp_string = character_text["examples"]
        self._instr_string = character_text["instruction"]
        self._lore_string = character_text["lore"]

        self._art_link = "https://bloodontheclocktower.com/wiki/images/c/cc/Witch_Token.png"
        self._art_link_cropped = "https://imgur.com/sCwwRsT.png"
        self._wiki_link = "https://bloodontheclocktower.com/wiki/Witch"

        self._role_enum = SnVRole.witch

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
        """Return True if witch has submitted the curse action"""

        import globvars
        if player.is_alive() and globvars.master_state.game.nb_alive_players > 3:
            current_phase_id = globvars.master_state.game._chrono.phase_id
            received_action = player.action_grid.retrieve_an_action(current_phase_id)
            return received_action is not None and received_action.action_type == ActionTypes.curse
        return True

    @GameLogic.requires_more_than_three_alive_players
    @GameLogic.requires_one_target
    @GameLogic.changes_not_allowed
    async def register_curse(self, player, targets):
        """Curse command"""

        import globvars

        # Must be 1 target
        assert len(targets) == 1, "Received a number of targets different than 1 for witch 'curse'"
        action = Action(player, targets, ActionTypes.curse, globvars.master_state.game._chrono.phase_id)
        player.action_grid.register_an_action(action, globvars.master_state.game._chrono.phase_id)
        msg = butterfly + " " + character_text["feedback"].format(targets[0].game_nametag)
        await player.user.send(msg)

    async def exec_curse(self, witch_player, cursed_player):
        """Execute the curse action (night ability interaction)"""

        import globvars
        if witch_player.is_alive():
            if witch_player.is_droisoned():
                log_msg = ">>> Witch: [droisoned] cursed nobody"
                globvars.logging.info(log_msg)
            else:
                cursed_player.add_status_effect(WitchCurse(witch_player, cursed_player))
                log_msg = f">>> Witch: cursed {cursed_player}"
                globvars.logging.info(log_msg)

    async def process_night_ability(self, player):
        """Process night actions for the witch character.
        @player : the Witch player (Player object)
        """

        import globvars

        phase = globvars.master_state.game._chrono.phase_id
        action = player.action_grid.retrieve_an_action(phase)

        # The witch has submitted an action. We call the execution function immediately. (If the witch has not submitted
        # an action, then we will not randomize the action since the cursing ability is a "privileged" ability.)
        if action:
            assert action.action_type == ActionTypes.curse, f"Wrong action type {action} in witch"
            targets = action.target_player
            cursed_player = targets[0]
            await self.exec_curse(player, cursed_player)
