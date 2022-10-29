import discord
from discord.ext import commands
import os

# cog files that will be used to run the bot
from help_cog import HelpCog
from music_cog import MusicCog

# the character used in discord to run the bot itself
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="/", intents=intents)

# removes the default help command since a custom one is being used for this bot
bot.remove_command("help")

# implement the files themselves into the bot
bot.add_cog(HelpCog(bot))
bot.add_cog(MusicCog(bot))

bot.run(os.getenv("TOKEN"))
