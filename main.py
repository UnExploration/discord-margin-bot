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
from datetime import datetime

listen_channels = [823334410945691709]

# 823334410945691709 - Channel item_id for main discord 
load_dotenv()  
TOKEN = os.getenv('DISCORD_TOKEN') 
bot = commands.Bot(command_prefix="!")


# delete !command messages
# maybe move embed into object check for existing object in channel before making new object.
# last update being red to signify stopped. 

refreshDelay = 10 # in seconds as this is for asyncio.sleep
stopRefresh = False
minMargin = 40 #default margin requirments that is used to generate table
minVolume = 500000 #default volume requirements that is used to generate table
minRefreshTime = 1 #time in second for the embed refresh
maxRefreshTime = 300

minNumberValue = 1
maxNumberValue = 1000000000

# load the mapping file here so we only have to load it once
with open('remakeMapping.json','r') as myfile:
        mappingResponse = myfile.read()
mappingData = json.loads(mappingResponse) 
# mappingResponse['itemitem_id']['keys'] Itemitem_id is item_id of item we want. 
# Keys are data insitem_ide this dictionary 
# examine | members (either True or False) | highalch | lowalch | value | icon | name |
errorlist = [
    f'Embed exceeds 6000 Character limit. Please adjust settings. \n Current Minimum Margin : {minMargin} \n Current Minimum Volume : {minVolume}',
    f'Syntax -- !make <margin|volume|refreshtime> <int> --',
    f'Current minimum margin is {minNumberValue}',
    f'Current minimum and maximum volume is {minNumberValue} and {maxNumberValue}',
    f'Current minimum and maximum refresh time is {minRefreshTime} and {maxRefreshTime}'





]

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
async def stop(ctx):
    global stopRefresh
    stopRefresh = True



@bot.command(pass_context = True)
async def make(ctx): # set variables like Margin/volume/ 
    #!make margin 10   ex 
    #!make volume 4000 ex
    global minMargin; global minVolume; global refreshDelay; global minResfeshTime; global maxRefreshTime; global minNumberValue; global maxNumberValue
    splitmsg = ctx.message.content.split()  # [0] is !make
    valueToChange = str(splitmsg[1]).lower()
    if splitmsg[2].isnumeric():
        newNumericValue = int(splitmsg[2])
    else:

        await sendErrorEmbed(ctx,1)

        return # new value not a number
    if valueToChange != "margin" and valueToChange != "volume" and valueToChange != "refreshtime" and valueToChange != "refresh":

        await sendErrorEmbed(ctx,1)
        return # 
    elif valueToChange == "margin":
        if newNumericValue < minNumberValue:

            await sendErrorEmbed(ctx,2)
        else:
            minMargin = newNumericValue
    elif valueToChange == "volume":
        if newNumericValue > maxNumberValue or newNumericValue < minNumberValue:
            await sendErrorEmbed(ctx,3)
        else: 
            minVolume = newNumericValue
    elif valueToChange == "refreshtime":# #default 30

        if newNumericValue > maxRefreshTime or newNumericValue < minRefreshTime:
            await sendErrorEmbed(ctx,4)

        else:
            newNumericValue = refreshDelay
            
        #make a min and max refresh time.     
   
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
    
    if prices == "":
        prices          += '------'
        items           += '------'
        margins_volumes += '---------------------'




    
    
    priceEmbed.add_field(name = "Item" , value = items)
    priceEmbed.add_field(name = "Price", value = prices)
    priceEmbed.add_field(name = "Margin -- Volume", value = margins_volumes)
    priceEmbed.set_footer(text = f'Min Margin : {minMargin} Min Volume : {minVolume /1000}k')

    global errorlist
    if len(priceEmbed) > 6000: # work around for two tables? #check for length and sent two embeds? 
        await sendErrorEmbed(ctx,0)
        return
    else:
        embedToEdit = await ctx.send(embed = priceEmbed)
        asyncio.create_task(startUpdateLoop(embedToEdit))
    # sort by limit * margin?
    

async def startUpdateLoop(embedToEdit):
    global stopRefresh
    global refreshDelay
   
    while stopRefresh == False:
        await asyncio.sleep(refreshDelay)
        await updateEmbed(embedToEdit)

async def sendErrorEmbed(ctx, error): #error is a number that correlates to an entry in the error list
    global errorlist
    errorEmbed = discord.Embed(color = discord.colour.Color.dark_red())
    errorEmbed.description = errorlist[error]
    await ctx.send(embed = errorEmbed)



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
    
    if prices == "":
        prices          += '------'
        items           += '------'
        margins_volumes += '---------------------'

    newEmbed.add_field(name = "Item" , value = items)
    newEmbed.add_field(name = "Price", value = prices)
    newEmbed.add_field(name = "Margin -- Volume", value = margins_volumes)
    newEmbed.set_footer(text = f'Min Margin : {minMargin} Min Volume : {minVolume /1000}k   Time : {datetime.now().strftime("%H:%M:%S")}  ')



    global errorlist 

    # no check for embed over 6000 ******

    await embedToUpdate.edit(embed = newEmbed)


    


bot.run(TOKEN)
