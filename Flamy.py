import discord
from discord import Intents
import asyncpg
import os
from discord.ext import commands, ipc
from dotenv import load_dotenv

load_dotenv()

#databases
async def create_db_pool():
    PREFIXES = os.environ['DATABASE_URL']
    REACTIONS = os.environ['HEROKU_POSTGRESQL_OLIVE_URL']
    LEVELS = os.environ['HEROKU_POSTGRESQL_SILVER_URL']
    SPLATNET = os.environ['HEROKU_POSTGRESQL_BRONZE_URL']
    client.pg_con1 = await asyncpg.create_pool(PREFIXES)
    client.pg_con2 = await asyncpg.create_pool(REACTIONS)
    client.pg_con3 = await asyncpg.create_pool(LEVELS)
    client.pg_con4 = await asyncpg.create_pool(SPLATNET)

class Flamy(commands.Bot):

	def __init__(self,*args,**kwargs):
		super().__init__(*args,**kwargs)

		#self.ipc = ipc.Server(self, secret_key = "lol")

	async def on_ready(self):
		print("Bot is ready.")

	#async def on_ipc_ready(self):
	#	print("Ipc server is ready.")

	#async def on_ipc_error(self, endpoint, error):
	#	print(endpoint, "raised", error)

#prefix
async def get_prefix(client, message):
    try:
        guild_id = str(message.guild.id)
        prefixes = await client.pg_con1.fetchrow("SELECT * FROM prefixes WHERE guild_id = $1", guild_id)
        return prefixes['prefix']
    except AttributeError:
        default_prefix = '.'
        return default_prefix

client = Flamy(command_prefix = get_prefix, intents = Intents().all(), owner_id = int(os.getenv("Owner")))

async def status():
    await client.wait_until_ready()
    await client.change_presence(status=discord.Status.online, activity = discord.Activity(name = f'over {len(client.guilds)} servers', type = discord.ActivityType.watching))

client.loop.create_task(status())

#@client.ipc.route()
#async def get_guild_count(data):
#	return len(client.guilds)

#@client.ipc.route()
#async def get_guild_ids(data):
#	final = []
#	for guild in client.guilds:
#		final.append(guild.id)
#	return final

#@client.ipc.route()
#async def get_guild(data):
#	guild = client.get_guild(data.guild_id)
#	if guild is None: return None

#	guild_data = {
#		"name": guild.name,
#		"id": guild.id,
#		"prefix" : "."
#	}

#	return guild_data

@client.event
async def on_ready():
    print('Flamy is awake!!')

#status
@client.listen('on_guild_join')
async def on_join(guild):
    current_guilds = len(client.guilds)
    await client.change_presence(status=discord.Status.online, activity = discord.Activity(name = f'over {current_guilds} servers', type = discord.ActivityType.watching))

@client.listen('on_guild_remove')
async def on_leave(guild):
    current_guilds = len(client.guilds)
    await client.change_presence(status=discord.Status.online, activity = discord.Activity(name = f'over {current_guilds} servers', type = discord.ActivityType.watching))

#delete dm
@client.command()
@commands.dm_only()
async def delete(ctx, range: int):
    async for message in ctx.channel.history(limit=range+1):
        if message.author == client.user:
            await message.delete()
            await ctx.send(f"Deleted message :)", delete_after=3)

#@client.command()
#@commands.dm_only()
#async def d(ctx, message_id):
#    message = await ctx.channel.fetch_message(message_id)
#    await message.delete()

#prefix_edit
@client.event
async def on_guild_join(guild):
    guild_id = str(guild.id)
    await client.pg_con1.execute("INSERT INTO prefixes (guild_id, prefix) VALUES ($1, '.')", guild_id)

@client.event
async def on_guild_remove(guild):
    guild_id = str(guild.id)
    await client.pg_con1.execute("DELETE FROM prefixes WHERE guild_id = $1", guild_id)

@client.command()
@commands.guild_only()
@commands.check_any(commands.is_owner(), commands.has_permissions(manage_guild=True))
async def change_prefix(ctx, prefix):
    guild_id = str(ctx.guild.id)
    await client.pg_con1.execute("UPDATE prefixes SET prefix = $1 WHERE guild_id = $2", prefix, guild_id)
    await ctx.send(f'Prefix changed to: {prefix}')

#leave
@client.command()
@commands.guild_only()
@commands.check_any(commands.is_owner(), commands.has_permissions(manage_guild=True))
async def leave(ctx):
    try:
        guild_id = str(ctx.message.guild.id)
        await client.pg_con2.execute("DELETE FROM reactions WHERE guild_id = $1", guild_id)
        await client.pg_con3.execute("DELETE FROM levels WHERE guild_id = $1", guild_id)
    except:
        print('no levels/reactions data for the server')
    else:
        print('levels/reactions data deleted')
    finally:
        await ctx.send('Thanks for having me!')
        await ctx.guild.leave()

#exceptions
#@client.event
#async def on_command_error(ctx, error):
#    if isinstance(error, commands.MissingRequiredArgument):
#        await ctx.send('Please pass in all required arguments.')
#    if isinstance(error, commands.CommandNotFound):
#        await ctx.send('Invalid command.')

#@client.command()
#@commands.is_owner()
#async def announce(ctx, *, announcement):
#    for guild in client.guilds:
#        for channel in guild.channels:
#            try:
#                await channel.send(announcement)
#            except Exception:
#                continue
#            else:
#                break

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

#client.ipc.start()
client.loop.run_until_complete(create_db_pool())
client.run(os.getenv("Token"))
