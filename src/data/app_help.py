import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import Select, Button, View

class dropdown(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Information", emoji="ℹ", value="1"),
            discord.SelectOption(label="Moderation", emoji="⚙", value="2"),
            discord.SelectOption(label="Random", emoji="🌀", value="3"),
            discord.SelectOption(label="Music", emoji="🎶", value="4")  # Added music option
        ]
        super().__init__(placeholder='Select an option...', min_values=1, max_values=1, options=options)
    
    async def callback(self, interaction: discord.Interaction):
        member = interaction.user
        server = interaction.guild
        bot = server.me
        if self.values[0] == "1":
            info_emb = discord.Embed(title="ℹ Information", color=bot.top_role.color)
            info_emb.add_field(name="🔧 `/info`", value="Bot information", inline=True)
            info_emb.add_field(name="🏓 `/ping`", value="Shows latency", inline=True)
            info_emb.add_field(name="🖼 `/avatar [user]`", value="Shows user avatar", inline=True)
            await interaction.response.edit_message(embed=info_emb)
        elif self.values[0] == "2":
            mod_embed = discord.Embed(title="🔧 Moderation", color=bot.top_role.color)
            mod_embed.add_field(name="⛔ `/ban {user} [reason]`", value="Bans a member from the guild", inline=True)
            mod_embed.add_field(name="🌻 `/unban {user} [reason]`", value="Unbans a member from the guild", inline=True)
            mod_embed.add_field(name="🚫 `/kick {user} [reason]`", value="Kicks a member from the guild", inline=True)
            mod_embed.add_field(name="🧹 `/clear {amount}`", value="Removes messages", inline=True)
            await interaction.response.edit_message(embed=mod_embed)
        elif self.values[0] == "3":
            music_embed = discord.Embed(title="🌀 Random", color=bot.top_role.color)
            music_embed.add_field(name="🔥 `/dionela`", value="marilaaggg", inline=True)
            music_embed.add_field(name="☹️ `/sad`", value="huhuhu", inline=True)
            music_embed.add_field(name="📜 `/linyahan`", value="Napaka-sadboy", inline=True)
            music_embed.add_field(name="📈 `/stats`", value="stats sa buhay", inline=True)
            await interaction.response.edit_message(embed=music_embed)
        elif self.values[0] == "4":  # New music option
            music_commands_emb = discord.Embed(title="🎶 Music Commands", color=bot.top_role.color)
            music_commands_emb.add_field(name="▶️ `/play {song}`", value="Play a song", inline=True)
            music_commands_emb.add_field(name="⏸ `/pause`", value="Pause the current song", inline=True)
            music_commands_emb.add_field(name="▶️ `/resume`", value="Resume the paused song", inline=True)
            music_commands_emb.add_field(name="🛑 `/stop`", value="Stop the music and clear the queue", inline=True)
            music_commands_emb.add_field(name="⏩ `/next`", value="Skip to the next song", inline=True)
            await interaction.response.edit_message(embed=music_commands_emb)

class helpview(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(dropdown())  # Adding the dropdown menu to the view

class help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="help", description="Get help 👍")
    async def help(self, interaction: discord.Interaction):
        member = interaction.user
        server = interaction.guild
        bot = server.me
        help_emb = discord.Embed(title='Help', color=bot.top_role.color,
                              description='Select a category in the dropdown menu to get more information about commands.')
        help_emb.add_field(name='Command Syntax', inline=True,
                        value='**`{arg}`** is a required argument\n'
                              '**`[arg]`** is an optional argument')
        help_emb.add_field(name='Links', inline=False,
                        value=f"**[{bot.name}.gg/invite](https://discord.com/api/oauth2/authorize?client_id=1040929438122131517&permissions=2654203206&scope=bot%20applications.commands)**")
        help_emb.set_thumbnail(url=bot.avatar.url)
        help_emb.set_footer(text=f"{member.display_name} | {server.name}",
                         icon_url=member.avatar.url)
        await interaction.response.send_message(embed=help_emb, view=helpview(), ephemeral=True)

async def setup(bot):
    await bot.add_cog(help(bot))
