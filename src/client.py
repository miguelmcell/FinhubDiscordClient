import os
import discord

from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

# intents = discord.Intents(messages=True, guilds=True)
intents = discord.Intents.default()
intents.typing = False
intents.presences = False
intents.members = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    global guild
    print('we have logged in as {0.user}'.format(client))
    guild = discord.utils.get(client.guilds, name=GUILD)
    members = '\n - '.join([member.name for member in guild.members])
    print(f'Guild Members:\n - {members}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    global guild
    is_dm = not message.guild

    if message.content.startswith('h'):
        # real_user = discord.utils.get(guild.members, name='judgemental_walrus')
        # print(real_user.id == message.author.id)
        await message.channel.send('user is {} and is dm is {}'.format(message.author.name, is_dm))
        # await mig.create_dm()
        # await mig.dm_channel.send(f'Hi {mig.name}, hello!')
    if 'error' in message.content:
        raise discord.DiscordException

@client.event
async def on_error(event, *args, **kwargs):
    if event == 'on_message':
        print(f'Unhandled message: {args[0]}\n')
    else:
        raise

client.run(TOKEN)
