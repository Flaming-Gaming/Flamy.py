import discord
import json
import asyncpg
import os
from discord.ext import commands, tasks, ipc
from itertools import cycle
from quart import cli
from dotenv import load_dotenv

load_dotenv()

async def create_db_pool():
    PREFIXES = os.environ['DATABASE_URL']
    REACTIONS = os.environ['HEROKU_POSTGRESQL_OLIVE_URL']
    LEVELS = os.environ['HEROKU_POSTGRESQL_SILVER_URL']
    client.pg_con = await asyncpg.create_pool(PREFIXES)
    client.pg_con = await asyncpg.create_pool(REACTIONS)
    client.pg_con = await asyncpg.create_pool(LEVELS)

class MyBot(commands.Bot):

	def __init__(self,*args,**kwargs):
		super().__init__(*args,**kwargs)

		self.ipc = ipc.Server(self, secret_key = "lol")

	async def on_ready(self):
		print("Bot is ready.")

	async def on_ipc_ready(self):
		print("Ipc server is ready.")

	async def on_ipc_error(self, endpoint, error):
		print(endpoint, "raised", error)

async def get_prefix(client, message):
    guild_id = str(message.guild.id)
    prefix = await client.pg_con.fetchrow("SELECT * FROM prefixes WHERE guild_id = $1", guild_id)
    return prefix['prefix']

client = MyBot(command_prefix = get_prefix, owner_id = int(os.getenv("Owner")))
#client.remove_command('help')
#status = cycle(['wip', 'in the making'])

@client.ipc.route()
async def get_guild_count(data):
	return len(client.guilds)

@client.ipc.route()
async def get_guild_ids(data):
	final = []
	for guild in client.guilds:
		final.append(guild.id)
	return final

@client.ipc.route()
async def get_guild(data):
	guild = client.get_guild(data.guild_id)
	if guild is None: return None

	guild_data = {
		"name": guild.name,
		"id": guild.id,
		"prefix" : "."
	}

	return guild_data

@client.event
async def on_ready():
    await client.change_presence(status=discord.Status.online, activity = discord.Activity(name = f'over {len(client.guilds)} servers', type = discord.ActivityType.watching))
#    change_status.start()
    print('Bot is online.')

#@tasks.loop(seconds=30)
#async def change_status():
#    await client.change_presence(status=discord.Status.online, activity = discord.Activity(name = f'over {str(len(client.guilds))} servers', type = discord.ActivityType.watching))

@client.listen('on_guild_join')
async def on_join(guild):
    current_guilds = len(client.guilds)
    await client.change_presence(status=discord.Status.online, activity = discord.Activity(name = f'over {current_guilds} servers', type = discord.ActivityType.watching))

@client.listen('on_guild_remove')
async def on_leave(guild):
    current_guilds = len(client.guilds)
    await client.change_presence(status=discord.Status.online, activity = discord.Activity(name = f'over {current_guilds} servers', type = discord.ActivityType.watching))

#prefix
@client.event
async def on_guild_join(guild):
    guild_id = str(guild.id)
    await client.pg_con.execute("INSERT INTO prefixes (guild_id, prefix) VALUES ($1, '.')", guild_id)

@client.event
async def on_guild_remove(guild):
    guild_id = str(guild.id)
    await client.pg_con.execute("DELETE FROM prefixes WHERE guild_id = $1", guild_id)

@client.command()
@commands.check_any(commands.is_owner(), commands.has_permissions(manage_guild=True))
async def change_prefix(ctx, prefix):
    guild_id = str(ctx.guild.id)
    await client.pg_con.execute("UPDATE prefixes SET prefix = $1 WHERE guild_id = $2", prefix, guild_id)
    await ctx.send(f'Prefix changed to: {prefix}')

#@client.command()
#async def help(ctx):


#exceptions
#@client.event
#async def on_command_error(ctx, error):
#    if isinstance(error, commands.MissingRequiredArgument):
#        await ctx.send('Please pass in all required arguments.')
#    if isinstance(error, commands.CommandNotFound):
#        await ctx.send('Invalid command.')

#cogs
@client.command()
@commands.is_owner()
async def load(ctx, extension):
    client.load_extension(f'cogs.{extension}')
    await ctx.send(f'{extension} loaded')

@client.command()
@commands.is_owner()
async def unload(ctx, extension):
    client.unload_extension(f'cogs.{extension}')
    await ctx.send(f'{extension} unloaded')

@client.command()
@commands.is_owner()
async def reload(ctx, extension):
    client.unload_extension(f'cogs.{extension}')
    client.load_extension(f'cogs.{extension}')  
    await ctx.send(f'{extension} reloaded')  

for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')

client.ipc.start()
client.loop.run_until_complete(create_db_pool())
client.run(os.getenv("Token"))
