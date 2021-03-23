#bot.py
import json
import os
import re
import time

import discord
import requests
from discord.ext import commands
from discord.ext.commands import Bot
from dotenv import load_dotenv

listen_channels = [823334410945691709]
itemList = []
# 823334410945691709 - Channel ID for main discord 
load_dotenv()  
TOKEN = os.getenv('DISCORD_TOKEN') 
bot = commands.Bot(command_prefix="!")

# Steps
# Aqquire Data - Refresh 1 min *
# Sort Data 
# Put Data in table
# Notification? 
# Future


minMargin = 40 #default margin requirments
minVolume = 500000 #default volume requirements

# load the mapping file here so we only have to load it once
with open('remakeMapping.json','r') as myfile:
        mappingResponse = myfile.read()
mappingData = json.loads(mappingResponse) 
# mappingResponse['itemID']['keys'] ItemID is ID of item we want. 
# Keys are data inside this dictionary 
# examine | members (either True or False) | highalch | lowalch | value | icon | name |


volumeUrl = 'https://prices.runescape.wiki/api/v1/osrs/volumes'
latestUrl = 'https://prices.runescape.wiki/api/v1/osrs/latest'  #requested User Agent for the API
headers = {
    'User-Agent': 'Margin Bot',
    'From': 'UnExploration@gmail.com'
}

latestResponse = requests.get(latestUrl,headers = headers) 
latestData = latestResponse.json()
latestData = latestData['data']
#####################
volumeResponse = requests.get(volumeUrl,headers = headers)
volumeData = volumeResponse.json()
volumeData = volumeData['data']

@bot.event
async def on_ready():
    print('Bot Online')


@bot.event
async def on_message(ctx):
    if ctx.channel.id not in listen_channels:
        return
    await bot.process_commands(message = ctx)

@bot.command(pass_context = True)
async def vSet(ctx): # set variables like Margin/volume/ 
    return

@bot.command(pass_context = True)
async def refreshData(ctx): # here we update global jsons
    global latestResponse 
    global volumeResponse 
    latestResponse = requests.get(latestUrl,headers = headers)
    volumeResponse = requests.get(volumeUrl,headers = headers)
    global volumeData
    global latestData
    volumeData = volumeResponse.json()
    volumeData = volumeData['data']

    latestData = latestResponse.json()
    latestData = latestData['data']
    

@bot.command(pass_context = True)
async def start(ctx):
    global latestData
    await refreshData(ctx)

    #latestData = latestResponse.json()
    #latestData = latestData['data']
    x = 0
    for each in latestData:
        if latestData[each]['high'] is not None and latestData[each]['low'] is not None:
           if latestData[each]['high'] - latestData[each]['low'] > 40:
                x += 1
                if volumeData.get(each) is not None and volumeData.get(each) > 500000 :
                    print(f'ID:{each} ---- Buy:{latestData[each]["high"]} Sell:{latestData[each]["low"]}---- Volume:{volumeData[each]} ----- Name:{mappingData[each]["name"]}')
    print('---------------')

@bot.command(pass_context = True)
async def create(ctx):

    global minMargin
    global minVolume
    priceEmbed = discord.Embed(color = discord.colour.Color.dark_purple())
    priceEmbed.set_author(name = "OSRS Margin Bot")
    await refreshData(ctx) # this should update global variables 
    items   = "" #name
    prices  = "" # buy and sell prices
    margins_volumes = "" #magrin
    volumes  = "" #volume of item
    
    for each in latestData:
        if latestData[each]['high'] is not None and latestData[each]['low'] is not None:
            if latestData[each]['high'] - latestData[each]['low'] > minMargin:
                currentmargin = latestData[each]['high'] - latestData[each]['low']
                if volumeData.get(each) is not None and volumeData.get(each) > minVolume:
                    items   += f'{mappingData[each]["name"]} \n '
                    prices  += f'Buy:{latestData[each]["high"]} - Sell:{latestData[each]["low"]} \n'
                    margins_volumes += f'{currentmargin} --- {volumeData[each]}\n'
                    # volumes  += f'{volumeData[each]} \n '

    priceEmbed.add_field(name = "Items" , value = items)
    priceEmbed.add_field(name = "Prices", value = prices)
    priceEmbed.add_field(name = "Margin --- Volume", value = margins_volumes)
    priceEmbed.set_footer(text = f'Min Margin : {minMargin} Min Volume : {minVolume}')
    # priceEmbed.add_field(name = "Volume", value = volumes, inline = True)

    await ctx.send(embed = priceEmbed)







bot.run(TOKEN)
