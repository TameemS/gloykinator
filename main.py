import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import logging
from googletrans import Translator
from discord import Webhook
import aiohttp

load_dotenv()
logger = logging.getLogger("discord")

intents = discord.Intents(guilds=True, messages=True, message_content=True, voice_states=True)
bot = commands.Bot(command_prefix=commands.when_mentioned_or("!"), intents=intents)
token = os.getenv("TOKEN")
t = Translator()

@bot.event
async def on_ready():
    logger.info(f"Logged in as {bot.user}")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        logger.info(f"message {message.id} is from the bot itself")
        return
    
    logger.info(f"translating message {message.id}")
    translated = t.translate(message.content, dest='en')

    if translated.src == "en":
        logger.info(f"translation of {message.id} not needed")
        return
    else:
        wh_url = await message.channel.webhooks()
        if wh_url == []:
            logger.info(f"no webhooks for channel {message.channel.id}")
            return
        wh_url = wh_url[0].url

        async with aiohttp.ClientSession() as session:
            webhook = Webhook.from_url(wh_url, session=session)
            if message.author.id != webhook.id:
                logger.info(f"message {message.id} translated")
                formatted = f"{message.content}\n-# `{translated.src} -> en` {translated.text}"
                
                await message.delete()
                await webhook.send(formatted, username=message.author.name, avatar_url=message.author.avatar.url)
            else:
                logger.info(f"message {message.id} is from webhook")

bot.run(token)
