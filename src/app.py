import discord
import os
import asyncio
from discord.ext import commands
from dotenv import load_dotenv

bot = commands.Bot(command_prefix= ['-'], intents=discord.Intents.all())

@bot.event
async def on_ready():
    act = discord.Activity(type=discord.ActivityType.listening, name='/help')
    await bot.change_presence(status=discord.Status.dnd, activity=act)
    print("it's working good job")
    try:
        synced_commands = await bot.tree.sync()
        print(f'Synced {len(synced_commands)} commands.')
    except Exception as e:
        print('An error with syncing app commands has occurred.', e)

async def load():
    for filename in os.listdir("./src/data"):
        if filename.endswith(".py"):
            await bot.load_extension(f"data.{filename[:-3]}")

async def main():
    async with bot:
        await load()
        load_dotenv()
        token = os.getenv("token")
        await bot.start(token)

asyncio.run(main())