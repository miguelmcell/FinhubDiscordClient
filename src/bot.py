import os
import json
import requests
from discord.ext import commands
from dotenv import load_dotenv
import discord

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
ENVIRONMENT = os.getenv('ENVIRONMENT')
ENDPOINTS = {}
endpoints_path = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))),'resources','endpoints.json')

intents = discord.Intents.default()
intents.typing = False
intents.presences = False
intents.members = True
help_command = commands.DefaultHelpCommand(
    no_category = 'Commands'
)
bot = commands.Bot(command_prefix='!', intents =intents, help_command = help_command)

def setup_init():
    ### Loading endpoints file
    global ENDPOINTS
    with open(endpoints_path) as file:
        data = file.read()
    ENDPOINTS = json.loads(data)

def is_dm(ctx):
    return not ctx.message.guild
### Check and handle any non-200 responses
async def handle_api_response(ctx, r):
    if r is None:
        print('couldnt contact server')
    if r.status_code == 200:
        return r
    elif r.status_code == 401:
        print('[401] Unauthorized request:', r)
        await ctx.send('[401] Unauthorized request 🔒')
    else:
        print(r)
        print('Other: response code:', r.status_code)
    return None
### Run get request while handling errors
async def call_get_request(ctx, url, params={}, headers={}):
    r = None
    try:
        r = requests.get(url = url, params = params, headers=headers)
    except Exception as e:
        if 'Max retries exceeded with url' in str(e):
            await ctx.send('Hello anyone there? 👀 👀 👀 [Unable to contact backend]')
        else:
            print(e)
            await ctx.send('Unknown exception for API call request, check logs')
    return r
### Run get request while handling errors
async def call_post_request(ctx, url, data={}):
    r = None
    try:
        r = requests.post(url = url, json = data)
    except Exception as e:
        if 'Max retries exceeded with url' in str(e):
            await ctx.send('Hello anyone there? 👀 👀 👀 [Unable to contact backend]')
        else:
            print(e)
            await ctx.send('Unknown exception for API post request, check logs')
    return r

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

@bot.command(name='health', help='[SERVER ONLY] Provides status of finhub backend')
async def check_health(ctx):
    if is_dm(ctx):
        await ctx.send('cant call this command in DM')
        return
    url = ENDPOINTS[ENVIRONMENT]['host']+ENDPOINTS[ENVIRONMENT]['finhub_test_status']
    r = await call_get_request(ctx, url)
    if await handle_api_response(ctx, r) is None:
        return
    ### r should now be a valid response
    if r.json() == 'OK':
        await ctx.send('Finhub is active ✅')
    else:
        await ctx.send('Unexpected response from finhub status')

@bot.command(name='signUp', help='[SERVER ONLY] Signs up the user to the server\'s finhub group')
async def signup_user(ctx):
    if is_dm(ctx):
        await ctx.send('cant call this command in DM')
        return
    url = ENDPOINTS[ENVIRONMENT]['host']+ENDPOINTS[ENVIRONMENT]['finhub_signup_user']
    data = {}

    data['discordId'] = ctx.message.author.id
    data['guildId'] = ctx.message.guild.id
    data['guildName'] = ctx.message.guild.name
    r = await call_post_request(ctx, url, data)
    if await handle_api_response(ctx, r) is None:
        return
    ## r should now be a valid response
    if 'Existing user added to new finhub group' in r.content.decode('utf-8'):
        print('Succesfully added {} '.format(ctx.message.author.name))
        await ctx.send('Successfully added {} to **{}**\'s finhub group 🎉 💯 🗣️'.format(ctx.message.author.name, ctx.message.guild.name))
    elif 'User already in given finhub group' in r.content.decode('utf-8'):
        print('{} is already in **{}**\'s finhub group'.format(ctx.message.author.name, ctx.message.guild.name))
        await ctx.send('{} is already in **{}**\'s finhub group 🤷'.format(ctx.message.author.name, ctx.message.guild.name))
    elif 'OK' in r.content.decode('utf-8'):
        print('Succesfully signed up {}'.format(ctx.message.author.name))
        await ctx.message.author.create_dm()
        await ctx.message.author.dm_channel.send(f'Yo, if this is your first'\
            ' time signing up for a finhub account type `!help` in this DM to'\
            ' learn how to sync your brokers into your account.\nIf you\'ve'\
            ' already configured your brokers for another discord server that'\
            ' uses finhub then you\'re already set\n**I recommend deleteting'\
            ' your sensitive broker credentials once your broker account'\
            ' has synced**')
        await ctx.send('Successfully signed up {} to **{}**\'s finhub group 🎉 💯 🗣️\nI DMd you instructions on how to configure your brokers on your account'.format(ctx.message.author.name, ctx.message.guild.name))
    else:
        print('Unkown response from signup: {}, {}'.format(r, r.content.decode('utf-8')))


@bot.command(name='listUsers', help='[SERVER ONLY] Lists all active finhub users within server')
async def list_users(ctx):
    if is_dm(ctx):
        await ctx.send('cant call this command in DM')
        return
    url = ENDPOINTS[ENVIRONMENT]['host']+ENDPOINTS[ENVIRONMENT]['finhub_list_users']
    headers = {"guildId": str(ctx.message.guild.id)}
    r = await call_get_request(ctx, url, headers=headers)
    if await handle_api_response(ctx, r) is None:
        return
    ### r should now be a valid response
    r = r.json()
    if len(r) == 0:
        await ctx.send('No active finhub members in **{}** 😔'.format(ctx.message.guild.name))
        return
    # Map IDs to user names
    guild_members = {}
    for member in  ctx.guild.members:
        guild_members[str(member.id)] = member.name
    response = 'Active finhub members in **{}**:'.format(ctx.message.guild.name)
    for i in r:
        response = response + '\n\t• {}'.format(guild_members[i.strip('\'')])
    await ctx.send(response)

setup_init()
bot.run(TOKEN)
