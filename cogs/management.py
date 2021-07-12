import discord
import json
import requests
from discord.ext import commands

class Management(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print('management.py cog is ready.')

    #@commands.Cog.listener()
    #async def on_raw_reaction_add(payload):
    #    if payload.member.bot:
    #        pass
    #    else:
    #        if

    #
    #@commands.command()
    #async def reaction_role(self, ctx, message_id, number, *, args):
    #    if len(args) == number * 2:
    #        await commands.pg_con.execute("INSERT INTO reaction_roles (message_id) VALUES ($1)", message_id)
    #        for i in range(0, number):
    #            message_id.add_reaction(args[i*2+1])
    #            await commands.pg_con.execute("ALTER TABLE reaction_roles ADD $1 datatype varchar ADD $2 datatype varchar", f'role_{i}', f'emoji_{i}')
    #            await commands.pg_con.execute("INSERT INTO reaction_roles ($1, $2) VALUES ($3, $4)", f'role_{i}', f'emoji_{i}', args[i*2].id, args[i*2+1])

def setup(client):
    client.add_cog(Management(client))