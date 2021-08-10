import discord
import json
import requests
from discord.ext import commands
import os
from dotenv import load_dotenv

class Converters(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print('converters.py cog loaded and ready to go!')

    #distance converter
    @commands.command()
    async def distance(self, ctx, distance: float, unit: str):
        if unit == "km":
            distance = distance / 1.609
            await ctx.send(f'{distance:0.5f} mi')
        elif unit == "mi":
            distance = distance * 1.609
            await ctx.send(f'{distance:0.5f} km')

    #height converter
    @commands.command()
    async def height(self, ctx, height, unit: str):
        if unit == "m":
            a = height.find('.')
            if a == -1:
                m = height
                cm = 0
            else:
                m, cm = height.split('.')
            inch = (float(m) * 100 + float(cm)) / 2.54
            ft = inch // 12
            inch = inch % 12
            await ctx.send(f'{round(ft)}\'{round(inch)} ft')
        elif unit == "ft":
            a = height.find('\'')
            if a == -1:
                ft = height
                inch = 0
            else:
                ft, inch = height.split('\'')
            cm = (float(ft) * 12 + float(inch)) * 2.54
            m = cm // 100
            cm = cm % 100
            await ctx.send(f'{round(m)}.{round(cm):02d} m')
        elif unit == "cm":
            cm = float(height)
            inch = cm / 2.54
            await ctx.send(f'{inch:0.5f} in')
        elif unit == "in":
            inch = float(height)
            cm = inch * 2.54
            await ctx.send(f'{cm:0.5f} cm')

    #currency converter
    @commands.command()
    async def currency(self, ctx, amount: float, currency_in: str, currency_out: str):
        currency_in = currency_in.upper()
        currency_out = currency_out.upper()
        response = requests.get(os.getenv("Currency_API"))
        if response and response.text:
            result = json.loads(response.text)
            if result["success"] == True:   
                if currency_in != "EUR":
                    amount = amount / result["rates"][f"{currency_in}"]
                amount = round(amount * result["rates"][f"{currency_out}"], 2)
                await ctx.send(f'{amount} {currency_out}')
        else:
            await ctx.send(f'Bad response from the API {response.success}')
            
    #temperature converter
    @commands.command()
    async def temperature(self, ctx, degrees: float, unit: str):
        if unit == 'C':
            await ctx.send(f'{degrees*9/5+32:0.5f} F')
        elif unit == 'F':
            await ctx.send(f'{(degrees-32)*5/9:0.5f} C')

def setup(client):
    client.add_cog(Converters(client))