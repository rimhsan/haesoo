import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import yt_dlp

# YouTube-DL Options
yt_dl_options = {"format": "bestaudio/best"}
ytdl = yt_dlp.YoutubeDL(yt_dl_options)

# FFmpeg Options
ffmpeg_options = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.voice_clients = {}
        self.queues = {}  # This will store queues for each guild

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{__name__} working.")

    @app_commands.command(name="play", description="Play a song from a URL or search term")
    async def play(self, interaction: discord.Interaction, query: str):
        """Play a song in the user's voice channel from a URL or search query"""
        try:
            print("Received play command.")
            
            # Immediately acknowledge the interaction (this prevents timeout)
            await interaction.response.defer(ephemeral=False)

            # Check if the query is a valid URL
            if not query.startswith("http"):
                query = f"ytsearch:{query}"  # Treat the query as a YouTube search
            
            # Make sure the user is connected to a voice channel
            if not interaction.user.voice:
                error_embed = discord.Embed(color=0xf33e43, description="**You need to join a voice channel first.**")
                await interaction.followup.send(embed=error_embed)
                return

            # Get the voice channel the user is in
            voice_channel = interaction.user.voice.channel
            
            # Get the current voice client
            voice_client = interaction.guild.voice_client
            
            # If there's no voice client, or the bot isn't playing, connect
            if not voice_client:
                voice_client = await voice_channel.connect()
                self.voice_clients[interaction.guild.id] = voice_client
            
            # Create a queue for this guild if it doesn't exist
            if interaction.guild.id not in self.queues:
                self.queues[interaction.guild.id] = []

            # Get song info from the URL (or search) using yt-dlp
            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(None, lambda: ytdl.extract_info(query, download=False))

            # If we searched for a song, extract the URL from the first result
            if 'entries' in data:
                song_url = data['entries'][0]['url']
                song_title = data['entries'][0]['title']
            else:
                song_url = data['url']
                song_title = data['title']

            # Add the song to the queue
            self.queues[interaction.guild.id].append((song_url, song_title))

            # Send the "Added to Queue" message and delete it after 6 seconds
            queue_embed = discord.Embed(
                color=interaction.guild.me.top_role.color,
                description=f"**Added to queue:** {song_title}"
            )
            msg = await interaction.followup.send(embed=queue_embed)  
            await asyncio.sleep(6)  # Wait for 6 seconds before deleting the message
            await msg.delete()  # Delete the "Added to Queue" message after 6 seconds

            # If the bot isn't already playing, start playing the next song
            if not voice_client.is_playing():
                await self.play_next_song(interaction.guild.id, interaction)  # Pass the interaction to play_next_song

        except Exception as e:
            print(f"Error in play command: {e}")
            error_embed = discord.Embed(color=0xf33e43, description="**An error occurred while trying to play the song.**")
            await interaction.followup.send(embed=error_embed)

    async def play_next_song(self, guild_id, interaction):
        """Play the next song in the queue"""
        if guild_id in self.queues and self.queues[guild_id]:
            voice_client = self.voice_clients.get(guild_id)
            if voice_client:
                song_url, song_title = self.queues[guild_id].pop(0)  # Get the first song in the queue
                player = discord.FFmpegOpusAudio(song_url, **ffmpeg_options)
                voice_client.play(player, after=lambda e: self.on_song_end(guild_id))  # Play the song
                print(f"Now playing: {song_title}")

                # Send Now Playing embed independently
                server = interaction.guild
                member = interaction.user
                now_playing_embed = discord.Embed(
                    color=interaction.guild.me.top_role.color,
                    description=f"**Now playing:** {song_title}"
                )
                now_playing_embed.set_footer(
                    text=f"{member.display_name} | {server.name}",
                    icon_url=member.avatar.url if member.avatar else None
                )
                await interaction.followup.send(embed=now_playing_embed)  # Send the embed to the same channel
        else:
            # If there are no more songs in the queue, disconnect
            voice_client = self.voice_clients.get(guild_id)
            if voice_client:
                await voice_client.disconnect()
                del self.voice_clients[guild_id]
                del self.queues[guild_id]

    def on_song_end(self, guild_id):
        """Called when a song ends. Plays the next song in the queue."""
        asyncio.run_coroutine_threadsafe(self.play_next_song(guild_id), self.bot.loop)

    @app_commands.command(name="pause", description="Pause the current song")
    async def pause(self, interaction: discord.Interaction):
        """Pause the currently playing song"""
        try:
            voice_client = self.voice_clients.get(interaction.guild.id)
            if voice_client and voice_client.is_playing():
                voice_client.pause()
                pause_embed = discord.Embed(
                    color=interaction.guild.me.top_role.color,
                    description="**Playback paused.**"
                )
                await interaction.response.send_message(embed=pause_embed)
            else:
                error_embed = discord.Embed(
                    color=0xf33e43,
                    description="**No song is currently playing.**"
                )
                await interaction.response.send_message(embed=error_embed, delete_after=6)
        except Exception as e:
            print(f"Error in pause command: {e}")
            error_embed = discord.Embed(
                color=0xf33e43,
                description="**An error occurred while trying to pause the song.**"
            )
            await interaction.response.send_message(embed=error_embed, delete_after=6)

    @app_commands.command(name="resume", description="Resume the paused song")
    async def resume(self, interaction: discord.Interaction):
        """Resume the currently paused song"""
        try:
            voice_client = self.voice_clients.get(interaction.guild.id)
            if voice_client and voice_client.is_paused():
                voice_client.resume()
                resume_embed = discord.Embed(
                    color=interaction.guild.me.top_role.color,
                    description="**Playback resumed.**"
                )
                await interaction.response.send_message(embed=resume_embed)
            else:
                error_embed = discord.Embed(
                    color=0xf33e43,
                    description="**No song is currently paused.**"
                )
                await interaction.response.send_message(embed=error_embed, delete_after=6)
        except Exception as e:
            print(f"Error in resume command: {e}")
            error_embed = discord.Embed(
                color=0xf33e43,
                description="**An error occurred while trying to resume the song.**"
            )
            await interaction.response.send_message(embed=error_embed, delete_after=6)

    @app_commands.command(name="next", description="Skip to the next song in the queue")
    async def next_song(self, interaction: discord.Interaction):
        """Skip to the next song in the queue"""
        try:
            voice_client = self.voice_clients.get(interaction.guild.id)

            if voice_client:
                if self.queues.get(interaction.guild.id):
                    # Defer the response first
                    await interaction.response.defer()

                    # Stop the current song and play the next one
                    voice_client.stop()  # Stop the current song
                    await self.play_next_song(interaction.guild.id, interaction)  # Pass the interaction to play_next_song

                    next_embed = discord.Embed(
                        color=interaction.guild.me.top_role.color,
                        description="**Skipping to the next song.**"
                    )
                    await interaction.followup.send(embed=next_embed, delete_after=6)
                else:
                    # No songs in the queue, disconnect
                    await voice_client.disconnect()
                    del self.voice_clients[interaction.guild.id]
                    del self.queues[interaction.guild.id]

                    error_embed = discord.Embed(
                        color=0xf33e43,
                        description="**There are no songs left in the queue. Disconnected.**"
                    )
                    await interaction.followup.send(embed=error_embed)
            else:
                error_embed = discord.Embed(
                    color=0xf33e43,
                    description="**No song is currently playing.**"
                )
                await interaction.response.send_message(embed=error_embed, delete_after=6)
        except Exception as e:
            print(f"Error in next command: {e}")
            error_embed = discord.Embed(
                color=0xf33e43,
                description="**An error occurred while trying to skip to the next song.**"
            )
            await interaction.response.send_message(embed=error_embed, delete_after=6)

    @app_commands.command(name="stop", description="Stop the current song and disconnect the bot")
    async def stop(self, interaction: discord.Interaction):
        """Stop the current song and disconnect the bot"""
        try:
            voice_client = self.voice_clients.get(interaction.guild.id)
            if voice_client:
                voice_client.stop()  # Stop the song
                await voice_client.disconnect()  # Disconnect from the voice channel
                del self.voice_clients[interaction.guild.id]
                del self.queues[interaction.guild.id]

                stop_embed = discord.Embed(
                    color=interaction.guild.me.top_role.color,
                    description="**Playback stopped and disconnected.**"
                )
                await interaction.response.send_message(embed=stop_embed)
            else:
                error_embed = discord.Embed(
                    color=0xf33e43,
                    description="**No song is currently playing.**"
                )
                await interaction.response.send_message(embed=error_embed, delete_after=6)
        except Exception as e:
            print(f"Error in stop command: {e}")
            error_embed = discord.Embed(
                color=0xf33e43,
                description="**An error occurred while trying to stop the song.**"
            )
            await interaction.response.send_message(embed=error_embed, delete_after=6)

async def setup(bot):
    await bot.add_cog(Music(bot))