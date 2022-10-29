import discord
from discord.ext import commands

from youtube_dl import YoutubeDL


class MusicCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # Specify the state the bot is in
        self.is_playing = False
        self.is_paused = False

        # This holds anything that has been queued by the user
        self.music_queue = []

        # Defines quality options
        self.YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'Tree'}
        self.FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnected_streamed 1 -reconnected_delay_max_5', 'options': '-vn'}

        self.vc = None

    # searches YouTube using the input from the user
    def search_yt(self, item):
        with YoutubeDL(self.YDL_OPTIONS) as yd1:
            try:
                # does not download but searches for the video only
                info = yd1.extract_info('ytsearch:%s' % item, download=False)['entries'][0]
            except Exception:
                return False
        return {'source': info['format'][0]['url'], 'title': info['title']}

    # queues up and plays next song
    def play_next(self):
        if len(self.music_queue) > 0:
            self.is_playing = True

            m_url = self.music_queue.pop(0)

            self.music_queue.pop(0)

            # this is a recursive function that continues to execute on the queue until the queue is empty
            self.vc.play(discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS), after=lambda e: self.play_next())
        else:
            self.is_playing = False

    # checks if bot is in voice channel
    async def play_music(self, ctx):
        if len(self.music_queue) > 0:
            self.is_playing = True
            m_url = self.music_queue[0][0]['source']

            # confirms on if it is VC or not
            if self.vc is None or not self.vc.is_connected():
                self.vc = await self.music_queue[0][1].connect()
                # if it is not then it sends an error to the user that it cannot join
                if self.vc is None:
                    await ctx.send('Count not connect to the voice channel.')
                    return
            else:
                await self.vc.move_to(self.music_queue[0][1])

            self.music_queue.pop(0)

            self.vc.play(discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS), after=lambda e: self.play_next())

        else:
            self.is_playing = False
