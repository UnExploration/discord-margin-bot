#bot.py
import os
import time
import re
import discord
import requests
from dotenv import load_dotenv
from datahandler import *  # important all functions from our datahandler python file
listen_channels = [822943904109166592]

# 822943904109166592 - Channel ID for main discord 
load_dotenv()  
TOKEN = os.getenv('DISCORD_TOKEN') 
bot - commands.Bot(command_prefix="!e")

# Steps
# Aqquire Data - Refresh 1 min
# Sort Data 
# Put Data in table
# Notification? 
# Future


@bot.event
async def on_ready():
    print('Bot Online')


@bot.event
async def on_message(ctx):
    if ctx.channel.id not in listen_channels:
        return
    await bot.process_commands(message = ctx)


@bot.command(pass_context = True)
async def start(ctx):
    url = "https://prices.runescape.wiki/api/v1/osrs/latest"  #requested User Agent for the API
    headers = {
        'User-Agent': 'Margin Bot',
        'From': 'UnExploration#6612'
    }
    response = requests.get(url,headers=headers)
    print(response.status_code)
    #collect data
    # map data together
    # pass to data visual



async def main():
    #retrive data 


bot.tun(TOKEN)