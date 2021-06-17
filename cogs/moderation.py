import discord
import json
import asyncio
from discord.ext import commands
import os
from dotenv import load_dotenv

class Moderation(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print('moderation.py cog is ready.')

    #clear
    @commands.command()
    @commands.check_any(commands.is_owner(), commands.has_permissions(manage_messages=True))
    async def clear(self, ctx, amount=5):
        await ctx.channel.purge(limit=amount+1)
        await ctx.send(f"Deleted {amount} messages :)", delete_after=3)

    @clear.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('Please specify an amount to delete.')

    #kick
    @commands.command()
    @commands.check_any(commands.is_owner(), commands.has_permissions(kick_members=True))
    async def kick(self, ctx, member : discord.Member, *, reason=None):
        if member.id == os.getenv("Owner"):
            await ctx.send('Can\'t kick my owner')
        else:
            await member.kick(reason=reason)
            await ctx.send(f'Kicked {member.mention}')

    #ban
    @commands.command()
    @commands.check_any(commands.is_owner(), commands.has_permissions(ban_members=True))
    async def ban(self, ctx, member : discord.Member, *, reason=None):
        if member.id == os.getenv("Owner"):
            await ctx.send('Can\'t ban my owner')
        else:
            await member.ban(reason=reason)
            await ctx.send(f'Banned {member.mention}')

    #unban
    @commands.command()
    @commands.check_any(commands.is_owner(), commands.has_permissions(ban_members=True))
    async def unban(self, ctx, *, member):
        banned_users = await ctx.guild.bans()
        member_name, member_discriminator = member.split('#')
    
        for ban_entry in banned_users:
            user = ban_entry.user
        
            if (user.name, user.discriminator) == (member_name, member_discriminator):
                await ctx.guild.unban(user)
                await ctx.send(f'Unbanned {user.mention}')
                return

    #tempban
    class DurationConverter(commands.Converter):
        async def convert(self, ctx, argument):
            amount = argument[:-1]
            unit = argument[-1]

            if amount.isdigit() and unit in ['s', 'm', 'h']:
                return (int(amount), unit)

            raise commands.BadArgument(message='Not a valid duration')

    @commands.command()
    @commands.check_any(commands.is_owner(), commands.has_permissions(ban_members=True))
    async def tempban (self, ctx, member: commands.MemberConverter, duration: DurationConverter):
    
        multiplier = {'s': 1, 'm': 60, 'h': 3600}
        amount, unit = duration

        if member.id == os.getenv("Owner"):
            await ctx.send('Can\'t ban my owner')
        else:
            await ctx.guild.ban(member)
            await ctx.send(f'{member} has been banned for {amount}{unit}.')
            await asyncio.sleep(amount * multiplier[unit])
            await ctx.guild.unban(member)

def setup(client):
    client.add_cog(Moderation(client))