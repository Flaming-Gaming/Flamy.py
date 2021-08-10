import discord
import json
from discord.errors import InvalidArgument
import requests
from discord.ext import commands
from datetime import datetime

class Management(commands.Cog):

    def __init__(self, client):
        self.client = client

    async def cog_check(self, ctx):
        return await commands.guild_only().predicate(ctx)

    @commands.Cog.listener()
    async def on_ready(self):
        print('management.py cog loaded and ready to go!')

    #@commands.command()
    #async def server_info(self, ctx):
    #    guild  = ctx.message.guild
    #    embed = discord.Embed(colour = ctx.author.color, description = guild.description if guild.description != None else '', timestamp = ctx.message.created_at)
    #    embed.set_author(name = guild.name, icon_url = guild.icon_url)
    #    embed.set_thumbnail(url = guild.banner_url)
    #    embed.add_field(name = 'Owner', value = guild.owner, inline = True)
    #    embed.add_field(name = 'Created', value = guild.created_at.strftime("on %d.%m.%Y\nat %H:%M:%S"), inline = True)
    #    await ctx.send(embed = embed)

        #guild  = await self.client.fetch_guild('bot has to be in this server :(')

    #reaction roles
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.member.bot:
            pass
        else:
            emojirole = await self.client.pg_con2.fetchrow("SELECT * FROM reactions WHERE message_id = $1", payload.message_id)
            for i in range(1, 11):
                if emojirole[i * 2] == str(payload.emoji):
                    role = discord.utils.get(self.client.get_guild(payload.guild_id).roles, id = emojirole[i * 2 - 1])
                    if role is not None:
                        await payload.member.add_roles(role)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        emojirole = await self.client.pg_con2.fetchrow("SELECT * FROM reactions WHERE message_id = $1", payload.message_id)
        for i in range(1, 11):
            if emojirole[i * 2] == str(payload.emoji):
                role = discord.utils.get(self.client.get_guild(payload.guild_id).roles, id = emojirole[i * 2 - 1])
                if role is not None:
                    await self.client.get_guild(payload.guild_id).get_member(payload.user_id).remove_roles(role)

    @commands.Cog.listener()
    async def on_raw_message_delete(self, payload):
        await self.client.pg_con2.execute("DELETE FROM reactions WHERE message_id = $1", payload.message_id)

    @commands.Cog.listener()
    async def on_raw_bulk_message_delete(self, payload):
        for id in payload.message_ids:
            await self.client.pg_con2.execute("DELETE FROM reactions WHERE message_id = $1", id)

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def reaction_role(self, ctx, message: discord.Message, role_1: discord.Role, emoji_1, role_2: discord.Role = None, emoji_2 = None, role_3: discord.Role = None, emoji_3 = None, role_4: discord.Role = None, emoji_4 = None, role_5: discord.Role = None, emoji_5 = None, role_6: discord.Role = None, emoji_6 = None, role_7: discord.Role = None, emoji_7 = None, role_8: discord.Role = None, emoji_8 = None, role_9: discord.Role = None, emoji_9 = None, role_10: discord.Role = None, emoji_10 = None):
        emoji = [emoji_1, emoji_2, emoji_3, emoji_4, emoji_5, emoji_6, emoji_7, emoji_8, emoji_9, emoji_10]
        await self.client.pg_con2.execute("INSERT INTO reactions (message_id, role_1, emoji_1, role_2, emoji_2, role_3, emoji_3, role_4, emoji_4, role_5, emoji_5, role_6, emoji_6, role_7, emoji_7, role_8, emoji_8, role_9, emoji_9, role_10, emoji_10) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18, $19, $20, $21)", message.id, role_1.id, emoji_1, role_2.id if role_2 is not None else None, emoji_2, role_3.id if role_3 is not None else None, emoji_3, role_4.id if role_4 is not None else None, emoji_4, role_5.id if role_5 is not None else None, emoji_5, role_6.id if role_6 is not None else None, emoji_6, role_7.id if role_7 is not None else None, emoji_7, role_8.id if role_8 is not None else None, emoji_8, role_9.id if role_9 is not None else None, emoji_9, role_10.id if role_10 is not None else None, emoji_10)
        for i in range(0, 10):
            try:
                await message.add_reaction(emoji[i])
            except InvalidArgument:
                continue
        await ctx.message.delete(delay = 3)

def setup(client):
    client.add_cog(Management(client))