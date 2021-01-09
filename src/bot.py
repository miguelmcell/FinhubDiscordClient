import os
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

bot = commands.Bot(command_prefix='!')

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

@bot.command(name='h', help='We shall see eventually')
async def something_idk(ctx, a_number: int, another: int):
    # print(ctx)
    await ctx.send('hello!'+str(a_number+another))

bot.run(TOKEN)
