import discord
import json
import random
from discord.ext import commands
from datetime import datetime

class Fun(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print('fun.py cog is ready.')

    #level system
    async def level_up(self, user):
        current_xp = user['xp']
        current_level = user['level']
        if current_level <= 16 and current_xp + 1 >= (current_level + 1) ** 2 + 6 * (current_level + 1):
            await self.client.pg_con3.execute("UPDATE levels SET level = $1 WHERE user_id = $2 AND guild_id = $3", current_level + 1, user['user_id'], user['guild_id'])
            return True
        elif current_level >= 17 and current_level <= 31 and current_xp + 1 >= 2.5 * (current_level + 1) ** 2 - 40.5 * (current_level + 1) + 360:
            await self.client.pg_con3.execute("UPDATE levels SET level = $1 WHERE user_id = $2 AND guild_id = $3", current_level + 1, user['user_id'], user['guild_id'])
            return True
        elif current_level >= 32 and current_xp + 1 >= 4.5 * (current_level + 1) ** 2 - 162.5 * (current_level + 1) + 2220:
            await self.client.pg_con3.execute("UPDATE levels SET level = $1 WHERE user_id = $2 AND guild_id = $3", current_level + 1, user['user_id'], user['guild_id'])
            return True
        else:
            return False

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.client.user:
            return

        author_id = str(message.author.id)
        guild_id = str(message.guild.id)
        user = await self.client.pg_con3.fetch("SELECT * FROM levels WHERE user_id = $1 AND guild_id = $2", author_id, guild_id)
        if not user:
            await self.client.pg_con3.execute("INSERT INTO levels (user_id, guild_id, level, xp) VALUES ($1, $2, 0, 0)", author_id, guild_id)
        user = await self.client.pg_con3.fetchrow("SELECT * FROM levels WHERE user_id = $1 AND guild_id = $2", author_id, guild_id)
        if random.random() <= 0.05:
            RANDOM = random.randrange(1, 11)
        else:
            RANDOM = random.randrange(1, 4)
        await self.client.pg_con3.execute("UPDATE levels SET xp = $1 WHERE user_id = $2 AND guild_id = $3", user['xp'] + 1, author_id, guild_id)
        if await self.level_up(user):
            await message.channel.send(f'{message.author.mention} is now level {user["level"] + 1}')
            return

    @commands.command()
    async def level(self, ctx):
        await ctx.send('h')

    #8ball
    @commands.command(aliases=['8ball', 'test8'])
    async def _8ball(self, ctx, *, question):
        responses = ['It is certain.',
                    'It is decidedly so.',
                    'Without a doubt.',
                    'Yes – definitely.',
                    'You may rely on it.',
                    'As I see it, yes.',
                    'Most likely.',
                    'Outlook good.',
                    'Yes.',
                    'Signs point to yes.',
                    'Reply hazy, try again.',
                    'Ask again later.',
                    'Better not tell you now.',
                    'Cannot predict now.',
                    'Concentrate and ask again.',
                    "Don't count on it.",
                    'My reply is no.',
                    'My sources say no.',
                    'Outlook not so good.',
                    'Very doubtful.']
        await ctx.send(f'Question: {question}\nAnswer: {random.choice(responses)}')

def setup(client):
    client.add_cog(Fun(client))