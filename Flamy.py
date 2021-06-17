import discord
import json
import os
from discord.ext import commands, tasks, ipc
from itertools import cycle

from quart import cli

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

with open('config.json', 'r') as f:
    config = json.load(f)

def get_prefix(client, message):
    with open('prefixes.json', 'r') as f:
        prefixes = json.load(f)

    return prefixes[str(message.guild.id)]

client = MyBot(command_prefix = get_prefix, owner_id = config["Owner"])
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

@client.event
async def on_ready():
    await client.change_presence(status=discord.Status.online, activity = discord.Activity(name = '.help', type = discord.ActivityType.watching))
#    change_status.start()
    print('Bot is online.')

#@tasks.loop(seconds=30)
#async def change_status():
#    await client.change_presence(activity=discord.Game(next(status)))

#prefix
@client.event
async def on_guild_join(guild):
    with open('prefixes.json', 'r') as f:
        prefixes = json.load(f)

    prefixes[str(guild.id)] = '.'

    with open('prefixes.json', 'w') as f:
        json.dump(prefixes, f, indent=4)

@client.event
async def on_guild_remove(guild):
    with open('prefixes.json', 'r') as f:
        prefixes = json.load(f)

    prefixes.pop(str(guild.id))

    with open('prefixes.json', 'w') as f:
        json.dump(prefixes, f, indent=4)

@client.command()
@commands.check_any(commands.is_owner(), commands.has_permissions(manage_guild=True))
async def change_prefix(ctx, prefix):
    with open('prefixes.json', 'r') as f:
        prefixes = json.load(f)

    prefixes[str(ctx.guild.id)] = prefix

    with open('prefixes.json', 'w') as f:
        json.dump(prefixes, f, indent=4)

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
client.run(config["Token"])
client.run(os.environ["Token"])
