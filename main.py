#bot.py
import json
import os
import re
import time

import discord
import asyncio
import threading
import requests
from discord.ext import commands
from discord.ext.commands import Bot
from dotenv import load_dotenv

listen_channels = [823334410945691709]

# 823334410945691709 - Channel item_id for main discord 
load_dotenv()  
TOKEN = os.getenv('DISCORD_TOKEN') 
bot = commands.Bot(command_prefix="!")

# Steps
# Aqquire Data - Refresh 1 min *
# Sort Data 
# Put Data in table
# Notification? 
# Future
refreshDelay = 30 # in seconds as this is for asyncio.sleep
stopRefresh = False
minMargin = 40 #default margin requirments
minVolume = 500000 #default volume requirements

# load the mapping file here so we only have to load it once
with open('remakeMapping.json','r') as myfile:
        mappingResponse = myfile.read()
mappingData = json.loads(mappingResponse) 
# mappingResponse['itemitem_id']['keys'] Itemitem_id is item_id of item we want. 
# Keys are data insitem_ide this dictionary 
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
async def make(ctx): # set variables like Margin/volume/ 
    #!make margin 10   ex 
    #!make volume 4000 ex
    global minMargin
    global minVolume
    splitmsg = ctx.message.content.split()  # [0] is !make
    valueToChange = str(splitmsg[1]).lower()
    if splitmsg[2].isnumeric():
        newNumericValue = int(splitmsg[2])
        if newNumericValue > 100000000 or newNumericValue < 1:
            errorEmbed = discord.Embed(color = discord.colour.Color.dark_red())
            errorEmbed.description = 'new value too large or below 1'
            errorEmbed.set_author(name = "Error")
            await ctx.send(embed = errorEmbed)
    else:
        return # new value not a number
    if valueToChange != "margin" and valueToChange != "volume" and valueToChange != "refreshtime" and valueToChange != "refresh":
        return # 
    elif valueToChange == "margin":
        #changing minMargin
        minMargin = newNumericValue
    elif valueToChange == "volume":
        #changing minVolume   
        minVolume = newNumericValue
    elif valueToChange == "refreshtime":# #default 30
        return
        #make a min and max refresh time.     
    elif valueToChange == "refresh":
        return
        #turn refresh on or off
    return

@bot.command()
async def refreshData(): # here we update global jsons
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
async def create(ctx): #this creates the intial embed and starts the fresh loop

    global minMargin; global minVolume; global latestData; global mappingData; global volumeData

    priceEmbed = discord.Embed(color = discord.colour.Color.dark_purple())
    # priceEmbed.set_author(name = "OSRS Margin Bot")
    await refreshData() # this should update global variables 
    items   = "" # name
    prices  = "" # buy and sell prices
    margins_volumes = "" #magrin
    # volumes  = "" #volume of item
    itemList = []
    for item_id in latestData:
        if latestData[item_id]['high'] is not None and latestData[item_id]['low'] is not None:
            if latestData[item_id]['high'] - latestData[item_id]['low'] > minMargin:
                currentmargin = latestData[item_id]['high'] - latestData[item_id]['low']
                if volumeData.get(item_id) is not None and volumeData.get(item_id) > minVolume:
                    itemList.append({
                        "item_id": item_id,
                           "name": mappingData[item_id]['name'],
                          "limit": mappingData[item_id]['limit'],
                           "high": latestData[item_id]['high'],
                            "low": latestData[item_id]['low'],
                         "margin": currentmargin,
                         "volume": round(volumeData.get(item_id)/1000)
                })
    itemList.sort(key=lambda item:item.get("margin"))
    itemList.reverse()
    for each in itemList:

        items += f'{each["name"]} \n'
        prices += f'B: {each["high"]} -- S: {each["low"]} \n'
        margins_volumes += f'{each["margin"]} - {each["volume"]}k \n'





    
    
    priceEmbed.add_field(name = "Item" , value = items)
    priceEmbed.add_field(name = "Price", value = prices)
    priceEmbed.add_field(name = "Margin -- Volume", value = margins_volumes)
    priceEmbed.set_footer(text = f'Min Margin : {minMargin} Min Volume : {minVolume /1000}k')

    
    if len(priceEmbed) > 6000: # work around for two tables? #check for length and sent two embeds? 
        errorEmbed = discord.Embed(color = discord.colour.Color.dark_red())
        errorEmbed.description = f'Embed exceeds 6000 Character limit. Please adjust settings. \n Current Minimum Margin : {minMargin} \n Current Minimum Volume : {minVolume}'
        errorEmbed.set_author(name = "Error")
        await ctx.send(embed = errorEmbed)
        return
    else:
        await ctx.send(embed = priceEmbed)
        
    # sort by limit * margin?
    

async def startUpdateLoop(embedToEdit):
    global stopRefresh
    global refreshDelay
   
    while stopRefresh == False:
        await asyncio.sleep(refreshDelay)
        await updateEmbed(embedToEdit)


async def updateEmbed(embedToUpdate):
    global minMargin; global minVolume; global latestData; global mappingData; global volumeData

    await refreshData()

    newEmbed = discord.Embed(color = discord.colour.Color.green())


    items   = "" # name
    prices  = "" # buy and sell prices
    margins_volumes = "" #magrin
    # volumes  = "" #volume of item
    itemList = []

    for item_id in latestData:
        if latestData[item_id]['high'] is not None and latestData[item_id]['low'] is not None:
            if latestData[item_id]['high'] - latestData[item_id]['low'] > minMargin:
                currentmargin = latestData[item_id]['high'] - latestData[item_id]['low']
                if volumeData.get(item_id) is not None and volumeData.get(item_id) > minVolume:
                    itemList.append({
                        "item_id": item_id,
                           "name": mappingData[item_id]['name'],
                          "limit": mappingData[item_id]['limit'],
                           "high": latestData[item_id]['high'],
                            "low": latestData[item_id]['low'],
                         "margin": currentmargin,
                         "volume": round(volumeData.get(item_id)/1000)
                })
    itemList.sort(key=lambda item:item.get("margin"))
    itemList.reverse()
    for each in itemList:

        items += f'{each["name"]} \n'
        prices += f'B: {each["high"]} -- S: {each["low"]} \n'
        margins_volumes += f'{each["margin"]} - {each["volume"]}k \n'




    await embedToUpdate.edit(embed = newEmbed)


bot.run(TOKEN)
