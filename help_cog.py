import discord
from discord.ext import commands


class HelpCog(commands.Cog):
    def __int__(self, bot):
        self.bot = bot

        self.help_message = """
            ```
            General Commands:
            /help - Displays my available commands.
            /p <keyword> - Finds the tracks on YouTube and plays it in your current channel.
            /q - Displays the current playlist.
            /s - Skips the current track.
            /c - Stops the music and clears the playlist.
            /leave - Disconnects me from the channel I currently in.
            /pause - Pause the track being played, resumes if I was paused already.
            /resume - Resumes the playing of the current track.
            ```
        """

        # holds all the text channels that the bot will have access to.
        self.text_channel_text = []

    @commands.Cog.listener()
    async def on_ready(self):
        for guild in self.bot.guilds:
            for channel in guild.text.text_channels:
                self.text_channel_text.append(channel)

        await self.send_to_all(self.help_message)

    async def send_to_all(self, msg):
        for text_channel in self.text_channel_text:
            await text_channel.send(msg)

    @commands.command(name="help", help="Displays my available commands.")
    async def help(self, ctx):
        await ctx.send(self.help_message)
