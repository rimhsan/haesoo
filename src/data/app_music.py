import discord
import os
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
import asyncio
import yt_dlp

# Load environment variables
load_dotenv()

# --- 🎵 yt-dlp Options ---
yt_dl_options = {
    'format': 'bestaudio[fext=webm][acodec=opus][channels=2]/bestaudio[channels=2]/bestaudio',
    'noplaylist': True,
    'quiet': True,
    'default_search': 'ytsearch',
    'source_address': '0.0.0.0',
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'skip_download': True,
    'cookiefile': 'cookies.txt',  # Use cookies to avoid 403
    'extractor_args': {
        'youtube': {
            'key': os.getenv('KEY')  # Use YouTube API key
        }
    },
    'http_headers': {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
    }
}

ytdl = yt_dlp.YoutubeDL(yt_dl_options)

# --- 🔊 FFmpeg Options (High Quality Stereo Audio) ---
ffmpeg_options = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn -c:a libopus -b:a 192k -ac 2 -application audio -vbr on -compression_level 10'
}

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.voice_clients = {}
        self.queues = {}           # Queue: guild_id -> [(url, title)]
        self.text_channels = {}    # Track text channel for follow-up messages
        self.interactions = {}     # Store interaction per guild to access .guild.me

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{__name__} loaded and ready.")

    @app_commands.command(name="play", description="Play a song from a URL or search term")
    async def play(self, interaction: discord.Interaction, query: str):
        """Play a song in the user's voice channel from a URL or search query"""
        try:
            await interaction.response.defer(ephemeral=False)
            if not interaction.user.voice:
                embed = discord.Embed(
                    color=0xf33e43,
                    description="**You need to join a voice channel first.**"
                )
                return await interaction.followup.send(embed=embed, ephemeral=True)

            voice_channel = interaction.user.voice.channel
            guild_id = interaction.guild.id

            # Connect to voice channel
            if guild_id not in self.voice_clients:
                vc = await voice_channel.connect()
                self.voice_clients[guild_id] = vc
            else:
                vc = self.voice_clients[guild_id]

            # Initialize queue and store text channel
            if guild_id not in self.queues:
                self.queues[guild_id] = []
            self.text_channels[guild_id] = interaction.channel
            self.interactions[guild_id] = interaction  # Store for use in play_next_song

            # Handle search vs direct URL
            if not query.startswith("http"):
                query = f"ytsearch:{query}"

            # Extract video info
            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(None, lambda: ytdl.extract_info(query, download=False))

            # Handle search vs direct URL
            if 'entries' in data:
                video = data['entries'][0]  # Take the first result
            else:
                video = data

            song_url = video['url']
            song_title = video['title']

            # Add to queue
            self.queues[guild_id].append((song_url, song_title))

            # Confirm addition
            color = interaction.guild.me.top_role.color
            if color.value == 0:  # Fallback if color is default (black)
                color = 0x00ff88

            queue_embed = discord.Embed(
                color=color,
                description=f"**Added to queue:** {song_title}"
            )
            msg = await interaction.followup.send(embed=queue_embed)
            await asyncio.sleep(6)
            await msg.delete()

            # Play next if not already playing
            if not vc.is_playing() and not vc.is_paused():
                await self.play_next_song(guild_id)

        except Exception as e:
            print(f"Error in play command: {e}")
            embed = discord.Embed(
                color=0xf33e43,
                description="**An error occurred while trying to play the song.**"
            )
            await interaction.followup.send(embed=embed)

    async def play_next_song(self, guild_id):
        """Play the next song in the queue"""
        if guild_id not in self.queues or not self.queues[guild_id]:
            # No more songs, disconnect
            vc = self.voice_clients.get(guild_id)
            if vc:
                await vc.disconnect()
                del self.voice_clients[guild_id]
                del self.queues[guild_id]
                if guild_id in self.text_channels:
                    del self.text_channels[guild_id]
                if guild_id in self.interactions:
                    del self.interactions[guild_id]
            return

        vc = self.voice_clients.get(guild_id)
        if not vc or not vc.is_connected():
            return

        # Get next song
        song_url, song_title = self.queues[guild_id].pop(0)
        try:
            # Re-extract to get direct stream URL and metadata
            info = ytdl.extract_info(song_url, download=False)
            audio_url = info['url']

            # Create high-quality player (stereo)
            player = discord.FFmpegOpusAudio(audio_url, **ffmpeg_options)
            vc.play(player, after=lambda e: self.on_song_end(guild_id))

            # Send "Now Playing" to stored text channel
            text_channel = self.text_channels.get(guild_id)
            if text_channel:
                interaction = self.interactions.get(guild_id)
                if not interaction:
                    # Fallback color if interaction missing
                    color = 0x00ff88
                else:
                    color = interaction.guild.me.top_role.color
                    if color.value == 0:
                        color = 0x00ff88  # Fallback green

                embed = discord.Embed(
                    color=color,
                    description=f"🎧 **Now playing:** {song_title}"
                )
                # Add thumbnail if available
                if 'thumbnail' in info and info['thumbnail']:
                    embed.set_thumbnail(url=info['thumbnail'])
                else:
                    # Optional: Set a fallback thumbnail
                    embed.set_thumbnail(url="https://i.imgur.com/4q2B6AX.png")  # Generic music icon

                embed.set_footer(
                    text=f"{text_channel.guild.name}",
                    icon_url=text_channel.guild.icon.url if text_channel.guild.icon else None
                )
                await text_channel.send(embed=embed)

        except Exception as e:
            print(f"Error playing {song_title}: {e}")
            await self.play_next_song(guild_id)  # Try next

    def on_song_end(self, guild_id):
        """Called when a song finishes. Thread-safe."""
        future = asyncio.run_coroutine_threadsafe(
            self.play_next_song(guild_id),
            self.bot.loop
        )
        try:
            future.result()
        except Exception as e:
            print(f"Error in on_song_end: {e}")

    @app_commands.command(name="pause", description="Pause the current song")
    async def pause(self, interaction: discord.Interaction):
        """Pause the currently playing song"""
        vc = self.voice_clients.get(interaction.guild.id)
        if vc and vc.is_playing():
            vc.pause()
            embed = discord.Embed(color=0xffd700, description="⏸️ **Paused.**")
            await interaction.response.send_message(embed=embed, delete_after=5)
        else:
            embed = discord.Embed(color=0xf33e43, description="**Nothing is playing.**")
            await interaction.response.send_message(embed=embed, delete_after=5)

    @app_commands.command(name="resume", description="Resume the paused song")
    async def resume(self, interaction: discord.Interaction):
        """Resume the currently paused song"""
        vc = self.voice_clients.get(interaction.guild.id)
        if vc and vc.is_paused():
            vc.resume()
            embed = discord.Embed(color=0x00ff88, description="▶️ **Resumed.**")
            await interaction.response.send_message(embed=embed, delete_after=5)
        else:
            embed = discord.Embed(color=0xf33e43, description="**Nothing is paused.**")
            await interaction.response.send_message(embed=embed, delete_after=5)

    @app_commands.command(name="next", description="Skip to the next song in the queue")
    async def next_song(self, interaction: discord.Interaction):
        """Skip to the next song in the queue"""
        await interaction.response.defer()
        vc = self.voice_clients.get(interaction.guild.id)
        if vc and vc.is_playing():
            vc.stop()
            embed = discord.Embed(color=0x00bfff, description="⏭️ **Skipped.**")
            await interaction.followup.send(embed=embed, delete_after=5)
        else:
            embed = discord.Embed(color=0xf33e43, description="**Nothing to skip.**")
            await interaction.followup.send(embed=embed)

    @app_commands.command(name="stop", description="Stop the current song and disconnect the bot")
    async def stop(self, interaction: discord.Interaction):
        """Stop the current song and disconnect the bot"""
        guild_id = interaction.guild.id
        vc = self.voice_clients.get(guild_id)
        if vc:
            self.queues[guild_id].clear()
            vc.stop()
            await vc.disconnect()
            del self.voice_clients[guild_id]
            del self.queues[guild_id]
            if guild_id in self.text_channels:
                del self.text_channels[guild_id]
            if guild_id in self.interactions:
                del self.interactions[guild_id]
            embed = discord.Embed(color=0x7289da, description="⏹️ **Stopped and disconnected.**")
            await interaction.response.send_message(embed=embed)
        else:
            embed = discord.Embed(color=0xf33e43, description="**Not connected to a voice channel.**")
            await interaction.response.send_message(embed=embed, delete_after=5)

    @app_commands.command(name="queue", description="Show the current music queue")
    async def show_queue(self, interaction: discord.Interaction):
        """Show the current music queue"""
        guild_id = interaction.guild.id
        queue = self.queues.get(guild_id, [])
        if not queue:
            embed = discord.Embed(color=0xf33e43, description="**The queue is empty.**")
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        description = ""
        for i, (url, title) in enumerate(queue[:10]):
            description += f"`{i+1}.` {title}\n"
        if len(queue) > 10:
            description += f"\n*... and {len(queue) - 10} more.*"

        color = interaction.guild.me.top_role.color
        if color.value == 0:
            color = 0x00ff88

        embed = discord.Embed(
            title="🎵 Music Queue",
            description=description,
            color=color
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot):
    await bot.add_cog(Music(bot))