from discord.ext import commands
import os

# cog files that will be used to run the bot
# from help_cog import help_cog
# from music_cog import music_cog

# the character used in discord to run the bot itself
bot = commands.Bot(command_prefix="/")

# implement the files themselves into the bot
# bot.add_cog(help_cog(bot))
# bot.add_cog(music_cog(bot))


bot.run(os.getenv("TOKEN"))
