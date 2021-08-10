import discord
import pytz
import zoneinfo
from discord.ext import commands
from datetime import datetime
from zoneinfo import ZoneInfo

class Time(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print('time.py cog loaded and ready to go!')

    #Time Converter
    @commands.command()
    async def timezone(self, ctx, time, timezone_in, timezone_out):
        abbreviations = {
            'AEDT' : 'Etc/GMT-11',
            'AEST' : 'Etc/GMT-10',
            'JST' : 'Etc/GMT-9',
            'AWST' : 'Etc/GMT-8',
            'EEST' : 'Etc/GMT-3',
            'EET' : 'Etc/GMT-2',
            'CEST' : 'Etc/GMT-2',
            'CET' : 'Etc/GMT-1',
            'BST' : 'Etc/GMT-1',
            'EDT' : 'Etc/GMT+4',
            'EST' : 'Etc/GMT+5',
            'CDT' : 'Etc/GMT+5',
            'CST' : 'Etc/GMT+6',
            'MDT' : 'Etc/GMT+6',
            'MST' : 'Etc/GMT+7',
            'PDT' : 'Etc/GMT+7',
            'PST' : 'Etc/GMT+8',
            'Etc/GMT-11' : 'AEDT',
            'Etc/GMT-10' : 'AEST',
            'Etc/GMT-9' : 'JST',
            'Etc/GMT-8' : 'AWST',
            'Etc/GMT-3' : 'EEST',
            'Etc/GMT-2' : 'EET',
            'Etc/GMT-2' : 'CEST',
            'Etc/GMT-1' : 'CET',
            'Etc/GMT-1' : 'BST',
            'Etc/GMT+4' : 'EDT',
            'Etc/GMT+5' : 'EST',
            'Etc/GMT+5' : 'CDT',
            'Etc/GMT+6' : 'CST',
            'Etc/GMT+6' : 'MDT',
            'Etc/GMT+7' : 'MST',
            'Etc/GMT+7' : 'PDT',
            'Etc/GMT+8' : 'PST',
        }
        
        try:
            timezone_in = abbreviations[f'{timezone_in}']
        except:
            ignore = 0
        try:
            finish1 = timezone_out
            timezone_out = abbreviations[f'{timezone_out}']
        except:
            finish1 = timezone_out

        time1: str = '0'
        a = time.find('am')
        if a != -1:
            time1 = time
            time = time[:-2]
        a1 = time.find('pm')
        if a1 != -1:
            time1 = time
            time = time[:-2]
        b = time.find(':')
        if b == -1:
            time = time + ":00"
        h, m = time.split(":")
        try:
            time = datetime(2017, 3, 3, int(h), int(m), tzinfo=ZoneInfo(f'{timezone_in}'))
            time = time.astimezone(ZoneInfo(f'{timezone_out}'))
            try:
                c = time1.find('am')
                if c != -1:
                    time = str(time.time())[:-3]
                    h, m = time.split(":")
                    if int(h) > 12:
                        h = int(h) - 12
                        time = datetime.strptime(f'{h}:{m}', "%I:%M")
                        await ctx.send(f'{str(time.time())[:-3]}pm {finish1}')
                    else:
                        time = datetime.strptime(f'{h}:{m}', "%I:%M")
                        await ctx.send(f'{str(time.time())[:-3]}am {finish1}')
                d = time1.find('pm')
                if d != -1:
                    time = str(time.time())[:-3]
                    h, m = time.split(":")
                    if int(h) > 12:
                        h = int(h) - 12
                        time = datetime.strptime(f'{h}:{m}', "%I:%M")
                        await ctx.send(f'{str(time.time())[:-3]}am {finish1}')
                    else:
                        time = datetime.strptime(f'{h}:{m}', "%I:%M")
                        await ctx.send(f'{str(time.time())[:-3]}pm {finish1}')
                if c == -1 and d == -1:
                    raise Exception("24h")
            except:
                await ctx.send(f'{str(time.time())[:-3]} {finish1}')
                
        except zoneinfo.ZoneInfoNotFoundError:
            await ctx.send('Can\'t find timezone. Check if the capitalization is correct?')

def setup(client):
    client.add_cog(Time(client))