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
       
    #temperature converter
    @commands.command()
    async def temperature2(self, ctx, degrees: float, type: str):
        if type == 'C':
            await ctx.send(f'{degrees*9/5+32} F')
        elif type == 'F':
            await ctx.send(f'{(degrees-32)*5/9} C')

def setup(client):
    client.add_cog(Management(client))