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

    # defining the play function
    @commands.command(name="play", aliases=["p", "playing"], help="Play the selected song from YouTube.")
    async def play(self, ctx, *args):
        # saving users input to use later as the search parameters
        query = " ".join(args)

        # look for user in which channel they are in
        voice_channel = ctx.author.voice.channel
        # if they are not in a channel then politely inform them to join one
        if voice_channel is None:
            await ctx.send("Connected to a voice channel!")
        elif self.is_paused:
            self.vc.resume()
        else:
            # after correctly searching for their input the `search_yt` is called to begin queueing up the song/s
            song = self.search_yt(query)
            if type(song) is type(True):
                await ctx.send("Could not down the song. Incorrect format, try a different keyword")
            else:
                await ctx.send("Song added to the queue.")
                self.music_queue.append([song, voice_channel])

                if self.is_playing is False:
                    await self.play_music(ctx)

    # defining the pause function
    @commands.command(name="pause", aliases=["p"], help="Pauses the current song being played")
    async def pause(self, ctx, *args):
        # setups up the bot to pause
        if self.is_playing:
            self.is_playing = False
            self.is_paused = True
            self.vc.pause()
        # setups up the bot to resume
        elif self.is_paused:
            self.is_playing = True
            self.is_paused = False
            self.vc.resume()

    # defining the resume function
    @commands.command(name="resume", aliases=["r"], help="Resumes playing the current song.")
    async def resume(self, ctx, *args):
        if self.is_paused:
            self.is_playing = True
            self.is_paused = False
            self.vc.resume()

    # defines the skip function
    @commands.command(name="skip", aliases=["s"], help="Skips the current song.")
    async def skip(self, ctx, *args):
        if self.vc is not None and self.vc:
            self.vc.stop()
            await self.play_music(ctx)

    # defines the queue function
    @commands.command(name="queue", aliases=["q"], help="Displays all the songs currently in the queue.")
    async def queue(self, ctx):
        retval = ""

        for i in range(0, len(self.music_queue)):
            if i > 4: break
            retval += self.music_queue[i][0]["title"] + '\n'

        if retval != "":
            await ctx.send(retval)
        else:
            await ctx.send("No music in the queue.")

    # defines the clear command
    @commands.command(name="clear", aliases=[], help="Stops the current song and clears the queue.")
    async def clear(self, ctx, *args):
        if self.vc is not None and self.is_playing:
            self.vc.stop()
        self.music_queue = []
        await ctx.send("Music queue cleared.")

    # defines the leave command
    @commands.command(name="leave", aliases=["disconnect", "d"], help="Kick the bot from the voice channel.")
    async def leave(self, ctx):
        self.is_playing = False
        self.is_paused = False
        await self.vc.disconnect()
