import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import Select, Button, View

class information(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{__name__} working.")

    @app_commands.command(name="info", description="Bot information")
    async def info(self, interaction: discord.Interaction):
        server = interaction.guild
        bot = server.me
        member = interaction.user
        servercount = len(self.bot.guilds)
        info_emb = discord.Embed(color=bot.top_role.color, title=f"{bot.name}")
        info_emb.set_thumbnail(url=bot.avatar.url)
        info_emb.add_field(name="<:book:1004359059723530250> Library", value="discord.py", inline=True)
        info_emb.add_field(name="<:developer:1004358534714105947> Dev", value="rimhsan", inline=True)
        info_emb.add_field(name="Invite", value=f"**[{bot.name}.gg/invite](https://discord.com/api/oauth2/authorize?client_id=1040929438122131517&permissions=2654203206&scope=bot%20applications.commands)**", inline=True)
        await interaction.response.send_message(embed=info_emb)

    @app_commands.command(name="ping", description='Shows latency')
    async def ping(self, interaction: discord.Interaction):
        await interaction.response.send_message(f":ping_pong: **Pong!** `{round(self.bot.latency * 1000)}ms`")

    @app_commands.command(name="avatar", description='Shows user avatar')
    async def avatar(self, interaction: discord.Interaction, member: discord.Member = None):
        server = interaction.guild
        bot = server.me
        member = member or interaction.user
        avatar_emb = discord.Embed(color=bot.top_role.color)
        avatar_emb.set_image(url=member.avatar.url)
        avatar_emb.set_author(name=f"{member.display_name}'s Avatar",
            icon_url= member.avatar.url)
        avatar_emb.set_footer(text=f"Try mentioning friends using this command!")
        await interaction.response.send_message(embed=avatar_emb)

async def setup(bot):
    await bot.add_cog(information(bot))
