import discord
from discord.ext import commands
from discord import app_commands
import aiohttp
import io

class random(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{__name__} working.")

    @app_commands.command(name="dionela", description='marilaaggg')
    async def dionela(self, interaction: discord.Interaction):
        url = 'https://i.scdn.co/image/ab6761610000e5eb50069ac992d74c5610ecb9cc'
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    # Save the image content temporarily in memory
                    image_data = await response.read()
                    # Send the image as a file
                    await interaction.response.send_message(
                        content="Hotshot running in mind nonstop vertigo \nCurled plot whiskey in a teapot ethanol",
                        file=discord.File(fp=io.BytesIO(image_data), filename="image.png")
                    )
                else:
                    await interaction.response.send_message("Failed to fetch the image!")

    @app_commands.command(name="sad", description='huhuhu')
    async def sad(self, interaction: discord.Interaction):
        url = 'https://media4.giphy.com/media/v1.Y2lkPTc5MGI3NjExZTRtd2E3ZjB1aWE0Z25zOGVxajIybmRpeHlxMHdnc3NvYmJ0N2Z3NyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/ISOckXUybVfQ4/giphy.gif'
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    # Save the image content temporarily in memory
                    image_data = await response.read()
                    # Send the image as a file
                    await interaction.response.send_message(
                        content="anong issue ang malungkot? edi imissue :(",
                        file=discord.File(fp=io.BytesIO(image_data), filename="image.png")
                    )
                else:
                    await interaction.response.send_message("Failed to fetch the image!")

    @app_commands.command(name="linyahan", description='Napaka-sadboy')
    async def linyahan(self, interaction: discord.Interaction):
        await interaction.response.send_message(f'*wala na kami bro pero nagpapa-salamat pa rin ako sa kanya kase... \nkahit sa konting panahon i was genuinely happy. <:what:1016599618072625172>*')

    @app_commands.command(name="stats", description='stats sa buhay')
    async def stats(self, interaction: discord.Interaction):
        member = interaction.user
        server = interaction.guild
        bot = server.me
        stats_embeded = discord.Embed(title='2025 stats', color=bot.top_role.color)
        stats_embeded.add_field(name="naagrabyadong tao", value="*3*", inline=False)
        stats_embeded.add_field(name="lambing", value="*0*", inline=False)
        stats_embeded.add_field(name="average hours of sleep", value="*6*", inline=False)
        stats_embeded.set_author(name=f"{member.name}", icon_url=member.avatar.url)
        await interaction.response.send_message(embed=stats_embeded)

async def setup(bot):
    await bot.add_cog(random(bot))
