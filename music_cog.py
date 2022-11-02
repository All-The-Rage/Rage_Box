import discord
from discord.ext import commands
from youtube_dl import YoutubeDL


class music_cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # all the music related stuff
        self.is_playing = False
        self.is_paused = False

        # 2d array containing [song, channel]
        self.music_queue = []
        self.YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'True'}
        self.FFMPEG_OPTIONS = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
            'options': '-vn'}

        self.vc = None

    # searches YouTube using the input from the user
    def search_yt(self, item):
        with YoutubeDL(self.YDL_OPTIONS) as ydl:
            try:
                info = ydl.extract_info("ytsearch:%s" % item, download=False)['entries'][0]
            except ValueError:
                return False

        return {'source': info['formats'][0]['url'], 'title': info['title']}

    # queues up and plays next song
    def play_next(self):
        if len(self.music_queue) > 0:
            self.is_playing = True

            m_url = self.music_queue[0][0]['source']

            self.music_queue.pop(0)

            # this is a recursive function that continues to execute on the queue until the queue is empty
            self.vc.play(discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS),
                         after=lambda e: self.play_next())
        else:
            self.is_playing = False

    # checks if bot is in voice channel
    async def play_music(self, ctx):
        if len(self.music_queue) > 0:
            self.is_playing = True

            m_url = self.music_queue[0][0]['source']

            # try to connect to voice channel if you are not already connected
            if self.vc is None or not self.vc.is_connected():
                self.vc = await self.music_queue[0][1].connect()

                # in case we fail to connect
                if self.vc is None:
                    await ctx.send("Could not connect to the voice channel")
                    return
            else:
                await self.vc.move_to(self.music_queue[0][1])

            # remove the first element as you are currently playing it
            self.music_queue.pop(0)

            self.vc.play(discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS),
                         after=lambda e: self.play_next())
        else:
            self.is_playing = False

    # defining the play function
    @commands.command(name="play", aliases=["playing"],
                      help="Find the track on YouTube and play it in your channel.")
    async def play(self, ctx, *args):
        query = " ".join(args)

        voice_channel = ctx.author.voice.channel
        if voice_channel is None:
            # you need to be connected so that the bot knows where to go
            await ctx.send("Connect to a voice channel!")
        elif self.is_paused:
            self.vc.resume()
        else:
            song = self.search_yt(query)
            if type(song):
                await ctx.send(
                    "Could not download the song. Incorrect format try another keyword. This could be due to playlist or a livestream format.")
            else:
                await ctx.send("Song added to the queue")
                self.music_queue.append([song, voice_channel])

                if not self.is_playing:
                    await self.play_music(ctx)

    # defining the pause function
    @commands.command(name="pause", aliases=["p"],
                      help="Pause the track being played, resumes if I was paused already.")
    async def pause(self, ctx, *args):
        # setups up the bot to pause
        if self.is_playing:
            self.is_playing = False
            self.is_paused = True
            self.vc.pause()
        # setups up the bot to resume
        elif self.is_paused:
            self.is_paused = False
            self.is_playing = True
            self.vc.resume()

    # defining the resume function
    @commands.command(name="resume", aliases=["r"], help="Resumes playing the current song.")
    async def resume(self, ctx, *args):
        if self.is_paused:
            self.is_paused = False
            self.is_playing = True
            self.vc.resume()

    # defines the skip function
    @commands.command(name="skip", aliases=["s"], help="Skips the current track.")
    async def skip(self, ctx):
        if self.vc is not None and self.vc:
            self.vc.stop()
            await self.play_music(ctx)

    # defines the queue function
    @commands.command(name="queue", aliases=["q"], help="Displays the current playlist.")
    async def queue(self, ctx):
        retval = ""
        for i in range(0, len(self.music_queue)):
            # display a max of 5 songs in the current queue
            if i > 4:
                break
            retval += self.music_queue[i][0]['title'] + "\n"

        if retval != "":
            await ctx.send(retval)
        else:
            await ctx.send("No music in queue")

    # defines the clear command
    @commands.command(name="clear", aliases=["c"], help="Stops the music and clears the playlist.")
    async def clear(self, ctx):
        if self.vc is not None and self.is_playing:
            self.vc.stop()
        self.music_queue = []
        await ctx.send("Music queue cleared.")

    # defines the leave command
    @commands.command(name="leave", aliases=["disconnect", "d"],
                      help="Disconnects me from the channel I currently in.")
    async def leave(self, ctx):
        self.is_playing = False
        self.is_paused = False
        await self.vc.disconnect()
