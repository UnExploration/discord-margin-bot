#bot.py
import os
import time
import re
import discord
import requests
import json
from dotenv import load_dotenv 
from discord.ext import commands
from discord.ext.commands import Bot
listen_channels = [822943904109166592]
itemList = []
# 822943904109166592 - Channel ID for main discord 
load_dotenv()  
TOKEN = os.getenv('DISCORD_TOKEN') 
bot = commands.Bot(command_prefix="!")

# Steps
# Aqquire Data - Refresh 1 min *
# Sort Data 
# Put Data in table
# Notification? 
# Future




# load the mapping file here so we only have to load it once
with open('remakeMapping.json','r') as mappingFile:
        mappingData = mappingFile.read()
mappingResponse = json.loads(mappingData) 
# mappingResponse['itemID']['keys'] ItemID is ID of item we want. 
# Keys are data inside this dictionary 
# examine | members (either True or False) | highalch | lowalch | value | icon | name |


class Item: # useless? 
    def __init__(self,itemId, highPrice, lowPrice, highTime, lowTime, highAlch, volume):
        self.itemId = itemId
        self.highPrice = highPrice #buy
        self.lowPrice = lowPrice #sell
        self.highTime = highTime #UNIX
        self.lowTime = lowTime
        self.highAlch = highAlch
        self.volume = volume






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
    volumeUrl = 'https://prices.runescape.wiki/api/v1/osrs/volumes'
    latestUrl = 'ttps://prices.runescape.wiki/api/v1/osrs/latest'  #requested User Agent for the API
    headers = {
        'User-Agent': 'Margin Bot',
        'From': 'UnExploration@gmail.com'
    }
    latestResponse = requests.get(latestUrl,headers = headers) 
    volumeResponse = requests.get(volumeUrl,headers = headers)

    
    

    
    


    # print(response.json()) # we get the json back
    
    volumeData = volumeResponse.json()
    volumeData = volumeData['data']



    obj = latestResponse.json()
    obj = obj['data']
    x = 0
    for each in obj:
        if obj[each]['high'] is not None and obj[each]['low'] is not None:
           if obj[each]['high'] - obj[each]['low'] > 40:
                x += 1
                if volumeData.get(each) is not None and volumeData.get(each) > 1000000 :
                    print(f'{each} ---- {volumeData[each]}')
    
    print(x)
    #text = json.dumps(obj,sort_keys=True,indent=4)
    #print(text)
    #collect data { data { 2:2} }
    # map data together
    # pass to data visual



async def main():
    #retrive data 
    return

bot.run(TOKEN)