"""Contains the fgame command cog"""

import botutils
import json
from library import fancy
from discord.ext import commands
from ._admin import Admin
from botc.gamemodes.Gamemode import Gamemode

with open('botutils/bot_text.json') as json_file:
    language = json.load(json_file)

fgame_str = language["cmd"]["fgame"]
game_pack_or_game_mode_not_found = language["errors"]["game_pack_or_game_mode_not_found"]


class Fgame(Admin, name = language["system"]["admin_cog"]):
    """Fgame command"""

    @commands.command(
        pass_context = True,
        name = "fgame",
        brief = language["doc"]["fgame"]["brief"],
        help = language["doc"]["fgame"]["help"],
        description = language["doc"]["fgame"]["description"]
    )
    async def fgame(self, ctx, game_pack_or_game_mode):
        """Force game command"""

        gp_or_gm_lower = game_pack_or_game_mode.lower()

        # BoTC
        if gp_or_gm_lower in ["tb", "bmr", "sv", "snv"]:

            # Trouble Brewing
            game = botutils.GameChooser().default_game

            if gp_or_gm_lower == "bmr":
                game.gamemode = Gamemode.bad_moon_rising
            elif gp_or_gm_lower in ["sv", "snv"]:
                game.gamemode = Gamemode.sects_and_violets

            botutils.GameChooser.selected_game = game

            await ctx.send(fgame_str.format(
                ctx.author.mention,
                f"{fancy.bold(game.gamemode.value)} - 𝕭𝖑𝖔𝖔𝖉 𝖔𝖓 𝖙𝖍𝖊 𝕮𝖑𝖔𝖈𝖐𝖙𝖔𝖜𝖊𝖗 (𝕭𝖔𝕿𝕮)"
            ))

        else:
            await ctx.send(game_pack_or_game_mode_not_found.format(ctx.author.mention))
