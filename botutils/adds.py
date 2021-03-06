"""Contains functions to handle roles and permissions"""

import configparser
import json

import globvars

Config = configparser.ConfigParser()
Config.read("config.INI")

LOBBY_CHANNEL_ID = Config["user"]["LOBBY_CHANNEL_ID"]
SERVER_ID = Config["user"]["SERVER_ID"]
ALIVE_ROLE_ID = Config["user"]["ALIVE_ROLE_ID"]
DEAD_ROLE_ID = Config["user"]["DEAD_ROLE_ID"]
ADMINS_ROLE_ID = Config["user"]["ADMINS_ROLE_ID"]
LOCK_CHANNELS_ID = json.loads(Config["user"]["LOCK_CHANNELS_ID"])


async def add_admin_role(user):
    """Grant the admin role to a member"""
    role = globvars.client.get_guild(int(SERVER_ID)).get_role(int(ADMINS_ROLE_ID))
    member_obj = globvars.client.get_guild(int(SERVER_ID)).get_member(user.id)
    await member_obj.add_roles(role)


async def remove_admin_role(user):
    """Remove the admin role from a member"""
    role = globvars.client.get_guild(int(SERVER_ID)).get_role(int(ADMINS_ROLE_ID))
    member_obj = globvars.client.get_guild(int(SERVER_ID)).get_member(user.id)
    await member_obj.remove_roles(role)


async def add_alive_role(member_obj):
    """Grant the alive role to a player"""
    alive_role = globvars.client.get_guild(int(SERVER_ID)).get_role(int(ALIVE_ROLE_ID))
    await member_obj.add_roles(alive_role)

    for lock_channel_id in LOCK_CHANNELS_ID:
        lock_channel = globvars.client.get_channel(lock_channel_id)
        await lock_channel.set_permissions(member_obj, read_messages=False)


async def remove_alive_role(member_obj, unlock=False):
    """Remove the alive role from a player"""
    alive_role = globvars.client.get_guild(int(SERVER_ID)).get_role(int(ALIVE_ROLE_ID))
    await member_obj.remove_roles(alive_role)

    if unlock:
        for lock_channel_id in LOCK_CHANNELS_ID:
            lock_channel = globvars.client.get_channel(lock_channel_id)
            await lock_channel.set_permissions(member_obj, read_messages=None)


async def add_dead_role(member_obj):
    """Grant the dead role to a player"""
    dead_role = globvars.client.get_guild(int(SERVER_ID)).get_role(int(DEAD_ROLE_ID))
    await member_obj.add_roles(dead_role)


async def remove_dead_role(member_obj, unlock=False):
    """Remove the dead role from a player"""
    dead_role = globvars.client.get_guild(int(SERVER_ID)).get_role(int(DEAD_ROLE_ID))
    await member_obj.remove_roles(dead_role)

    if unlock:
        for lock_channel_id in LOCK_CHANNELS_ID:
            lock_channel = globvars.client.get_channel(lock_channel_id)
            await lock_channel.set_permissions(member_obj, read_messages=None)


async def remove_all_alive_roles_pregame():
    """Remove the alive roles from all players during pregame"""
    for userid in globvars.master_state.pregame:
        member_obj = globvars.client.get_guild(int(SERVER_ID)).get_member(int(userid))
        await remove_alive_role(member_obj, unlock=True)


async def remove_all_alive_dead_roles_after_game():
    """Remove the alive and the dead roles from all players after the game is over"""
    for player in globvars.master_state.game.sitting_order:
        await remove_alive_role(player.user, unlock=True)
        await remove_dead_role(player.user, unlock=True)


async def lock_lobby():
    """Lock the lobby channel from non players"""
    server = globvars.client.get_guild(int(SERVER_ID))

    lobby_channel = globvars.client.get_channel(int(LOBBY_CHANNEL_ID))
    await lobby_channel.set_permissions(server.default_role, send_messages=False)


async def unlock_lobby():
    """Unlock the lobby channel to non players"""
    server = globvars.client.get_guild(int(SERVER_ID))

    lobby_channel = globvars.client.get_channel(int(LOBBY_CHANNEL_ID))
    await lobby_channel.set_permissions(server.default_role, send_messages=None)
