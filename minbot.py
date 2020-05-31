# bot.py
import os

import discord
import random
import asyncio
import giphy_client
import pymongo

from discord.ext import commands
from dotenv import load_dotenv
from giphy_client.rest import ApiException
from pymongo import MongoClient

# setup
load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
GIPHY_TOKEN = os.getenv('GIPHY_TOKEN')
MONGO_URL = os.getenv('MONGO_URL')

# connections and usage
client = commands.Bot(command_prefix = '!')
api_instance = giphy_client.DefaultApi()
cluster = MongoClient(MONGO_URL)
db = cluster["minDB"]
collection = db["UserData"]

@client.event
async def on_ready():
	print(f'{client.user} has connected to Discord!')
	
# list of active commands
@client.command()
async def commands(ctx):
	commands = 'ping', '8ball', 'timer'
	await ctx.send(f'List of available commands: {commands}')

# ping pong ping pong
@client.command()
async def ping(ctx):
	await ctx.send(f'pong! {round(client.latency*1000)} ms')
	
# 8ball 
@client.command(aliases=['8ball'])
async def _8ball(ctx, *, question):
	responses = [
	'It is certain',
	'It is decidedly so',
	'Without a doubt',
	'Yes - definitely',
	'You may rely on it',
	'As I see it, yes',
	'Most likely',
	'Outlook good',
	'Signs point to yes',
	'Reply hazy',
	'try again',
	'Ask again later',
	'Better not tell you now',
	'Cannot predict now',
	'Concentrate and ask again',
	'Dont count on it',
	'My reply is no',
	'My sources say no',
	'Outlook not so good',
	'Very doubtful',
	]
	
	await ctx.send(f'{random.choice(responses)}')
	
# timer in minutes (time input is in seconds for asyncio)
@client.command()
async def timer(ctx, time):
	if time.isdigit() :
		await ctx.send(f'Setting a timer for {time} minute(s)')
		await asyncio.sleep(int(time)*60)
		await ctx.send(f'Times up! {time} minute(s) has passed')
		
	else :
		await ctx.send(f'Not a valid value')

# bts giphy thing
@client.command(aliases=['BTS'])
async def bts(ctx):
	gif = await search_gifs('bts')
	await ctx.send(gif)
	
# blackpink giphy thing
@client.command(aliases=['bp, blackpink'])
async def bp(ctx):
	gif = await search_gifs('blackpink')
	await ctx.send(gif)
	
async def search_gifs(query):
	try:
		response = api_instance.gifs_random_get(GIPHY_TOKEN, tag=query)
		return response.data.url
	
	except ApiException as e:
		return "Exception when calling DefaultApi->gifs_random_get: %s\n" % e

# testing mongo db usage with channel messages
@client.event
async def on_message(ctx):
	await client.process_commands(ctx)
	print(f'{ctx.channel}: {ctx.author}: {ctx.author.name}: {ctx.content}')
	query = {"_id": ctx.author.id}
	
	# new entry with score attribute
	if collection.count_documents(query) == 0:
		if "python" in str(ctx.content.lower()):
			post = {"_id": ctx.author.id, "score": 1}
			collection.insert_one(post)
			await ctx.channel.send('accepted!')

	# increment score attribute
	else:
		if "python" in str(ctx.content.lower()):
			user = collection.find(query)
			for result in user:
				score = result["score"]
			score = score + 1
			collection.update_one({"_id": ctx.author.id}, {"$set": {"score":score}})
			await ctx.channel.send('accepted!')		
	
@client.command
async def checkScore(ctx):
		print(f'checking score for {ctx.author.name}')
		query = {"_id": ctx.author.id}

		if collection.count_documents(query):
			get = {"_id": ctx.author.id}
			score = collections.find(get)
			await ctx.send(score['score'])
		
client.run(DISCORD_TOKEN)