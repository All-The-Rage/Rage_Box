import discord
import os
from discord.ext import commands
from dotenv import load_dotenv

# cog files that will be used to run the bot
from help_cog import help_cog
from music_cog import music_cog

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

# the character used in discord to run the bot itself
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!")

# removes the default help command since a custom one is being used for this bot
bot.remove_command('help')


@bot.event
async def on_ready():
    print('--------------------')
    print('This bot is in use.')
    await bot.add_cog(help_cog(bot))
    await bot.add_cog(music_cog(bot))

# if __name__ == '__main__':
#     # implement the files themselves into the bot
#

bot.run(token)
