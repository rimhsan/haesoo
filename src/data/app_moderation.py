import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import Select, Button, View

class moderation(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{__name__} working.")

    @app_commands.command(name="ban", description='Bans a member from the guild')
    @app_commands.checks.has_permissions(ban_members=True)
    async def ban(self, interaction: discord.Interaction, member: discord.Member, reason: str = None):
        reason = reason or "Not specified."
        try:
            await member.ban(reason=reason)
            embed = discord.Embed(color=0x23a55a, description=f"✅ **{member}** was banned. **|** {reason} ")
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            await interaction.response.send_message(e)

    @app_commands.command(name="unban", description='Unbans a member from the guild')
    @app_commands.checks.has_permissions(ban_members=True)
    async def unban(self, interaction: discord.Interaction, member: str, reason: str = None):
        reason = reason or "Not specified."
        banned_users = await interaction.guild.bans()
        member_name, member_discriminator = member.split('#')
        for ban_entry in banned_users:
            user = ban_entry.user
            if (user.name, user.discriminator) == (member_name, member_discriminator):
                await interaction.guild.unban(user)
                embed = discord.Embed(description=f"✅ **{member}** was unbanned. **|** {reason} ")
                await interaction.response.send_message(embed=embed)
                return

    @app_commands.command(name="kick", description='Kicks a member from the guild')
    @app_commands.checks.has_permissions(kick_members=True)
    async def kick(self, interaction: discord.Interaction, member: discord.Member, reason: str = None):
        reason = reason or "Not specified."
        try:
            await member.kick(reason=reason)
            embed = discord.Embed(color=0x23a55a, description=f"✅ **{member}** was kicked. **|** {reason} ")
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            await interaction.response.send_message(e)

    @app_commands.command(name="clear", description='Removes messages')
    @app_commands.checks.has_permissions(manage_messages=True) 
    async def purge(self, interaction: discord.Interaction, amount: int):
        server = interaction.guild
        bot = server.me
        channel = interaction.channel
        if amount <= 0:
            await interaction.response.send_message(
                embed=discord.Embed(color=0xf33e43, description="**You need to specify a number greater than 0.**"), ephemeral=True)
            return
        embed = discord.Embed(color=bot.top_role.color, description=f"**Deleting {amount} messages...**")
        await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=6)
        deleted = await channel.purge(limit=amount)
        embed = discord.Embed(color=0x23a55a, description=f"**Successfully deleted {len(deleted)} messages.**")
        await interaction.edit_original_response(embed=embed)

async def setup(bot):
    await bot.add_cog(moderation(bot))
