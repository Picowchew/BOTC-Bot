"""Contains admins only commands"""

import traceback
import json
import botutils
from discord.ext import commands

with open('botutils/bot_text.json') as json_file:
    language = json.load(json_file)

user_not_found_str = language["errors"]["user_not_found"]
missing_user_str = language["errors"]["missing_user"]
missing_game_pack_or_game_mode_str = language["errors"]["missing_game_pack_or_game_mode"]
error_str = language["system"]["error"]


class Admin(commands.Cog, name = language["system"]["admin_cog"]):
    """Admins only commands cog"""

    def __init__(self, client):
        self.client = client

    def cog_check(self, ctx):
        return botutils.check_if_admin(ctx)

    async def cog_command_error(self, ctx, error):
        """Error handling on command"""

        # Case: check failure
        if isinstance(error, commands.CheckFailure):
            return

        # Case: bad argument (user not found)
        elif isinstance(error, commands.BadArgument):
            await ctx.send(user_not_found_str.format(ctx.author.mention))
            return

        # Case: missing required argument (<game pack or game mode>/<user> not specified)
        elif isinstance(error, commands.MissingRequiredArgument):
            if str(ctx.command) == "fgame":
                await ctx.send(missing_game_pack_or_game_mode_str.format(ctx.author.mention))
                return
            else:
                await ctx.send(missing_user_str.format(ctx.author.mention))
                return

        # For other cases we will want to see the error logged
        else:
            try:
                raise error
            except Exception:
                await ctx.send(error_str)
                await botutils.log(botutils.Level.error, traceback.format_exc())
